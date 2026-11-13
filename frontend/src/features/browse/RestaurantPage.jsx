import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { formatPrice, formatWhen, plural } from '../../lib/format';
import { useDebouncedValue } from '../../lib/useDebouncedValue';
import { useRemote } from '../../lib/useRemote';
import { getRestaurant, getRestaurantMenu, getRestaurantReviews } from '../../services/restaurants';
import { useBasket } from '../../state/BasketProvider';
import { useSession } from '../../state/SessionProvider';
import EmptyState from '../../ui/EmptyState';
import Icon from '../../ui/Icon';
import Notice from '../../ui/Notice';
import Pager from '../../ui/Pager';
import Spinner from '../../ui/Spinner';
import { RatingBadge, StarRow } from '../../ui/Stars';
import DishTile from './DishTile';
import MenuFilters from './MenuFilters';

const START_FILTERS = { search: '', min_price: '', max_price: '', sort: 'name', available_only: false };

function useFlash() {
  const [message, setMessage] = useState('');
  useEffect(() => {
    if (!message) return undefined;
    const timer = setTimeout(() => setMessage(''), 1800);
    return () => clearTimeout(timer);
  }, [message]);
  return [message, setMessage];
}

function ReviewList({ restaurantId }) {
  const { data } = useRemote(() => getRestaurantReviews(restaurantId, { page_size: 5 }), [restaurantId]);
  const reviews = data?.items ?? [];

  return (
    <section className="panel">
      <h2 className="panel-title">What people say</h2>
      {reviews.length === 0 ? (
        <p className="subtle">No one has reviewed this kitchen yet — be the first after your order.</p>
      ) : (
        <ul className="review-list">
          {reviews.map((review) => (
            <li key={review.id}>
              <div className="review-meta">
                <StarRow value={review.rating} />
                <strong>{review.customer_name}</strong>
                <span className="subtle">{formatWhen(review.created_at)}</span>
              </div>
              {review.comment && <p>{review.comment}</p>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function RestaurantPage() {
  const { restaurantId } = useParams();
  const { user } = useSession();
  const basket = useBasket();
  const [filters, setFilters] = useState(START_FILTERS);
  const [page, setPage] = useState(1);
  const [flash, setFlash] = useFlash();
  const query = useDebouncedValue(filters);

  const venue = useRemote(() => getRestaurant(restaurantId), [restaurantId]);
  const menu = useRemote(
    () => getRestaurantMenu(restaurantId, { ...query, page, page_size: 24 }),
    [restaurantId, query, page],
  );

  if (venue.firstLoad) return <Spinner label="Opening the menu…" />;
  if (venue.error) {
    return (
      <div className="page">
        <Notice onRetry={venue.refetch}>{venue.error}</Notice>
      </div>
    );
  }

  const restaurant = venue.data;
  let mode = 'view';
  if (!user) mode = 'guest';
  else if (user.role === 'customer') mode = 'order';

  const handleAdd = (dish) => {
    if (basket.conflictsWith(restaurant)) {
      const ok = window.confirm(
        `Your basket has food from ${basket.restaurant.name}. Orders can only come from one kitchen — start over with ${restaurant.name}?`,
      );
      if (!ok) return;
    }
    basket.addDish(restaurant, dish);
    setFlash(`${dish.name} is in your basket`);
  };

  const basketIsHere = basket.restaurant?.id === restaurant.id && basket.itemCount > 0;

  return (
    <div className="page">
      <Link to="/restaurants" className="back">
        <Icon name="arrowLeft" size={16} /> All kitchens
      </Link>

      <section className="venue-hero">
        {restaurant.image_url && <img src={restaurant.image_url} alt="" />}
        <div className="venue-hero-text">
          <span className="eyebrow">{restaurant.cuisine || 'Campus kitchen'}</span>
          <h1>{restaurant.name}</h1>
          {restaurant.description && <p>{restaurant.description}</p>}
          <div className="venue-facts">
            <RatingBadge rating={restaurant.avg_rating} count={restaurant.review_count} />
            {restaurant.address && (
              <span>
                <Icon name="pin" size={15} /> {restaurant.address}
              </span>
            )}
          </div>
        </div>
      </section>

      <MenuFilters
        value={filters}
        onChange={(next) => {
          setFilters(next);
          setPage(1);
        }}
      />

      <Notice onRetry={menu.refetch}>{menu.error}</Notice>
      {menu.firstLoad ? (
        <Spinner label="Loading dishes…" />
      ) : menu.data?.items.length ? (
        <div className="dish-grid">
          {menu.data.items.map((dish) => (
            <DishTile key={dish.id} dish={dish} mode={mode} onAdd={handleAdd} />
          ))}
        </div>
      ) : (
        !menu.error && (
          <EmptyState icon="search" title="No dishes fit those filters">
            Loosen the budget or clear the search to see more.
          </EmptyState>
        )
      )}
      <Pager result={menu.data} onPage={setPage} />

      <ReviewList restaurantId={restaurantId} />

      {basketIsHere && (
        <Link to="/basket" className="basket-dock">
          <span>
            <Icon name="bag" /> {plural(basket.itemCount, 'item')}
          </span>
          <strong>{formatPrice(basket.subtotal)}</strong>
          <span className="basket-dock-cta">
            Review basket <Icon name="arrowRight" size={16} />
          </span>
        </Link>
      )}
      {flash && <div className="flash" role="status">{flash}</div>}
    </div>
  );
}
