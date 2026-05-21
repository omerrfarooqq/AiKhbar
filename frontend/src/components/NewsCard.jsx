import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';
import CategoryBadge from './CategoryBadge';
import { formatDate } from '../lib/utils';

/** Editorial article card with a lead image, used in feeds and Top News. */
export default function NewsCard({ article, delay = 0 }) {
  return (
    <motion.a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.45, delay }}
      whileHover={{ y: -6 }}
      className="glass glass-hover group flex flex-col overflow-hidden"
    >
      {/* Lead image */}
      <div className="relative h-44 overflow-hidden bg-steel-100">
        {article.image_url ? (
          <img
            src={article.image_url}
            alt=""
            loading="lazy"
            onError={(e) => {
              e.currentTarget.style.display = 'none';
            }}
            className="h-full w-full object-cover transition-transform
                       duration-700 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center
                          bg-gradient-to-br from-steel-200 to-cream-200
                          font-display text-3xl text-steel-400">
            AiKhbar
          </div>
        )}
        <div className="absolute left-3 top-3">
          <CategoryBadge category={article.category} />
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-1 flex-col p-5">
        <span className="text-[11px] uppercase tracking-wider text-steel-400">
          {article.source}
        </span>
        <h3 className="urdu mt-2 text-lg text-ink-900 line-clamp-3">
          {article.headline}
        </h3>
        <div className="mt-auto flex items-center justify-between pt-5">
          <span className="flex items-center gap-1.5 text-xs text-steel-400">
            <Clock size={13} />
            {formatDate(article.published_at)}
          </span>
          <span className="text-sm font-semibold text-ocean-600
                           group-hover:text-ocean-500">
            Read
          </span>
        </div>
      </div>
    </motion.a>
  );
}
