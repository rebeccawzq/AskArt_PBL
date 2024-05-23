<template>
  <div class="chat-interface">
    <div class="messages" @mouseup="checkSelectedText">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="{'message-user': message.type === 'user', 'message-ai': message.type === 'ai'}"
        @contextmenu.prevent="handleContextMenu($event)"
      >
        {{ message.content }}
      </div>
    </div>
    <div ref="contextMenu" v-if="showContextMenu" :style="{ top: menuPosition.y, left: menuPosition.x }" class="context-menu">
      <ul>
        <li @click="generateImageFromText">生成图片</li>
        <li @click="fetchFollowUpQuestions">追问</li>
        <li @click="addAsKeyword">添加为修饰语</li>
      </ul>
    </div>
    <div class="follow-up-questions-container">
        <div class="follow-up-questions" v-if="followUpQuestions.length > 0">
          <ul>
            <li v-for="(question, index) in followUpQuestions" :key="index" @click="selectQuestion(question)">
              {{ question }}
            </li>
          </ul>
        </div>
      </div>
    <div class="input-container-wrapper">
      <div class="input-container">
        <button @mousedown="startRecognition" @mouseup="stopRecognition" @mouseleave="stopRecognition" class="voice-button">
          🎙️
        </button>
        <textarea v-model="userInput" placeholder="我的问题是" @keydown.enter="sendInput"></textarea>
        <button @click="sendInput">发送</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userInput: '',
      messages: [],  // todo: limit the length of messages
      showContextMenu: false,
      menuPosition: { x: '0px', y: '0px' },
      selectedText: '',
      followUpQuestions: [],
      thinkingMessageId: null,
      localStorageKey: 'chat-messages',
      messageCounter: 0,
      hardcodedFollowUpQuestions: ["How can I help you?", "Do you need more information?", "Is there anything else you want to know?"],
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
          // only load the first 20 messages
          this.messages = JSON.parse(savedMessages).slice(-20);
          this.messageCounter = this.messages[this.messages.length - 1].id + 1;
        } catch (e) {
          console.error('Error parsing JSON from localStorage:', e);
          this.messages = [];
        }
      }
    },
    async sendInput() {
      if (!this.userInput.trim()) {
      return;
    }
      const response = await fetch(`http://18.223.254.93/backend/chat/true`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_prompt: this.userInput })
      });

      const userMessage = { id: this.messageCounter++, type: 'user', content: this.userInput };
      this.messages.push(userMessage);
      this.saveMessageToLocalStorage(userMessage);

      this.userInput = ''; // Clear input field
      // Add user message
      const thinkingMessage = { id: this.messageCounter++, type: 'ai', content: '正在思考...' };
      this.messages.push(thinkingMessage);
      this.thinkingMessageId = thinkingMessage.id;

      // Handle streaming response
      const reader = response.body.getReader();
      let receivedLength = 0; // received that many bytes at the moment
      let chunks = []; // array of received binary chunks (comprises the body)

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        chunks.push(value);
        receivedLength += value.length;
      }

      // Concatenate chunks into a single string
      const allChunks = new Uint8Array(receivedLength);
      let position = 0;
      for (let chunk of chunks) {
        allChunks.set(chunk, position);
        position += chunk.length;
      }

      const text = new TextDecoder("utf-8").decode(allChunks);
      // Remove thinking message
      const index = this.messages.findIndex(message => message.id === this.thinkingMessageId);
      if (index !== -1) {
        this.messages.splice(index, 1);
      }
      const aiMessage = { id: this.messageCounter++, type: 'ai', content: text };
      this.messages.push(aiMessage);
      this.saveMessageToLocalStorage(aiMessage);
      window.messages = this.messages;
      await this.fetchFollowUpQuestions();
    },
    async fetchFollowUpQuestions() {
      try {
        const response = await fetch('http://18.223.254.93/backend/chat/follow-up');
        if (response.ok) {
          const data = await response.json();
          this.followUpQuestions = data.message.length > 0 ? data.message : this.hardcodedFollowUpQuestions;
        } else {
          throw new Error('Failed to fetch follow-up questions');
        }
      } catch (error) {
        console.error('Error:', error);
        this.followUpQuestions = this.hardcodedFollowUpQuestions; // Use hardcoded questions on error
      }
    },
    handleContextMenu(event) {
      event.preventDefault();
      this.selectedText = window.getSelection().toString();
      if (this.selectedText.trim().length > 0) {
        this.menuPosition.x = event.clientX + 'px';
        this.menuPosition.y = event.clientY + 'px';
        this.showContextMenu = true;
      }
    },
    generateImageFromText() {
      this.showContextMenu = false;
      this.$emit('selected-text', this.selectedText); // Emit the event with the selected text
    },
    checkSelectedText() {
      if (window.getSelection().toString().trim() !== '') {
        this.selectedText = window.getSelection().toString();
      }
    },
    closeContextMenu(event) {
      if (this.showContextMenu && !this.$refs.contextMenu.contains(event.target)) {
        this.showContextMenu = false;
      }
    },
    selectQuestion(question) {
      this.userInput = question; // Set the selected question as the new user input
      this.followUpQuestions = []; // Clear the follow-up questions
    },
    addAsKeyword() {
      this.$emit('add-keyword', this.selectedText);
      this.showContextMenu = false;
    },
    startRecognition() {
      if (!this.recognition) {
        this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        this.recognition.lang = 'zh-CN'; // Set the language to Chinese
        this.recognition.continuous = true;
        this.recognition.interimResults = false;
        this.recognition.onresult = (event) => {
          const transcript = event.results[event.results.length - 1][0].transcript;
          this.userInput += transcript;
        };
      }
      this.isRecognizing = true;
      this.recognition.start();
    },
    stopRecognition() {
      if (this.isRecognizing) {
        this.isRecognizing = false;
        this.recognition.stop();
      }
    }
  },
  mounted() {
    const start_msg = { id: this.messageCounter++, type: 'ai', content: '你好' };
    this.messages.push(start_msg);
    const savedMessages = localStorage.getItem(this.localStorageKey);
    if (!savedMessages || savedMessages === '[object Object]') {
        localStorage.setItem(this.localStorageKey, JSON.stringify([]));
    } else {
        // this.loadMessagesFromLocalStorage();
    }
    document.addEventListener('mousedown', this.closeContextMenu);
    this.followUpQuestions = this.hardcodedFollowUpQuestions;
  },
  beforeDestroy() {
    document.removeEventListener('mousedown', this.closeContextMenu);
  }
};
</script>

<style scoped>

.context-menu {
  position: fixed;
  z-index: 100;
  background: white;
  border: 1px solid #ccc;
  border-radius: 5px;
  width: 150px;
}
.context-menu ul {
  list-style: none;
  padding: 10px;
  margin: 0;
}
.context-menu li {
  padding: 5px 10px;
  cursor: pointer;
  color: #676767;
}
.context-menu li:hover {
  background-color: #f0f0f0;
}
.follow-up-questions {
  width: 100%; /* 确保追问问题容器占满可用宽度 */
  margin-top: 10px; /* 给输入容器和追问问题容器之间增加一些间距 */
}

.follow-up-questions ul {
  display: block; /* 确保问题显示为块级元素 */
  background: #fff;
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 5px;
  width: auto;
  max-width: 90%; /* 确保在大屏幕上不会太宽 */
  margin: 0 auto; /* 居中显示 */
}

.follow-up-questions li {
  padding: 5px 10px;
  cursor: pointer;
  display: block; /* 确保每个问题显示在单独的一行上 */
  color: #676767;
}

.follow-up-questions li:hover {
  background-color: #f0f0f0;
}
.message-user,
.message-ai {
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

.message-user {
  background: #DCF8C6;
  margin-left: auto;
  border-top-right-radius: 0;
}

.message-ai {
  background: #ffffff;
  margin-right: auto;
  border-top-left-radius: 0;
}

.input-container {
  display: flex;
  align-items: flex-start;
  padding: 10px;
  background: white;
  border-top: 1px solid #e0e0e0;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.1);
}

.input-container-wrapper {
  display: flex;
  flex-direction: column-reverse;
  background: #f9f9f9;
}

.follow-up-questions-container {
  display: flex;
  justify-content: center;
  background: #f9f9f9;
  height: 200px;
  align-items: flex-end;
}


.voice-button:hover {
  background: #e0e0e0;
}
</style>
