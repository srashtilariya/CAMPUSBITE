import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useDebouncedValue } from '../../lib/useDebouncedValue';
import { useRemote } from '../../lib/useRemote';
import { listRestaurants } from '../../services/restaurants';
import { useSession } from '../../state/SessionProvider';
import EmptyState from '../../ui/EmptyState';
import Icon from '../../ui/Icon';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';
import Pager from '../../ui/Pager';
import Spinner from '../../ui/Spinner';
import { RatingBadge } from '../../ui/Stars';
import { firstName } from '../../lib/format';

const PAGE_SIZE = 12;

function RestaurantTile({ restaurant }) {
  const { id, name, cuisine, address, image_url: image, avg_rating: rating, review_count: reviews } = restaurant;
  return (
    <Link to={`/restaurants/${id}`} className="venue">
      <div className="venue-cover">
        {image ? <img src={image} alt="" loading="lazy" /> : <span className="venue-initial">{name.charAt(0)}</span>}
        <RatingBadge rating={rating} count={reviews} />
      </div>
      <div className="venue-body">
        <h3>{name}</h3>
        <p className="subtle">
          <span>{cuisine || 'Mixed menu'}</span>
          <span aria-hidden="true"> • </span>
          <span>{address || 'On campus'}</span>
        </p>
      </div>
    </Link>
  );
}

export default function RestaurantDirectory() {
  const { user } = useSession();
  const [term, setTerm] = useState('');
  const [page, setPage] = useState(1);
  const search = useDebouncedValue(term.trim());

  const { data, error, firstLoad, refetch } = useRemote(
    () => listRestaurants({ search, page, page_size: PAGE_SIZE }),
    [search, page],
  );

  return (
    <div className="page">
      <PageHead
        eyebrow={user ? `Hey ${firstName(user.name)}` : 'Welcome'}
        title="What are you craving?"
        lead="Every kitchen on campus, one tap away."
      >
        <label className="searchbox">
          <Icon name="search" />
          <input
            type="search"
            placeholder="Try “biryani” or a restaurant name"
            value={term}
            onChange={(e) => {
              setTerm(e.target.value);
              setPage(1);
            }}
          />
        </label>
      </PageHead>

      <Notice onRetry={refetch}>{error}</Notice>

      {firstLoad ? (
        <Spinner label="Finding kitchens…" />
      ) : data?.items.length ? (
        <div className="venue-grid">
          {data.items.map((restaurant) => (
            <RestaurantTile key={restaurant.id} restaurant={restaurant} />
          ))}
        </div>
      ) : (
        !error && (
          <EmptyState icon="search" title="Nothing matched">
            {search ? `No kitchens found for “${search}”. Try a broader word.` : 'No restaurants have joined yet.'}
          </EmptyState>
        )
      )}

      <Pager result={data} onPage={setPage} />
    </div>
  );
}
