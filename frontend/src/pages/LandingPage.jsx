import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Radio,
  MessagesSquare,
  Scale,
  Clock3,
  Newspaper,
  ArrowRight,
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import SectionHeading from '../components/SectionHeading';

const FEATURES = [
  {
    icon: Newspaper,
    title: 'Real-time Aggregation',
    text: 'Continuously scrapes BBC Urdu, Geo and Jang, then deduplicates and classifies every story.',
  },
  {
    icon: Radio,
    title: 'Urdu Audio Briefings',
    text: 'AI-generated podcast-style narration with headline emphasis and natural pauses.',
  },
  {
    icon: Scale,
    title: 'Opinion Aggregation',
    text: 'RAG-driven analysis surfaces public sentiment, political views and expert opinion.',
  },
  {
    icon: MessagesSquare,
    title: 'Conversational News',
    text: 'Ask “why does this matter?” or “what happened before?” and get grounded answers.',
  },
  {
    icon: Clock3,
    title: 'Timeline & Context',
    text: 'Every major story carries a historical timeline reconstructed from past coverage.',
  },
  {
    icon: Sparkles,
    title: 'One-click Daily Brief',
    text: 'A personalized briefing of top stories, summaries and Urdu audio in a single tap.',
  },
];

export default function LandingPage() {
  return (
    <div>
      {/* ---------- Hero ---------- */}
      <section className="relative mx-auto max-w-7xl px-6 pb-24 pt-20 md:pt-28">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
          className="max-w-3xl"
        >
          <span className="chip text-gold-300">
            <Sparkles size={13} className="mr-1.5" />
            AI-powered media intelligence
          </span>

          <h1 className="mt-6 font-display text-5xl font-semibold leading-tight
                         text-slate-100 md:text-7xl">
            Urdu news,
            <span className="block gold-text">understood by AI.</span>
          </h1>

          <p className="mt-6 max-w-xl text-lg text-slate-400">
            AiKhbar aggregates, summarizes and narrates the news in Urdu — then
            lets you explore opinions, history and context through conversation.
          </p>

          <div className="mt-9 flex flex-wrap gap-4">
            <Link to="/brief" className="btn-primary">
              <Sparkles size={17} />
              Generate Daily Brief
            </Link>
            <Link to="/news" className="btn-ghost">
              Browse News <ArrowRight size={16} />
            </Link>
          </div>
        </motion.div>

        {/* Floating stat panel */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="mt-16 grid grid-cols-2 gap-4 md:grid-cols-4"
        >
          {[
            ['7', 'Categories'],
            ['3', 'Live Sources'],
            ['RAG', 'Opinion Engine'],
            ['Urdu', 'AI Narration'],
          ].map(([value, label], i) => (
            <GlassCard key={label} delay={i * 0.08} className="text-center">
              <div className="font-display text-3xl font-semibold gold-text">
                {value}
              </div>
              <div className="mt-1 text-xs uppercase tracking-wider text-slate-500">
                {label}
              </div>
            </GlassCard>
          ))}
        </motion.div>
      </section>

      {/* ---------- Features ---------- */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        <SectionHeading
          eyebrow="Capabilities"
          title="More than a news app"
          subtitle="A complete AI media intelligence system — from ingestion to insight."
        />
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f, i) => (
            <GlassCard key={f.title} delay={i * 0.07}>
              <div className="flex h-11 w-11 items-center justify-center rounded-xl
                              bg-gold-500/15 text-gold-400">
                <f.icon size={20} />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-slate-100">
                {f.title}
              </h3>
              <p className="mt-2 text-sm text-slate-400">{f.text}</p>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* ---------- CTA ---------- */}
      <section className="mx-auto max-w-5xl px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="glass relative overflow-hidden p-12 text-center"
        >
          <div className="absolute inset-0 bg-gold-radial" />
          <div className="relative">
            <h2 className="font-display text-3xl font-semibold text-slate-100 md:text-4xl">
              Your morning brief, in one click.
            </h2>
            <p className="mx-auto mt-3 max-w-xl text-slate-400">
              Top stories, multi-source summaries and an Urdu audio narration —
              generated on demand.
            </p>
            <Link to="/brief" className="btn-primary mt-8">
              <Sparkles size={17} />
              Start Now
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
