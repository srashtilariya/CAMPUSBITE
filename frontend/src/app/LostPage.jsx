import { Link } from 'react-router-dom';
import Icon from '../ui/Icon';

export default function LostPage() {
  return (
    <section className="lost">
      <span className="lost-code">404</span>
      <h1>This plate is empty</h1>
      <p className="lead">The page you were looking for isn’t on the menu. It may have moved, or the link is off by a letter.</p>
      <Link to="/" className="btn btn-primary">
        <Icon name="arrowLeft" /> Back to CampusBite
      </Link>
    </section>
  );
}
