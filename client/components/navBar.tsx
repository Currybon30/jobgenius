"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { getCurrentUser, handleLogout } from "@/auth/api";
import "./navBar.css";

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

const HIDDEN_ROUTES = ["/login", "/register"] as const;

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

export function NavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const hideNav = HIDDEN_ROUTES.some((route) => pathname === route);

  const checkAuth = useCallback(async () => {
    try {
      await getCurrentUser();
      setIsLoggedIn(true);
    } catch {
      setIsLoggedIn(false);
    }
  }, []);

  useEffect(() => {
    if (hideNav) return;
    checkAuth();
  }, [checkAuth, hideNav]);

  const onLogout = async () => {
    try {
      await handleLogout();
      setIsLoggedIn(false);
      router.push("/login");
      router.refresh();
    } catch {
      setIsLoggedIn(false);
      router.push("/login");
    }
  };

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  if (hideNav) return null;

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

        <div className="navbar-actions">
          {isLoggedIn ? (
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
          ) : (
            <Link href="/login" className="navbar-login-btn">
              Log in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
