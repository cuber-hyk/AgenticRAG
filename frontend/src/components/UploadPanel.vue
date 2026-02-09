<template>
  <div>
    <h3>知识库上传</h3>
    <input type="file" multiple @change="onFiles" :disabled="isUploading" />
    <div style="margin-top:8px;">
      <button @click="upload" :disabled="isUploading || files.length===0">
        {{ isUploading ? '上传处理中...' : '上传并索引' }}
      </button>
    </div>
    
    <!-- 进度展示 -->
    <div v-if="isUploading || progress.total > 0" style="margin-top:12px;">
      <div style="width:100%; background:#eee; height:10px; border-radius:5px; overflow:hidden;">
        <div :style="{width: progress.percent+'%', background:'#4caf50', height:'100%', transition:'width 0.3s'}"></div>
      </div>
      <div style="font-size:12px; color:#666; margin-top:4px; text-align:right;">
        {{ progress.current }} / {{ progress.total }}
      </div>
    </div>

    <div style="margin-top:8px; font-size:12px; color:#666;">{{ status }}</div>
  </div>
</template>
<script setup>
import { ref, reactive } from "vue";
import { AgenticRAGClient } from "../../sdk-js";
const client = new AgenticRAGClient(import.meta.env.VITE_API_BASE || "http://localhost:8000");
const files = ref([]);
const status = ref("");
const isUploading = ref(false);
const progress = reactive({ current: 0, total: 0, percent: 0 });

function onFiles(e){
  files.value = Array.from(e.target.files || []);
  // Reset status on new file selection
  status.value = "";
  progress.total = 0;
  progress.current = 0;
  progress.percent = 0;
}

async function upload(){
  if(files.value.length === 0) return;
  
  isUploading.value = true;
  progress.total = files.value.length;
  progress.current = 0;
  progress.percent = 0;
  status.value = "开始处理...";

  let successCount = 0;
  try{
    for(let i=0; i<files.value.length; i++){
      const file = files.value[i];
      status.value = `正在解析并索引: ${file.name}`;
      
      // Upload one by one to show progress
      const res = await client.upload([file]);
      
      successCount += (res.count || 0); // Although usually 1 file -> 1 doc, could be 0 if empty
      progress.current = i + 1;
      progress.percent = Math.floor(((i + 1) / files.value.length) * 100);
    }
    status.value = `全部完成: 成功索引 ${successCount} 文档`;
  }catch(err){
    status.value = `处理中断: ${err}`;
  }finally{
    isUploading.value = false;
  }
}
</script>
