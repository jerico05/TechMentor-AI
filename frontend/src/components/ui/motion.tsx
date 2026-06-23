"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

type Anim = "fade-in" | "slide-up" | "slide-down" | "scale-in";

interface MotionProps {
  children: React.ReactNode;
  className?: string;
  animation?: Anim;
  delay?: 1 | 2 | 3 | 4 | 5 | 6;
  as?: keyof JSX.IntrinsicElements;
}

const animClass: Record<Anim, string> = {
  "fade-in": "animate-fade-in",
  "slide-up": "animate-slide-up",
  "slide-down": "animate-slide-down",
  "scale-in": "animate-scale-in",
};

const delayClass = {
  1: "stagger-1",
  2: "stagger-2",
  3: "stagger-3",
  4: "stagger-4",
  5: "stagger-5",
  6: "stagger-6",
} as const;

/** Lightweight CSS animation wrapper (no extra deps). */
export function Motion({
  children,
  className,
  animation = "slide-up",
  delay,
  as: Tag = "div",
}: MotionProps) {
  const Component = Tag as React.ElementType;
  return (
    <Component
      className={cn(animClass[animation], delay && delayClass[delay], className)}
    >
      {children}
    </Component>
  );
}
