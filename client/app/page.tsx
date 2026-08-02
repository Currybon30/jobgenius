"use client";

import { useEffect } from "react";
import { handleAnonymousReady } from "@/auth/api";
import { useAuth } from "@/contexts/AuthContext";
import "./globals.css";

export default function Home() {
  const { status } = useAuth();
  useEffect(() => {
    if (status === "unauthenticated") {
      handleAnonymousReady();
    }
  }, [status]);

  return (
    <>
      <div>Home Page. Pending...</div>
    </>
  );
}
