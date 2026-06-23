"use client";

import * as React from "react";

/** False on server and first client render; true after hydration. */
export function useMounted(): boolean {
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);
  return mounted;
}
