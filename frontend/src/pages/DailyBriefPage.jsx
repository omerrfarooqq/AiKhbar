import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { Sparkles, RefreshCw } from 'lucide-react';
import { generateBrief, clearBrief } from '../store/briefSlice';
import SectionHeading from '../components/SectionHeading';
import GlassCard from '../components/GlassCard';
import AudioPlayer from '../components/AudioPlayer';
import CategoryBadge from '../components/CategoryBadge';
import Loader from '../components/Loader';

export default function DailyBriefPage() {
  const dispatch = useDispatch();
  const { data, status, error } = useSelector((s) => s.brief);

  const run = () =>
    dispatch(
      generateBrief({
        max_stories: 6,
        mode: 'morning',
        include_audio: true,
        include_opinions: true,
      }),
    );

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <SectionHeading
        eyebrow="Flagship"
        title="One-click Daily Brief"
        subtitle="Top stories, unified summaries, multi-perspective analysis and an Urdu audio narration."
      />

      {/* Generate panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass relative overflow-hidden p-10 text-center"
      >
        <div className="absolute inset-0 bg-gold-radial" />
        <div className="relative">
          <p className="text-slate-300">
            Generate today&apos;s intelligence briefing.
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <button
              onClick={run}
              disabled={status === 'loading'}
              className="btn-primary"
            >
              <Sparkles size={17} />
              {status === 'loading' ? 'Generating…' : 'Generate Daily Brief'}
            </button>
            {data && (
              <button
                onClick={() => dispatch(clearBrief())}
                className="btn-ghost"
              >
                <RefreshCw size={15} />
                Clear
              </button>
            )}
          </div>
        </div>
      </motion.div>

      {status === 'loading' && (
        <Loader label="Summarizing stories and synthesizing Urdu audio…" />
      )}
      {status === 'failed' && (
        <p className="mt-8 text-rose-300">Brief failed: {error}</p>
      )}

      {/* Result */}
      {data && (
        <div className="mt-10 space-y-6">
          {data.audio_url && (
            <AudioPlayer
              src={data.audio_url}
              title={`Daily Brief — Urdu Narration (${data.audio_provider})`}
            />
          )}

          {data.stories?.map((story, i) => (
            <GlassCard key={story.cluster_id} delay={i * 0.06}>
              <div className="flex items-center justify-between">
                <CategoryBadge category={story.category} />
                <span className="text-xs text-slate-500">
                  Story {i + 1}
                </span>
              </div>
              <h3 className="urdu mt-3 text-xl text-slate-100">
                {story.title}
              </h3>
              <p className="urdu mt-3 text-slate-300">{story.summary}</p>

              {story.opinions?.length > 0 && (
                <div className="mt-5 border-t border-white/10 pt-4">
                  <p className="mb-2 text-xs font-semibold uppercase
                                tracking-wider text-gold-400">
                    Perspectives
                  </p>
                  <div className="space-y-2">
                    {story.opinions.map((op, j) => (
                      <div key={j} className="rounded-lg bg-white/5 p-3">
                        <span className="text-xs font-semibold text-slate-200">
                          {op.perspective}
                          {op.stance && (
                            <span className="ml-2 text-gold-400">
                              · {op.stance}
                            </span>
                          )}
                        </span>
                        <p className="urdu mt-1 text-sm text-slate-400">
                          {op.summary}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
}
