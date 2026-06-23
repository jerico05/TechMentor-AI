"use client";

import * as React from "react";

import { hasSessionCookie } from "@/lib/session-cookie";

/** Cookie session flag (client-only, safe for hydration). */
export function useSessionCookie(): boolean {
  const [active, setActive] = React.useState(false);

  React.useEffect(() => {
    setActive(hasSessionCookie());
  }, []);

  return active;
}
