export default function PageHead({ eyebrow, title, lead, children }) {
  return (
    <header className="page-head">
      <div>
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h1>{title}</h1>
        {lead && <p className="lead">{lead}</p>}
      </div>
      {children && <div className="page-head-actions">{children}</div>}
    </header>
  );
}
