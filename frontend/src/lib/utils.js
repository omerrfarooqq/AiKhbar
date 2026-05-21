import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Merge Tailwind classes safely (conditional + conflict-resolving). */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/** Format an ISO timestamp into a short, readable label. */
export function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/** Human label + accent colour for a category key (tuned for light chips). */
export const CATEGORY_META = {
  politics: { label: 'Politics', color: 'text-rose-600' },
  sports: { label: 'Sports', color: 'text-emerald-600' },
  economy: { label: 'Economy', color: 'text-amber-600' },
  crime: { label: 'Crime', color: 'text-red-600' },
  international: { label: 'International', color: 'text-sky-700' },
  technology: { label: 'Technology', color: 'text-violet-600' },
  entertainment: { label: 'Entertainment', color: 'text-pink-600' },
  general: { label: 'General', color: 'text-steel-500' },
};
