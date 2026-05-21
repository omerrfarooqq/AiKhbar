import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import SectionHeading from '../components/SectionHeading';
import NewsCard from '../components/NewsCard';
import Loader from '../components/Loader';
import { newsService } from '../services/newsService';
import globe from '../assets/logo-globe.png';

export default function LandingPage() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    newsService
      .listNews({ page_size: 6 })
      .then((res) => setNews(res.items || []))
      .catch(() => setNews([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      {/* Hero */}
      <section className="mx-auto max-w-7xl px-6 pb-16 pt-16 md:pt-24">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: 'easeOut' }}
          >
            <div className="font-urdu font-semibold text-ink-900">
              <h1 className="text-5xl leading-[1.5] md:text-6xl">
                اے آئی خبر
              </h1>
              <p className="mt-3 text-3xl leading-[1.5] brand-text md:text-4xl">
                خبر سے گفتگو تک
              </p>
            </div>
            <p className="mt-5 max-w-xl text-lg text-steel-600">
              AI powered Urdu news briefing system
            </p>
            <div className="mt-9 flex flex-wrap gap-4">
              <Link to="/brief" className="btn-primary">
                Today&apos;s Bulletin
              </Link>
              <Link to="/news" className="btn-ghost">
                Browse News
              </Link>
            </div>
          </motion.div>

          {/* Globe */}
          <motion.div
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.9, delay: 0.2, ease: 'easeOut' }}
            className="relative mx-auto hidden max-w-md lg:block"
          >
            <div className="absolute inset-6 -z-10 rounded-full bg-ocean-300/35
                            blur-[90px]" />
            <img
              src={globe}
              alt="AiKhbar"
              className="w-full animate-float drop-shadow-2xl"
            />
          </motion.div>
        </div>
      </section>

      {/* Top News */}
      <section className="mx-auto max-w-7xl px-6 pb-24">
        <SectionHeading
          eyebrow="Latest"
          title="Top News"
          subtitle="The most recent coverage, aggregated and classified from live Urdu sources."
        />
        {loading ? (
          <Loader label="Loading the latest news…" />
        ) : news.length === 0 ? (
          <p className="text-steel-500">No news available yet.</p>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {news.map((article, i) => (
              <NewsCard key={article.id} article={article} delay={i * 0.06} />
            ))}
          </div>
        )}
        <div className="mt-10 text-center">
          <Link to="/news" className="btn-ghost">
            All News
          </Link>
        </div>
      </section>
    </div>
  );
}
