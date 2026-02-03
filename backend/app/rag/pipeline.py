import logging
from typing import Dict, List
from ..config import Settings
from .vector_store import get_vector_store
from ..services.llm_siliconcloud import SiliconCloudLLM

logger = logging.getLogger(__name__)
_settings = Settings()
_agent = None

# Optional imports with fallback
try:
    from llama_index.core import Document
except Exception:
    Document = None
try:
    from langgraph.graph import Graph, END
except Exception:
    Graph = None
    END = "END"


class AgentPipeline:
    def __init__(self, llm: SiliconCloudLLM):
        self.llm = llm
        self.vs = get_vector_store()

    def run(self, query: str, session) -> Dict:
        retrieved = self.vs.query(query, top_k=_settings.retrieval_top_k)
        context = "\n\n".join([f"- {r['text']}" for r in retrieved])
        history = "\n".join([f"{m['role']}: {m['content']}" for m in session.history[-4:]])
        prompt = (
            "你是一个帮助用户检索与总结文档的智能助手。"
            f"\n对话历史：\n{history}\n"
            f"\n检索到的上下文：\n{context}\n"
            f"\n用户问题：{query}\n"
            "要求：优先使用上下文，无法回答时明确说明。"
        )
        answer = self.llm.complete(prompt)
        session.history.append({"role": "user", "content": query})
        session.history.append({"role": "assistant", "content": answer})
        return {"answer": answer, "sources": [r["source"] for r in retrieved]}


def build_langgraph(llm: SiliconCloudLLM):
    if Graph is None:
        return None
    g = Graph()

    def retrieve(state):
        q = state["query"]
        vs = get_vector_store()
        hits = vs.query(q, top_k=_settings.retrieval_top_k)
        state["context"] = hits
        return state

    def decide(state):
        return "generate"

    def generate(state):
        hits: List[Dict] = state.get("context", [])
        context = "\n".join([h["text"] for h in hits])
        prompt = f"基于以下检索到的上下文回答：\n{context}\n\n用户问题：{state['query']}"
        state["answer"] = llm.complete(prompt)
        state["sources"] = [h["source"] for h in hits]
        return state

    g.add_node("retrieve", retrieve)
    g.add_node("generate", generate)
    g.add_edge("retrieve", "generate")
    g.set_entry_point("retrieve")
    g.set_finish_point("generate")
    return g


def get_agent_pipeline() -> AgentPipeline:
    global _agent
    if _agent:
        return _agent
    llm = SiliconCloudLLM(_settings)
    _agent = AgentPipeline(llm)
    return _agent
