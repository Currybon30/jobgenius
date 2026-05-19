"use client";

import axios from "axios";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { ToastContainer, toast } from "react-toastify";
import { handleGoogleLogin } from "@/auth/oauth";
import { handleLogin } from "@/auth/api";
import { LoginRequest } from "@/auth/types";

import "react-toastify/dist/ReactToastify.css";
import "./login.css";

export function LoginForm() {
  const router = useRouter();
  const controllerRef = useRef<AbortController | null>(null);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    return () => {
      controllerRef.current?.abort();
    };
  }, []);

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();

    // abort previous request if user clicks multiple times
    controllerRef.current?.abort();

    const controller = new AbortController();
    controllerRef.current = controller;

    controller.signal.addEventListener("abort", () => {
      toast.error("Login failed: Request was aborted by user");
    });

    try {
      const loginRequest: LoginRequest = {
        email,
        password,
      };

      await handleLogin(loginRequest, { signal: controller.signal, withCredentials: true });

      toast.success("Login successful");

      router.push("/");
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        if (error.name === "CanceledError") {
          toast.error("Login failed: Request was aborted by user");
        } else {
          toast.error(
            "Login failed: " + (error.response?.data?.message || error.message),
          );
        }
      } else if (error instanceof Error) {
        toast.error("Login failed: " + error.message);
      } else {
        toast.error("Login failed");
      }
    }
  };

  return (
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
            required
          />

          <label htmlFor="password">Password</label>
        </div>
        <p className="forgot-password-text">
          <a
            href="#"
            className="forgot-password-link is-disabled"
            onClick={(e) => e.preventDefault()}
            aria-disabled="true"
          >
            Forgot Password?
          </a>
        </p>

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
        <p className="register-link">
          Do not have an account? <Link href="/register">Register</Link>
        </p>
      </div>
      <ToastContainer position="top-right" autoClose={5000} />
    </div>
  );
}
