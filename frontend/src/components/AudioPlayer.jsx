import { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, Volume2 } from 'lucide-react';

/** Minimal glass audio player for Urdu briefing playback. */
export default function AudioPlayer({ src, title = 'Urdu Audio Briefing' }) {
  const audioRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  const toggle = () => {
    const el = audioRef.current;
    if (!el) return;
    if (playing) el.pause();
    else el.play();
    setPlaying(!playing);
  };

  const onTime = () => {
    const el = audioRef.current;
    if (el?.duration) setProgress((el.currentTime / el.duration) * 100);
  };

  return (
    <div className="glass flex items-center gap-4 p-4">
      <button
        onClick={toggle}
        className="flex h-12 w-12 shrink-0 items-center justify-center
                   rounded-full bg-gradient-to-r from-gold-500 to-gold-600
                   text-ink-950 transition hover:shadow-glow"
        aria-label={playing ? 'Pause' : 'Play'}
      >
        {playing ? <Pause size={20} /> : <Play size={20} className="ml-0.5" />}
      </button>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 text-sm text-slate-300">
          <Volume2 size={14} className="text-gold-400" />
          <span className="truncate">{title}</span>
        </div>
        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
          <motion.div
            className="h-full bg-gradient-to-r from-gold-400 to-gold-600"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <audio
        ref={audioRef}
        src={src}
        onTimeUpdate={onTime}
        onEnded={() => setPlaying(false)}
      />
    </div>
  );
}
