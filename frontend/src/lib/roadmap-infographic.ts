import type { LucideIcon } from "lucide-react";
import {
  Handshake,
  Presentation,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";

import type { RoadmapMonth } from "@/types";

export const ROAD_VIEWBOX_HEIGHT = 520;

const ROAD_Y_CENTER = 260;
const ROAD_Y_AMPLITUDE = 145;

export const ROAD_STROKE = {
  navy: "#1e3d6e",
  white: "#ffffff",
  dash: "#ffffff",
} as const;

export interface RoadmapStepTheme {
  color: string;
  icon: LucideIcon;
}

export const ROADMAP_STEP_THEMES: RoadmapStepTheme[] = [
  { color: "#e85d6f", icon: Target },
  { color: "#f5923a", icon: Users },
  { color: "#5fbf7d", icon: Presentation },
  { color: "#4a9fd4", icon: TrendingUp },
  { color: "#8b6fd4", icon: Handshake },
  { color: "#e85d6f", icon: Target },
];

export interface RoadGeometry {
  pathD: string;
  viewBox: { width: number; height: number };
}

/** Build a winding road whose horizontal span grows with the step count. */
export function buildDynamicRoadPath(stepCount: number): RoadGeometry {
  const steps = Math.max(1, Math.min(12, stepCount));
  const marginX = 72;
  const segmentWidth = steps <= 3 ? 168 : steps <= 6 ? 152 : steps <= 9 ? 132 : 112;
  const width = marginX * 2 + segmentWidth * steps;
  const height = ROAD_VIEWBOX_HEIGHT;

  const yAt = (index: number) => {
    if (steps === 1) return ROAD_Y_CENTER;
    const phase = (index / steps) * Math.PI * 2;
    return ROAD_Y_CENTER + Math.sin(phase) * ROAD_Y_AMPLITUDE;
  };

  let x = marginX;
  let y = yAt(0);
  let d = `M ${x} ${y}`;

  for (let i = 0; i < steps; i++) {
    const nx = marginX + segmentWidth * (i + 1);
    const ny = yAt(i + 1);
    const cp1x = x + segmentWidth * 0.42;
    const cp1y = y;
    const cp2x = nx - segmentWidth * 0.42;
    const cp2y = ny;
    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${nx} ${ny}`;
    x = nx;
    y = ny;
  }

  const endX = width - marginX;
  if (x < endX - 8) {
    const endY = yAt(steps);
    d += ` C ${x + segmentWidth * 0.3} ${y}, ${endX - segmentWidth * 0.3} ${endY}, ${endX} ${endY}`;
  }

  return { pathD: d, viewBox: { width, height } };
}

export function roadDisplayAspect(
  viewBoxWidth: number,
  viewBoxHeight = ROAD_VIEWBOX_HEIGHT,
): number {
  return viewBoxWidth / (viewBoxHeight * 0.72);
}

export function formatRoadmapStepNumber(index: number): string {
  return String(index + 1);
}

export function buildStepDescription(month: RoadmapMonth, preview = false): string {
  if (preview) return "Le détail sera généré pour ce mois.";
  const parts: string[] = [];
  if (month.actions?.[0]) parts.push(month.actions[0]);
  if (month.actions?.[1]) parts.push(month.actions[1]);
  if (parts.length) return parts.join(" ");
  const skills = month.skills?.slice(0, 2).join(", ");
  return skills ?? "Étape clé de votre progression.";
}

export function buildPreviewMonths(count: number): RoadmapMonth[] {
  return Array.from({ length: count }, (_, i) => ({
    month: i + 1,
    title: `Mois ${i + 1}`,
    skills: [],
    actions: [],
    courses: [],
  }));
}

export interface RoadAnchor {
  x: number;
  y: number;
}

/** Fallback pin positions when SVG path length is not measured yet. */
export function computeFallbackAnchors(count: number): RoadAnchor[] {
  if (count <= 0) return [];
  return Array.from({ length: count }, (_, i) => {
    const t = count === 1 ? 0.5 : (i + 0.5) / count;
    const phase = (t * count) / count * Math.PI * 2;
    const yNorm = 0.5 + (Math.sin(phase) * ROAD_Y_AMPLITUDE) / ROAD_VIEWBOX_HEIGHT;
    return { x: t * 100, y: yNorm * 100 };
  });
}

/** Map SVG viewBox coordinates to % of the overlay container (accounts for letterboxing). */
export function viewBoxToOverlayPercent(
  point: { x: number; y: number },
  viewBox: { width: number; height: number },
  containerAspect = roadDisplayAspect(viewBox.width, viewBox.height),
): RoadAnchor {
  const vbAspect = viewBox.width / viewBox.height;

  if (containerAspect > vbAspect) {
    const scale = vbAspect / containerAspect;
    const padX = (1 - scale) / 2;
    return {
      x: (padX + (point.x / viewBox.width) * scale) * 100,
      y: (point.y / viewBox.height) * 100,
    };
  }

  const scale = containerAspect / vbAspect;
  const padY = (1 - scale) / 2;
  return {
    x: (point.x / viewBox.width) * 100,
    y: (padY + (point.y / viewBox.height) * scale) * 100,
  };
}

/** Place steps at equal intervals along the road path. */
export function computeRoadAnchors(
  count: number,
  path: SVGPathElement,
  viewBox: { width: number; height: number },
): RoadAnchor[] {
  if (count <= 0) return [];

  const containerAspect = roadDisplayAspect(viewBox.width, viewBox.height);
  const length = path.getTotalLength();
  const anchors: RoadAnchor[] = [];

  for (let i = 0; i < count; i++) {
    const t = count === 1 ? 0.5 : (i + 0.5) / count;
    const point = path.getPointAtLength(length * t);
    anchors.push(viewBoxToOverlayPercent(point, viewBox, containerAspect));
  }

  return anchors;
}
