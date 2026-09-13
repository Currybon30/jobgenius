"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { handleRefreshToken } from "@/auth/api";
import { getCurrentUser } from "@/services/userService";
import { getUserPlan } from "@/services/userService";

export type AuthStatus = "loading" | "authenticated" | "unauthenticated";

const AUTH_STATUS_STORAGE_KEY = "jobgenius_auth_status";
/** Access JWT TTL is 15 minutes — refresh slightly early to avoid expiry races. */
const ACCESS_TOKEN_REFRESH_MS = 14 * 60 * 1000;

export type AuthContextValue = {
  status: AuthStatus;
  tier: string | null;
  refreshAuth: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function readStoredStatus(): AuthStatus | null {
  if (typeof window === "undefined") return null;
  const stored = sessionStorage.getItem(AUTH_STATUS_STORAGE_KEY);
  if (stored === "authenticated" || stored === "unauthenticated") {
    return stored;
  }
  return null;
}

function persistStatus(status: AuthStatus) {
  if (typeof window === "undefined" || status === "loading") return;
  sessionStorage.setItem(AUTH_STATUS_STORAGE_KEY, status);
}

function clearStoredStatus() {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(AUTH_STATUS_STORAGE_KEY);
}

const AUTH_RESOLVE_TIMEOUT_MS = 4000;

async function resolveAuthStatus(): Promise<AuthStatus> {
  try {
    const user = await Promise.race([
      getCurrentUser(),
      new Promise<never>((_, reject) => {
        window.setTimeout(
          () => reject(new Error("Auth check timed out")),
          AUTH_RESOLVE_TIMEOUT_MS,
        );
      }),
    ]);
    return user ? "authenticated" : "unauthenticated";
  } catch {
    return "unauthenticated";
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  // Always "loading" on first render so SSR and client markup match (no sessionStorage in useState).
  const [status, setStatus] = useState<AuthStatus>("loading"); // status: "loading" | "authenticated" | "unauthenticated"
  const [tier, setTier] = useState<string | null>(null);
  const initialFetchDoneRef = useRef(false);
  const fetchInFlightRef = useRef<Promise<AuthStatus> | null>(null);
  const tokenRefreshInFlightRef = useRef<Promise<void> | null>(null);

  const refreshAuth = useCallback(async () => {
    if (fetchInFlightRef.current) {
      await fetchInFlightRef.current;
      return;
    }

    const run = (async () => {
      const next = await resolveAuthStatus();
      setStatus(next);
      persistStatus(next);
      if (next === "authenticated") {
        const nextTier = await getUserPlan();
        setTier(nextTier);
      } else {
        setTier(null);
      }
      return next;
    })();

    fetchInFlightRef.current = run;
    try {
      await run;
    } finally {
      fetchInFlightRef.current = null;
    }
  }, []);

  const refreshAccessToken = useCallback(async () => {
    if (tokenRefreshInFlightRef.current) {
      await tokenRefreshInFlightRef.current;
      return;
    }

    const run = (async () => {
      try {
        await handleRefreshToken();
      } catch {
        clearStoredStatus();
        setStatus("unauthenticated");
        setTier(null);
      }
    })();

    tokenRefreshInFlightRef.current = run;
    try {
      await run;
    } finally {
      tokenRefreshInFlightRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (initialFetchDoneRef.current) return;
    initialFetchDoneRef.current = true;

    const stored = readStoredStatus();
    if (stored) {
      setStatus(stored);
      void refreshAuth(); // void is used to avoid the warning of async function in useEffect
      return;
    }

    void (async () => {
      const next = await resolveAuthStatus();
      setStatus(next);
      persistStatus(next);
      if (next === "authenticated") {
        const nextTier = await getUserPlan();
        setTier(nextTier);
      } else {
        setTier(null);
      }
    })();
  }, [refreshAuth]);

  // Keep access token fresh while the user stays authenticated.
  useEffect(() => {
    if (status !== "authenticated") return;

    const intervalId = window.setInterval(() => {
      void refreshAccessToken();
    }, ACCESS_TOKEN_REFRESH_MS);

    const onVisible = () => {
      if (document.visibilityState === "visible") {
        void refreshAccessToken();
      }
    };
    document.addEventListener("visibilitychange", onVisible);

    return () => {
      window.clearInterval(intervalId);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [status, refreshAccessToken]);

  const value = useMemo<AuthContextValue>(
    () => ({ status, tier, refreshAuth }),
    [status, tier, refreshAuth],
  );

  return (
    <AuthContext.Provider value={value}>
      <div suppressHydrationWarning>
        {children}
      </div>
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export function clearAuthSession(): void {
  clearStoredStatus();
}
