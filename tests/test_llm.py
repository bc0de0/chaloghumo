import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from services.llm import LLMService

@pytest.fixture
def llm_service():
    with patch('services.llm.SentenceTransformer') as mock_st, \
         patch('google.generativeai.GenerativeModel') as mock_gm:
        service = LLMService()
        return service, mock_st.return_value, mock_gm.return_value

@pytest.mark.asyncio
async def test_generate_embedding(llm_service):
    service, mock_st, _ = llm_service
    
    # Mock embedding generation
    import numpy as np
    mock_st.encode.return_value = np.array([0.1]*384)
    
    embedding = await service.generate_embedding("test text")
    
    assert len(embedding) == 384
    assert embedding[0] == 0.1
    mock_st.encode.assert_called_once()

@pytest.mark.asyncio
async def test_generate_reasoning_chain(llm_service):
    service, _, mock_model = llm_service
    
    # Force genai_client to be the mocked module
    service.genai_client = MagicMock()
    service.genai_client.GenerativeModel.return_value = mock_model
    
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = '[{"step_id": 1, "logic": "test logic"}]'
    mock_model.generate_content_async = AsyncMock(return_value=mock_response)
    
    chain = await service.generate_reasoning_chain({}, {}, {})
    
    assert len(chain) == 1
    assert chain[0]["logic"] == "test logic"
    mock_model.generate_content_async.assert_called_once()
