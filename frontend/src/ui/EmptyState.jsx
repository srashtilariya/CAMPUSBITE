import Icon from './Icon';

export default function EmptyState({ icon = 'bag', title, children }) {
  return (
    <div className="empty-state">
      <span className="empty-icon">
        <Icon name={icon} size={26} />
      </span>
      <h3>{title}</h3>
      {children && <div className="subtle">{children}</div>}
    </div>
  );
}
