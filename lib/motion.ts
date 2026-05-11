import type { Variants } from "framer-motion";

// ─── Durations (seconds) ───────────────────────────────────────────────────
export const DUR_MICRO = 0.14;
export const DUR_SHORT = 0.24;
export const DUR_BASE = 0.36;
export const DUR_MEDIUM = 0.48;
export const DUR_LONG = 0.60;

// ─── Easing ───────────────────────────────────────────────────────────────
// Cubic-bezier arrays — no springs (springs feel playful, not enterprise)
export const EASE_OUT_EXPO: [number, number, number, number] = [0.22, 1, 0.36, 1];
export const EASE_OUT_QUINT: [number, number, number, number] = [0.16, 1, 0.30, 1];
export const EASE_STANDARD: [number, number, number, number] = [0.4, 0, 0.2, 1];

// ─── Stagger ──────────────────────────────────────────────────────────────
export const STAGGER_TIGHT = 0.06;
export const STAGGER_BASE = 0.07;

// ─── Translate distances (px) ─────────────────────────────────────────────
export const DIST_SM = 4;
export const DIST_MD = 6;
export const DIST_LG = 8;
export const DIST_XL = 12;

// ─── Reusable variants ────────────────────────────────────────────────────

export const navVariant: Variants = {
  hidden: { opacity: 0, y: -DIST_SM },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: DUR_SHORT, ease: EASE_OUT_EXPO },
  },
};

export const footerVariant: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: DUR_SHORT, delay: 0.05 },
  },
};

export const leftContainer: Variants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: STAGGER_TIGHT, delayChildren: 0.16 },
  },
};

export const rightPanel: Variants = {
  hidden: { opacity: 0, x: DIST_XL },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: DUR_MEDIUM, delay: 0.12, ease: EASE_OUT_QUINT },
  },
};

export const rightContainer: Variants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: STAGGER_BASE, delayChildren: 0.44 },
  },
};

// item — used by most left-panel children (fade + slide up)
export const itemUp: Variants = {
  hidden: { opacity: 0, y: DIST_MD },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: DUR_BASE, ease: EASE_OUT_EXPO },
  },
};

// item — used by right-panel bullets (fade + slide in from left)
export const itemLeft: Variants = {
  hidden: { opacity: 0, x: -DIST_LG },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: DUR_BASE, ease: EASE_OUT_EXPO },
  },
};

// DQ watermark entrance
export const watermarkVariant: Variants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: DUR_LONG, delay: 0.32, ease: EASE_OUT_EXPO },
  },
};
