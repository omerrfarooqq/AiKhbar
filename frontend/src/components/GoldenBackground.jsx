import { motion } from 'framer-motion';

/**
 * Layered ambient background: a warm cream-to-steel gradient with a soft
 * diagonal light beam and slow-drifting ocean/steel glows. Purely decorative;
 * rendered once per page beneath the layout.
 */
export default function GoldenBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {/* Base cream → steel wash */}
      <div
        className="absolute inset-0"
        style={{
          background:
            'radial-gradient(ellipse 170% 130% at 0% 0%, #FCFAF4 0%, ' +
            '#F8F3E7 24%, #F1E9D7 42%, #E8E4DB 60%, #DCE1E6 78%, #CFD7DE 100%)',
        }}
      />

      {/* Diagonal light beam from the top-left */}
      <div
        className="absolute -left-40 -top-40 h-[60rem] w-[60rem]"
        style={{
          background:
            'linear-gradient(to right, rgba(255,255,255,0.75) 0%, ' +
            'rgba(255,255,255,0.28) 38%, transparent 72%)',
          transform: 'rotate(38deg)',
          transformOrigin: 'top left',
          filter: 'blur(22px)',
        }}
      />

      {/* Drifting ocean glow */}
      <motion.div
        className="absolute -right-44 top-8 h-[34rem] w-[34rem] rounded-full
                   bg-ocean-300/25 blur-[150px]"
        animate={{ x: [0, -60, 0], y: [0, 50, 0] }}
        transition={{ duration: 28, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Drifting steel glow */}
      <motion.div
        className="absolute -bottom-48 left-1/4 h-[32rem] w-[32rem] rounded-full
                   bg-steel-300/40 blur-[150px]"
        animate={{ x: [0, 55, 0], y: [0, -40, 0] }}
        transition={{ duration: 32, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Faint dot grid texture */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            'radial-gradient(rgba(52,60,69,0.06) 1px, transparent 1px)',
          backgroundSize: '34px 34px',
        }}
      />
    </div>
  );
}
