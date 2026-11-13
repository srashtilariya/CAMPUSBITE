import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './app/AppRoutes';
import { BasketProvider } from './state/BasketProvider';
import { SessionProvider } from './state/SessionProvider';
import './styles/tokens.css';
import './styles/base.css';
import './styles/shell.css';
import './styles/controls.css';
import './styles/features.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <SessionProvider>
        <BasketProvider>
          <AppRoutes />
        </BasketProvider>
      </SessionProvider>
    </BrowserRouter>
  </StrictMode>,
);
