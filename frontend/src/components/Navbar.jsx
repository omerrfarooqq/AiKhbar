import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Menu, X, Sparkles } from 'lucide-react';

const LINKS = [
  { to: '/news', label: 'News' },
  { to: '/brief', label: 'Daily Brief' },
  { to: '/chat', label: 'Ask AiKhbar' },
];

/** Sticky glass navigation bar. */
export default function Navbar() {
  const [open, setOpen] = useState(false);

  const linkClass = ({ isActive }) =>
    `text-sm font-medium transition-colors ${
      isActive ? 'text-gold-400' : 'text-slate-300 hover:text-gold-300'
    }`;

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="sticky top-0 z-50 border-b border-white/10 bg-ink-950/70
                 backdrop-blur-xl"
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg
                           bg-gradient-to-br from-gold-400 to-gold-600
                           font-display text-lg font-bold text-ink-950">
            A
          </span>
          <span className="font-display text-xl font-semibold gold-text">
            AiKhbar
          </span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          {LINKS.map((l) => (
            <NavLink key={l.to} to={l.to} className={linkClass}>
              {l.label}
            </NavLink>
          ))}
          <Link to="/brief" className="btn-primary !px-5 !py-2 text-sm">
            <Sparkles size={15} />
            Generate Brief
          </Link>
        </div>

        <button
          className="md:hidden text-slate-200"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {open && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          className="overflow-hidden border-t border-white/10 md:hidden"
        >
          <div className="flex flex-col gap-4 px-6 py-5">
            {LINKS.map((l) => (
              <NavLink
                key={l.to}
                to={l.to}
                className={linkClass}
                onClick={() => setOpen(false)}
              >
                {l.label}
              </NavLink>
            ))}
          </div>
        </motion.div>
      )}
    </motion.header>
  );
}
