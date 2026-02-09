<template>
  <div>
    <h3>多轮对话</h3>
    <div style="border:1px solid #ddd; padding:12px; height:360px; overflow:auto;">
      <div v-for="(m,i) in messages" :key="i" style="margin-bottom:8px;">
        <strong>{{ m.role }}:</strong> {{ m.content }}
      </div>
    </div>
    <div style="display:flex; gap:8px; margin-top:12px;">
      <input v-model="input" @keyup.enter="send" placeholder="请输入问题..." style="flex:1; padding:8px;" />
      <button @click="send">发送</button>
    </div>
    <div style="margin-top:8px; font-size:12px; color:#666;">延迟: {{ latency }} ms</div>
  </div>
</template>
<script setup>
import { ref } from "vue";
import { AgenticRAGClient } from "../../sdk-js";

const client = new AgenticRAGClient(import.meta.env.VITE_API_BASE || "http://localhost:8000");
const sessionId = "demo-session";
const messages = ref([]);
const input = ref("");
const latency = ref(0);

async function send(){
  if(!input.value) return;
  const content = input.value;
  input.value = ""; // Clear input immediately
  messages.value.push({role:"user", content: content});
  
  try {
    const resp = await client.chat(sessionId, content);
    messages.value.push({role:"assistant", content: resp.answer});
    latency.value = resp.latency_ms;
  } catch (err) {
    messages.value.push({role:"assistant", content: "Error: " + err.message});
    // Optional: restore input on error? 
    // input.value = content; 
  }
}
</script>
