import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styling/Home.css";

interface RAGEvaluationResult {
  status: string;
  aggregate_metrics?: {
    faithfulness_rate: number;
    hallucination_rate: number;
    inferred_rate: number;
    extrapolated_rate: number;
    total_sentences: number;
    faithful_count: number;
    hallucination_count: number;
    inferred_count: number;
    extrapolated_count: number;
  };
  sentence_evaluations?: Array<{
    sentence_number: number;
    sentence_text: string;
    classification: string;
    justification: string;
    supporting_chunk: string;
  }>;
  error?: string;
}

export default function Home() {
  const navigate = useNavigate();

  const [fileContent, setFileContent] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [evaluationResult, setEvaluationResult] = useState<RAGEvaluationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // --- Logout ---
  const handleLogout = () => {
    localStorage.removeItem("token");
    alert("You have been logged out.");
    navigate("/");
  };
  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  // --- Handle RAG Evaluation ---
  const handleEvaluation = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setEvaluationResult(null);
    setUploadMessage(null);

    const formData = new FormData(event.currentTarget);
    const file = formData.get("file") as File | null;
    
    let query = formData.get("query") as string;
    let context = formData.get("context") as string;
    const answer = formData.get("answer") as string;

    try {
      // Handle context input: prioritize file upload, fallback to textarea
      if (file && file.size > 0) {
        // File uploaded - use file content as context
        if (!file.name.endsWith(".txt")) {
          alert("Only .txt files are supported.");
          setIsLoading(false);
          return;
        }
        
        const text = await file.text();
        setFileName(file.name);
        setFileContent(text);
        context = text; // Override textarea context with file content
        setUploadMessage(`📄 Using uploaded file "${file.name}" as context`);
      } else {
        // No file uploaded - use textarea context
        setFileName(null);
        setFileContent(null);
        if (!context.trim()) {
          alert("Please provide context either by typing in the textarea or uploading a .txt file.");
          setIsLoading(false);
          return;
        }
        setUploadMessage("📝 Using manually entered context");
      }

      // Validate required fields
      if (!query.trim() || !context.trim() || !answer.trim()) {
        alert("Please fill in all required fields: Query, Context, and Answer.");
        setIsLoading(false);
        return;
      }

      // Call RAG evaluation API
      const token = localStorage.getItem("token");
      const response = await fetch(`${apiBase}/api/v1/rag/evaluate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": token ? `Bearer ${token}` : "",
        },
        body: JSON.stringify({
          query: query.trim(),
          context: context.trim(),
          llm_output: answer.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result: RAGEvaluationResult = await response.json();
      setEvaluationResult(result);
      
      // Update success message based on context source
      if (file && file.size > 0) {
        setUploadMessage(`✅ RAG evaluation completed! Used uploaded file "${file.name}" as context.`);
      } else {
        setUploadMessage("✅ RAG evaluation completed! Used manually entered context.");
      }

    } catch (err) {
      console.error("Error during RAG evaluation:", err);
      setUploadMessage(`❌ Error: ${err instanceof Error ? err.message : 'Unknown error occurred'}`);
      setEvaluationResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="home-content">
        {/* Account Settings and Logout Buttons - Top Right */}
        <div className="account-actions">
          <button onClick={() => navigate("/account-settings")}>Account Settings</button>
          <button onClick={handleLogout} className="logout-button">Log Out</button>
        </div>

        <header>
          <h1>Dashboard</h1>
          <p>Welcome to your RAG Evaluator workspace</p>
        </header>

        {/* RAG Evaluation section */}
        <section>
          <h2>RAG Response Evaluation</h2>
          <form onSubmit={handleEvaluation}>
            <label>
              Query:
              <textarea
                placeholder="Enter your original query here..."
                name="query"
                rows={2}
                required
                disabled={isLoading}
              />
            </label>

            <label>
              Context:
              <textarea
                placeholder="Enter the context or retrieved information here..."
                name="context"
                rows={4}
                disabled={isLoading}
              />
              <small className="context-hint">
                💡 <strong>Two ways to provide context:</strong><br/>
                1. Type directly in the textarea above, OR<br/>
                2. Upload a .txt file below (file content will override textarea)
              </small>
              <input type="file" name="file" accept=".txt" className="context-file-input" disabled={isLoading} />
            </label>

            <label>
              LLM Answer:
              <textarea
                placeholder="Enter the LLM-generated answer to evaluate..."
                name="answer"
                rows={4}
                required
                disabled={isLoading}
              />
            </label>

            <button type="submit" disabled={isLoading}>
              {isLoading ? "Evaluating..." : "Evaluate RAG Response"}
            </button>
          </form>

          {/* --- Status message --- */}
          {uploadMessage && (
            <div className={`upload-message ${uploadMessage.includes('❌') ? 'error' : 'success'}`} role="status">
              <p>{uploadMessage}</p>
              {fileContent && (
                <details className="file-preview">
                  <summary>📄 View {fileName}</summary>
                  <pre>{fileContent}</pre>
                </details>
              )}
            </div>
          )}

          {/* --- Evaluation Results --- */}
          {evaluationResult && evaluationResult.status === "success" && (
            <div className="evaluation-results">
              <h3>📊 Evaluation Results</h3>
              
              {/* Aggregate Metrics */}
              {evaluationResult.aggregate_metrics && (
                <div className="aggregate-metrics">
                  <h4>Summary Metrics</h4>
                  <div className="metrics-grid">
                    <div className="metric">
                      <span className="metric-label">Faithfulness Rate:</span>
                      <span className="metric-value faithful">{(evaluationResult.aggregate_metrics.faithfulness_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Hallucination Rate:</span>
                      <span className="metric-value hallucinated">{(evaluationResult.aggregate_metrics.hallucination_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Inferred Rate:</span>
                      <span className="metric-value inferred">{(evaluationResult.aggregate_metrics.inferred_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Extrapolated Rate:</span>
                      <span className="metric-value extrapolated">{(evaluationResult.aggregate_metrics.extrapolated_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Total Sentences:</span>
                      <span className="metric-value">{evaluationResult.aggregate_metrics.total_sentences}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Detailed Results */}
              <details className="detailed-results">
                <summary>📋 Detailed Sentence Analysis ({evaluationResult.sentence_evaluations?.length} sentences)</summary>
                {evaluationResult.sentence_evaluations && (
                  <div className="sentence-evaluations">
                    {evaluationResult.sentence_evaluations.map((evaluation, index) => (
                      <div key={index} className={`sentence-evaluation ${evaluation.classification}`}>
                        <div className="sentence-header">
                          <span className="sentence-number">#{evaluation.sentence_number}</span>
                          <span className={`classification ${evaluation.classification}`}>
                            {evaluation.classification.toUpperCase()}
                          </span>
                        </div>
                        <div className="sentence-text">"{evaluation.sentence_text}"</div>
                        <div className="justification">
                          <strong>Justification:</strong> {evaluation.justification}
                        </div>
                        {evaluation.supporting_chunk !== "N/A" && (
                          <div className="supporting-chunk">
                            <strong>Supporting Evidence:</strong> "{evaluation.supporting_chunk}"
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </details>

              {/* Raw JSON for debugging (collapsible) */}
              <details className="raw-json">
                <summary>🔧 Raw JSON Response</summary>
                <pre>{JSON.stringify(evaluationResult, null, 2)}</pre>
              </details>
            </div>
          )}
        </section>

        <footer>
          <p>©️ {new Date().getFullYear()} RAG Pipeline Evaluator</p>
        </footer>
      </div>
    </div>
  );
}