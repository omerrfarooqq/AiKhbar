import { CATEGORY_META } from '../lib/utils';

/** Small coloured category label. */
export default function CategoryBadge({ category }) {
  const meta = CATEGORY_META[category] || CATEGORY_META.general;
  return (
    <span className={`chip ${meta.color}`}>
      <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-current" />
      {meta.label}
    </span>
  );
}
