"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { handleLogout } from "@/auth/api";
import { clearAuthSession, useAuth } from "@/contexts/AuthContext";
import { getUserPlan } from "@/services/userServices";
import "./navBar.css";
import { toast } from "react-toastify";

const NAV_LINKS = [
  { label: "Home", href: "/" },
  { label: "Resume Analyzer", href: "/resume-analyzer" },
  { label: "Jobs", href: "/jobs" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
] as const;

const PROFILE_LINKS = [
  { label: "My Account", href: "/my-account" },
  { label: "Settings", href: "/settings" },
  { label: "Help", href: "/help" },
] as const;

function ProfileIcon() {
  return (
    <svg
      className="profile-icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      aria-hidden="true"
    >
      <circle cx="12" cy="8" r="4" />
      <path d="M5 20c1.5-3.5 4.5-5.5 7-5.5s5.5 2 7 5.5" strokeLinecap="round" />
    </svg>
  );
}

function AuthActionSkeleton() {
  return (
    <div
      className="navbar-auth-skeleton"
      aria-hidden="true"
      aria-busy="true"
    />
  );
}

export function NavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const { status, refreshAuth } = useAuth();
  const [userPlanState, setUserPlanState] = useState("");
  const planFetchedRef = useRef(false);

  const checkUserPlan = useCallback(async () => {
    try {
      setUserPlanState(await getUserPlan());
    } catch {
      setUserPlanState("FREE");
    }
  }, []);

  useEffect(() => {
    if (status !== "authenticated") {
      setUserPlanState("");
      planFetchedRef.current = false;
      return;
    }
    if (planFetchedRef.current) return;

    planFetchedRef.current = true;
    void checkUserPlan();
  }, [status, checkUserPlan]);

  const onLogout = async () => {
    try {
      await handleLogout();
      toast.success("Logged out successfully");
    } catch {
      /* still clear local session state */
    } finally {
      setUserPlanState("");
      planFetchedRef.current = false;
      clearAuthSession();
      await refreshAuth();
      router.push("/");
      router.refresh();
    }
  };

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  const renderPlanBanner = () => {
    if (status !== "authenticated") return null;

    return userPlanState === "FREE" ? (
      <button
        type="button"
        className="plan-banner is-free"
        // onClick={() => router.push("/upgrade")}
      >
        Upgrade ★
      </button>
    ) : (
      <p className="plan-banner is-premium">
        {userPlanState}
      </p>
    );
  };

  const renderAuthAction = () => {
    if (status === "loading") {
      return <AuthActionSkeleton />;
    }

    if (status === "authenticated") {
      return (
        <div className="profile-menu">
          <button
            type="button"
            className="profile-trigger"
            aria-label="Account menu"
            aria-haspopup="true"
          >
            <ProfileIcon />
          </button>
          <div className="profile-dropdown" role="menu">
            {PROFILE_LINKS.map(({ label, href }) => (
              <Link
                key={href}
                href={href}
                className="profile-dropdown-item"
                role="menuitem"
              >
                {label}
              </Link>
            ))}
            <button
              type="button"
              className="profile-dropdown-item logout"
              role="menuitem"
              onClick={onLogout}
            >
              Logout
            </button>
          </div>
        </div>
      );
    }

    return (
      <Link href="/login" className="navbar-login-btn">
        Log in
      </Link>
    );
  };

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link href="/" className="navbar-brand">
          JobGenius
        </Link>

        <nav className="navbar-center" aria-label="Main navigation">
          {NAV_LINKS.map(({ label, href }) => (
            <Link
              key={href}
              href={href}
              className={`navbar-link${isActive(href) ? " is-active" : ""}`}
            >
              {label}
            </Link>
          ))}
        </nav>

        <div className="navbar-end">
          {renderPlanBanner()}
          <div className="navbar-actions">
            {renderAuthAction()}
          </div>
        </div>
      </div>
    </header>
  );
}
