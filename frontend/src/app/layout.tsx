"use client";

import { useEffect, useState } from "react";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getMe, logout, isAuthenticated } from "@/lib/auth";
import { User } from "@/lib/types";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const PUBLIC_PATHS = ["/auth/login", "/auth/register"];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      const isPublicPage = PUBLIC_PATHS.some(
        (p) => pathname === p || pathname.startsWith("/[")
      );
      const isBookingPage = pathname.match(/^\/[^/]+\/[^/]+$/);

      if (isPublicPage || isBookingPage) {
        setLoading(false);
        return;
      }

      if (!isAuthenticated()) {
        router.push("/auth/login");
        return;
      }

      try {
        const me = await getMe();
        setUser(me);
      } catch {
        router.push("/auth/login");
      } finally {
        setLoading(false);
      }
    }
    checkAuth();
  }, [pathname, router]);

  function handleLogout() {
    logout();
  }

  if (loading) {
    return (
      <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
        <body className="min-h-full flex flex-col">
          <main className="flex-1 flex items-center justify-center">
            <div className="text-gray-500">Loading...</div>
          </main>
        </body>
      </html>
    );
  }

  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <Link href="/" className="text-xl font-bold text-gray-900">
                Scheduling Service
              </Link>
              <nav className="flex items-center space-x-4">
                {user ? (
                  <>
                    <Link
                      href="/"
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Event Types
                    </Link>
                    <Link
                      href="/schedules"
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Schedules
                    </Link>
                    <span className="text-sm text-gray-500">
                      {user.name || user.username}
                    </span>
                    <button
                      onClick={handleLogout}
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/auth/login"
                      className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                    >
                      Sign In
                    </Link>
                    <Link
                      href="/auth/register"
                      className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
                    >
                      Register
                    </Link>
                  </>
                )}
              </nav>
            </div>
          </div>
        </header>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
