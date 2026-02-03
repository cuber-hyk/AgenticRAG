<template>
  <div style="max-width: 960px; margin: 0 auto; padding: 24px;">
    <h1>Agentic RAG 演示</h1>
    <div style="display:flex; gap:24px;">
      <div style="flex:2;">
        <ChatBox />
      </div>
      <div style="flex:1;">
        <UploadPanel />
      </div>
    </div>
  </div>
</template>
<script setup>
import ChatBox from "./components/ChatBox.vue";
import UploadPanel from "./components/UploadPanel.vue";
</script>
