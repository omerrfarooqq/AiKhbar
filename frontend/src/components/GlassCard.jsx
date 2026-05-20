import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

/**
 * Reusable glassmorphism card with an entrance animation.
 * `delay` staggers cards within a list/grid.
 */
export default function GlassCard({ children, className, delay = 0, hover = true }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, delay, ease: 'easeOut' }}
      className={cn('glass p-6', hover && 'glass-hover', className)}
    >
      {children}
    </motion.div>
  );
}
