/** Sidebar entries per role: [path, label, icon]. */
export const NAV_BY_ROLE = {
  guest: [['/restaurants', 'Explore', 'store']],
  customer: [
    ['/restaurants', 'Explore', 'store'],
    ['/orders', 'My orders', 'receipt'],
    ['/ask', 'Ask CampusBite', 'sparkle'],
  ],
  restaurant_owner: [
    ['/kitchen', 'Overview', 'grid'],
    ['/kitchen/orders', 'Order queue', 'list'],
    ['/kitchen/menu', 'Menu', 'book'],
    ['/kitchen/refunds', 'Refunds', 'undo'],
  ],
  delivery_partner: [
    ['/rides', 'Active drops', 'bike'],
    ['/rides/history', 'Past drops', 'clock'],
  ],
};

export const ROLE_TITLES = {
  customer: 'Student',
  restaurant_owner: 'Kitchen',
  delivery_partner: 'Rider',
};
