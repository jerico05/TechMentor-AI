import Link from "next/link";
import { Sparkles } from "lucide-react";

import { APP_NAME } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface SiteHeaderProps {
  className?: string;
  rightSlot?: React.ReactNode;
}

/** Header landing - style Crextio. */
export function SiteHeader({ className, rightSlot }: SiteHeaderProps) {
  return (
    <header className={cn("w-full px-4 py-6 sm:px-8", className)}>
      <div className={cn("mx-auto flex max-w-6xl items-center rounded-full bg-white px-6 py-3 shadow-[0_4px_24px_rgba(26,43,75,0.06)]", rightSlot ? "justify-between" : "justify-center sm:justify-start")}>
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[hsl(var(--navy))] text-white shadow-md">
            <Sparkles className="h-4 w-4" />
          </span>
          <span className="text-lg font-bold tracking-tight text-[hsl(var(--navy))]">{APP_NAME}</span>
        </Link>
        {rightSlot ? <div className="flex items-center gap-2">{rightSlot}</div> : null}
      </div>
    </header>
  );
}
