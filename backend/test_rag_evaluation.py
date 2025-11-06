#!/usr/bin/env python3
"""
Test script for RAG Evaluation API
This script tests the RAG evaluation functionality without requiring a real Gemini API key.
"""

import json
import sys
import os

# Add the backend app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_sentence_splitting():
    """Test the sentence splitting functionality"""
    print("Testing sentence splitting functionality...")
    
    from app.services.rag_evaluation_service import RAGEvaluationService
    
    # Create service instance
    service = RAGEvaluationService()
    
    # Test sentence splitting
    test_text = """
    The quick brown fox jumps over the lazy dog. 
    This is a second sentence! And this is a third sentence?
    """
    
    sentences = service.split_into_sentences(test_text.strip())
    
    print(f"Original text: {test_text.strip()}")
    print(f"Split into {len(sentences)} sentences:")
    for i, sentence in enumerate(sentences, 1):
        print(f"   {i}. {sentence}")
    
    return len(sentences) > 0

def test_prompt_building():
    """Test the prompt building functionality"""
    print("\nTesting prompt building functionality...")
    
    from app.services.rag_evaluation_service import RAGEvaluationService
    
    service = RAGEvaluationService()
    
    test_query = "What did the fox do?"
    test_context = "A quick brown fox named Vixey jumps over the lazy dog."
    test_sentences = [
        "The fox jumped over the dog.",
        "The fox was brown in color.",
        "The fox ran away afterwards."
    ]
    
    prompt = service.build_batch_judge_prompt(test_query, test_context, test_sentences)
    
    print(f"Prompt generated successfully!")
    print(f"Prompt length: {len(prompt)} characters")
    print(f"Sample (first 200 chars): {prompt[:200]}...")
    
    return len(prompt) > 0

def test_pydantic_models():
    """Test the Pydantic models"""
    print("\nTesting Pydantic models...")
    
    from app.schemas.rag_evaluation import RAGEvaluationRequest, RAGEvaluationResponse
    
    # Test request model
    test_request = RAGEvaluationRequest(
        query="What did the fox do?",
        context="A quick brown fox named Vixey jumps over the lazy dog.",
        llm_output="The fox jumped over the dog and ran away."
    )
    
    print(f"RAGEvaluationRequest created successfully!")
    print(f"Query: {test_request.query}")
    print(f"Context length: {len(test_request.context)} chars")
    print(f"Output length: {len(test_request.llm_output)} chars")
    
    # Test response model (success case)
    test_response_data = {
        "status": "success",
        "aggregate_metrics": {
            "faithfulness_rate": 0.67,
            "hallucination_rate": 0.33,
            "inferred_rate": 0.0,
            "extrapolated_rate": 0.0,
            "total_sentences": 3,
            "faithful_count": 2,
            "hallucination_count": 1,
            "inferred_count": 0,
            "extrapolated_count": 0
        },
        "sentence_evaluations": [
            {
                "sentence_number": 1,
                "sentence_text": "The fox jumped over the dog.",
                "classification": "faithful",
                "justification": "Directly supported by context.",
                "supporting_chunk": "fox named Vixey jumps over the lazy dog"
            }
        ]
    }
    
    test_response = RAGEvaluationResponse(**test_response_data)
    print(f"RAGEvaluationResponse created successfully!")
    print(f"Status: {test_response.status}")
    
    return True

def main():
    """Main test function"""
    print("RAG Evaluation API - Component Testing")
    print("=" * 50)
    
    try:
        # Test individual components
        test1 = test_sentence_splitting()
        test2 = test_prompt_building()  
        test3 = test_pydantic_models()

        print(f"\nTest Results Summary:")
        print(f"   • Sentence Splitting: {'✅ PASS' if test1 else '❌ FAIL'}")
        print(f"   • Prompt Building: {'✅ PASS' if test2 else '❌ FAIL'}")
        print(f"   • Pydantic Models: {'✅ PASS' if test3 else '❌ FAIL'}")
        
        if all([test1, test2, test3]):
            print(f"\nAll tests passed! The RAG evaluation system is ready.")
            print(f"\nNext steps:")
            print(f"   1. Add your Gemini API key to the .env file")
            print(f"   2. Start the FastAPI server: uvicorn app.main:app --reload")
            print(f"   3. Test the API endpoint: POST /api/v1/rag/evaluate")
            return True
        else:
            print(f"\nSome tests failed. Please check the implementation.")
            return False
            
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)