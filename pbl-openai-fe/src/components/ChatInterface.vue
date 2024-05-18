<template>
  <div class="chat-interface">
    <div class="messages" @mouseup="checkSelectedText">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="{'message-user': message.text.startsWith('User:'), 'message-ai': message.text.startsWith('AI:')}"
        @contextmenu.prevent="handleContextMenu($event)"
      >
        {{ stripPrefix(message.text) }}
      </div>
    </div>
    <div ref="contextMenu" v-if="showContextMenu" :style="{ top: menuPosition.y, left: menuPosition.x }" class="context-menu">
      <ul>
        <li @click="generateImageFromText">生成图片</li>
        <li @click="fetchFollowUpQuestions">追问</li>
        <li @click="addAsKeyword">添加为关键词句</li>
      </ul>
    </div>
        <div class="input-container">
      <button @mousedown="startRecognition" @mouseup="stopRecognition" @mouseleave="stopRecognition" class="voice-button">
        🎙️
      </button>
      <textarea v-model="userInput" placeholder="我的问题是"></textarea>
      <button @click="sendInput">发送</button>
    </div>
    <div class="follow-up-questions" v-if="followUpQuestions.length > 0">
      <ul>
        <li v-for="(question, index) in followUpQuestions" :key="index" @click="selectQuestion(question)">
          {{ question }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userInput: '',
      messages: [],
      showContextMenu: false,
      menuPosition: { x: '0px', y: '0px' },
      selectedText: '',
      followUpQuestions: [],
      thinkingMessageId: null
    };
  },
  methods: {
    async sendInput() {
      if (!this.userInput.trim()) {
      return;
    }
      const response = await fetch(`http://localhost:8300/chat/true`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_prompt: this.userInput })
      });

      this.messages.push({ id: this.messages.length, text: `User: ${this.userInput}` });
      this.userInput = ''; // Clear input field
      // Add user message
      const thinkingMessage = { id: this.messages.length, text: `AI: 正在思考...` };
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
      this.messages.push({ id: this.messages.length, text: `AI: ${text}` });
    },
    async fetchFollowUpQuestions() {
      try {
        const response = await fetch('http://localhost:8300/chat/follow-up');
        if (response.ok) {
          const data = await response.json();
          this.followUpQuestions = data.message; // Assuming the response contains an array of questions
          this.showContextMenu = false; // Close the context menu
        } else {
          throw new Error('Failed to fetch follow-up questions');
        }
      } catch (error) {
        console.error('Error:', error);
        this.followUpQuestions = []; // Reset follow-up questions on error
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
    stripPrefix(text) {
      if (text.startsWith('User:')) {
        return text.slice(5).trim();
      } else if (text.startsWith('AI:')) {
        return text.slice(3).trim();
      }
      return text;
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
    document.addEventListener('mousedown', this.closeContextMenu);
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
/*.follow-up-questions ul {*/
/*  display: flex;*/
/*  bottom: 10px; !* Adjusted to ensure it does not overlap chat input *!*/
/*  left: 0;*/
/*  right: 0;*/
/*  margin: auto;*/
/*  background: #fff;*/
/*  border: 1px solid #ccc;*/
/*  padding: 10px;*/
/*  border-radius: 5px;*/
/*  width: auto;*/
/*  max-width: 90%; !* Ensures it does not get too wide on large screens *!*/
/*  z-index: 100;*/
/*}*/
/*.follow-up-questions li {*/
/*  padding: 5px 10px;*/
/*  cursor: pointer;*/
/*  display: block; !* Ensures each question is on a new line *!*/
/*  color: #676767;*/
/*}*/
/*.follow-up-questions li:hover {*/
/*  background-color: #f0f0f0;*/
/*}*/
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

/*.voice-button {*/

/*}*/

.voice-button:hover {
  background: #e0e0e0;
}
</style>
