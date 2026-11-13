export const DEMO_PASSWORD = 'password123';

export const DEMO_ACCOUNTS = [
  { group: 'Students', role: 'customer', people: ['customer', 'customer2'] },
  { group: 'Kitchens', role: 'restaurant_owner', people: ['owner', 'owner2', 'owner3', 'owner4'] },
  { group: 'Riders', role: 'delivery_partner', people: ['partner', 'partner2'] },
].map((section) => ({
  ...section,
  people: section.people.map((local) => ({ local, email: `${local}@campusbite.app` })),
}));
