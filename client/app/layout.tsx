import type { Metadata, Viewport } from "next";
import { NavBar } from "@/components/navBar";
import { Footer } from "@/components/footer";
import { Providers } from "./providers";
import "./globals.css";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

export const metadata: Metadata = {
  title: {
    default: "JobGenius — AI career clarity",
    template: "%s · JobGenius",
  },
  description:
    "JobGenius helps you analyze resumes, match roles, and move your job search forward with AI.",
  keywords: ["JobGenius", "resume analyzer", "job search", "AI career"],
  icons: {
    icon: [
      { url: "/favicon.svg?v=3", type: "image/svg+xml" },
      { url: "/assets/images/icon.png?v=3", type: "image/png", sizes: "32x32" },
      { url: "/favicon.ico?v=3", sizes: "48x48" },
    ],
    shortcut: "/favicon.ico?v=3",
    apple: [{ url: "/assets/images/apple-icon.png?v=3", sizes: "180x180" }],
  },
};

export const viewport: Viewport = {
  themeColor: "#e6effc",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen flex flex-col" suppressHydrationWarning>
        <Providers>
          <NavBar />
          <main className="flex-1 flex flex-col">{children}</main>
          <Footer />
          <ToastContainer
            position="top-right"
            autoClose={2000}
            hideProgressBar={true}
            style={{ marginTop: "60px" }}
          />
        </Providers>
      </body>
    </html>
  );
}
