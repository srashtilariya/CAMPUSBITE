import { useState } from 'react';
import { askAboutOrders } from '../../services/insights';
import { describeError } from '../../services/http';
import Icon from '../../ui/Icon';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';
import Spinner from '../../ui/Spinner';

const STARTERS = [
  'What did I order in my last five orders?',
  'Do I have anything that hasn’t arrived yet?',
  'How much have I spent this week?',
  'What do I order the most?',
];

export default function AskCampusBite() {
  const [draft, setDraft] = useState('');
  const [thread, setThread] = useState([]);
  const [thinking, setThinking] = useState(false);
  const [problem, setProblem] = useState('');

  const ask = async (question) => {
    setThinking(true);
    setProblem('');
    try {
      const reply = await askAboutOrders(question);
      setThread((prev) => [
        { id: Date.now(), question: question || 'Give me an overview of my orders', ...reply },
        ...prev,
      ]);
      setDraft('');
    } catch (err) {
      setProblem(describeError(err, 'The assistant couldn’t answer that.'));
    } finally {
      setThinking(false);
    }
  };

  return (
    <div className="page page-narrow">
      <PageHead
        eyebrow="Assistant"
        title="Ask CampusBite"
        lead="Questions about your own orders, answered in plain language. Only your order history is shared."
      />

      <section className="panel ask-box">
        <form
          className="ask-row"
          onSubmit={(e) => {
            e.preventDefault();
            if (draft.trim()) ask(draft.trim());
          }}
        >
          <input
            maxLength={500}
            placeholder="Ask something like “what did I spend in October?”"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          <button className="btn btn-primary" disabled={thinking || !draft.trim()}>
            Ask
          </button>
        </form>
        <div className="starter-row">
          <button type="button" className="starter starter-strong" disabled={thinking} onClick={() => ask('')}>
            <Icon name="sparkle" size={15} /> Quick overview
          </button>
          {STARTERS.map((text) => (
            <button type="button" key={text} className="starter" disabled={thinking} onClick={() => ask(text)}>
              {text}
            </button>
          ))}
        </div>
      </section>

      <Notice>{problem}</Notice>
      {thinking && <Spinner label="Reading through your orders…" />}

      <div className="answers">
        {thread.map((entry) => (
          <article key={entry.id} className="answer">
            <p className="answer-q">{entry.question}</p>
            <div className="answer-a">{entry.answer}</div>
            <footer className="subtle small">
              Looked at {entry.orders_considered} order{entry.orders_considered === 1 ? '' : 's'} · {entry.model}
            </footer>
          </article>
        ))}
      </div>
    </div>
  );
}
