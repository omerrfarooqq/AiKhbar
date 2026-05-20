import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Layers, ArrowUpRight } from 'lucide-react';
import CategoryBadge from './CategoryBadge';

/** A clustered story card — multiple sources, one unified summary. */
export default function StoryCard({ story, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.45, delay }}
      whileHover={{ y: -6 }}
      className="glass glass-hover flex flex-col p-6"
    >
      <div className="flex items-center justify-between">
        <CategoryBadge category={story.category} />
        <span className="flex items-center gap-1.5 text-xs text-slate-500">
          <Layers size={13} />
          {story.article_count} sources
        </span>
      </div>

      <h3 className="urdu mt-4 text-xl text-slate-100 line-clamp-2">
        {story.title}
      </h3>

      {story.unified_summary && (
        <p className="urdu mt-3 text-sm text-slate-400 line-clamp-3">
          {story.unified_summary}
        </p>
      )}

      <Link
        to={`/story/${story.id}`}
        className="mt-auto inline-flex items-center gap-1 pt-5 text-sm
                   font-semibold text-gold-400 hover:text-gold-300"
      >
        Open story <ArrowUpRight size={15} />
      </Link>
    </motion.div>
  );
}
