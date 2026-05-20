import { motion } from 'framer-motion';

/** Animated editorial section heading with an eyebrow label. */
export default function SectionHeading({ eyebrow, title, subtitle }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="mb-10"
    >
      {eyebrow && (
        <span className="text-xs font-semibold uppercase tracking-[0.3em] text-gold-400">
          {eyebrow}
        </span>
      )}
      <h2 className="mt-2 font-display text-3xl font-semibold text-slate-100 md:text-4xl">
        {title}
      </h2>
      {subtitle && (
        <p className="mt-3 max-w-2xl text-slate-400">{subtitle}</p>
      )}
    </motion.div>
  );
}
