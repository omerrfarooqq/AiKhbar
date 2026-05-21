import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { RefreshCw, Volume2, Radio } from 'lucide-react';
import { generateBrief, clearBrief } from '../store/briefSlice';
import { newsService } from '../services/newsService';
import SectionHeading from '../components/SectionHeading';
import GlassCard from '../components/GlassCard';
import AudioPlayer from '../components/AudioPlayer';
import CategoryBadge from '../components/CategoryBadge';
import Loader from '../components/Loader';

export default function DailyBriefPage() {
  const dispatch = useDispatch();
  const { data, status, error } = useSelector((s) => s.brief);

  // The 2 to 3 minute combined audio brief.
  const [digest, setDigest] = useState({ status: 'idle', url: null, error: null });
  // Per-story audio, keyed by cluster_id.
  const [storyAudio, setStoryAudio] = useState({});

  const run = () => {
    setDigest({ status: 'idle', url: null, error: null });
    setStoryAudio({});
    // Audio is generated on demand, not as part of the brief.
    dispatch(
      generateBrief({
        max_stories: 6,
        mode: 'morning',
        include_audio: false,
        include_opinions: true,
      }),
    );
  };

  const playDigest = async () => {
    setDigest({ status: 'loading', url: null, error: null });
    try {
      const res = await newsService.audioDigest();
      if (!res.audio_url) throw new Error('No audio was returned.');
      setDigest({ status: 'done', url: res.audio_url, error: null });
    } catch (e) {
      setDigest({ status: 'error', url: null, error: e.message });
    }
  };

  const playStory = async (story) => {
    setStoryAudio((s) => ({
      ...s,
      [story.cluster_id]: { status: 'loading' },
    }));
    try {
      const res = await newsService.synthesize({
        text: story.summary,
        narration_mode: 'neutral',
      });
      setStoryAudio((s) => ({
        ...s,
        [story.cluster_id]: { status: 'done', url: res.audio_url },
      }));
    } catch (e) {
      setStoryAudio((s) => ({
        ...s,
        [story.cluster_id]: { status: 'error', error: e.message },
      }));
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <SectionHeading
        eyebrow="Daily Edition"
        title="Today's News Bulletin"
        subtitle="Top stories with unified summaries. Listen to the full 2 to 3 minute brief, or play any single story on its own."
      />

      {/* Generate panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass relative overflow-hidden p-10 text-center"
      >
        <div className="absolute inset-0 bg-ocean-radial" />
        <div className="relative">
          <p className="text-steel-600">
            Compile today&apos;s top stories into a narrated news bulletin.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <button
              onClick={run}
              disabled={status === 'loading'}
              className="btn-primary"
            >
              {status === 'loading' ? 'Preparing Bulletin…' : "Get Today's Bulletin"}
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
        <Loader label="Compiling today's top stories…" />
      )}
      {status === 'failed' && (
        <p className="mt-8 text-rose-600">Bulletin failed: {error}</p>
      )}

      {/* Result */}
      {data && (
        <div className="mt-10 space-y-6">
          {/* Option 1: the 2 to 3 minute combined brief */}
          <div className="glass p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h3 className="font-semibold text-ink-900">
                  2 to 3 Minute News Brief
                </h3>
                <p className="mt-1 text-sm text-steel-500">
                  A concise Urdu audio bulletin of today&apos;s most important
                  news.
                </p>
              </div>
              <button
                onClick={playDigest}
                disabled={digest.status === 'loading'}
                className="btn-primary"
              >
                <Radio size={15} />
                {digest.status === 'loading' ? 'Generating…' : 'Play Brief'}
              </button>
            </div>
            {digest.status === 'error' && (
              <p className="mt-3 text-sm text-rose-600">{digest.error}</p>
            )}
            {digest.url && (
              <div className="mt-4">
                <AudioPlayer
                  src={digest.url}
                  title="2 to 3 Minute News Brief"
                />
              </div>
            )}
          </div>

          {/* Option 2: each story with its own audio */}
          {data.stories?.map((story, i) => {
            const audio = storyAudio[story.cluster_id] || {};
            return (
              <GlassCard key={story.cluster_id} delay={i * 0.06}>
                <div className="flex items-center justify-between">
                  <CategoryBadge category={story.category} />
                  <span className="text-xs text-steel-400">Story {i + 1}</span>
                </div>
                <h3 className="urdu mt-3 text-xl text-ink-900">{story.title}</h3>
                <p className="urdu mt-3 text-ink-700">{story.summary}</p>

                <div className="mt-4">
                  <button
                    onClick={() => playStory(story)}
                    disabled={audio.status === 'loading'}
                    className="btn-ghost"
                  >
                    <Volume2 size={15} />
                    {audio.status === 'loading'
                      ? 'Generating…'
                      : 'Listen to this story'}
                  </button>
                </div>
                {audio.status === 'error' && (
                  <p className="mt-2 text-sm text-rose-600">{audio.error}</p>
                )}
                {audio.url && (
                  <div className="mt-3">
                    <AudioPlayer
                      src={audio.url}
                      title={`Story ${i + 1} Narration`}
                    />
                  </div>
                )}

                {story.opinions?.length > 0 && (
                  <div className="mt-5 border-t border-steel-200 pt-4">
                    <p className="mb-2 text-xs font-semibold uppercase
                                  tracking-wider text-ocean-600">
                      Perspectives
                    </p>
                    <div className="space-y-2">
                      {story.opinions.map((op, j) => (
                        <div
                          key={j}
                          className="rounded-lg border border-steel-200
                                     bg-white/60 p-3"
                        >
                          <span className="text-xs font-semibold text-ink-800">
                            {op.perspective}
                            {op.stance && (
                              <span className="ml-2 text-ocean-600">
                                · {op.stance}
                              </span>
                            )}
                          </span>
                          <p className="urdu mt-1 text-sm text-steel-500">
                            {op.summary}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </GlassCard>
            );
          })}
        </div>
      )}
    </div>
  );
}
