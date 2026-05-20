import { Link } from 'react-router-dom';

/** Site footer. */
export default function Footer() {
  return (
    <footer className="mt-24 border-t border-white/10 bg-ink-900/60 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="flex flex-col items-start justify-between gap-8 md:flex-row">
          <div className="max-w-sm">
            <span className="font-display text-2xl font-semibold gold-text">
              AiKhbar
            </span>
            <p className="mt-3 text-sm text-slate-400">
              An AI-powered Urdu news intelligence platform — aggregation,
              summarization, opinion analysis and audio briefings.
            </p>
          </div>
          <div className="flex gap-12 text-sm">
            <div className="flex flex-col gap-2">
              <span className="font-semibold text-slate-200">Explore</span>
              <Link to="/news" className="text-slate-400 hover:text-gold-400">
                News
              </Link>
              <Link to="/brief" className="text-slate-400 hover:text-gold-400">
                Daily Brief
              </Link>
              <Link to="/chat" className="text-slate-400 hover:text-gold-400">
                Ask AiKhbar
              </Link>
            </div>
            <div className="flex flex-col gap-2">
              <span className="font-semibold text-slate-200">About</span>
              <span className="text-slate-400">Media Intelligence</span>
              <span className="text-slate-400">RAG &amp; Analysis</span>
            </div>
          </div>
        </div>
        <p className="mt-10 text-xs text-slate-600">
          © {new Date().getFullYear()} AiKhbar. Built as an AI media
          intelligence system.
        </p>
      </div>
    </footer>
  );
}
