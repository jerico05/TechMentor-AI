"use client";

import { DashboardNav } from "@/components/dashboard/dashboard-nav";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto min-h-screen max-w-[1400px] px-4 py-6 md:px-8">
      <DashboardNav />
      {children}
    </div>
  );
}
