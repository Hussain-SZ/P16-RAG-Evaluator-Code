#!/usr/bin/env python3
"""
Full API test for RAG Evaluation
This script tests the complete RAG evaluation workflow including the mock API response.
"""

import sys
import os
import asyncio

# Add the backend app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_full_evaluation():
    """Test the complete RAG evaluation workflow"""
    print("🔄 Testing complete RAG evaluation workflow...")
    
    from app.services.rag_evaluation_service import rag_evaluation_service
    
    # Test data
    test_query = "What did the fox do?"
    test_context = """
    A quick brown fox named Vixey jumps over the lazy dog. 
    The dog, named Frodo, did not even open its eyes. 
    The fox then ran into the forest.
    """
    test_llm_output = """
    The quick brown fox, Vixey, jumped over Sparky, the lazy dog. 
    The fox's jump was very high. After that, it ran away.
    """
    
    # Call the evaluation service
    result = await rag_evaluation_service.evaluate_faithfulness(
        query=test_query.strip(),
        context=test_context.strip(),
        llm_output=test_llm_output.strip()
    )
    
    print(f"📊 Evaluation Result:")
    print(f"   Status: {result.get('status')}")
    
    if result.get('status') == 'success':
        metrics = result.get('aggregate_metrics', {})
        print(f"   📈 Aggregate Metrics:")
        print(f"      • Faithfulness Rate: {metrics.get('faithfulness_rate', 0):.1%}")
        print(f"      • Hallucination Rate: {metrics.get('hallucination_rate', 0):.1%}")
        print(f"      • Inferred Rate: {metrics.get('inferred_rate', 0):.1%}")
        print(f"      • Extrapolated Rate: {metrics.get('extrapolated_rate', 0):.1%}")
        print(f"      • Total Sentences: {metrics.get('total_sentences', 0)}")
        
        evaluations = result.get('sentence_evaluations', [])
        print(f"   📝 Sentence Evaluations ({len(evaluations)} sentences):")
        for eval_item in evaluations[:3]:  # Show first 3 for brevity
            print(f"      {eval_item['sentence_number']}. [{eval_item['classification'].upper()}] \"{eval_item['sentence_text'][:50]}...\"")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    return result.get('status') == 'success'

async def main():
    """Main test function"""
    print("🧪 RAG Evaluation API - Full Integration Test")
    print("=" * 55)
    
    try:
        # Test the full workflow
        success = await test_full_evaluation()
        
        print(f"\n📊 Full Integration Test: {'✅ PASS' if success else '❌ FAIL'}")
        
        if success:
            print(f"\n🎉 RAG Evaluation system is working correctly!")
            print(f"💡 The system is currently using mock responses.")
            print(f"   To use real AI evaluation, add your Gemini API key to .env")
        
        return success
            
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)