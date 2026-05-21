import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Newspaper, Radio, MessagesSquare, Info, Menu, X } from 'lucide-react';
import logo from '../assets/logo-globe.png';

const LINKS = [
  { to: '/news', label: 'News', icon: Newspaper },
  { to: '/brief', label: 'Bulletin', icon: Radio },
  { to: '/chat', label: 'Ask AiKhbar', icon: MessagesSquare },
  { to: '/about', label: 'About', icon: Info },
];

/** Fixed dark navigation bar, editorial newsroom style. */
export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <motion.header
      initial={{ y: -90 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="sticky top-0 z-50 border-b border-white/10 bg-ink-950/90
                 backdrop-blur-xl"
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between
                      px-5 py-3 md:px-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <img src={logo} alt="AiKhbar" className="h-10 w-10 md:h-11 md:w-11" />
          <span className="flex flex-col leading-none">
            <span className="font-display text-xl font-semibold text-white">
              AiKhbar
            </span>
            <span className="mt-1 text-[9px] uppercase tracking-[0.22em]
                             text-steel-400">
              Urdu News Intelligence
            </span>
          </span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden items-center gap-2 md:flex">
          {LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to}>
              {({ isActive }) => (
                <motion.div
                  whileHover={{ y: -2 }}
                  whileTap={{ scale: 0.97 }}
                  className={`flex items-center gap-2 px-4 py-2.5 text-sm
                    font-semibold transition-colors ${
                      isActive
                        ? 'bg-white text-ink-900'
                        : 'bg-white/5 text-steel-300 hover:bg-white/10 hover:text-white'
                    }`}
                >
                  <Icon size={15} />
                  {label}
                </motion.div>
              )}
            </NavLink>
          ))}
        </div>

        {/* Mobile toggle */}
        <button
          className="text-steel-200 md:hidden"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t border-white/10 md:hidden"
          >
            <div className="flex flex-col gap-2 px-5 py-4">
              {LINKS.map(({ to, label, icon: Icon }) => (
                <NavLink key={to} to={to} onClick={() => setOpen(false)}>
                  {({ isActive }) => (
                    <div
                      className={`flex items-center gap-3 px-4 py-3 text-sm
                        font-semibold ${
                          isActive
                            ? 'bg-white text-ink-900'
                            : 'text-steel-300 hover:bg-white/10 hover:text-white'
                        }`}
                    >
                      <Icon size={17} />
                      {label}
                    </div>
                  )}
                </NavLink>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
