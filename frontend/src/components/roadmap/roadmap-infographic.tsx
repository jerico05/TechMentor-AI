"use client";

import * as React from "react";
import type { LucideIcon } from "lucide-react";
import { ExternalLink, GraduationCap } from "lucide-react";

import {
  ROAD_STROKE,
  ROAD_VIEWBOX_HEIGHT,
  ROADMAP_STEP_THEMES,
  buildDynamicRoadPath,
  buildStepDescription,
  computeRoadAnchors,
  formatRoadmapStepNumber,
  type RoadAnchor,
  type RoadGeometry,
  type RoadmapStepTheme,
} from "@/lib/roadmap-infographic";
import { cn } from "@/lib/utils";
import type { RoadmapCourse, RoadmapMonth } from "@/types";

const COURSE_TYPE_LABELS: Record<string, string> = {
  gratuit: "Gratuit",
  payant: "Payant",
  freemium: "Freemium",
};

const COURSE_TYPE_CLASS: Record<string, string> = {
  gratuit: "bg-emerald-500/10 text-emerald-700",
  payant: "bg-amber-500/10 text-amber-800",
  freemium: "bg-sky-500/10 text-sky-800",
};

function RoadmapCoursesList({
  courses,
  compact,
  align = "center",
}: {
  courses: RoadmapCourse[];
  compact?: boolean;
  align?: "center" | "left";
}) {
  if (!courses.length) return null;

  return (
    <div
      className={cn(
        "border-t border-[#eef1f5] pt-3",
        compact ? "mt-2 pt-2" : "mt-3",
        align === "left" ? "text-left" : "text-center",
      )}
    >
      <p
        className={cn(
          "mb-2 flex items-center gap-1 font-bold uppercase tracking-wide text-[#1e3d6e]/70",
          compact ? "justify-center text-[8px]" : "justify-center text-[9px]",
          align === "left" && "justify-start",
        )}
      >
        <GraduationCap className={compact ? "h-3 w-3" : "h-3.5 w-3.5"} />
        Cours à suivre
      </p>
      <ul className={cn("space-y-2", align === "left" ? "text-left" : "")}>
        {courses.slice(0, 2).map((course) => {
          const typeKey = course.type?.toLowerCase() ?? "freemium";
          const typeLabel = COURSE_TYPE_LABELS[typeKey] ?? course.type;
          const typeClass = COURSE_TYPE_CLASS[typeKey] ?? COURSE_TYPE_CLASS.freemium;
          return (
            <li key={`${course.url}-${course.title}`}>
              <a
                href={course.url}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  "group/course block rounded-xl border border-[#e8ecf2] bg-[#f8fafc] p-2 transition hover:border-primary/30 hover:bg-primary/5",
                  align === "left" ? "text-left" : "text-left",
                )}
              >
                <div className="flex items-start gap-1.5">
                  <ExternalLink
                    className={cn(
                      "mt-0.5 shrink-0 text-primary",
                      compact ? "h-3 w-3" : "h-3.5 w-3.5",
                    )}
                  />
                  <div className="min-w-0 flex-1">
                    <p
                      className={cn(
                        "font-semibold leading-snug text-[#1e3d6e] group-hover/course:text-primary break-words",
                        compact ? "text-[9px]" : "text-[10px]",
                      )}
                    >
                      {course.title}
                    </p>
                    <div className="mt-1 flex flex-wrap items-center gap-1">
                      <span
                        className={cn(
                          "rounded-full px-1.5 py-0.5 font-medium",
                          compact ? "text-[8px]" : "text-[9px]",
                          typeClass,
                        )}
                      >
                        {typeLabel}
                      </span>
                      <span
                        className={cn(
                          "text-muted-foreground",
                          compact ? "text-[8px]" : "text-[9px]",
                        )}
                      >
                        {course.platform}
                      </span>
                    </div>
                    {course.note ? (
                      <p
                        className={cn(
                          "mt-1 leading-snug text-muted-foreground",
                          compact ? "text-[8px]" : "text-[9px]",
                        )}
                      >
                        {course.note}
                      </p>
                    ) : null}
                  </div>
                </div>
              </a>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

interface RoadmapInfographicProps {
  months: RoadmapMonth[];
  summary?: string;
  className?: string;
  isPreview?: boolean;
}

const PIN_BASE_MS = 900;
const PIN_STAGGER_MS = 380;
const CARD_BASE_MS = 1100;
const CARD_STAGGER_MS = 220;

function stepTheme(index: number): RoadmapStepTheme {
  return ROADMAP_STEP_THEMES[index % ROADMAP_STEP_THEMES.length]!;
}

function useReducedMotion() {
  const [reduced, setReduced] = React.useState(false);
  React.useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

function useInView(threshold = 0.25) {
  const ref = React.useRef<HTMLDivElement>(null);
  const [inView, setInView] = React.useState(false);

  React.useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [threshold]);

  return { ref, inView };
}

function useRoadAnchors(count: number, geometry: RoadGeometry) {
  const pathRef = React.useRef<SVGPathElement>(null);
  const [anchors, setAnchors] = React.useState<RoadAnchor[]>([]);
  const [pathLength, setPathLength] = React.useState(0);

  const measure = React.useCallback(() => {
    const path = pathRef.current;
    if (!path || count === 0) {
      setAnchors([]);
      setPathLength(0);
      return;
    }
    const length = path.getTotalLength();
    setPathLength(length);
    if (length > 0) {
      setAnchors(computeRoadAnchors(count, path, geometry.viewBox));
    } else {
      setAnchors([]);
    }
  }, [count, geometry.pathD, geometry.viewBox.width, geometry.viewBox.height]);

  React.useLayoutEffect(() => {
    measure();
    const id = window.requestAnimationFrame(measure);
    window.addEventListener("resize", measure);
    return () => {
      window.cancelAnimationFrame(id);
      window.removeEventListener("resize", measure);
    };
  }, [measure]);

  return {
    pathRef,
    anchors,
    pathLength,
    ready: anchors.length === count && count > 0 && pathLength > 0,
  };
}

function AnimatedRoadSvg({
  pathRef,
  pathD,
  viewBox,
  pathLength,
  animate,
  reducedMotion,
}: {
  pathRef: React.RefObject<SVGPathElement>;
  pathD: string;
  viewBox: { width: number; height: number };
  pathLength: number;
  animate: boolean;
  reducedMotion: boolean;
}) {
  const uid = React.useId().replace(/:/g, "");
  const roadVisible = pathLength > 0;
  const drawStyle = (delayMs: number): React.CSSProperties => {
    if (!roadVisible) {
      return { opacity: 0 };
    }
    if (reducedMotion || !animate) {
      return { strokeDasharray: pathLength, strokeDashoffset: 0, opacity: 1 };
    }
    return {
      strokeDasharray: pathLength,
      strokeDashoffset: 0,
      opacity: 1,
      transition: `stroke-dashoffset 1.8s cubic-bezier(0.22, 1, 0.36, 1) ${delayMs}ms`,
    };
  };

  return (
    <svg
      className="absolute inset-0 h-full w-full"
      viewBox={`0 0 ${viewBox.width} ${viewBox.height}`}
      preserveAspectRatio="xMidYMid meet"
      aria-hidden
    >
      <defs>
        <filter id={`roadmap-road-shadow-${uid}`} x="-15%" y="-15%" width="130%" height="130%">
          <feDropShadow dx="0" dy="8" stdDeviation="10" floodColor="#0f2744" floodOpacity="0.28" />
        </filter>
        <linearGradient id={`roadmap-navy-gradient-${uid}`} x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#1a3358" />
          <stop offset="50%" stopColor="#1e3d6e" />
          <stop offset="100%" stopColor="#254a82" />
        </linearGradient>
      </defs>
      <path ref={pathRef} d={pathD} fill="none" stroke="transparent" strokeWidth="1" />
      <path
        d={pathD}
        fill="none"
        stroke={ROAD_STROKE.white}
        strokeWidth="62"
        strokeLinecap="round"
        strokeLinejoin="round"
        filter={`url(#roadmap-road-shadow-${uid})`}
        style={drawStyle(0)}
      />
      <path
        d={pathD}
        fill="none"
        stroke={`url(#roadmap-navy-gradient-${uid})`}
        strokeWidth="48"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={drawStyle(80)}
      />
      <path
        d={pathD}
        fill="none"
        stroke={ROAD_STROKE.dash}
        strokeWidth="3"
        strokeDasharray="12 14"
        strokeLinecap="round"
        opacity={roadVisible ? 0.95 : 0}
        style={drawStyle(120)}
      />
    </svg>
  );
}

function MapPin({
  color,
  icon: Icon,
  floating,
  compact,
}: {
  color: string;
  icon: LucideIcon;
  floating?: boolean;
  compact?: boolean;
}) {
  return (
    <div className={cn("relative flex flex-col items-center", floating && !compact && "animate-float")}>
      <div
        className={cn(
          "flex items-center justify-center rounded-full shadow-[0_8px_20px_rgba(15,39,68,0.32)] ring-[3px] ring-white",
          compact ? "h-8 w-8 ring-2" : "h-12 w-12",
        )}
        style={{ backgroundColor: color }}
      >
        <Icon className={cn("text-white", compact ? "h-3.5 w-3.5" : "h-5 w-5")} strokeWidth={2.25} />
      </div>
      <div
        className={cn("rotate-45 shadow-sm", compact ? "-mt-1 h-2.5 w-2.5" : "-mt-1.5 h-3.5 w-3.5")}
        style={{ backgroundColor: color }}
      />
    </div>
  );
}

function RoadPin({
  anchor,
  index,
  animate,
  compact,
  staggerMs,
}: {
  anchor: RoadAnchor;
  index: number;
  animate: boolean;
  compact?: boolean;
  staggerMs: number;
}) {
  const theme = stepTheme(index);
  const delay = PIN_BASE_MS + index * staggerMs;

  return (
    <div
      className={cn(
        "absolute z-20 opacity-0 motion-reduce:opacity-100",
        animate && "motion-safe:animate-pin-drop",
      )}
      style={{
        left: `${anchor.x}%`,
        top: `${anchor.y}%`,
        transform: compact ? "translate(-50%, -90%)" : "translate(-50%, -92%)",
        animationDelay: animate ? `${delay}ms` : undefined,
      }}
    >
      <MapPin color={theme.color} icon={theme.icon} floating={animate} compact={compact} />
    </div>
  );
}

function StepConnector({
  color,
  animate,
  index,
  compact,
  staggerMs,
}: {
  color: string;
  animate: boolean;
  index: number;
  compact?: boolean;
  staggerMs: number;
}) {
  return (
    <div
      className={cn(
        "mb-2 w-px origin-top opacity-0 motion-reduce:opacity-100",
        compact ? "h-5" : "h-8",
        animate && "motion-safe:animate-connector-grow",
      )}
      style={{
        backgroundColor: color,
        animationDelay: animate ? `${CARD_BASE_MS + index * staggerMs - 80}ms` : undefined,
      }}
    />
  );
}

function StepCard({
  month,
  index,
  animate,
  compact,
  staggerMs,
  isPreview,
}: {
  month: RoadmapMonth;
  index: number;
  animate: boolean;
  compact?: boolean;
  staggerMs: number;
  isPreview?: boolean;
}) {
  const theme = stepTheme(index);
  const description = buildStepDescription(month, isPreview);
  const courses = month.courses ?? [];
  const delay = CARD_BASE_MS + index * staggerMs;

  return (
    <div
      className={cn(
        "flex flex-col items-center px-2",
        compact ? "w-[10.5rem] shrink-0" : "",
        animate ? "opacity-0 motion-safe:animate-card-rise" : "opacity-100",
      )}
      style={{ animationDelay: animate ? `${delay}ms` : undefined }}
    >
      <div
        className={cn(
          "mb-2 flex items-center justify-center rounded-full font-bold text-white shadow-lg opacity-0 motion-reduce:opacity-100",
          compact ? "h-7 w-7 text-xs" : "h-9 w-9 text-sm",
          animate && "motion-safe:animate-badge-pop",
        )}
        style={{
          backgroundColor: theme.color,
          animationDelay: animate ? `${delay - 60}ms` : undefined,
        }}
      >
        {formatRoadmapStepNumber(index)}
      </div>

      <StepConnector color={theme.color} animate={animate} index={index} compact={compact} staggerMs={staggerMs} />

      <article
        className={cn(
          "group w-full rounded-2xl border bg-white text-center shadow-[0_10px_32px_rgba(26,43,75,0.09)] transition-all duration-300 ease-smooth",
          isPreview
            ? "border-dashed border-[#c5cdd8] bg-white/70"
            : "border-white/80 hover:-translate-y-1 hover:shadow-[0_16px_40px_rgba(26,43,75,0.14)]",
          compact ? "max-w-[10.5rem] px-3 py-3" : "max-w-[15rem] px-4 py-4",
        )}
        style={{ borderTop: isPreview ? undefined : `4px solid ${theme.color}` }}
      >
        <p
          className={cn(
            "font-extrabold uppercase leading-snug tracking-wide",
            compact ? "text-[10px]" : "text-[11px]",
            isPreview && "text-[#9aa5b5]",
          )}
          style={isPreview ? undefined : { color: theme.color }}
        >
          {isPreview ? `Mois ${month.month}` : month.title}
        </p>
        <p className={cn("mt-2 leading-relaxed text-[#7b8798]", compact ? "text-[10px]" : "text-xs")}>
          {description}
        </p>
        {!isPreview && month.skills?.length ? (
          <div className={cn("mt-3 flex flex-wrap justify-center gap-1 border-t border-[#eef1f5] pt-3", compact && "mt-2 pt-2")}>
            {month.skills.slice(0, compact ? 2 : 3).map((skill) => (
              <span
                key={skill}
                className={cn(
                  "rounded-full font-semibold transition-colors group-hover:opacity-90",
                  compact ? "px-1.5 py-0.5 text-[9px]" : "px-2 py-0.5 text-[10px]",
                )}
                style={{ backgroundColor: `${theme.color}18`, color: theme.color }}
              >
                {skill}
              </span>
            ))}
          </div>
        ) : null}
        {!isPreview && courses.length > 0 ? (
          <RoadmapCoursesList courses={courses} compact={compact} />
        ) : null}
      </article>
    </div>
  );
}

function MobileTimeline({
  months,
  animate,
  isPreview,
}: {
  months: RoadmapMonth[];
  animate: boolean;
  isPreview?: boolean;
}) {
  return (
    <div className="space-y-4 md:hidden">
      {months.map((month, index) => {
        const theme = stepTheme(index);
        const Icon = theme.icon;
        return (
          <div
            key={month.month}
            className={cn(
              "flex gap-4 rounded-2xl border border-white/60 bg-white/90 p-4 shadow-md opacity-0 backdrop-blur-sm",
              animate && "animate-slide-up",
            )}
            style={{
              animationDelay: animate ? `${index * 120}ms` : undefined,
              borderLeft: `4px solid ${theme.color}`,
            }}
          >
            <div
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-white shadow-md"
              style={{ backgroundColor: theme.color }}
            >
              <Icon className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-bold uppercase" style={{ color: theme.color }}>
                {formatRoadmapStepNumber(index)}. {isPreview ? `Mois ${month.month}` : month.title}
              </p>
              <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
                {buildStepDescription(month, isPreview)}
              </p>
              {!isPreview && (month.courses?.length ?? 0) > 0 ? (
                <RoadmapCoursesList courses={month.courses ?? []} align="left" />
              ) : null}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function RoadmapInfographic({ months, summary, className, isPreview }: RoadmapInfographicProps) {
  const steps = months;
  const geometry = React.useMemo(() => buildDynamicRoadPath(steps.length), [steps.length]);
  const isCompact = steps.length > 6;
  const staggerMs = isCompact ? 120 : PIN_STAGGER_MS;
  const cardStaggerMs = isCompact ? 100 : CARD_STAGGER_MS;
  const { pathRef, anchors, pathLength, ready } = useRoadAnchors(steps.length, geometry);
  const { ref: viewportRef, inView } = useInView(0.15);
  const reducedMotion = useReducedMotion();
  const roadAnimate = pathLength > 0 || reducedMotion;
  const contentAnimate = (inView && ready) || reducedMotion;
  const roadAspect = geometry.viewBox.width / (ROAD_VIEWBOX_HEIGHT * 0.72);

  return (
    <div
      ref={viewportRef}
      className={cn(
        "relative overflow-hidden rounded-[2rem] border border-white/60 px-4 py-8 shadow-crextio sm:px-8 sm:py-10",
        "bg-gradient-to-br from-[#f6f8fb] via-[#eef2f7] to-[#e6ebf2]",
        className,
      )}
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.35]"
        style={{
          backgroundImage: "radial-gradient(circle, #c5cdd8 1px, transparent 1px)",
          backgroundSize: "22px 22px",
        }}
      />

      <header
        className={cn(
          "relative mb-10 text-center opacity-0",
          inView && "animate-fade-in",
        )}
      >
        <p className="text-[11px] font-bold uppercase tracking-[0.4em] text-[#1e3d6e]/60">Roadmap</p>
        <h2 className="mt-2 text-xl font-extrabold uppercase tracking-[0.08em] text-[#1e3d6e] sm:text-2xl sm:tracking-[0.12em] lg:text-[1.75rem]">
          Votre parcours · {steps.length} mois
        </h2>
        <div className="mx-auto mt-3 h-1 w-16 rounded-full bg-gradient-to-r from-[#e85d6f] via-[#5fbf7d] to-[#4a9fd4]" />
        <p className="mx-auto mt-4 max-w-2xl text-sm leading-relaxed text-[#7b8798]">
          {summary ?? (isPreview
            ? `Aperçu de votre parcours sur ${steps.length} mois. Générez la roadmap pour le contenu détaillé.`
            : "Plan d'apprentissage personnalisé, étape par étape, pour atteindre votre objectif.")}
        </p>
        {isPreview ? (
          <p className="mx-auto mt-2 inline-flex rounded-full bg-[#eef2f7] px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-[#1e3d6e]/70">
            Aperçu · {steps.length} étape{steps.length > 1 ? "s" : ""}
          </p>
        ) : null}
      </header>

      <MobileTimeline months={steps} animate={inView} isPreview={isPreview} />

      <div className="relative mx-auto hidden max-w-[min(100%,72rem)] md:block">
        <div
          className={cn(
            "relative w-full min-h-[14rem] transition-[aspect-ratio] duration-700 ease-[cubic-bezier(0.22,1,0.36,1)]",
            isCompact && "overflow-x-auto pb-2 [scrollbar-width:thin]",
          )}
          style={{ aspectRatio: isCompact ? undefined : `${roadAspect}`, minHeight: "14rem" }}
        >
          <div
            className={cn("relative w-full", isCompact && "min-w-max")}
            style={isCompact ? { width: `${Math.max(100, steps.length * 14)}%`, aspectRatio: `${roadAspect}` } : undefined}
          >
            <AnimatedRoadSvg
              pathRef={pathRef}
              pathD={geometry.pathD}
              viewBox={geometry.viewBox}
              pathLength={pathLength}
              animate={roadAnimate}
              reducedMotion={reducedMotion}
            />
            {ready
              ? steps.map((_, index) => (
                  <RoadPin
                    key={steps[index]!.month}
                    anchor={anchors[index]!}
                    index={index}
                    animate={contentAnimate}
                    compact={isCompact}
                    staggerMs={staggerMs}
                  />
                ))
              : null}
          </div>
        </div>

        {isCompact ? (
          <div className="relative mt-4 -mx-2 overflow-x-auto pb-2 [scrollbar-width:thin]">
            <p className="mb-2 px-2 text-center text-[10px] text-[#7b8798]">Faites défiler pour voir toutes les étapes</p>
            <div className="flex min-w-max gap-2 px-2">
              {steps.map((month, index) => (
                <StepCard
                  key={month.month}
                  month={month}
                  index={index}
                  animate={contentAnimate}
                  compact
                  staggerMs={cardStaggerMs}
                  isPreview={isPreview}
                />
              ))}
            </div>
          </div>
        ) : (
          <div
            className="relative mt-4 grid gap-3"
            style={{ gridTemplateColumns: `repeat(${steps.length}, minmax(0, 1fr))` }}
          >
            {steps.map((month, index) => (
              <StepCard
                key={month.month}
                month={month}
                index={index}
                animate={contentAnimate}
                staggerMs={cardStaggerMs}
                isPreview={isPreview}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
