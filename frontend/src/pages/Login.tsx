// src/pages/Register.jsx
import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styling/Login.css";

interface APIResponse {
  message?: string;
  detail?: string;
  access_token?: string;
  token_type?: string;
}

export default function Login() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [message, setMessage] = useState<string>("");
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  const response = await fetch(`${apiBase}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        password: password, 
      }),
    });
    
    const data: APIResponse = await response.json();
    if (response.ok) {
      // Store the access token in localStorage
      if (data.access_token) {
        localStorage.setItem("token", data.access_token);
      }
      setMessage(data.message ?? "Login Successful");
      navigate('/home')
    } else {
      setMessage(data.detail ?? "Invalid Credentials");
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <input placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <button type="submit">Log In</button>
          
          <div className='reset-link'>
            <Link to={"/request-reset-password"}>Forgot password?</Link>
          </div>
        </form>
        
        {message && <p className={message.includes("Invalid") || message.includes("Failed") ? "error" : "success"}>{message}</p>}
        
        <div className="signup-link-section">
          <p className="signup-prompt">Don't have an account?</p>
          <Link to={"/register"}>
            <button type="button" className="signup-button">Create Account</button>
          </Link>
        </div>
      </div>
    </div>
  );
}
