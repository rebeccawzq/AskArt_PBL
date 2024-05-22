 <template>
  <div class="image-display">
  <div class="messages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="{'message-user': message.type === 'user', 'message-image': message.type === 'image', 'message-thinking': message.type === 'thinking'}"
      >
        <img v-if="message.type === 'image'" :src="message.content" alt="Generated Image" class="fixed-image-size"/>
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
import timeoutImage from '../assets/timeout.png';
import errorImage from '../assets/error.png';
export default {
  props: ['imagePrompt', 'keywords'],
  data() {
    return {
      userInput: this.imagePrompt,
      messages: [],
      imageUrl: '',
      thinkingMessageId: null,
      showKeywords: true,
      localStorageKey: 'img-messages',
      messageCounter: 0,
    };
  },
  methods: {
    saveMessageToLocalStorage(message) {
      const savedMessages = JSON.parse(localStorage.getItem(this.localStorageKey)) || [];
      savedMessages.push(message);
      localStorage.setItem(this.localStorageKey, JSON.stringify(savedMessages));
      window.savedMessages = savedMessages;
    },
    loadMessagesFromLocalStorage() {
      const savedMessages = localStorage.getItem(this.localStorageKey);
      if (savedMessages) {
        try {
          // only load the first 4 messages
          this.messages = JSON.parse(savedMessages).slice(-10);
          this.messageCounter = this.messages[this.messages.length - 1].id + 1;
        } catch (e) {
          console.error('Error parsing JSON from localStorage:', e);
          this.messages = [];
        }
      }
    },
    async fetchImage() {
      if (!this.userInput.trim()) {
        return;
      }
      // Add user message
      const userMessage = { id: this.messageCounter++, type: 'user', content: this.userInput };
      this.messages.push(userMessage);
      // if keyword is not empty, add it to user message
      if (this.keywords.length > 0) {
        userMessage.keywords = this.keywords;
      }
      this.saveMessageToLocalStorage(userMessage);
      const userInput = this.userInput;
      this.userInput = ''; // Clear input field

      // Add thinking message
      const thinkingMessage = { id: this.messageCounter++, type: 'thinking', content: '图片生成中...' };
      this.messages.push(thinkingMessage);
      this.thinkingMessageId = thinkingMessage.id;

      const timeout = 10000; // 10 seconds timeout
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Request timed out')), timeout)
      );
      try {
        const response = await Promise.race([
          fetch('http://localhost:8300/image/false', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_prompt: userInput, key_words: this.keywords })
          }),
          timeoutPromise
        ]);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        this.imageUrl = data.image_url;

        // Remove thinking message
        const index = this.messages.findIndex(message => message.id === this.thinkingMessageId);
        if (index !== -1) {
          this.messages.splice(index, 1);
        }

        // Add image message
        const imageMessage = { id: this.messageCounter++, type: 'image', content: this.imageUrl };
        this.messages.push(imageMessage);
        this.saveMessageToLocalStorage(imageMessage);

      } catch (error) {
        console.error('Error fetching image:', error);

        // Remove thinking message
        const index = this.messages.findIndex(message => message.id === this.thinkingMessageId);
        if (index !== -1) {
          this.messages.splice(index, 1);
        }

        // Add error or timeout image
        const errorMessage = {
          id: this.messageCounter++,
          type: 'image',
          content: error.message === 'Request timed out' ? timeoutImage : errorImage
        };
        this.messages.push(errorMessage);
        this.saveMessageToLocalStorage(errorMessage);
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
    const savedMessages = localStorage.getItem(this.localStorageKey);
    if (!savedMessages || savedMessages === '[object Object]') {
        localStorage.setItem(this.localStorageKey, JSON.stringify([]));
    } else {
        // this.loadMessagesFromLocalStorage();
    }
  }
}
</script>

<style scoped>
.fixed-image-size {
  width: 256px;
  height: 256px;
  object-fit: cover; /* Ensure the image covers the area without distortion */
}
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
