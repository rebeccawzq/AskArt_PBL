<template>
  <div class="image-display">
    <div class="messages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.type === 'user' ? 'message-user' : '', message.type === 'image' ? 'message-image' : '', message.type === 'thinking' ? 'message-thinking' : '', message.className ? message.className : '']"
      >
        <img v-if="message.type === 'image'" :src="message.content" alt="Generated Image" class="fixed-image-size"/>
        <span v-else v-html="message.content"></span>
      </div>
    </div>
    <div class="input-container-wrapper">
      <div class="keywords-container">
        <div class="keywords-list">
          <div v-for="(keyword, index) in keywords" :key="index" class="keyword">
              <span class="keyword-text">{{ keyword }}</span>
              <span class="close-button" @click="removeKeyword(index)">x</span>
          </div>
        </div>
      </div>
      <div class="input-container">
        <textarea v-model="userInput" placeholder="我想生成的图片是"></textarea>
        <button @click="fetchImage">生成图片</button>
      </div>
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
      messages: [], // todo: limit the length of messages
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

      const timeout = 20000;
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Request timed out')), timeout)
      );
      try {
        const response = await Promise.race([
          fetch('http://18.223.254.93/backend/image/false', {
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
const start_msg = { id: this.messageCounter++, type: 'ai', content: '哈喽👋我是你的小画师，有什么想画的都可以告诉我！<br>' +
    '你可以说：<br>' +
    '绘制螭吻龙，表现它在吞食东西，装饰在古代建筑的脊尾上。<br>' +
    '如果你和智囊团在聊天的时候提到了想画出来的东西，可以选中聊天记录后点击右键，通过生成图片/添加为修饰语告诉我哦🎨', className: 'start-message' };
  this.messages.push(start_msg);
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

.start-message {
  color: black;
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

.input-container-wrapper {
  display: flex;
  flex-direction: column;
  background: #f9f9f9;
}
.keywords-container {
  display: flex;
  justify-content: flex-start;
  background: #f9f9f9;
  padding: 10px;
}

.keywords-list {
  display: flex;
  flex-direction: row; /* Display items in a row */
  flex-wrap: wrap; /* Allow items to wrap to the next line */
  gap: 5px; /* Add space between items */
  align-items: flex-end; /* Align items at the top */
  height: 180px;
}

.keyword {
  position: relative;
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  margin: 5px;
  background: #f0f4ff; /* 背景颜色 */
  border-radius: 15px; /* 圆角 */
  border: 1px solid #d0d7ff; /* 边框颜色 */
  font-size: 12px; /* 字体大小 */
  color: #333; /* 字体颜色 */
}

.keyword .keyword-text {
  margin-right: 5px;
}

.keyword .close-button {
  cursor: pointer;
  color: #999; /* 关闭按钮颜色 */
  font-weight: bold;
  margin-left: 5px;
}
</style>
