"use client";

import { AppPrefetcher } from "@/components/app/app-prefetcher";
import { DashboardNav } from "@/components/dashboard/dashboard-nav";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background px-2 py-3 sm:px-4 sm:py-6 md:px-6 md:py-8">
      <AppPrefetcher />
      <div className="crextio-shell mx-auto max-w-[1440px] px-3 py-4 sm:px-6 sm:py-8 md:px-10 md:py-10">
        <DashboardNav />
        <main className="mt-6 min-w-0 md:mt-8 lg:mt-10">{children}</main>
      </div>
    </div>
  );
}
