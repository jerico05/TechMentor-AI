import type { LucideIcon } from "lucide-react";
import { BookOpen, GraduationCap, School } from "lucide-react";

import type { AcademicLevel } from "@/types";

export const ACADEMIC_LEVEL_OPTIONS: {
  value: AcademicLevel;
  label: string;
  description: string;
  icon: LucideIcon;
  group: string;
}[] = [
  {
    value: "licence1",
    label: "Licence 1",
    description: "Première année de licence",
    icon: BookOpen,
    group: "Licence",
  },
  {
    value: "licence2",
    label: "Licence 2",
    description: "Deuxième année de licence",
    icon: BookOpen,
    group: "Licence",
  },
  {
    value: "licence3",
    label: "Licence 3",
    description: "Troisième année de licence",
    icon: BookOpen,
    group: "Licence",
  },
  {
    value: "master1",
    label: "Master 1",
    description: "Première année de master",
    icon: GraduationCap,
    group: "Master",
  },
  {
    value: "master2",
    label: "Master 2",
    description: "Deuxième année de master",
    icon: GraduationCap,
    group: "Master",
  },
  {
    value: "other",
    label: "Autre",
    description: "Parcours ou niveau personnalisé",
    icon: School,
    group: "Autre",
  },
];

export const ACADEMIC_LEVEL_GROUP_ORDER = ["Licence", "Master", "Autre"] as const;
