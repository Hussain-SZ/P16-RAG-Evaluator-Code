import os
import json
import re
import logging
from typing import Dict, List, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    GENAI_AVAILABLE = True
    # Load environment variables
    load_dotenv()
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("Google GenerativeAI or dotenv not available. Service will run in test mode.")

class RAGEvaluationService:
    """Service for evaluating RAG responses using Google Gemini AI"""
    
    def __init__(self):
        """Initialize the RAG evaluation service"""
        self._configure_api()
    
    def _configure_api(self):
        """Configure the Gemini API key"""
        if not GENAI_AVAILABLE:
            logger.warning("Gemini API not available - running in test mode")
            return
            
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY environment variable not set.")
                return
            genai.configure(api_key=api_key)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Splits text into sentences using simple regex."""
        if not text:
            return []
        # Use regex to split on periods, question marks, exclamation marks
        # while trying to keep delimiters. This is a simple split.
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s for s in sentences if s]  # Filter out empty strings
    
    def build_batch_judge_prompt(self, query: str, context: str, sentences: List[str]) -> str:
        """Builds the complete prompt for the batched LLM judge."""
        
        # Convert sentence list to a numbered string
        sentence_list_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(sentences))

        return f"""
        You are an expert evaluator for a RAG system. Your goal is to evaluate each sentence of a generated answer for faithfulness to a given context.

        **Task:**
        For each sentence in the "Answer Sentences" list, classify it into one of four categories based *only* on the "Context". You must also provide a brief justification and quote the supporting evidence.

        **Categories:**
        1.  **faithful**: The sentence is directly supported or clearly paraphrased from the context.
        2.  **inferred**: The sentence is not explicitly stated but can be logically inferred from the context.
        3.  **extrapolated**: The sentence introduces new information that is related to the topic but is NOT present in the context.
        4.  **hallucinated**: The sentence contradicts the context or states information that is completely absent and unrelated.

        **Inputs:**
        
        **1. Original Query:**
        {query}

        **2. Context:**
        {context}

        **3. Answer Sentences (as a list):**
        {sentence_list_str}

        **Output Format:**
        You MUST respond with *only* a valid JSON object. The object should have a single key "evaluations", which is a list of objects. Each object in the list must have the following keys:
        - "sentence_number": The number of the sentence being evaluated.
        - "sentence_text": The text of the sentence.
        - "classification": Your classification (faithful, inferred, extrapolated, or hallucinated).
        - "justification": Your brief, one-sentence justification.
        - "supporting_chunk": The exact quote from the context that supports your judgment (or "N/A" if hallucinated/extrapolated).

        **Example JSON Response:**
        {{
          "evaluations": [
            {{
              "sentence_number": 1,
              "sentence_text": "The sky is blue.",
              "classification": "faithful",
              "justification": "The context directly states that the sky's color is blue.",
              "supporting_chunk": "The color of the sky is blue."
            }},
            {{
              "sentence_number": 2,
              "sentence_text": "It is daytime.",
              "classification": "inferred",
              "justification": "The context mentions the blue sky, which implies it is daytime.",
              "supporting_chunk": "The color of the sky is blue."
            }}
          ]
        }}

        Begin your evaluation now.
        """
    
    async def evaluate_faithfulness(
        self, 
        query: str, 
        context: str, 
        llm_output: str
    ) -> Dict[str, Any]:
        """
        Evaluates the faithfulness of an LLM output against a context using
        a single, batched Gemini API call.

        Args:
            query: The original user query.
            context: The retrieved context chunks (as a single string).
            llm_output: The answer generated by the LLM.

        Returns:
            A dictionary containing the evaluation results or an error.
        """
        
        try:
            # 1. Split the answer into sentences
            sentences = self.split_into_sentences(llm_output)
            if not sentences:
                return {
                    "status": "error",
                    "error": "LLM output was empty or could not be split into sentences."
                }

            # 2. Create the batched prompt for the LLM-as-a-Judge
            judge_prompt = self.build_batch_judge_prompt(query, context, sentences)
            
            # 3. Check if Gemini is available
            if not GENAI_AVAILABLE:
                return logger.warning("GEMINI_API_KEY environment variable not set.")
            
            # 4. Set up the Gemini model
            model_name = os.getenv("GEMINI_MODEL_NAME")
            model = genai.GenerativeModel(
                model_name, 
                generation_config={"response_mime_type": "application/json"}  # Enforce JSON output!
            )
            
            # 5. Make the single API call
            logger.info("Making API call to Gemini for RAG evaluation")
            response = model.generate_content(judge_prompt)
            
            # 6. Parse the JSON response
            # The 'response.text' should be a JSON string
            evaluation_results = json.loads(response.text)
            
            # 7. Calculate Aggregate Metrics
            evaluations_list = evaluation_results.get("evaluations", [])
            total = len(evaluations_list)
            
            if total == 0:
                return {
                    "status": "error",
                    "error": "No evaluations returned from the model."
                }
            
            faithful_count = sum(1 for e in evaluations_list if e.get("classification") == "faithful")
            hallucination_count = sum(1 for e in evaluations_list if e.get("classification") == "hallucinated")
            inferred_count = sum(1 for e in evaluations_list if e.get("classification") == "inferred")
            extrapolated_count = sum(1 for e in evaluations_list if e.get("classification") == "extrapolated")
            
            # Calculate Precision and Recall
            # Precision: Proportion of generated sentences that are faithful (accurate)
            precision = round((faithful_count / total), 3) if total > 0 else 0
            
            # Recall: Proportion of answer that is grounded in context (faithful + inferred)
            # This measures how much of the answer is actually supported by the retrieved context
            context_grounded_count = faithful_count + inferred_count
            recall = round((context_grounded_count / total), 3) if total > 0 else 0
            
            # F1 Score: Harmonic mean of precision and recall
            f1_score = round((2 * precision * recall) / (precision + recall), 3) if (precision + recall) > 0 else 0
            
            aggregate_metrics = {
                "faithfulness_rate": round((faithful_count / total), 3) if total > 0 else 0,
                "hallucination_rate": round((hallucination_count / total), 3) if total > 0 else 0,
                "inferred_rate": round((inferred_count / total), 3) if total > 0 else 0,
                "extrapolated_rate": round((extrapolated_count / total), 3) if total > 0 else 0,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "total_sentences": total,
                "faithful_count": faithful_count,
                "hallucination_count": hallucination_count,
                "inferred_count": inferred_count,
                "extrapolated_count": extrapolated_count
            }

            logger.info(f"RAG evaluation completed successfully. Total sentences: {total}")
            
            return {
                "status": "success",
                "aggregate_metrics": aggregate_metrics,
                "sentence_evaluations": evaluations_list
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode LLM response as JSON: {e}")
            return {
                "status": "error",
                "error": "Failed to decode LLM response as JSON.",
                "raw_response": response.text if 'response' in locals() else "No response"
            }
        except Exception as e:
            logger.error(f"RAG evaluation error: {e}")
            return {
                "status": "error",
                "error": f"An error occurred during evaluation: {str(e)}"
            }


# Create a singleton instance
rag_evaluation_service = RAGEvaluationService()