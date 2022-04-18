import { createApp } from 'vue'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/antd.css';
import App from './App';

const app = createApp(App)

app.use(Antd).mount('#app');