import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { formatPrice, plural } from '../../lib/format';
import { placeOrder } from '../../services/orders';
import { describeError } from '../../services/http';
import { useBasket } from '../../state/BasketProvider';
import { useSession } from '../../state/SessionProvider';
import EmptyState from '../../ui/EmptyState';
import Icon from '../../ui/Icon';
import Notice from '../../ui/Notice';
import PageHead from '../../ui/PageHead';

const TEST_CARD = '4242 4242 4242 4242';

function QuantityStepper({ value, onChange, label }) {
  return (
    <div className="stepper" aria-label={`Quantity of ${label}`}>
      <button type="button" onClick={() => onChange(value - 1)} aria-label="One less">
        <Icon name="minus" size={14} />
      </button>
      <output>{value}</output>
      <button type="button" onClick={() => onChange(value + 1)} aria-label="One more">
        <Icon name="plus" size={14} />
      </button>
    </div>
  );
}

export default function BasketCheckout() {
  const { user } = useSession();
  const basket = useBasket();
  const navigate = useNavigate();
  const [address, setAddress] = useState(user?.address ?? '');
  const [note, setNote] = useState('');
  const [cardNumber, setCardNumber] = useState(TEST_CARD);
  const [cardHolder, setCardHolder] = useState(user?.name ?? '');
  const [submitting, setSubmitting] = useState(false);
  const [problem, setProblem] = useState('');

  if (basket.isEmpty) {
    return (
      <div className="page">
        <EmptyState icon="bag" title="Your basket is waiting">
          <p>Add a few dishes from any campus kitchen and they’ll show up here.</p>
          <Link to="/restaurants" className="btn btn-primary">
            Browse kitchens
          </Link>
        </EmptyState>
      </div>
    );
  }

  const pay = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setProblem('');
    try {
      const order = await placeOrder({
        restaurant_id: basket.restaurant.id,
        items: basket.lines.map(({ id, quantity }) => ({ menu_item_id: id, quantity })),
        delivery_address: address,
        notes: note || null,
        payment_method: 'dummy_card',
      });
      basket.empty();
      navigate(`/orders/${order.id}`, { state: { fresh: true } });
    } catch (err) {
      setProblem(describeError(err, 'The order didn’t go through.'));
      setSubmitting(false);
    }
  };

  return (
    <div className="page">
      <PageHead
        eyebrow="Checkout"
        title="Your basket"
        lead={
          <>
            {plural(basket.itemCount, 'item')} from{' '}
            <Link to={`/restaurants/${basket.restaurant.id}`}>{basket.restaurant.name}</Link>
          </>
        }
      />

      <div className="split">
        <section className="panel">
          <ul className="basket-lines">
            {basket.lines.map((line) => (
              <li key={line.id}>
                <div className="basket-line-name">
                  <strong>{line.name}</strong>
                  <span className="subtle">{formatPrice(line.price)} each</span>
                </div>
                <QuantityStepper
                  value={line.quantity}
                  label={line.name}
                  onChange={(qty) => basket.setQuantity(line.id, qty)}
                />
                <span className="basket-line-total">{formatPrice(line.price * line.quantity)}</span>
                <button
                  type="button"
                  className="icon-button"
                  aria-label={`Remove ${line.name}`}
                  onClick={() => basket.dropLine(line.id)}
                >
                  <Icon name="trash" size={16} />
                </button>
              </li>
            ))}
          </ul>
          <div className="sum-row">
            <span>To pay</span>
            <strong>{formatPrice(basket.subtotal)}</strong>
          </div>
          <button type="button" className="link-button" onClick={basket.empty}>
            Empty basket
          </button>
        </section>

        <form className="panel stack" onSubmit={pay}>
          <h2 className="panel-title">Delivery & payment</h2>
          <Notice>{problem}</Notice>
          <label className="field">
            <span>Deliver to</span>
            <input
              required
              minLength={3}
              placeholder="Hostel, block, room…"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
            />
          </label>
          <label className="field">
            <span>Note for the kitchen <em>(optional)</em></span>
            <textarea
              rows={2}
              placeholder="Extra napkins, go easy on the chilli…"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </label>

          <div className="mock-card">
            <div className="mock-card-head">
              <Icon name="card" />
              <strong>Test card</strong>
              <span className="tag">Simulated</span>
            </div>
            <p className="subtle">Nothing is charged. Any number works — this just mimics a real checkout.</p>
            <label className="field">
              <span>Card number</span>
              <input inputMode="numeric" value={cardNumber} onChange={(e) => setCardNumber(e.target.value)} />
            </label>
            <label className="field">
              <span>Cardholder</span>
              <input value={cardHolder} onChange={(e) => setCardHolder(e.target.value)} />
            </label>
          </div>

          <button className="btn btn-primary btn-block btn-large" disabled={submitting}>
            {submitting ? 'Confirming payment…' : `Pay ${formatPrice(basket.subtotal)}`}
          </button>
        </form>
      </div>
    </div>
  );
}
