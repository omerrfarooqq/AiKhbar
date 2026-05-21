import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Volume2, Scale, Clock3, Layers } from 'lucide-react';
import SectionHeading from '../components/SectionHeading';
import GlassCard from '../components/GlassCard';
import AudioPlayer from '../components/AudioPlayer';
import CategoryBadge from '../components/CategoryBadge';
import Loader from '../components/Loader';
import { newsService } from '../services/newsService';

export default function StoryDetailPage() {
  const { id } = useParams();
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [busy, setBusy] = useState('');

  useEffect(() => {
    newsService
      .getStory(id)
      .then(setStory)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  const enrich = async (kind) => {
    setBusy(kind);
    try {
      if (kind === 'opinions') {
        const opinions = await newsService.getOpinions(id);
        setStory((s) => ({ ...s, opinions }));
      } else if (kind === 'timeline') {
        const timeline_events = await newsService.getTimeline(id);
        setStory((s) => ({ ...s, timeline_events }));
      } else if (kind === 'audio') {
        const summary = story.summaries?.[0]?.content || story.unified_summary;
        const res = await newsService.synthesize({
          text: summary,
          narration_mode: 'podcast',
        });
        setAudioUrl(res.audio_url);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy('');
    }
  };

  if (loading) return <Loader label="Loading story…" />;
  if (error)
    return <p className="mx-auto max-w-3xl px-6 py-20 text-rose-600">{error}</p>;
  if (!story) return null;

  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3">
          <CategoryBadge category={story.category} />
          <span className="flex items-center gap-1.5 text-xs text-steel-400">
            <Layers size={13} /> {story.article_count} sources
          </span>
        </div>
        <h1 className="urdu mt-4 font-display text-3xl text-ink-900 md:text-4xl">
          {story.title}
        </h1>
      </motion.div>

      {/* Action toolbar */}
      <div className="mt-8 flex flex-wrap gap-3">
        <button
          onClick={() => enrich('audio')}
          disabled={busy === 'audio'}
          className="btn-ghost"
        >
          <Volume2 size={15} />
          {busy === 'audio' ? 'Synthesizing…' : 'Listen in Urdu'}
        </button>
        <button
          onClick={() => enrich('opinions')}
          disabled={busy === 'opinions'}
          className="btn-ghost"
        >
          <Scale size={15} />
          {busy === 'opinions' ? 'Analyzing…' : 'Aggregate Opinions'}
        </button>
        <button
          onClick={() => enrich('timeline')}
          disabled={busy === 'timeline'}
          className="btn-ghost"
        >
          <Clock3 size={15} />
          {busy === 'timeline' ? 'Building…' : 'Build Timeline'}
        </button>
      </div>

      {audioUrl && (
        <div className="mt-6">
          <AudioPlayer src={audioUrl} title="Story Urdu Narration" />
        </div>
      )}

      {/* Unified summary */}
      <GlassCard className="mt-8" hover={false}>
        <SectionHeading eyebrow="Summary" title="Unified Story" />
        <p className="urdu text-ink-800">
          {story.summaries?.[0]?.content ||
            story.unified_summary ||
            'No summary generated yet.'}
        </p>
      </GlassCard>

      {/* Opinions */}
      {story.opinions?.length > 0 && (
        <GlassCard className="mt-6" hover={false}>
          <SectionHeading eyebrow="RAG" title="Perspectives" />
          <div className="space-y-3">
            {story.opinions.map((op) => (
              <div
                key={op.id}
                className="rounded-xl border border-steel-200 bg-white/60 p-4"
              >
                <span className="text-sm font-semibold text-ocean-700">
                  {op.perspective}
                  {op.stance && (
                    <span className="ml-2 text-steel-500">· {op.stance}</span>
                  )}
                </span>
                <p className="urdu mt-2 text-sm text-ink-700">{op.summary}</p>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Timeline */}
      {story.timeline_events?.length > 0 && (
        <GlassCard className="mt-6" hover={false}>
          <SectionHeading eyebrow="Context" title="Historical Timeline" />
          <div className="relative space-y-6 border-l border-steel-200 pl-6">
            {story.timeline_events.map((ev) => (
              <div key={ev.id} className="relative">
                <span className="absolute -left-[31px] top-1 h-3 w-3
                                 rounded-full bg-ocean-500 ring-4
                                 ring-ocean-500/15" />
                <span className="text-xs font-semibold text-ocean-600">
                  {ev.date_label || 'Earlier'}
                </span>
                <h4 className="mt-1 font-semibold text-ink-900">{ev.title}</h4>
                <p className="urdu mt-1 text-sm text-steel-500">
                  {ev.description}
                </p>
              </div>
            ))}
          </div>
        </GlassCard>
      )}
    </div>
  );
}
