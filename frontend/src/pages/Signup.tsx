// src/pages/Register.jsx
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styling/Signup.css";


interface APIResponse {
  message?: string;
  detail?: string;
}

export default function Signup() {
  const [name, setName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [otp, setOtp] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const [otpSent, setOtpSent] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleRequestOtp = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");

    try {
  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const response = await fetch(`${apiBase}/auth/request-registration-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name,
          email: email,
          password: password,
        }),
      });

      const data: APIResponse = await response.json();
      if (response.ok) {
        setOtpSent(true);
        setMessage(data.message ?? "OTP sent to your email!");
      } else {
        setMessage(data.detail ?? "Failed to send OTP");
      }
    } catch (err) {
      setMessage("Server error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOtp = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");

    try {
  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const response = await fetch(`${apiBase}/auth/verify-registration-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email,
          otp: otp,
        }),
      });

      const data: APIResponse = await response.json();
      if (response.ok) {
        setMessage(data.message ?? "Account created successfully!");
        setTimeout(() => navigate('/login'), 2000);
      } else {
        setMessage(data.detail ?? "Invalid OTP. Please try again.");
      }
    } catch (err) {
      setMessage("Server error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-box">
        <h2>{otpSent ? "Verify Email" : "Register"}</h2>
        
        {!otpSent ? (
          // Step 1: Request OTP
          <form onSubmit={handleRequestOtp}>
            <input 
              placeholder="Name" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
              required
              disabled={isLoading}
            />
            <input 
              placeholder="Email" 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required
              disabled={isLoading}
            />
            <input 
              placeholder="Password" 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required
              minLength={6}
              disabled={isLoading}
            />
            
            <p className="terms-text">
              By creating an account, you agree to the Terms of Service and Privacy Policy.
            </p>
            
            <button type="submit" disabled={isLoading}>
              {isLoading ? "Sending..." : "Sign Up"}
            </button>
          </form>
        ) : (
          // Step 2: Verify OTP
          <form onSubmit={handleVerifyOtp}>
            <p className="otp-info">
              We've sent a verification code to <strong>{email}</strong>
            </p>
            <input 
              placeholder="Enter 6-digit OTP" 
              type="text" 
              value={otp} 
              onChange={(e) => setOtp(e.target.value)} 
              required
              maxLength={6}
              pattern="\d{6}"
              disabled={isLoading}
            />
            
            <button type="submit" disabled={isLoading}>
              {isLoading ? "Verifying..." : "Verify & Create Account"}
            </button>
            
            <button 
              type="button" 
              onClick={() => {
                setOtpSent(false);
                setOtp("");
                setMessage("");
              }}
              className="back-button"
              disabled={isLoading}
            >
              Back
            </button>
          </form>
        )}
        
        {message && (
          <p className={message.includes("successfully") || message.includes("sent") ? "success-message" : "error-message"}>
            {message}
          </p>
        )}
        
        <div className="login-link-section">
          <p className="login-prompt">Already have an account?</p>
          <Link to={"/login"}>
            <button type="button" className="login-redirect-button">Log In</button>
          </Link>
        </div>
      </div>
    </div>
  );
}
