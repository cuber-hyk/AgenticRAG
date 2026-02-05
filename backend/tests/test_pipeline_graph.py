
import unittest
from unittest.mock import MagicMock, patch
from app.rag.pipeline import AgentPipeline, AgentState

class TestAgentPipeline(unittest.TestCase):
    @patch('app.rag.pipeline.SiliconCloudLLM')
    @patch('app.rag.pipeline.get_vector_store')
    @patch('app.rag.pipeline.Settings')
    def test_graph_structure(self, MockSettings, MockGetVS, MockLLM):
        # Setup mocks
        mock_llm = MockLLM.return_value
        mock_vs = MockGetVS.return_value
        
        # Instantiate pipeline
        pipeline = AgentPipeline(mock_llm)
        
        # Check if app is created
        self.assertIsNotNone(pipeline.app)
        
        # Verify graph structure (implicitly by checking it compiles)
        # We can also run a dummy invocation
        
        mock_vs.query.return_value = [{"text": "doc1", "source": "src1"}]
        mock_llm.complete.return_value = "Generated answer"
        
        session_mock = MagicMock()
        session_mock.history = []
        
        result = pipeline.run("test query", session_mock)
        
        self.assertEqual(result["answer"], "Generated answer")
        self.assertEqual(result["sources"], ["src1"])
        self.assertEqual(len(session_mock.history), 2) # user + assistant

if __name__ == '__main__':
    unittest.main()
