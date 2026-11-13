import { Route, Routes } from 'react-router-dom';
import SignIn from '../features/auth/SignIn';
import SignUp from '../features/auth/SignUp';
import RestaurantDirectory from '../features/browse/RestaurantDirectory';
import RestaurantPage from '../features/browse/RestaurantPage';
import AskCampusBite from '../features/customer/AskCampusBite';
import BasketCheckout from '../features/customer/BasketCheckout';
import MyOrders from '../features/customer/MyOrders';
import OrderView from '../features/customer/OrderView';
import CourierBoard from '../features/courier/CourierBoard';
import CourierLog from '../features/courier/CourierLog';
import KitchenOverview from '../features/owner/KitchenOverview';
import MenuEditor from '../features/owner/MenuEditor';
import OrderQueue from '../features/owner/OrderQueue';
import RefundDesk from '../features/owner/RefundDesk';
import { GuestOnly, RequireRole, StartRedirect } from './guards';
import LostPage from './LostPage';
import Shell from './Shell';

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<GuestOnly />}>
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
      </Route>

      <Route element={<Shell />}>
        <Route index element={<StartRedirect />} />
        <Route path="restaurants" element={<RestaurantDirectory />} />
        <Route path="restaurants/:restaurantId" element={<RestaurantPage />} />

        <Route element={<RequireRole allow={['customer']} />}>
          <Route path="basket" element={<BasketCheckout />} />
          <Route path="orders" element={<MyOrders />} />
          <Route path="ask" element={<AskCampusBite />} />
        </Route>

        {/* Any signed-in role may open an order it is involved in; the API enforces access. */}
        <Route element={<RequireRole />}>
          <Route path="orders/:orderId" element={<OrderView />} />
        </Route>

        <Route path="kitchen" element={<RequireRole allow={['restaurant_owner']} />}>
          <Route index element={<KitchenOverview />} />
          <Route path="orders" element={<OrderQueue />} />
          <Route path="menu" element={<MenuEditor />} />
          <Route path="refunds" element={<RefundDesk />} />
        </Route>

        <Route path="rides" element={<RequireRole allow={['delivery_partner']} />}>
          <Route index element={<CourierBoard />} />
          <Route path="history" element={<CourierLog />} />
        </Route>

        <Route path="*" element={<LostPage />} />
      </Route>
    </Routes>
  );
}
