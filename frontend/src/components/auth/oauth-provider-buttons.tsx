import { GitHubIcon, GoogleIcon } from "@/components/auth/oauth-icons";
import { cn } from "@/lib/utils";

interface OAuthProviderButtonsProps {
  disabled?: boolean;
  onGoogle: () => void;
  onGithub: () => void;
  className?: string;
}

/** Boutons OAuth carrés avec logos - style sous le bouton Login. */
export function OAuthProviderButtons({
  disabled,
  onGoogle,
  onGithub,
  className,
}: OAuthProviderButtonsProps) {
  return (
    <div className={cn("space-y-5", className)}>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-border/80" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-white px-3 text-muted-foreground">or</span>
        </div>
      </div>

      <div className="flex items-center justify-center gap-4">
        <button
          type="button"
          disabled={disabled}
          onClick={onGoogle}
          aria-label="Continuer avec Google"
          className="flex h-14 w-14 items-center justify-center rounded-2xl border border-border/80 bg-white shadow-sm transition-all hover:border-primary/30 hover:bg-secondary/40 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50"
        >
          <GoogleIcon />
        </button>
        <button
          type="button"
          disabled={disabled}
          onClick={onGithub}
          aria-label="Continuer avec GitHub"
          className="flex h-14 w-14 items-center justify-center rounded-2xl border border-border/80 bg-white text-[hsl(var(--navy))] shadow-sm transition-all hover:border-primary/30 hover:bg-secondary/40 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50"
        >
          <GitHubIcon />
        </button>
      </div>
    </div>
  );
}
