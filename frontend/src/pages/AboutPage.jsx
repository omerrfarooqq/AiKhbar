import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import SectionHeading from '../components/SectionHeading';

const TEAM = [{ name: 'Omer Farooq Khan' }];

const PIPELINE = [
  {
    step: '01',
    title: 'Aggregation',
    text: 'Real-time scraping of BBC Urdu, Jang, Express, ARY and Hum Sub through resilient RSS pipelines.',
  },
  {
    step: '02',
    title: 'Classification',
    text: 'Every article is sorted into seven editorial categories by an LLM zero-shot classifier.',
  },
  {
    step: '03',
    title: 'Summarization',
    text: 'Related coverage is clustered and condensed into a single unified Urdu summary.',
  },
  {
    step: '04',
    title: 'Urdu Narration',
    text: 'Summaries are voiced as natural, podcast-style Urdu audio briefings.',
  },
  {
    step: '05',
    title: 'RAG Intelligence',
    text: 'A vector index powers conversational answers, opinion aggregation and historical context.',
  },
];

const initials = (name) =>
  name
    .replace(/^(Mr\.|Ms\.|Dr\.)\s*/, '')
    .split(' ')
    .slice(0, 2)
    .map((p) => p[0])
    .join('');

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-6xl px-6 py-20">
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-3xl"
      >
        <span className="chip text-ocean-600">Our Mission</span>
        <h1 className="mt-6 font-display text-4xl font-semibold leading-[1.15]
                       text-ink-900 md:text-6xl">
          Making Urdu news
          <span className="block brand-text">intelligent and accessible.</span>
        </h1>
        <p className="mt-6 text-lg leading-relaxed text-steel-600">
          AiKhbar was built to cut through the noise of Pakistan&apos;s news
          cycle. It aggregates reporting from the country&apos;s major Urdu
          outlets, then uses AI to summarize, narrate and explain the news, so
          readers can understand a story, its history and its many perspectives
          in minutes.
        </p>
      </motion.section>

      {/* Story */}
      <section className="mt-24 grid gap-12 md:grid-cols-2">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em]
                          text-ocean-600">
            The Problem
          </div>
          <h2 className="mt-3 font-display text-2xl font-semibold text-ink-900">
            Too much news, too little context
          </h2>
          <p className="mt-4 leading-relaxed text-steel-600">
            Urdu readers face dozens of outlets publishing the same story with
            different framing. Important context, timelines and opposing
            viewpoints are scattered, and there is rarely time to piece them
            together.
          </p>
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em]
                          text-ocean-600">
            Our Approach
          </div>
          <h2 className="mt-3 font-display text-2xl font-semibold text-ink-900">
            One intelligent newsroom
          </h2>
          <p className="mt-4 leading-relaxed text-steel-600">
            AiKhbar treats the news as a single connected system. It clusters
            related coverage, generates balanced summaries, surfaces multiple
            perspectives and answers questions conversationally, all in Urdu.
          </p>
        </div>
      </section>

      {/* Pipeline */}
      <section className="mt-24">
        <SectionHeading
          eyebrow="How It Works"
          title="From raw feeds to intelligence"
        />
        <div className="space-y-3">
          {PIPELINE.map((p, i) => (
            <motion.div
              key={p.step}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              className="glass flex items-start gap-5 p-6"
            >
              <span className="font-display text-2xl font-semibold
                               text-ocean-400">
                {p.step}
              </span>
              <div>
                <h3 className="font-semibold text-ink-900">{p.title}</h3>
                <p className="mt-1 text-sm text-steel-600">{p.text}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Stats band */}
      <section className="mt-24 grid grid-cols-2 gap-px overflow-hidden
                          border border-steel-200 bg-steel-200 md:grid-cols-4">
        {[
          ['5', 'News Sources'],
          ['7', 'Categories'],
          ['RAG', 'Opinion Engine'],
          ['Urdu', 'AI Narration'],
        ].map(([value, label]) => (
          <div key={label} className="bg-cream-50 px-6 py-10 text-center">
            <div className="font-display text-3xl font-semibold brand-text">
              {value}
            </div>
            <div className="mt-2 text-xs uppercase tracking-wider text-steel-500">
              {label}
            </div>
          </div>
        ))}
      </section>

      {/* Team */}
      <section className="mt-24">
        <SectionHeading eyebrow="The Team" title="Built by" />
        <div className="flex justify-center">
          {TEAM.map((m) => (
            <motion.div
              key={m.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4 }}
              className="glass flex w-full max-w-xs flex-col items-center
                         p-8 text-center"
            >
              <div className="flex h-24 w-24 items-center justify-center
                              rounded-full bg-gradient-to-br from-ocean-500
                              to-ocean-700 font-display text-3xl font-semibold
                              text-white">
                {initials(m.name)}
              </div>
              <h3 className="mt-5 text-lg font-semibold text-ink-900">
                {m.name}
              </h3>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Closing */}
      <section className="mt-24 text-center">
        <h2 className="font-display text-2xl font-semibold text-ink-900
                       md:text-3xl">
          Explore the news, intelligently.
        </h2>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link to="/news" className="btn-primary">
            Browse News
          </Link>
          <Link to="/brief" className="btn-ghost">
            Today&apos;s Bulletin
          </Link>
        </div>
      </section>
    </div>
  );
}
