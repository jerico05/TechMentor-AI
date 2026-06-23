"use client";

import * as React from "react";

import { CAREER_GROUP_ORDER, getCareerMeta } from "@/lib/career-meta";
import { ModernSelect, type SelectOption } from "@/components/ui/modern-select";
import type { CareerPath } from "@/types";

export interface CareerSelectProps {
  id?: string;
  value: number | null | undefined;
  onChange: (value: number | null) => void;
  careers: CareerPath[];
  placeholder?: string;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}

function careerSortIndex(slug: string): number {
  const group = getCareerMeta(slug).group;
  const groupIndex = CAREER_GROUP_ORDER.indexOf(group as (typeof CAREER_GROUP_ORDER)[number]);
  return groupIndex === -1 ? 999 : groupIndex;
}

export function CareerSelect({
  id,
  value,
  onChange,
  careers,
  placeholder = "Sélectionner un métier",
  disabled = false,
  loading = false,
  className,
}: CareerSelectProps) {
  const options = React.useMemo<SelectOption<number>[]>(
    () =>
      [...careers]
        .sort((a, b) => {
          const byGroup = careerSortIndex(a.slug) - careerSortIndex(b.slug);
          if (byGroup !== 0) return byGroup;
          return a.name.localeCompare(b.name, "fr");
        })
        .map((career) => {
          const meta = getCareerMeta(career.slug);
          return {
            value: career.id,
            label: career.name,
            description: career.description ?? undefined,
            icon: meta.icon,
            group: meta.group,
            badge: meta.trending ? "Prometteur" : undefined,
          };
        }),
    [careers],
  );

  return (
    <ModernSelect
      id={id}
      value={value ?? null}
      onChange={onChange}
      options={options}
      placeholder={placeholder}
      disabled={disabled}
      loading={loading}
      searchable
      searchPlaceholder="Rechercher un métier…"
      groupOrder={CAREER_GROUP_ORDER}
      emptyMessage={loading ? "Chargement…" : "Aucun métier trouvé."}
      footer={options.length > 0 ? `${options.length} métiers disponibles, faites défiler pour tout voir` : undefined}
      className={className}
    />
  );
}
