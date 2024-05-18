import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { User } from '@element-plus/icons-vue'

const app = createApp(App);
app.component('user-icon', User);
app.use(ElementPlus);
app.mount('#app');
