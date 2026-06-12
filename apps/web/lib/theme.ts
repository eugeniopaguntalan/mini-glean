/**
 * Material Design 3 Theme Configuration
 *
 * Typography scale and reusable class combinations for MiniGlean.
 * Colors are defined as MD3 tokens in `tailwind.config.ts` / `globals.css`
 * and consumed directly via Tailwind utilities (e.g. `text-primary`).
 *
 * Each typography role encodes size / line-height / weight / letter-spacing
 * exactly per the MD3 type scale using Tailwind arbitrary values.
 */

export const typography = {
  display: {
    large: 'text-[57px] leading-[64px] font-normal tracking-[-0.25px]',
    medium: 'text-[45px] leading-[52px] font-normal tracking-normal',
    small: 'text-[36px] leading-[44px] font-normal tracking-normal',
  },
  headline: {
    large: 'text-[32px] leading-[40px] font-normal tracking-normal',
    medium: 'text-[28px] leading-[36px] font-normal tracking-normal',
    small: 'text-[24px] leading-[32px] font-normal tracking-normal',
  },
  title: {
    large: 'text-[22px] leading-[28px] font-normal tracking-normal',
    medium: 'text-[16px] leading-[24px] font-medium tracking-[0.15px]',
    small: 'text-[14px] leading-[20px] font-medium tracking-[0.1px]',
  },
  body: {
    large: 'text-[16px] leading-[24px] font-normal tracking-[0.5px]',
    medium: 'text-[14px] leading-[20px] font-normal tracking-[0.25px]',
    small: 'text-[12px] leading-[16px] font-normal tracking-[0.4px]',
  },
  label: {
    large: 'text-[14px] leading-[20px] font-medium tracking-[0.1px]',
    medium: 'text-[12px] leading-[16px] font-medium tracking-[0.5px]',
    small: 'text-[11px] leading-[16px] font-medium tracking-[0.5px]',
  },
} as const

/**
 * Reusable MD3 shape + elevation + state-layer class combinations.
 */
export const surfaces = {
  /** Elevated card: tonal surface with a low shadow that lifts on hover. */
  elevatedCard:
    'bg-surface text-on-surface shadow-sm rounded-xl transition-shadow hover:shadow-md',
  /** Outlined card: surface with a hairline outline, no elevation. */
  outlinedCard: 'bg-surface text-on-surface border border-outline-variant rounded-xl',
} as const

/**
 * Filled primary button (MD3 Filled Button): pill shape with a hover state layer.
 */
export const filledButton =
  'inline-flex items-center justify-center gap-2 rounded-full bg-primary text-on-primary ' +
  'px-6 py-2.5 font-medium transition-shadow hover:shadow-md ' +
  'disabled:opacity-[0.38] disabled:pointer-events-none focus:outline-none ' +
  'focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 ' +
  'focus-visible:ring-offset-surface'

/**
 * Text button tinted with the error color (used for destructive actions).
 */
export const textButtonError =
  'inline-flex items-center justify-center rounded-full px-3 py-1.5 ' +
  'text-error font-medium transition-colors hover:bg-error/8 ' +
  'focus:outline-none focus-visible:ring-2 focus-visible:ring-error'
