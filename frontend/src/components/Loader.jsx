import { motion } from 'framer-motion';

/** Branded loading indicator. */
export default function Loader({ label = 'Loading…' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <motion.div
        className="h-12 w-12 rounded-full border-2 border-white/10
                   border-t-gold-500"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      />
      <p className="text-sm text-slate-400">{label}</p>
    </div>
  );
}
