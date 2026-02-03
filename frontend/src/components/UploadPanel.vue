<template>
  <div>
    <h3>知识库上传</h3>
    <input type="file" multiple @change="onFiles" />
    <div style="margin-top:8px;">
      <button @click="upload">上传并索引</button>
    </div>
    <div style="margin-top:8px; font-size:12px; color:#666;">{{ status }}</div>
  </div>
</template>
<script setup>
import { ref } from "vue";
import { AgenticRAGClient } from "../../sdk-js";
const client = new AgenticRAGClient(import.meta.env.VITE_API_BASE || "http://localhost:8000");
const files = ref([]);
const status = ref("");
function onFiles(e){
  files.value = Array.from(e.target.files || []);
}
async function upload(){
  if(files.value.length === 0) return;
  try{
    const res = await client.upload(files.value);
    status.value = `成功索引 ${res.count} 文档`;
  }catch(err){
    status.value = `上传失败: ${err}`;
  }
}
</script>
