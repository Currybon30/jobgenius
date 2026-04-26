import React from "react";
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import "./Login.css";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export function Login() {
  const navigate = useNavigate();
  const controllerRef = useRef(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    // cleanup: abort any ongoing requests if the component unmounts (e.g., user navigates away)
    return () => {
      controllerRef.current?.abort();
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // abort previous request if user clicks multiple times
    controllerRef.current?.abort();

    const controller = new AbortController();
    controllerRef.current = controller;

    try {
      const body = {
        email,
        password,
      };
      const response = await axios.post(
        `${import.meta.env.REACT_APP_API_URL}/auth/login`,
        body,
        { signal: controller.signal,
          withCredentials: true
         },
      );
      const token = response.data?.token;
      if (token) {
        localStorage.setItem("token", token);
      }
      navigate("/");
      toast.success("Login successful");
    } catch (error) {
      if (error.name === "CanceledError") {
        console.log("Request aborted");
      } else {
        toast.error(
          "Registration failed: " +
            (error.response?.data?.message || error.message),
        );
      }
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = `${import.meta.env.REACT_APP_SPRING_API_URL}/oauth2/authorization/google`;
  };

  // const handleFacebookLogin = () => {
  //   window.location.href = `#`;
  // };

  return (
    <div className="login-container">
      <div className="wrapper">
        <h2>Login to JobGenius</h2>
        <form onSubmit={handleSubmit} className="login-form" autoComplete="off">
          <div className="input-field">
            <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder=" "
                autoComplete="off"
                required
              />
              <label htmlFor="email">Email</label>
            </div>
            <div className="input-field">
              <input
                id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder=" "
              autoComplete="new-password"
              required
            />
            <label htmlFor="password">Password</label>    
            </div>
          <button type="submit">Login</button>
          <div className="third-app-section">
            <p className="third-app-text">Or continue with</p>
            <div className="social-login-row">
              <button
                type="button"
                className="social-login-btn google-login-btn"
                onClick={handleGoogleLogin}
              >
                <img
                  src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
                  alt="Google logo"
                />
                <span>Google</span>
              </button>
              <button
                type="button"
                className="social-login-btn facebook-login-btn"
                // onClick={handleFacebookLogin}
                disabled
              >
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/0/05/Facebook_Logo_%282019%29.png"
                  alt="Facebook logo"
                />
                <span>Facebook</span>
              </button>
            </div>
          </div>
        </form>
        <div className="login-form-bottom">
          <p className="register-link">Don't have an account? <Link to="/register">Register</Link></p>
        </div>
        <ToastContainer position="top-right" autoClose={5000} />
      </div>
    </div>
  );
}