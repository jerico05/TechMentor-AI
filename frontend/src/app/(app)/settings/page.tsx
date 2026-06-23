"use client";

import { FileText, Github, Settings, UserCircle } from "lucide-react";
import * as React from "react";

import { CVSettingsPanel } from "@/components/settings/cv-settings-panel";
import { GitHubSettingsPanel } from "@/components/settings/github-settings-panel";
import { ProfileSettingsPanel } from "@/components/settings/profile-settings-panel";
import { Motion } from "@/components/ui/motion";
import { cn } from "@/lib/utils";

const SECTIONS = [
  { id: "profile", label: "Profil", icon: UserCircle },
  { id: "cv", label: "CV", icon: FileText },
  { id: "github", label: "GitHub", icon: Github },
] as const;

type SectionId = (typeof SECTIONS)[number]["id"];

export default function SettingsPage() {
  const [active, setActive] = React.useState<SectionId>("profile");

  function scrollToSection(id: SectionId) {
    setActive(id);
    document.getElementById(`settings-${id}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  React.useEffect(() => {
    const hash = window.location.hash.replace("#", "");
    if (hash.startsWith("settings-")) {
      setActive(hash.replace("settings-", "") as SectionId);
      requestAnimationFrame(() => {
        document.getElementById(hash)?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  }, []);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible?.target.id?.startsWith("settings-")) {
          setActive(visible.target.id.replace("settings-", "") as SectionId);
        }
      },
      { rootMargin: "-20% 0px -55% 0px", threshold: [0.1, 0.4, 0.7] },
    );

    for (const section of SECTIONS) {
      const el = document.getElementById(`settings-${section.id}`);
      if (el) observer.observe(el);
    }
    return () => observer.disconnect();
  }, []);

  return (
    <div className="mx-auto max-w-2xl">
      <Motion animation="slide-up" delay={1} className="mb-6">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-accent text-white shadow-lg shadow-primary/25">
            <Settings className="h-5 w-5" />
          </span>
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-[hsl(var(--navy))]">Paramètres</h1>
            <p className="text-muted-foreground">
              Gérez votre profil, votre CV et votre GitHub au même endroit.
            </p>
          </div>
        </div>
      </Motion>

      <div className="sticky top-4 z-40 mb-6">
        <nav className="glass-card flex flex-wrap gap-1.5 p-2.5">
          {SECTIONS.map((section) => {
            const Icon = section.icon;
            const isActive = active === section.id;
            return (
              <button
                key={section.id}
                type="button"
                onClick={() => scrollToSection(section.id)}
                className={cn(
                  "inline-flex items-center gap-2",
                  isActive ? "nav-pill-active" : "nav-pill",
                )}
              >
                <Icon className="h-4 w-4" />
                {section.label}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="space-y-10 pb-8">
        <section id="settings-profile" className="scroll-mt-28">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-[hsl(var(--navy))]">
            <UserCircle className="h-5 w-5 text-primary" />
            Profil étudiant
          </h2>
          <ProfileSettingsPanel />
        </section>

        <section id="settings-cv" className="scroll-mt-28">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-[hsl(var(--navy))]">
            <FileText className="h-5 w-5 text-primary" />
            Mon CV
          </h2>
          <CVSettingsPanel />
        </section>

        <section id="settings-github" className="scroll-mt-28">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-[hsl(var(--navy))]">
            <Github className="h-5 w-5 text-primary" />
            GitHub
          </h2>
          <GitHubSettingsPanel />
        </section>
      </div>
    </div>
  );
}
