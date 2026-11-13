import { useEffect, useRef } from 'react';
import Icon from './Icon';

export default function Dialog({ heading, subheading, onDismiss, children }) {
  const panelRef = useRef(null);

  useEffect(() => {
    const handleKey = (event) => {
      if (event.key === 'Escape') onDismiss();
    };
    document.addEventListener('keydown', handleKey);
    document.body.classList.add('no-scroll');
    panelRef.current?.querySelector('input, textarea, select, button')?.focus();
    return () => {
      document.removeEventListener('keydown', handleKey);
      document.body.classList.remove('no-scroll');
    };
  }, [onDismiss]);

  return (
    <div className="overlay" onMouseDown={onDismiss}>
      <section
        ref={panelRef}
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-label={heading}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="dialog-head">
          <div>
            <h2>{heading}</h2>
            {subheading && <p className="subtle">{subheading}</p>}
          </div>
          <button type="button" className="icon-button" onClick={onDismiss} aria-label="Close dialog">
            <Icon name="close" />
          </button>
        </header>
        {children}
      </section>
    </div>
  );
}
