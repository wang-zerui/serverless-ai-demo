<template>
  <a-layout class="layout">
    <a-layout-header :style="{ position: 'fixed', zIndex: 1, width: '100%', color: 'white', fontSize: '16px' }">
      <div class="logo" />
      漫画风图片生成
    </a-layout-header>
    <a-layout-content :style="{ padding: '0 400px', marginTop: '80px' }">
      <a-card>
        <a-upload-dragger
          ref="up"
          name="file"
          :customRequest="upload"
          :beforeUpload="beforeUpload"
          @drop="handleDrop"
          :disabled="loading"
        >
            <div v-if="loading">
              <p class="ant-upload-drag-icon">
                <loading-outlined />
              </p>
              <p class="ant-upload-text">
                Transforming...
              </p>
            </div>
            <div v-else>
              <p class="ant-upload-drag-icon">
                <inbox-outlined />
              </p>
              <p class="ant-upload-text">
                点击或拖动图片到这个区域
              </p>
            </div>
        </a-upload-dragger>
        <a-space v-if="imageUrl" class="result">
          <a-card title="原图" style="width: 100%">
            <template #extra>
              <a-button>
                保存
              </a-button>
            </template>
            <img :src="imageUrl" alt="">
          </a-card>

          <a-card title="转换结果" style="width: 100%" v-if="animeUrl">
            <template #extra>
              <a-button>
                保存
              </a-button>
            </template>
            <img :src="animeUrl" alt="">
          </a-card>
        </a-space>
      </a-card>
    </a-layout-content>
    <a-layout-footer :style="{ textAlign: 'center' }">
      xinwuyun ©2022 Powerd by serverless and animeGAN2 
    </a-layout-footer>
  </a-layout>
</template>

<script>
import { InboxOutlined,LoadingOutlined } from "@ant-design/icons-vue";
import { message } from "ant-design-vue";
import { defineComponent, ref } from "vue";
import Compressor from 'compressorjs';


export default defineComponent({
  components: {
    InboxOutlined, LoadingOutlined
  },
  setup() {
    const up = ref(null);
    const imageUrl = ref('');
    const animeUrl = ref('');
    const loading = ref(false)
    // function getBase64(img, callback) {
    //   const reader = new FileReader();
    //   reader.addEventListener('load', () => callback(reader.result));
    //   reader.readAsDataURL(img);
    // }
    const compressor = (file) =>  {
      return new Promise(resolve => {
        new Compressor(file, {
          quality: 0.5,
          success: resolve,
          error(err) {
            console.log(err.message)
          },
        })
      })
    };

    const beforeUpload = (file) => {
      loading.value = true;
      if(file.size > 100 * 1024){
        message.error("图片过大，请上传小于100k的图片")
        loading.value = false;
        return false;
      }else{
        return true;
      }
    }
    const upload = async (option) => {
      loading.value = true;
      animeUrl.value = "";
      imageUrl.value = ""
      const reader = new FileReader();
      let file = option.file;
      if(option.file.size > 100 * 1024){
        message.error("图片过大，请上传小于100k的图片")
        loading.value = false;
        up.value.abort();
        option.onError();
        return;
      }else if(option.file.size > 50 * 1024){
        file = await compressor(file);
        console.log(file);
      }
      reader.readAsDataURL(file);
      reader.onloadend = function(e) {
        const base64 = e.target.result.toString().split(',')[1];
        imageUrl.value = `data:image/jpg;base64, ${base64}`;
        if (e && e.target && e.target.result) {
          var raw = JSON.stringify({
            "image": base64
          });

          var requestOptions = {
            method: 'POST',
            body: raw,
          };

          fetch("https://image-server-cloud-homework-bmntzdwfom.cn-hangzhou.fcapp.run/images/comic_style", requestOptions)
            .then(response => response.json())
            .then(result => {
              const animeBase64 = result.photo;
              animeUrl.value = animeBase64;
              loading.value = false;
              message.success("转换成功");
              option.onSuccess();
            })
            .catch((error) => {
              message.error(`转换失败${error}`);
              up.value.abort();
              option.onError();
            });
        }
      }
      return true;
    }
    return {
      title: "漫画风图片生成",
      up,
      imageUrl,
      animeUrl,
      loading,
      upload,
      beforeUpload,
      fileList: ref([]),
      handleDrop: (e) => {
        console.log(e);
      },
    };
  },
});
</script>

<style>
.layout {
  height: 100vh;
}
.layout .logo {
  width: 120px;
  height: 31px;
  background: rgba(255, 255, 255, 0.2);
  margin: 16px 24px 16px 0;
  float: left;
}
.site-layout .site-layout-background {
  background: #fff;
}

.result {
  width: 100%;
}

[data-theme="dark"] .site-layout .site-layout-background {
  background: #141414;
}
</style>
