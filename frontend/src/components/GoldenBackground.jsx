import { motion } from 'framer-motion';

/**
 * Layered, animated ambient background — soft gold/blue orbs drifting behind
 * page content. Purely decorative; rendered once per page beneath the layout.
 */
export default function GoldenBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {/* Drifting gold orb */}
      <motion.div
        className="absolute -left-32 -top-32 h-[36rem] w-[36rem] rounded-full
                   bg-gold-500/20 blur-[120px]"
        animate={{ x: [0, 60, 0], y: [0, 40, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
      />
      {/* Drifting accent orb */}
      <motion.div
        className="absolute -right-40 top-1/3 h-[30rem] w-[30rem] rounded-full
                   bg-accent/20 blur-[130px]"
        animate={{ x: [0, -50, 0], y: [0, 60, 0] }}
        transition={{ duration: 26, repeat: Infinity, ease: 'easeInOut' }}
      />
      {/* Faint grid texture */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,.6) 1px,transparent 1px),' +
            'linear-gradient(90deg,rgba(255,255,255,.6) 1px,transparent 1px)',
          backgroundSize: '64px 64px',
        }}
      />
    </div>
  );
}
