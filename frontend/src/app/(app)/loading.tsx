/** Instant route transition: thin bar, no full-page spinner. */
export default function AppLoading() {
  return <div className="h-0.5 w-full animate-pulse bg-primary/40" aria-hidden />;
}
