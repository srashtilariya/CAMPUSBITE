import { Link } from 'react-router-dom';
import { formatPrice } from '../../lib/format';
import Icon from '../../ui/Icon';

/** `mode`: 'order' (customer), 'guest' (prompt to sign in) or 'view' (other roles). */
export default function DishTile({ dish, mode, onAdd }) {
  const soldOut = !dish.is_available;

  return (
    <article className={`dish ${soldOut ? 'is-sold-out' : ''}`}>
      {dish.image_url && <img className="dish-photo" src={dish.image_url} alt="" loading="lazy" />}
      <div className="dish-info">
        <header>
          <h3>{dish.name}</h3>
          {dish.category && <span className="tag">{dish.category}</span>}
        </header>
        {dish.description && <p className="subtle">{dish.description}</p>}
      </div>
      <footer className="dish-foot">
        <span className="price">{formatPrice(dish.price)}</span>
        {soldOut && <span className="sold-out">Sold out today</span>}
        {!soldOut && mode === 'order' && (
          <button type="button" className="btn btn-primary btn-small" onClick={() => onAdd(dish)}>
            <Icon name="plus" size={16} /> Add
          </button>
        )}
        {!soldOut && mode === 'guest' && (
          <Link to="/signin" className="btn btn-quiet btn-small">
            Sign in to order
          </Link>
        )}
      </footer>
    </article>
  );
}
