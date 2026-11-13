import Icon from '../../ui/Icon';

const SORTS = [
  ['name', 'A → Z'],
  ['price_asc', 'Cheapest first'],
  ['price_desc', 'Priciest first'],
];

export default function MenuFilters({ value, onChange }) {
  const patch = (changes) => onChange({ ...value, ...changes });

  return (
    <div className="menu-filters">
      <label className="searchbox">
        <Icon name="search" />
        <input
          type="search"
          placeholder="Search this menu"
          value={value.search}
          onChange={(e) => patch({ search: e.target.value })}
        />
      </label>
      <div className="price-range">
        <span className="subtle">Budget</span>
        <input
          type="number"
          min="0"
          inputMode="decimal"
          placeholder="₹ min"
          aria-label="Minimum price"
          value={value.min_price}
          onChange={(e) => patch({ min_price: e.target.value })}
        />
        <span aria-hidden="true">–</span>
        <input
          type="number"
          min="0"
          inputMode="decimal"
          placeholder="₹ max"
          aria-label="Maximum price"
          value={value.max_price}
          onChange={(e) => patch({ max_price: e.target.value })}
        />
      </div>
      <select aria-label="Sort dishes" value={value.sort} onChange={(e) => patch({ sort: e.target.value })}>
        {SORTS.map(([key, text]) => (
          <option key={key} value={key}>
            {text}
          </option>
        ))}
      </select>
      <label className="toggle">
        <input
          type="checkbox"
          checked={value.available_only}
          onChange={(e) => patch({ available_only: e.target.checked })}
        />
        <span className="toggle-track" />
        In stock only
      </label>
    </div>
  );
}
