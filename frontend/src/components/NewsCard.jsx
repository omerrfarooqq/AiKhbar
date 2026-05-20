import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Clock } from 'lucide-react';
import CategoryBadge from './CategoryBadge';
import { formatDate } from '../lib/utils';

/** Editorial article card used in feeds and category grids. */
export default function NewsCard({ article, delay = 0 }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.45, delay }}
      whileHover={{ y: -6 }}
      className="glass glass-hover flex flex-col p-5"
    >
      <div className="flex items-center justify-between">
        <CategoryBadge category={article.category} />
        <span className="text-[11px] uppercase tracking-wider text-slate-500">
          {article.source}
        </span>
      </div>

      <h3 className="urdu mt-4 text-lg text-slate-100 line-clamp-3">
        {article.headline}
      </h3>

      <div className="mt-auto flex items-center justify-between pt-5">
        <span className="flex items-center gap-1.5 text-xs text-slate-500">
          <Clock size={13} />
          {formatDate(article.published_at)}
        </span>
        <Link
          to={`/article/${article.id}`}
          className="text-sm font-medium text-gold-400 hover:text-gold-300"
        >
          Read →
        </Link>
      </div>
    </motion.article>
  );
}
