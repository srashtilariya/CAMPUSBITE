// A handful of stroke icons drawn on a 24px grid (Feather-style).
const PATHS = {
  store: 'M3 9l1.5-5h15L21 9M3 9h18M3 9v1a3 3 0 006 0 3 3 0 006 0 3 3 0 006 0V9M5 13v7h14v-7',
  receipt: 'M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6M9 16h3',
  sparkle: 'M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM19 17l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7z',
  bag: 'M5 8h14l-1 13H6zM9 8V6a3 3 0 016 0v2',
  grid: 'M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z',
  list: 'M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01',
  book: 'M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2zM4 5v16',
  undo: 'M9 14L4 9l5-5M4 9h11a5 5 0 010 10h-3',
  bike: 'M5 18a3 3 0 100-6 3 3 0 000 6zM19 18a3 3 0 100-6 3 3 0 000 6zM5 15l4-7h5l3 7M9 8l3 7h2M14 5h3',
  clock: 'M12 21a9 9 0 100-18 9 9 0 000 18zM12 7v5l3 2',
  logout: 'M15 4h4v16h-4M10 8l-4 4 4 4M6 12h10',
  login: 'M9 4H5v16h4M14 8l4 4-4 4M18 12H8',
  menu: 'M4 7h16M4 12h16M4 17h16',
  close: 'M6 6l12 12M18 6L6 18',
  search: 'M11 18a7 7 0 100-14 7 7 0 000 14zM20 20l-4-4',
  star: 'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z',
  refresh: 'M20 11a8 8 0 10-2.3 5.7M20 4v7h-7',
  plus: 'M12 5v14M5 12h14',
  minus: 'M5 12h14',
  arrowLeft: 'M19 12H5M11 6l-6 6 6 6',
  arrowRight: 'M5 12h14M13 6l6 6-6 6',
  check: 'M5 12l5 5L20 7',
  bell: 'M6 16V11a6 6 0 0112 0v5l2 2H4zM10 21h4',
  pin: 'M12 21s7-6.2 7-12a7 7 0 00-14 0c0 5.8 7 12 7 12zM12 11a2 2 0 100-4 2 2 0 000 4z',
  phone: 'M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z',
  card: 'M3 6h18v12H3zM3 10h18M7 15h3',
  trash: 'M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3',
  edit: 'M4 20h4L19 9l-4-4L4 16zM13 7l4 4',
};

export default function Icon({ name, size = 18, className = '', ...rest }) {
  const d = PATHS[name];
  if (!d) return null;
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className={`icon ${className}`}
      {...rest}
    >
      <path d={d} />
    </svg>
  );
}
