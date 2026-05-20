import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, MessagesSquare } from 'lucide-react';
import SectionHeading from '../components/SectionHeading';
import { newsService } from '../services/newsService';

const SUGGESTIONS = [
  'Summarize today\'s top story in Urdu',
  'Why is this important?',
  'What happened before this?',
  'What are people saying about this?',
];

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text) => {
    const question = (text ?? input).trim();
    if (!question || loading) return;

    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { role: 'user', content: question }]);
    setInput('');
    setLoading(true);

    try {
      const res = await newsService.ask({ question, history, language: 'ur' });
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: res.answer, sources: res.sources },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: `⚠️ ${err.message}`, sources: [] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-3xl flex-col px-6 py-16">
      <SectionHeading
        eyebrow="Conversational"
        title="Ask AiKhbar"
        subtitle="A RAG-grounded news assistant. Answers are drawn from indexed coverage."
      />

      {/* Conversation */}
      <div className="glass min-h-[26rem] flex-1 space-y-4 p-6">
        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center gap-5 py-12 text-center">
            <MessagesSquare className="text-gold-400" size={36} />
            <p className="text-slate-400">Ask anything about the news.</p>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="chip hover:border-gold-500/40 hover:text-gold-300"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        <AnimatePresence initial={false}>
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${
                m.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                  m.role === 'user'
                    ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-ink-950'
                    : 'bg-white/5 text-slate-200'
                }`}
              >
                <p className={m.role === 'assistant' ? 'urdu' : ''}>
                  {m.content}
                </p>
                {m.sources?.length > 0 && (
                  <div className="mt-2 border-t border-white/10 pt-2 text-xs
                                  text-slate-400">
                    Sources:{' '}
                    {m.sources.slice(0, 3).map((s) => s.source).join(', ')}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-white/5 px-4 py-3">
              <motion.div
                className="flex gap-1"
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 1.2, repeat: Infinity }}
              >
                <span className="h-2 w-2 rounded-full bg-gold-400" />
                <span className="h-2 w-2 rounded-full bg-gold-400" />
                <span className="h-2 w-2 rounded-full bg-gold-400" />
              </motion.div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Composer */}
      <div className="mt-4 flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Ask a question about the news…"
          className="flex-1 rounded-xl border border-white/10 bg-white/5 px-4
                     py-3 text-sm text-slate-100 placeholder:text-slate-500
                     focus:border-gold-500/50 focus:outline-none"
        />
        <button
          onClick={() => send()}
          disabled={loading}
          className="btn-primary !px-5"
          aria-label="Send"
        >
          <Send size={17} />
        </button>
      </div>
    </div>
  );
}
