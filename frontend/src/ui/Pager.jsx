import Icon from './Icon';

/** Works with the API's { page, pages, total } envelope. */
export default function Pager({ result, onPage }) {
  if (!result || result.pages <= 1) return null;
  const { page, pages, total } = result;
  return (
    <nav className="pager" aria-label="Pages">
      <button type="button" className="btn btn-quiet btn-small" disabled={page <= 1} onClick={() => onPage(page - 1)}>
        <Icon name="arrowLeft" size={16} /> Previous
      </button>
      <span className="pager-status">
        {page} / {pages} <span className="subtle">({total} results)</span>
      </span>
      <button type="button" className="btn btn-quiet btn-small" disabled={page >= pages} onClick={() => onPage(page + 1)}>
        Next <Icon name="arrowRight" size={16} />
      </button>
    </nav>
  );
}
