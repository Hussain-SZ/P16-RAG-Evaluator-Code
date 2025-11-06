// import React from "react";
import { Link } from "react-router-dom";
import "../styling/Welcome.css";
import BlurText from "../assets/blurtext.tsx";

// const handleAnimationComplete = () => {
//   console.log('Animation completed!');
// };

export default function Welcome() {
  return (
    <div className="welcome-container">
      <div className="welcome-content">
        {/* Top Right Navigation */}
        <div className="top-nav">
          <Link to="/register" className="nav-button">Create Account</Link>
          <Link to="/login" className="nav-button secondary">Sign In</Link>
        </div>
        <header>
          <BlurText
            text="RAG Pipeline Evaluator"
            delay={60}
            animateBy="words"
            direction="top"
            className="header-title"
          />
          <BlurText
            text="Test, debug, and optimize your RAG pipelines to improve quality, reduce hallucinations, and deliver trusted AI outcomes."
            delay={100}
            animateBy="words"
            direction="top"
            className="header-subtitle"
          />
        </header>


        <main>
          <section>
            <h2>What this does</h2>
            <p>
              This tool helps you evaluate Retrieval-Augmented Generation (RAG) systems
              for faithfulness, hallucination, and overall quality. Ensure your AI retrieves 
              the right data and uses it correctly.
            </p>
          </section>

          <section>
            <h2>Why it matters</h2>
            <p>
              Automate and scale RAG evaluation with our platform. Generate test data and 
              run quality checks to get reliable, fact-based answers in production 
              environments.
            </p>
          </section>
        </main>

        <div className="features-grid">
          <div className="feature-card">
            <span className="feature-icon">Target</span>
            <h3>Synthetic Data</h3>
            <p>Automatically create test cases from your internal data sources to evaluate retrieval accuracy.</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">Chart</span>
            <h3>Quality Metrics</h3>
            <p>Use built-in RAG metrics to measure faithfulness, relevance, and completeness of responses.</p>
          </div>
          <div className="feature-card">
            <span className="feature-icon">Search</span>
            <h3>Debug & Optimize</h3>
            <p>Pinpoint retrieval or generation failures and optimize your pipeline before impact.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
