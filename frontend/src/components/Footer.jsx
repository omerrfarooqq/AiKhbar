import { Link } from 'react-router-dom';
import logo from '../assets/logo-globe.png';

/** Site footer. */
export default function Footer() {
  return (
    <footer className="mt-24 border-t border-white/70 bg-cream-50/70
                       backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="flex flex-col items-start justify-between gap-8 md:flex-row">
          <div className="max-w-sm">
            <div className="flex items-center gap-2.5">
              <img src={logo} alt="" className="h-9 w-9" />
              <span className="font-display text-2xl font-semibold text-ink-900">
                Ai<span className="brand-text">Khbar</span>
              </span>
            </div>
            <p className="mt-3 text-sm text-steel-500">
              An AI-powered Urdu news intelligence platform for aggregation,
              summarization, opinion analysis and audio briefings.
            </p>
          </div>
          <div className="flex gap-12 text-sm">
            <div className="flex flex-col gap-2">
              <span className="font-semibold text-ink-800">Explore</span>
              <Link to="/news" className="text-steel-500 hover:text-ocean-600">
                News
              </Link>
              <Link to="/brief" className="text-steel-500 hover:text-ocean-600">
                Daily Brief
              </Link>
              <Link to="/chat" className="text-steel-500 hover:text-ocean-600">
                Ask AiKhbar
              </Link>
            </div>
            <div className="flex flex-col gap-2">
              <span className="font-semibold text-ink-800">About</span>
              <span className="text-steel-500">Media Intelligence</span>
              <span className="text-steel-500">RAG &amp; Analysis</span>
            </div>
          </div>
        </div>
        <p className="mt-10 text-xs text-steel-400">
          © {new Date().getFullYear()} AiKhbar. Built as an AI media
          intelligence system.
        </p>
      </div>
    </footer>
  );
}
