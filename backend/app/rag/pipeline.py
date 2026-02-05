import logging
from typing import Dict, List, TypedDict, Any
from langgraph.graph import StateGraph, END
from ..config import Settings
from .vector_store import get_vector_store
from ..services.llm_siliconcloud import SiliconCloudLLM

logger = logging.getLogger(__name__)
_settings = Settings()
_agent = None

class AgentState(TypedDict):
    query: str
    context: List[Dict]
    history: List[Dict]
    answer: str
    sources: List[str]
    decision: str
    # New fields for optimization
    retrieve_count: int
    generate_count: int
    is_relevant: bool
    compliance_issues: List[str]

class AgentPipeline:
    def __init__(self, llm: SiliconCloudLLM):
        self.llm = llm
        self.vs = get_vector_store()
        self.app = self._build_graph()

    def _router(self, state: AgentState):
        query = state["query"]
        logger.info(f"Routing query: {query}")
        
        prompt = (
            "你是一个智能查询路由助手。请根据用户的查询内容，决定下一步的操作。\n"
            f"用户查询：{query}\n\n"
            "操作选项：\n"
            "1. \"direct\" - 如果查询是简单的问候、闲聊、或者你不需要检索外部文档就能回答的通用知识（例如'你好'、'你是谁'、'1+1等于几'）。\n"
            "2. \"rewrite\" - 如果查询需要检索外部文档、特定领域的知识、或者查询比较模糊需要优化后才能检索。\n\n"
            "请仅输出一个单词：\"direct\" 或 \"rewrite\"。不要输出其他任何内容。"
        )
        
        try:
            decision = self.llm.complete(prompt).strip().lower()
            # Simple fallback
            if "rewrite" in decision:
                decision = "rewrite"
            else:
                decision = "direct"
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            decision = "direct" # Default to direct on error
            
        logger.info(f"Routing decision: {decision}")
        # Reset counters
        return {"decision": decision, "retrieve_count": 0, "generate_count": 0, "compliance_issues": []}

    def _rewrite(self, state: AgentState):
        query = state["query"]
        logger.info(f"Rewriting query: {query}")
        
        prompt = (
            "你是一个查询重写专家。请将用户的查询重写为一个更适合向量检索的版本。\n"
            "重写后的查询应该包含更多相关的关键词，去除无关的词语，并且更加具体。\n"
            f"用户查询：{query}\n\n"
            "请仅输出重写后的查询内容，不要包含解释或其他文字。"
        )
        
        try:
            new_query = self.llm.complete(prompt).strip()
            logger.info(f"Rewritten query: {new_query}")
        except Exception as e:
            logger.error(f"Rewriting failed: {e}")
            new_query = query
            
        return {"query": new_query}

    def _direct_answer(self, state: AgentState):
        query = state["query"]
        history = state.get("history", [])
        
        # Format history (last 4 messages)
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])
        
        prompt = (
            "你是一个智能助手。请直接回答用户的问题。\n"
            f"\n对话历史：\n{history_str}\n"
            f"\n用户问题：{query}\n"
        )
        
        try:
            answer = self.llm.complete(prompt)
        except Exception as e:
            logger.error(f"Direct answer failed: {e}")
            answer = "抱歉，生成回答时遇到错误。"
            
        return {"answer": answer, "sources": []}

    def _retrieve(self, state: AgentState):
        query = state["query"]
        logger.info(f"Retrieving for query: {query}")
        # Retrieve documents
        try:
            retrieved = self.vs.query(query, top_k=_settings.retrieval_top_k)
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            retrieved = []
        return {"context": retrieved}

    def _evaluate_relevance(self, state: AgentState):
        query = state["query"]
        context_docs = state["context"]
        
        if not context_docs:
            logger.info("No context docs to evaluate.")
            return {"is_relevant": False}

        # Use LLM to evaluate relevance
        context_text = "\n".join([f"- {r['text'][:200]}..." for r in context_docs[:3]]) # Check top 3
        prompt = (
            "你是一个文档相关性评估专家。请判断以下检索到的文档是否包含回答用户问题所需的信息。\n"
            f"用户问题：{query}\n"
            f"检索文档片段：\n{context_text}\n\n"
            "如果文档包含相关信息，请输出 \"relevant\"。\n"
            "如果文档完全不相关或无法回答问题，请输出 \"irrelevant\"。\n"
            "请仅输出一个单词。"
        )
        
        try:
            result = self.llm.complete(prompt).strip().lower()
            is_relevant = "relevant" in result and "irrelevant" not in result
        except Exception as e:
            logger.error(f"Relevance evaluation failed: {e}")
            is_relevant = True # Default to relevant to avoid loop
            
        logger.info(f"Relevance evaluation: {is_relevant}")
        return {"is_relevant": is_relevant}

    def _rewrite_relevance(self, state: AgentState):
        query = state["query"]
        retry_count = state.get("retrieve_count", 0) + 1
        logger.info(f"Rewriting for relevance (attempt {retry_count}): {query}")
        
        prompt = (
            "你是一个搜索专家。用户的原始查询没有检索到相关文档。\n"
            "请重写查询以提高检索相关性。你可以：\n"
            "1. 使用同义词替换\n"
            "2. 补充领域术语\n"
            "3. 展开缩写\n"
            f"原始查询：{query}\n\n"
            "如果查询过短（少于4个字），请尝试添加上下文约束。\n"
            "请直接输出重写后的查询，不要包含解释。"
        )
        
        try:
            new_query = self.llm.complete(prompt).strip()
            logger.info(f"Expanded query: {new_query}")
        except Exception as e:
            logger.error(f"Relevance rewrite failed: {e}")
            new_query = query
            
        return {"query": new_query, "retrieve_count": retry_count}

    def _evaluate_compliance(self, state: AgentState):
        answer = state["answer"]
        
        prompt = (
            "你是一个内容合规审核员。请检查以下回答是否符合安全规范。\n"
            "检查维度：\n"
            "1. 敏感词检测（政治敏感、暴力恐怖等）\n"
            "2. 合法性检测（是否包含违法建议）\n"
            "3. 事实一致性（是否包含明显的虚假信息，仅基于常识判断）\n\n"
            f"待审核回答：\n{answer}\n\n"
            "如果回答符合规范，请输出 \"compliant\"。\n"
            "如果有问题，请列出具体违规点，用分号分隔，例如 \"violation: 包含暴力内容; 事实错误\"。\n"
            "请优先输出状态。"
        )
        
        try:
            result = self.llm.complete(prompt).strip()
            if "compliant" in result.lower() and "non-compliant" not in result.lower() and "violation" not in result.lower():
                return {"compliance_issues": []}
            else:
                # Extract issues
                issues = [s.strip() for s in result.replace("violation:", "").split(";") if s.strip()]
                if not issues: issues = ["Unknown compliance issue"]
                logger.info(f"Compliance issues found: {issues}")
                return {"compliance_issues": issues}
        except Exception as e:
            logger.error(f"Compliance evaluation failed: {e}")
            return {"compliance_issues": []} # Default to pass on error

    def _fix_generation(self, state: AgentState):
        answer = state["answer"]
        issues = state.get("compliance_issues", [])
        retry_count = state.get("generate_count", 0) + 1
        
        prompt = (
            f"上一版回答因以下原因未通过审核：{'; '.join(issues)}。\n"
            "请修改回答，删除敏感表述，补充缺失信息，并控制字数在 300 字以内。\n"
            f"原回答：{answer}\n\n"
            "请直接输出修改后的回答。"
        )
        
        try:
            new_answer = self.llm.complete(prompt)
        except Exception as e:
            logger.error(f"Fix generation failed: {e}")
            new_answer = answer
            
        return {"answer": new_answer, "generate_count": retry_count}

    def _fallback_safe(self, state: AgentState):
        logger.warning("Max generation retries reached. Falling back to safe response.")
        return {"answer": "抱歉，无法提供该信息。"}

    def _knowledge_fallback(self, state: AgentState):
        query = state["query"]
        logger.warning(f"Knowledge base missing for query: {query}")
        return {"answer": "抱歉，知识库中未找到相关信息，无法回答您的问题。", "sources": []}

    def _generate(self, state: AgentState):
        query = state["query"]
        context_docs = state["context"]
        history = state.get("history", [])
        
        # Format context
        if context_docs:
            context_str = "\n\n".join([f"- {r['text']}" for r in context_docs])
        else:
            context_str = "无检索结果。"
        
        # Format history (last 4 messages)
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])
        
        prompt = (
            "你是一个帮助用户检索与总结文档的智能助手。"
            f"\n对话历史：\n{history_str}\n"
            f"\n检索到的上下文：\n{context_str}\n"
            f"\n用户问题：{query}\n"
            "要求：优先使用上下文，无法回答时明确说明。"
        )
        
        try:
            answer = self.llm.complete(prompt)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            answer = "抱歉，生成回答时遇到错误。"
            
        sources = [r["source"] for r in context_docs] if context_docs else []
        return {"answer": answer, "sources": sources}

    def _route_decision(self, state: AgentState):
        return state.get("decision", "direct")

    def _build_graph(self):
        """Build the LangGraph workflow"""
        # Define the graph
        workflow = StateGraph(AgentState)
        workflow.add_node("router", self._router)
        workflow.add_node("rewrite", self._rewrite)
        workflow.add_node("direct_answer", self._direct_answer)
        workflow.add_node("retrieve", self._retrieve)
        workflow.add_node("generate", self._generate)
        
        # New nodes
        workflow.add_node("evaluate_relevance", self._evaluate_relevance)
        workflow.add_node("rewrite_relevance", self._rewrite_relevance)
        workflow.add_node("evaluate_compliance", self._evaluate_compliance)
        workflow.add_node("fix_generation", self._fix_generation)
        workflow.add_node("fallback_safe", self._fallback_safe)
        workflow.add_node("knowledge_fallback", self._knowledge_fallback)
        
        # Define edges
        workflow.set_entry_point("router")
        
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "direct": "direct_answer",
                "rewrite": "rewrite"
            }
        )
        
        workflow.add_edge("rewrite", "retrieve")
        workflow.add_edge("retrieve", "evaluate_relevance")
        
        def check_relevance(state: AgentState):
            if state.get("is_relevant", False):
                return "generate"
            elif state.get("retrieve_count", 0) < 2:
                return "rewrite_relevance"
            else:
                return "knowledge_fallback"

        workflow.add_conditional_edges(
            "evaluate_relevance",
            check_relevance,
            {
                "generate": "generate",
                "rewrite_relevance": "rewrite_relevance",
                "knowledge_fallback": "knowledge_fallback"
            }
        )
        
        workflow.add_edge("rewrite_relevance", "retrieve")
        workflow.add_edge("knowledge_fallback", END)
        
        workflow.add_edge("generate", "evaluate_compliance")
        
        def check_compliance(state: AgentState):
            if not state.get("compliance_issues"):
                return "end"
            elif state.get("generate_count", 0) < 2:
                return "fix"
            else:
                return "fallback"

        workflow.add_conditional_edges(
            "evaluate_compliance",
            check_compliance,
            {
                "end": END,
                "fix": "fix_generation",
                "fallback": "fallback_safe"
            }
        )
        
        workflow.add_edge("fix_generation", "evaluate_compliance")
        workflow.add_edge("fallback_safe", END)
        workflow.add_edge("direct_answer", END)
        
        return workflow.compile()

    def run(self, query: str, session) -> Dict:
        """Execute the agent workflow"""
        # Prepare initial state
        initial_state = {
            "query": query,
            "history": session.history,
            "context": [],
            "answer": "",
            "sources": [],
            "decision": ""
        }
        
        # Run the graph
        try:
            result = self.app.invoke(initial_state)
            
            # Extract results
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            
            # Update session history
            session.history.append({"role": "user", "content": query})
            session.history.append({"role": "assistant", "content": answer})
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise e

def get_agent_pipeline() -> AgentPipeline:
    global _agent
    if _agent:
        return _agent
    llm = SiliconCloudLLM(_settings)
    _agent = AgentPipeline(llm)
    return _agent
