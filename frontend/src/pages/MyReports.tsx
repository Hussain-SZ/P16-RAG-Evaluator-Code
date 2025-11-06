import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styling/MyReports.css";

interface ReportSummary {
  report_id: string;
  report_name: string;
  faithfulness_rate: number;
  hallucination_rate: number;
  total_sentences: number;
  created_at: string;
  tags: string[];
}

interface ReportDetail {
  report_id: string;
  report_name: string;
  query: string;
  context: string;
  llm_output: string;
  aggregate_metrics: any;
  sentence_evaluations: any[];
  created_at: string;
  tags: string[];
  notes: string;
}

export default function MyReports() {
  const navigate = useNavigate();
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReportDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  // Fetch all reports on component mount
  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/login");
        return;
      }

      const response = await fetch(`${apiBase}/api/v1/reports/my-reports`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem("token");
          navigate("/login");
          return;
        }
        throw new Error(`Failed to fetch reports: ${response.status}`);
      }

      const data = await response.json();
      setReports(data);
    } catch (err) {
      console.error("Error fetching reports:", err);
      setError(err instanceof Error ? err.message : "Failed to load reports");
    } finally {
      setIsLoading(false);
    }
  };

  const fetchReportDetails = async (reportId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${apiBase}/api/v1/reports/report/${reportId}`, {
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch report details: ${response.status}`);
      }

      const data = await response.json();
      setSelectedReport(data);
    } catch (err) {
      console.error("Error fetching report details:", err);
      setError(err instanceof Error ? err.message : "Failed to load report details");
    } finally {
      setIsLoading(false);
    }
  };

  const deleteReport = async (reportId: string) => {
    if (!confirm("Are you sure you want to delete this report?")) {
      return;
    }

    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`${apiBase}/api/v1/reports/report/${reportId}`, {
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to delete report");
      }

      // Refresh the list
      fetchReports();
      setSelectedReport(null);
      alert("Report deleted successfully!");
    } catch (err) {
      console.error("Error deleting report:", err);
      alert(err instanceof Error ? err.message : "Failed to delete report");
    }
  };

  return (
    <div className="my-reports-container">
      <div className="my-reports-content">
        {/* Header with navigation */}
        <div className="reports-header">
          <button onClick={() => navigate("/home")} className="back-button">
            ← Back to Dashboard
          </button>
          <h1>My Saved Reports</h1>
        </div>

        {/* Error message */}
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {/* Loading state */}
        {isLoading && reports.length === 0 && (
          <div className="loading-message">
            Loading reports...
          </div>
        )}

        <div className="reports-layout">
          {/* Reports List */}
          <div className="reports-list">
            <h2>Saved Evaluations ({reports.length})</h2>
            
            {reports.length === 0 && !isLoading && (
              <div className="no-reports">
                <p>No saved reports yet</p>
                <button onClick={() => navigate("/home")}>
                  Create Your First Evaluation
                </button>
              </div>
            )}

            {reports.map((report) => (
              <div
                key={report.report_id}
                className={`report-card ${selectedReport?.report_id === report.report_id ? 'selected' : ''}`}
                onClick={() => fetchReportDetails(report.report_id)}
              >
                <div className="report-card-header">
                  <h3>{report.report_name}</h3>
                  <span className="report-date">
                    {new Date(report.created_at).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="report-card-metrics">
                  <div className="metric-badge faithful">
                    ✓ {(report.faithfulness_rate * 100).toFixed(0)}%
                  </div>
                  <div className="metric-badge hallucinated">
                    ✗ {(report.hallucination_rate * 100).toFixed(0)}%
                  </div>
                  <div className="metric-badge">
                    📝 {report.total_sentences} sentences
                  </div>
                </div>

                {report.tags.length > 0 && (
                  <div className="report-tags">
                    {report.tags.map((tag, idx) => (
                      <span key={idx} className="tag">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Report Details Panel */}
          <div className="report-details-panel">
            {!selectedReport && (
              <div className="no-selection">
                <p>Select a report to view details</p>
              </div>
            )}

            {selectedReport && (
              <div className="report-details">
                <div className="report-details-header">
                  <h2>{selectedReport.report_name}</h2>
                  <button
                    onClick={() => deleteReport(selectedReport.report_id)}
                    className="delete-button"
                  >
                    🗑️ Delete
                  </button>
                </div>

                <div className="report-meta">
                  <span>Created: {new Date(selectedReport.created_at).toLocaleString()}</span>
                  {selectedReport.tags.length > 0 && (
                    <div className="tags">
                      {selectedReport.tags.map((tag, idx) => (
                        <span key={idx} className="tag">{tag}</span>
                      ))}
                    </div>
                  )}
                </div>

                {selectedReport.notes && (
                  <div className="report-notes">
                    <strong>Notes:</strong> {selectedReport.notes}
                  </div>
                )}

                {/* Original Inputs */}
                <details className="report-section">
                  <summary>📝 Original Inputs</summary>
                  <div className="input-display">
                    <div>
                      <strong>Query:</strong>
                      <p>{selectedReport.query}</p>
                    </div>
                    <div>
                      <strong>Context:</strong>
                      <pre>{selectedReport.context}</pre>
                    </div>
                    <div>
                      <strong>LLM Output:</strong>
                      <p>{selectedReport.llm_output}</p>
                    </div>
                  </div>
                </details>

                {/* Aggregate Metrics */}
                <div className="report-section">
                  <h3>📊 Summary Metrics</h3>
                  <div className="metrics-grid">
                    <div className="metric">
                      <span className="metric-label">Faithfulness Rate:</span>
                      <span className="metric-value faithful">
                        {(selectedReport.aggregate_metrics.faithfulness_rate * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Hallucination Rate:</span>
                      <span className="metric-value hallucinated">
                        {(selectedReport.aggregate_metrics.hallucination_rate * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Inferred Rate:</span>
                      <span className="metric-value inferred">
                        {(selectedReport.aggregate_metrics.inferred_rate * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Extrapolated Rate:</span>
                      <span className="metric-value extrapolated">
                        {(selectedReport.aggregate_metrics.extrapolated_rate * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Sentence Evaluations */}
                <details className="report-section" open>
                  <summary>📋 Detailed Sentence Analysis ({selectedReport.sentence_evaluations.length} sentences)</summary>
                  <div className="sentence-evaluations">
                    {selectedReport.sentence_evaluations.map((evaluation, index) => (
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
                </details>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
