 <template>
  <div class="image-display">
  <div class="messages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="{'message-user': message.type === 'user', 'message-image': message.type === 'image', 'message-thinking': message.type === 'thinking'}"
      >
        <img v-if="message.type === 'image'" :src="message.content" alt="Generated Image" />
        <span v-else>{{ message.content }}</span>
      </div>
    </div>
    <div class="input-container">
      <textarea v-model="userInput" placeholder="我想生成的图片是"></textarea>
      <button @click="fetchImage">生成图片</button>
    </div>
    <button @click="toggleKeywords">关键词</button>
    <div class="keywords-list" v-if="showKeywords">
      <p v-for="(keyword, index) in keywords" :key="index" class="keyword">
        {{ keyword }} <button @click="removeKeyword(index)">移除</button>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  props: ['imagePrompt', 'keywords'],
  data() {
    return {
      userInput: this.imagePrompt,
      messages: [],
      imageUrl: '',
      thinkingMessageId: null,
      showKeywords: true
    };
  },
  methods: {
    async fetchImage() {
      if (!this.userInput.trim()) {
        return;
      }
      // Add user message
      this.messages.push({ type: 'user', content: this.userInput });
      const userInput = this.userInput;
      this.userInput = ''; // Clear input field

      // Add thinking message
      const thinkingMessage = { type: 'thinking', content: '图片生成中...' };
      this.messages.push(thinkingMessage);
      this.thinkingMessageId = this.messages.length - 1; // Save thinking message index

      try {
        const response = await fetch('http://localhost:8300/image/false', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ user_prompt: userInput })
        });
        const data = await response.json();
        this.imageUrl = data.image_url;

        // Remove thinking message
        if (this.thinkingMessageId !== null) {
          this.messages.splice(this.thinkingMessageId, 1);
          this.thinkingMessageId = null;
        }

        // Add image message
        this.messages.push({ type: 'image', content: this.imageUrl });

      } catch (error) {
        console.error('Error fetching image:', error);
      }
    },
    removeKeyword(index) {
      this.$emit('remove-keyword', index);
    },
    toggleKeywords() {
      this.showKeywords = !this.showKeywords; // Toggle the visibility of keywords
    },
  },
  watch: {
    imagePrompt(newVal) {
      this.userInput = newVal; // Update userInput whenever imagePrompt changes
    }
  },
  mounted() {
    // Make keywords accessible in the browser's console for debugging
    window.img_keywords = this.keywords;
  }
}
</script>

<style scoped>
.image-display img {
  max-width: 100%;
  border-radius: 4px;
  margin-top: 20px;
}

.input-container {
  display: flex;
  align-items: flex-start;
  padding: 10px;
  background: white;
  border-top: 1px solid #e0e0e0;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
}
.message-user,
.message-image,
.message-thinking {
  display: inline-block;
  position: relative;
  margin: 10px 0;
  padding: 10px;
  border-radius: 15px;
  max-width: 70%;
  word-wrap: break-word;
  color: #000;
  font-family: 'Helvetica', 'Arial', sans-serif;
}

.message-thinking {
  background: #ffffff;
  margin-right: auto;
  border-top-left-radius: 0;
}

.message-user {
  background: #DCF8C6;
  margin-left: auto;
  border-top-right-radius: 0;
}

.message-image img {
  max-width: 100%;
  border-radius: 4px;
}

.keyword {
  color: #000000; /* 设置关键词颜色为黑色 */
}
</style>
