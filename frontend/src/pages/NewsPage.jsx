import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { fetchNews, setCategory } from '../store/newsSlice';
import SectionHeading from '../components/SectionHeading';
import NewsCard from '../components/NewsCard';
import Loader from '../components/Loader';
import { CATEGORY_META } from '../lib/utils';

const CATEGORIES = Object.keys(CATEGORY_META).filter((c) => c !== 'general');

export default function NewsPage() {
  const dispatch = useDispatch();
  const { articles, status, error, activeCategory } = useSelector((s) => s.news);

  useEffect(() => {
    dispatch(
      fetchNews({
        category: activeCategory || undefined,
        page: 1,
        page_size: 24,
      }),
    );
  }, [dispatch, activeCategory]);

  return (
    <div className="mx-auto max-w-7xl px-6 py-16">
      <SectionHeading
        eyebrow="Newsroom"
        title="Latest News"
        subtitle="Filtered, classified and continuously updated from live Urdu sources."
      />

      {/* Category filter */}
      <div className="mb-10 flex flex-wrap gap-2.5">
        <FilterChip
          label="All"
          active={!activeCategory}
          onClick={() => dispatch(setCategory(null))}
        />
        {CATEGORIES.map((c) => (
          <FilterChip
            key={c}
            label={CATEGORY_META[c].label}
            active={activeCategory === c}
            onClick={() => dispatch(setCategory(c))}
          />
        ))}
      </div>

      {status === 'loading' && <Loader label="Fetching news…" />}
      {status === 'failed' && (
        <p className="text-rose-600">Could not load news: {error}</p>
      )}

      {status === 'succeeded' && articles.length === 0 && (
        <p className="text-steel-500">
          No articles yet. Trigger an ingestion run from the backend.
        </p>
      )}

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {articles.map((a, i) => (
          <NewsCard key={a.id} article={a} delay={i * 0.04} />
        ))}
      </div>
    </div>
  );
}

function FilterChip({ label, active, onClick }) {
  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`rounded-none border px-4 py-1.5 text-sm font-medium
        transition-all ${
          active
            ? 'border-ocean-500 bg-ocean-500 text-white shadow-soft'
            : 'border-steel-200 bg-white/60 text-steel-500 ' +
              'hover:border-ocean-300 hover:text-ocean-600'
        }`}
    >
      {label}
    </motion.button>
  );
}
