"use client";

import dynamic from "next/dynamic";
import { AlertTriangle, Briefcase, FileText, FolderKanban, Github, Loader2, Settings, UserCircle } from "lucide-react";
import * as React from "react";

import { Motion } from "@/components/ui/motion";
import { cn } from "@/lib/utils";

const ProfileSettingsPanel = dynamic(
  () => import("@/components/settings/profile-settings-panel").then((m) => m.ProfileSettingsPanel),
  { loading: () => <PanelSkeleton /> },
);
const CVSettingsPanel = dynamic(
  () => import("@/components/settings/cv-settings-panel").then((m) => m.CVSettingsPanel),
  { loading: () => <PanelSkeleton /> },
);
const LinkedInSettingsPanel = dynamic(
  () => import("@/components/settings/linkedin-settings-panel").then((m) => m.LinkedInSettingsPanel),
  { loading: () => <PanelSkeleton /> },
);
const GitHubSettingsPanel = dynamic(
  () => import("@/components/settings/github-settings-panel").then((m) => m.GitHubSettingsPanel),
  { loading: () => <PanelSkeleton /> },
);
const PortfolioSettingsPanel = dynamic(
  () => import("@/components/settings/portfolio-settings-panel").then((m) => m.PortfolioSettingsPanel),
  { loading: () => <PanelSkeleton /> },
);
const ProfileDangerZone = dynamic(
  () => import("@/components/settings/profile-danger-zone").then((m) => m.ProfileDangerZone),
  { loading: () => <PanelSkeleton /> },
);

function PanelSkeleton() {
  return (
    <div className="flex justify-center py-12">
      <Loader2 className="h-7 w-7 animate-spin text-primary" />
    </div>
  );
}

/** Ordre logique : identité → documents → parcours pro → technique → projets */
const SECTIONS = [
  { id: "profile", label: "Profil", icon: UserCircle, step: 1 },
  { id: "cv", label: "CV", icon: FileText, step: 2 },
  { id: "linkedin", label: "LinkedIn", icon: Briefcase, step: 3 },
  { id: "github", label: "GitHub", icon: Github, step: 4 },
  { id: "portfolio", label: "Projets", icon: FolderKanban, step: 5 },
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
      const sectionId = hash.replace("settings-", "") as SectionId;
      if (SECTIONS.some((s) => s.id === sectionId)) {
        setActive(sectionId);
        requestAnimationFrame(() => {
          document.getElementById(hash)?.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      }
    }
  }, []);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible?.target.id?.startsWith("settings-")) {
          const id = visible.target.id.replace("settings-", "") as SectionId;
          if (SECTIONS.some((s) => s.id === id)) {
            setActive(id);
          }
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
              Complétez votre profil étape par étape pour un mentorat personnalisé.
            </p>
          </div>
        </div>
      </Motion>

      <div className="sticky top-4 z-40 mb-6">
        <nav className="glass-card flex flex-wrap gap-1.5 p-2.5" aria-label="Sections des paramètres">
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
                <span className="hidden sm:inline">{section.step}.</span>
                {section.label}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="space-y-10 pb-8">
        <section id="settings-profile" className="scroll-mt-28">
          <SectionHeader
            step={1}
            icon={UserCircle}
            title="Profil étudiant"
            description="Université, filière, métier visé et présentation."
          />
          <ProfileSettingsPanel />
        </section>

        <section id="settings-cv" className="scroll-mt-28">
          <SectionHeader
            step={2}
            icon={FileText}
            title="Mon CV"
            description="Document officiel pour l'analyse de compétences."
          />
          <CVSettingsPanel />
        </section>

        <section id="settings-linkedin" className="scroll-mt-28">
          <SectionHeader
            step={3}
            icon={Briefcase}
            title="LinkedIn"
            description="Parcours professionnel, stages et expériences."
          />
          <LinkedInSettingsPanel />
        </section>

        <section id="settings-github" className="scroll-mt-28">
          <SectionHeader
            step={4}
            icon={Github}
            title="GitHub"
            description="Dépôts, langages et activité technique."
          />
          <GitHubSettingsPanel />
        </section>

        <section id="settings-portfolio" className="scroll-mt-28">
          <SectionHeader
            step={5}
            icon={FolderKanban}
            title="Mes projets"
            description="Liens vers vos réalisations (comptent pour votre niveau)."
          />
          <PortfolioSettingsPanel />
        </section>

        <section id="settings-danger" className="scroll-mt-28 border-t border-destructive/15 pt-10">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Zone de danger
          </h2>
          <ProfileDangerZone />
        </section>
      </div>
    </div>
  );
}

function SectionHeader({
  step,
  icon: Icon,
  title,
  description,
}: {
  step: number;
  icon: typeof UserCircle;
  title: string;
  description: string;
}) {
  return (
    <div className="mb-4">
      <h2 className="flex items-center gap-2 text-lg font-bold text-[hsl(var(--navy))]">
        <Icon className="h-5 w-5 text-primary" />
        <span className="text-sm font-bold text-primary/70">{step}.</span>
        {title}
      </h2>
      <p className="mt-1 text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
