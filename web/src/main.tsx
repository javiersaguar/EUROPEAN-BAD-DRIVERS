import { StrictMode, lazy, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import '@fontsource-variable/dm-sans/wght.css'
import './styles.css'
const Audit = import.meta.env.DEV ? lazy(() => import('./Audit')) : null
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
    {Audit && new URLSearchParams(location.search).get('audit') === '1' && (
      <Suspense fallback={null}>
        <Audit />
      </Suspense>
    )}
  </StrictMode>,
)
