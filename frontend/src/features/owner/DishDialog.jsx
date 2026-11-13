import { useState } from 'react';
import { createDish, updateDish } from '../../services/kitchen';
import { describeError } from '../../services/http';
import Dialog from '../../ui/Dialog';
import Notice from '../../ui/Notice';

function toDraft(dish) {
  return {
    name: dish?.name ?? '',
    price: dish?.price ?? '',
    category: dish?.category ?? '',
    description: dish?.description ?? '',
    image_url: dish?.image_url ?? '',
    is_available: dish?.is_available ?? true,
  };
}

/** Convert form strings into the shape the API expects (blanks become null). */
function toPayload(draft) {
  const orNull = (text) => (text.trim() ? text.trim() : null);
  return {
    name: draft.name.trim(),
    description: orNull(draft.description),
    price: Number(draft.price).toFixed(2),
    category: orNull(draft.category),
    image_url: orNull(draft.image_url),
    is_available: draft.is_available,
  };
}

export default function DishDialog({ dish, onDismiss, onSaved }) {
  const editing = Boolean(dish?.id);
  const [draft, setDraft] = useState(() => toDraft(dish));
  const [saving, setSaving] = useState(false);
  const [problem, setProblem] = useState('');

  const field = (key) => ({
    value: draft[key],
    onChange: (e) => setDraft((d) => ({ ...d, [key]: e.target.value })),
  });

  const save = async (event) => {
    event.preventDefault();
    setSaving(true);
    setProblem('');
    try {
      const payload = toPayload(draft);
      if (editing) await updateDish(dish.id, payload);
      else await createDish(payload);
      onSaved();
      onDismiss();
    } catch (err) {
      setProblem(describeError(err));
      setSaving(false);
    }
  };

  return (
    <Dialog heading={editing ? `Edit “${dish.name}”` : 'New dish'} onDismiss={onDismiss}>
      <form className="stack" onSubmit={save}>
        <Notice>{problem}</Notice>
        <label className="field">
          <span>Dish name</span>
          <input required placeholder="Paneer tikka wrap" {...field('name')} />
        </label>
        <div className="field-pair">
          <label className="field">
            <span>Price (₹)</span>
            <input required type="number" min="1" step="0.01" placeholder="120" {...field('price')} />
          </label>
          <label className="field">
            <span>Section</span>
            <input placeholder="Wraps, Drinks…" {...field('category')} />
          </label>
        </div>
        <label className="field">
          <span>Short description</span>
          <textarea rows={2} placeholder="What makes it good?" {...field('description')} />
        </label>
        <label className="field">
          <span>Photo URL</span>
          <input type="url" placeholder="https://…" {...field('image_url')} />
        </label>
        <label className="toggle">
          <input
            type="checkbox"
            checked={draft.is_available}
            onChange={(e) => setDraft((d) => ({ ...d, is_available: e.target.checked }))}
          />
          <span className="toggle-track" />
          Customers can order this now
        </label>
        <button className="btn btn-primary btn-block" disabled={saving}>
          {saving ? 'Saving…' : editing ? 'Save changes' : 'Add to menu'}
        </button>
      </form>
    </Dialog>
  );
}
