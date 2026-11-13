import { useState } from 'react';
import { formatPrice } from '../../lib/format';
import { useAction } from '../../lib/useAction';
import { useDebouncedValue } from '../../lib/useDebouncedValue';
import { useRemote } from '../../lib/useRemote';
import { deleteDish, listDishes, toggleDish } from '../../services/kitchen';
import EmptyState from '../../ui/EmptyState';
import Icon from '../../ui/Icon';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';
import Pager from '../../ui/Pager';
import Spinner from '../../ui/Spinner';
import DishDialog from './DishDialog';

export default function MenuEditor() {
  const [term, setTerm] = useState('');
  const [page, setPage] = useState(1);
  const [editing, setEditing] = useState(null); // null = closed, {} = new dish, dish = edit
  const search = useDebouncedValue(term.trim());

  const dishes = useRemote(() => listDishes({ search, page, page_size: 15 }), [search, page]);
  const action = useAction(dishes.refetch);

  const destroy = (dish) => {
    if (window.confirm(`Remove “${dish.name}” from the menu for good?`)) {
      action.run(dish.id, () => deleteDish(dish.id));
    }
  };

  return (
    <div className="page">
      <PageHead eyebrow="Kitchen" title="Menu" lead="Add dishes, tweak prices and mark things as sold out.">
        <label className="searchbox searchbox-small">
          <Icon name="search" />
          <input
            type="search"
            placeholder="Find a dish"
            value={term}
            onChange={(e) => {
              setTerm(e.target.value);
              setPage(1);
            }}
          />
        </label>
        <button type="button" className="btn btn-primary" onClick={() => setEditing({})}>
          <Icon name="plus" /> New dish
        </button>
      </PageHead>

      <Notice onRetry={dishes.error ? dishes.refetch : undefined}>{dishes.error || action.error}</Notice>

      {dishes.firstLoad ? (
        <Spinner label="Loading your menu…" />
      ) : dishes.data?.items.length ? (
        <div className="panel panel-flush">
          <table className="grid-table">
            <thead>
              <tr>
                <th>Dish</th>
                <th>Section</th>
                <th className="num">Price</th>
                <th>On sale</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {dishes.data.items.map((dish) => (
                <tr key={dish.id} className={dish.is_available ? '' : 'is-dimmed'}>
                  <td data-label="Dish">
                    <strong>{dish.name}</strong>
                    {dish.description && <small className="subtle block">{dish.description}</small>}
                  </td>
                  <td data-label="Section">{dish.category || <span className="subtle">—</span>}</td>
                  <td data-label="Price" className="num">
                    {formatPrice(dish.price)}
                  </td>
                  <td data-label="On sale">
                    <label className="toggle">
                      <input
                        type="checkbox"
                        checked={dish.is_available}
                        disabled={action.busyKey === dish.id}
                        onChange={(e) => action.run(dish.id, () => toggleDish(dish.id, e.target.checked))}
                      />
                      <span className="toggle-track" />
                      <span className="sr-only">{dish.is_available ? 'Available' : 'Sold out'}</span>
                    </label>
                  </td>
                  <td className="row-actions">
                    <button type="button" className="icon-button" aria-label={`Edit ${dish.name}`} onClick={() => setEditing(dish)}>
                      <Icon name="edit" size={16} />
                    </button>
                    <button
                      type="button"
                      className="icon-button is-danger"
                      aria-label={`Delete ${dish.name}`}
                      disabled={action.busyKey === dish.id}
                      onClick={() => destroy(dish)}
                    >
                      <Icon name="trash" size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        !dishes.error && (
          <EmptyState icon="book" title={search ? 'No dish by that name' : 'Your menu is blank'}>
            {search ? 'Try a different word.' : 'Start with your most popular dish.'}
          </EmptyState>
        )
      )}

      <Pager result={dishes.data} onPage={setPage} />
      {editing && <DishDialog dish={editing} onDismiss={() => setEditing(null)} onSaved={dishes.refetch} />}
    </div>
  );
}
