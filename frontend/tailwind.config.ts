import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        navy: {
          DEFAULT: "hsl(var(--navy))",
          dark: "hsl(var(--navy-dark))",
          foreground: "hsl(var(--navy-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 4px)",
        sm: "calc(var(--radius) - 8px)",
        "3xl": "1.5rem",
        "4xl": "2rem",
        shell: "var(--shell-radius)",
      },
      boxShadow: {
        crextio: "0 8px 40px rgba(26, 43, 75, 0.08)",
        "crextio-sm": "0 4px 24px rgba(26, 43, 75, 0.06)",
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans Variable"', "system-ui", "Segoe UI", "sans-serif"],
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "slide-up": {
          from: { opacity: "0", transform: "translateY(16px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "slide-down": {
          from: { opacity: "0", transform: "translateY(-8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          from: { opacity: "0", transform: "scale(0.96)" },
          to: { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "pulse-soft": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-4px)" },
        },
        "pin-drop": {
          "0%": { opacity: "0", transform: "translate(-50%, -120%) scale(0.35)" },
          "70%": { opacity: "1", transform: "translate(-50%, -88%) scale(1.08)" },
          "100%": { opacity: "1", transform: "translate(-50%, -92%) scale(1)" },
        },
        "card-rise": {
          from: { opacity: "0", transform: "translateY(28px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "badge-pop": {
          "0%": { opacity: "0", transform: "scale(0.5)" },
          "70%": { transform: "scale(1.12)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "connector-grow": {
          from: { transform: "scaleY(0)", opacity: "0" },
          to: { transform: "scaleY(1)", opacity: "1" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.25s ease-out forwards",
        "slide-up": "slide-up 0.28s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        "slide-down": "slide-down 0.25s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        "scale-in": "scale-in 0.22s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        shimmer: "shimmer 2s linear infinite",
        "pulse-soft": "pulse-soft 2s ease-in-out infinite",
        float: "float 3s ease-in-out infinite",
        "pin-drop": "pin-drop 0.65s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        "card-rise": "card-rise 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        "badge-pop": "badge-pop 0.45s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        "connector-grow": "connector-grow 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
