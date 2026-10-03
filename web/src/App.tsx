import { useEffect, useState, useRef, type ComponentType } from 'react'
import {
  Radar,
  LayoutDashboard,
  Map,
  MapPin,
  Columns3,
  Car,
  TrendingUp,
  Globe2,
  SlidersHorizontal,
  Workflow,
  Database,
  Menu,
  X,
  Link,
  ArrowUpRight,
  RefreshCw,
} from 'lucide-react'
import { readFilters, serializeFilters, type Dataset, type Filters, type Page } from './data'
import {
  Overview,
  Territories,
  Profile,
  Compare,
  Insurance,
  Trends,
  Europe,
  Laboratory,
  Models,
  Sources,
  type PageProps,
} from './Pages'
const navigation = [
  {
    page: 'overview',
    name: 'Panorama',
    icon: LayoutDashboard,
    description: 'El contexto antes de los números.',
  },
  {
    page: 'territories',
    name: 'Territorios',
    icon: Map,
    description: 'Tasas, exposición y diferencias entre provincias.',
  },
  {
    page: 'profile',
    name: 'Ficha provincial',
    icon: MapPin,
    description: 'Una provincia, su evolución y su contexto.',
  },
  {
    page: 'compare',
    name: 'Comparar',
    icon: Columns3,
    description: 'Dos o tres territorios bajo el mismo criterio.',
  },
  {
    page: 'insurance',
    name: 'Golpes de chapa',
    icon: Car,
    description: 'Daños materiales y coberturas del seguro.',
  },
  {
    page: 'trends',
    name: 'Series históricas',
    icon: TrendingUp,
    description: 'Quince años de mortalidad vial europea.',
  },
  {
    page: 'europe',
    name: 'Europa',
    icon: Globe2,
    description: 'Una definición común, con límites de comparabilidad.',
  },
  {
    page: 'laboratory',
    name: 'Laboratorio',
    icon: SlidersHorizontal,
    description: 'Haz visibles las decisiones detrás del índice.',
  },
  {
    page: 'models',
    name: 'Modelos',
    icon: Workflow,
    description: 'Gravedad de siniestros, validación e interpretación.',
  },
  {
    page: 'sources',
    name: 'Fuentes',
    icon: Database,
    description: 'Cobertura, procedencia y trazabilidad.',
  },
] as const
const views: Record<Page, ComponentType<PageProps>> = {
  overview: Overview,
  territories: Territories,
  profile: Profile,
  compare: Compare,
  insurance: Insurance,
  trends: Trends,
  europe: Europe,
  laboratory: Laboratory,
  models: Models,
  sources: Sources,
}
export default function App() {
  const [data, setData] = useState<Dataset | null>(null),
    [error, setError] = useState(''),
    [retry, setRetry] = useState(0),
    [f, setFilters] = useState(() => readFilters(window.location.search)),
    [mobile, setMobile] = useState(false),
    [share, setShare] = useState(''),
    [compact, setCompact] = useState(() => window.matchMedia('(max-width:760px)').matches),
    main = useRef<HTMLElement>(null),
    wasMobileOpen = useRef(false),
    sidebar = useRef<HTMLElement>(null),
    closeButton = useRef<HTMLButtonElement>(null),
    menuButton = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    const controller = new AbortController()
    setError('')
    fetch(`${import.meta.env.BASE_URL}data/observatory.json`, { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw new Error('No se pudo recuperar la publicación.')
        return r.json()
      })
      .then((value: Dataset) => {
        if (value.schema_version !== 1 || value.tables.spain_metrics.length !== 156)
          throw new Error('La publicación no cumple el contrato de datos.')
        setData(value)
      })
      .catch((e) => {
        if (e.name !== 'AbortError') setError(e instanceof Error ? e.message : 'Error de conexión.')
      })
    return () => controller.abort()
  }, [retry])
  useEffect(() => {
    const onPop = () => setFilters(readFilters(window.location.search))
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])
  useEffect(() => {
    const query = window.matchMedia('(max-width:760px)')
    const onChange = () => {
      setCompact(query.matches)
      if (!query.matches) setMobile(false)
    }
    query.addEventListener('change', onChange)
    return () => query.removeEventListener('change', onChange)
  }, [])
  useEffect(() => {
    if (mobile) closeButton.current?.focus()
    else if (wasMobileOpen.current) menuButton.current?.focus()
    wasMobileOpen.current = mobile
  }, [mobile])
  useEffect(() => {
    document.title = `${navigation.find((n) => n.page === f.page)?.name} · Observatorio europeo`
  }, [f.page])
  function update(patch: Partial<Filters>) {
    const next = { ...f, ...patch }
    setFilters(next)
    window.history.pushState(null, '', `${window.location.pathname}?${serializeFilters(next)}`)
    if (patch.page) {
      setMobile(false)
      window.scrollTo({ top: 0 })
      requestAnimationFrame(() => main.current?.focus())
    }
  }
  async function shareLink() {
    try {
      const url = new URL(window.location.href)
      url.search = serializeFilters(f)
      await navigator.clipboard.writeText(url.href)
      setShare('Enlace copiado con todos los filtros.')
    } catch {
      setShare('El enlace de la barra de dirección contiene todos los filtros.')
    }
  }
  const current = navigation.find((n) => n.page === f.page)!,
    View = views[f.page]
  return (
    <>
      <a className="skip-link" href="#main">
        Saltar al contenido
      </a>
      {mobile && (
        <button
          className="nav-overlay"
          aria-label="Cerrar navegación"
          onClick={() => {
            setMobile(false)
            menuButton.current?.focus()
          }}
        />
      )}
      <aside
        ref={sidebar}
        inert={compact && !mobile}
        className={`sidebar ${mobile ? 'open' : ''}`}
        aria-label="Navegación principal"
        onKeyDown={(e) => {
          if (e.key === 'Escape') {
            setMobile(false)
            menuButton.current?.focus()
          }
          if (mobile && e.key === 'Tab') {
            const controls = sidebar.current?.querySelectorAll<HTMLElement>(
              'a[href],button:not([disabled])',
            )
            const first = controls?.[0],
              last = controls?.[controls.length - 1]
            if (e.shiftKey && document.activeElement === first) {
              e.preventDefault()
              last?.focus()
            } else if (!e.shiftKey && document.activeElement === last) {
              e.preventDefault()
              first?.focus()
            }
          }
        }}
      >
        <a
          className="brand"
          href={`?${serializeFilters({ ...f, page: 'overview' })}`}
          onClick={(e) => {
            e.preventDefault()
            update({ page: 'overview' })
          }}
        >
          <span className="brand-mark">
            <Radar size={23} />
          </span>
          <span>
            Observatorio<span>Siniestralidad vial · Europa</span>
          </span>
        </a>
        <button
          ref={closeButton}
          className="mobile-close icon-button"
          aria-label="Cerrar menú"
          onClick={() => {
            setMobile(false)
            menuButton.current?.focus()
          }}
        >
          <X size={20} />
        </button>
        <nav>
          <span className="nav-label">Explorar</span>
          {navigation.map((n, i) => (
            <div key={n.page}>
              {i === 7 && <span className="nav-label method-label">Método y evidencia</span>}
              <a
                href={`?${serializeFilters({ ...f, page: n.page })}`}
                className={f.page === n.page ? 'active' : ''}
                aria-current={f.page === n.page ? 'page' : undefined}
                onClick={(e) => {
                  if (!e.ctrlKey && !e.metaKey && !e.shiftKey) {
                    e.preventDefault()
                    update({ page: n.page })
                  }
                }}
              >
                <n.icon size={18} />
                {n.name}
              </a>
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>
            Publicación verificada<strong>2022–2024 · España / UE</strong>
          </span>
          <a
            href="https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS"
            target="_blank"
            rel="noreferrer"
            aria-label="Abrir repositorio GitHub"
          >
            <ArrowUpRight size={15} />
          </a>
        </div>
      </aside>
      <div inert={mobile} className="workspace">
        <header className="topbar">
          <button
            ref={menuButton}
            className="mobile-menu icon-button"
            aria-label="Abrir navegación"
            aria-expanded={mobile}
            onClick={() => setMobile(!mobile)}
          >
            <Menu size={22} />
          </button>
          <span className="breadcrumb">
            Observatorio <span>/</span> {current.name}
          </span>
          <div>
            <span className="release">v{data?.release ?? '0.2.0'}</span>
            <span className="status-dot" />
            <span className="topbar-status">Datos verificados</span>
          </div>
        </header>
        <main ref={main} id="main" tabIndex={-1}>
          <div className="page-heading">
            <div>
              <span className="eyebrow">EVIDENCIA PARA ENTENDER LA MOVILIDAD</span>
              <h1>{current.name}</h1>
              <p>{current.description}</p>
            </div>
            <div className="page-actions">
              {!['insurance', 'trends', 'models', 'sources'].includes(f.page) && (
                <label>
                  Año
                  <select value={f.year} onChange={(e) => update({ year: Number(e.target.value) })}>
                    {[2024, 2023, 2022].map((y) => (
                      <option key={y}>{y}</option>
                    ))}
                  </select>
                </label>
              )}
              <button className="button" onClick={() => void shareLink()}>
                <Link size={14} />
                Compartir
              </button>
            </div>
          </div>
          <span className="share-status" role="status">
            {share}
          </span>
          {error ? (
            <div className="panel error" role="alert">
              <h2>La publicación no está disponible</h2>
              <p>{error}</p>
              <button className="button" onClick={() => setRetry(retry + 1)}>
                <RefreshCw size={15} />
                Reintentar
              </button>
            </div>
          ) : data ? (
            <View data={data} f={f} update={update} />
          ) : (
            <div className="loading" role="status">
              <div className="skeleton" />
              <p>Cargando la publicación verificada…</p>
            </div>
          )}
          <footer className="page-footer">
            <span>Observatorio europeo de siniestralidad vial</span>
            <span>
              Javier Saguar · v{data?.release ?? '0.2.0'} ·{' '}
              <a
                href={`?${serializeFilters({ ...f, page: 'sources' })}`}
                onClick={(e) => {
                  e.preventDefault()
                  update({ page: 'sources' })
                }}
              >
                Fuentes y metodología
              </a>
            </span>
          </footer>
        </main>
      </div>
    </>
  )
}
