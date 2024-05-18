<template>
  <el-container style="height: 100vh; display: flex; justify-content: center; align-items: center; padding: 0;">
    <el-header height="auto" style="display: flex; align-items: center; justify-content: center; padding-top: 20px; padding-bottom: 10px;">
      <div class="logo">
        <span class="title">AskArt</span>
      </div>
    </el-header>
    <el-main style="padding-bottom: 0; padding-top: 0; padding-left: 0;">
      <div class="app-container">
        <div class="chat-container">
          <chat-interface @selected-text="handleSelectedText" @add-keyword="addKeyword"/>
        </div>
        <div class="image-container">
          <image-display :imagePrompt="imagePrompt" :keywords="keywords" @remove-keyword="removeKeyword"/>
        </div>
      </div>
    </el-main>
  </el-container>

</template>

<script setup>
import ChatInterface from './components/ChatInterface.vue';
import ImageDisplay from './components/ImageDisplay.vue';
import { ref } from 'vue';
import 'element-plus/dist/index.css';


const imagePrompt = ref('');
const keywords = ref([]);
// for debugging purposes
window.imagePrompt = imagePrompt;
window.keywords = keywords;

function handleSelectedText(text) {
  imagePrompt.value = text; // Set the selected text as the image prompt
}
function addKeyword(keyword) {
  keywords.value.push(keyword);
}

function removeKeyword(index) {
  keywords.value.splice(index, 1);
}
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: row;
  justify-content: space-around; /* Centers the child components with space around them */
  align-items: start; /* Aligns items to the start of the flex container */
  width: 80vw;
  background-color: #fff;
  padding: 20px; /* Padding around the containers */
  box-shadow: 0px 4px 8px rgba(0,0,0,0.1); /* Enhance shadow for depth */
  border: 1px solid #ccc; /* Thicker border */
  border-radius: 8px;
  margin: 100px auto; /* Center the container horizontally */
}

.chat-container, .image-container {
  flex: 1;
  margin: 20px;
  background: #FFFFFF;
  box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
  border-radius: 8px;
  overflow: hidden;
}

.title {
  font-size: 50px; /* 标题的字体大小 */
  font-weight: bold;
  background: -webkit-linear-gradient(45deg, #FF6B6B, #FFD93D);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

:deep(.chat-interface textarea), :deep(.image-display textarea) {
  flex: 1;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  resize: vertical;
  font-family: 'Helvetica', 'Arial', sans-serif;
  min-height: 40px;
  max-height: 150px;
  overflow-y: auto;
  margin-right: 5px;
  height: 40px; /* Set the same height as the send button */
  box-sizing: border-box; /* Ensure padding is included in the height */
}

:deep(.chat-interface button), :deep(.image-display button) {
  background-color: #409EFF;
  color: white;
  cursor: pointer;
  padding: 10px 10px;
  border: none;
  border-radius: 5px;
  transition: background 0.3s;
  font-family: 'Helvetica', 'Arial', sans-serif;
  height: 40px;
}
:deep(.chat-interface button:hover), :deep(.image-display button:hover) {
  background-color: #367DDC;
}
:deep(.chat-interface .voice-button), :deep(.image-display .voice-button) {
  margin-right: 5px;
  padding: 0 10px;
  background: #e3e1e1;
  color: #e3e1e1;
  border: 1px solid #e3e1e1;
  border-radius: 5px;
  cursor: pointer;
  height: 40px; /* Match the height of the other button and textarea */
  display: flex;
  align-items: center;
  justify-content: center;
}
:deep(.chat-interface .voice-button:hover), :deep(.image-display .voice-button:hover) {
  background: #a6a4a4;
}
:deep(.chat-interface .voice-button:active), :deep(.image-display .voice-button:active) {
  background: #f8a600;
}
:deep(.chat-interface .messages), :deep(.image-display .messages) {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  height: 60vh;
}
@media (max-width: 868px) {
  .app-container {
    flex-direction: column; /* Stacks the components vertically on smaller screens */
    width: 100%; /* Use full width on smaller screens */
    margin: 0 auto; /* Remove horizontal margin on smaller screens */
    padding: 20px; /* Adjust padding for smaller screens */
  }
}
</style>
