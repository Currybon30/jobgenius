import React from "react";
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import "./Register.css";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export function Register() {
  const navigate = useNavigate();
  const controllerRef = useRef(null);

  const [lastname, setLastname] = useState("");
  const [firstname, setFirstname] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [country, setCountry] = useState("");

  useEffect(() => {
    axios.get("http://ip-api.com/json").then((res) => {
      setCountry(res.data.country);
    });

    // cleanup: abort any ongoing requests if the component unmounts (e.g., user navigates away)
    return () => {
      controllerRef.current?.abort();
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    // abort previous request if user clicks multiple times
    controllerRef.current?.abort();

    const controller = new AbortController();
    controllerRef.current = controller;

    try {
      let name = "";
      if (country === "Vietnam") {
        name = `${lastname} ${firstname}`;
      } else {
        name = `${firstname} ${lastname}`;
      }

      const body = {
        name,
        email,
        password,
      };
      await axios.post(
        `${import.meta.env.REACT_APP_API_URL}/auth/register`,
        body,
        { signal: controller.signal,
          withCredentials: true
        },
      );
      navigate("/login");
      toast.success("Registration successful");
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

  return (
    <div className="register-container">
      <div className="wrapper">
        <h2>Welcome to JobGenius</h2>
        <form onSubmit={handleSubmit} className="register-form" autoComplete="off">
          <div className="name-row">
            <div className="input-field">
              <input
                id="lastname"
                type="text"
                value={lastname}
                onChange={(e) => setLastname(e.target.value)}
                placeholder=" "
                autoComplete="off"
                required
              />
              <label htmlFor="lastname">Last Name</label>
            </div>
            <div className="input-field">
              <input
                id="firstname"
                type="text"
                value={firstname}
                onChange={(e) => setFirstname(e.target.value)}
                placeholder=" "
                autoComplete="off"
                required
              />
              <label htmlFor="firstname">First Name</label>
            </div>
          </div>
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
          <div className="input-field">
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder=" "
              autoComplete="new-password"
              required
            />
            <label htmlFor="confirmPassword">Confirm Password</label>
          </div>
          <button type="submit">Register</button>
        </form>
        <div className="register-form-bottom">
          <p className="login-link">Already have an account? <Link to="/login">Login</Link></p>
        </div>
        <ToastContainer position="top-right" autoClose={5000} />
      </div>
    </div>
  );
}