import Link from "next/link";

import { APP_NAME } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface SiteHeaderProps {
  className?: string;
  rightSlot?: React.ReactNode;
}

/** Public landing header — logo + optional actions slot. */
export function SiteHeader({ className, rightSlot }: SiteHeaderProps) {
  return (
    <header className={cn("sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur", className)}>
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold">
            T
          </span>
          <span className="text-lg font-semibold tracking-tight">{APP_NAME}</span>
        </Link>
        <div className="flex items-center gap-2">{rightSlot}</div>
      </div>
    </header>
  );
}
