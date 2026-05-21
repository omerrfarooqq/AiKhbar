import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, MessagesSquare } from 'lucide-react';
import SectionHeading from '../components/SectionHeading';
import { newsService } from '../services/newsService';
import { useChatSocket } from '../hooks/useChatSocket';

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

  // Live chat socket; the server keeps conversation memory per connection.
  const { ready, lastMessage, send: wsSend } = useChatSocket();

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Append assistant replies that arrive over the WebSocket.
  useEffect(() => {
    if (!lastMessage) return;
    const content = lastMessage.error
      ? `Error: ${lastMessage.error}`
      : lastMessage.answer;
    setMessages((m) => [
      ...m,
      { role: 'assistant', content, sources: lastMessage.sources || [] },
    ]);
    setLoading(false);
  }, [lastMessage]);

  const send = async (text) => {
    const question = (text ?? input).trim();
    if (!question || loading) return;

    // History is only needed for the REST path; the socket keeps its own.
    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { role: 'user', content: question }]);
    setInput('');
    setLoading(true);

    // Preferred path: live WebSocket. The reply is handled by the effect above.
    if (ready) {
      wsSend({ question, language: 'ur' });
      return;
    }

    // Fallback path: REST endpoint.
    try {
      const res = await newsService.ask({ question, history, language: 'ur' });
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: res.answer, sources: res.sources },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: `Error: ${err.message}`, sources: [] },
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

      {/* Connection status indicator */}
      <div className="mb-4 flex justify-end">
        <span
          title={ready ? 'Connected' : 'Disconnected'}
          aria-label={ready ? 'Connected' : 'Disconnected'}
          className={`h-3 w-3 rounded-full ring-4 transition-colors ${
            ready
              ? 'bg-emerald-500 ring-emerald-500/20'
              : 'bg-rose-500 ring-rose-500/20'
          }`}
        />
      </div>

      {/* Conversation */}
      <div className="glass min-h-[26rem] flex-1 space-y-4 p-6">
        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center gap-5 py-12 text-center">
            <MessagesSquare className="text-ocean-500" size={36} />
            <p className="text-steel-500">Ask anything about the news.</p>
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-none border border-steel-300 bg-white/70
                             px-3.5 py-2 text-xs font-medium text-steel-600
                             transition-colors hover:border-ocean-400
                             hover:text-ocean-600"
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
                    ? 'bg-gradient-to-r from-ocean-500 to-ocean-600 text-white'
                    : 'border border-steel-200 bg-white/80 text-ink-800'
                }`}
              >
                <p className={m.role === 'assistant' ? 'urdu' : ''}>
                  {m.content}
                </p>
                {m.sources?.length > 0 && (
                  <div className="mt-2 border-t border-steel-200 pt-2 text-xs
                                  text-steel-500">
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
            <div className="rounded-2xl border border-steel-200 bg-white/80
                            px-4 py-3">
              <motion.div
                className="flex gap-1"
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 1.2, repeat: Infinity }}
              >
                <span className="h-2 w-2 rounded-full bg-ocean-400" />
                <span className="h-2 w-2 rounded-full bg-ocean-400" />
                <span className="h-2 w-2 rounded-full bg-ocean-400" />
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
          className="flex-1 rounded-xl border border-steel-200 bg-white/80 px-4
                     py-3 text-sm text-ink-800 placeholder:text-steel-400
                     focus:border-ocean-400 focus:outline-none"
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
