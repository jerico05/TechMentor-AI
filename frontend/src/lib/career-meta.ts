import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BarChart3,
  Brain,
  Bug,
  Cloud,
  Container,
  Database,
  Layers,
  Layout,
  MessageSquare,
  Palette,
  Server,
  Shield,
  Smartphone,
  Sparkles,
  Target,
} from "lucide-react";

export interface CareerMeta {
  group: string;
  icon: LucideIcon;
  trending?: boolean;
}

export const CAREER_META: Record<string, CareerMeta> = {
  "ai-engineer": { group: "IA & Data", icon: Sparkles, trending: true },
  "ml-engineer": { group: "IA & Data", icon: Brain, trending: true },
  "prompt-engineer": { group: "IA & Data", icon: MessageSquare, trending: true },
  "data-scientist": { group: "IA & Data", icon: BarChart3 },
  "data-engineer": { group: "IA & Data", icon: Database },
  "backend-developer": { group: "Développement", icon: Server },
  "frontend-developer": { group: "Développement", icon: Layout },
  "fullstack-developer": { group: "Développement", icon: Layers },
  "mobile-developer": { group: "Développement", icon: Smartphone },
  "devops-engineer": { group: "Infrastructure & Cloud", icon: Container },
  "cloud-architect": { group: "Infrastructure & Cloud", icon: Cloud },
  "sre-engineer": { group: "Infrastructure & Cloud", icon: Activity },
  "cybersecurity-engineer": { group: "Sécurité & Qualité", icon: Shield },
  "qa-engineer": { group: "Sécurité & Qualité", icon: Bug },
  "product-manager-tech": { group: "Produit & Design", icon: Target },
  "ux-ui-designer": { group: "Produit & Design", icon: Palette },
};

export const CAREER_GROUP_ORDER = [
  "IA & Data",
  "Développement",
  "Infrastructure & Cloud",
  "Sécurité & Qualité",
  "Produit & Design",
  "Autres",
] as const;

export function getCareerMeta(slug: string): CareerMeta {
  return (
    CAREER_META[slug] ?? {
      group: "Autres",
      icon: Target,
    }
  );
}
