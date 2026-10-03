import { useEffect, useState } from 'react'
import { fmt, number, type Row } from './data'
type Feature = {
  properties: { province_code: string; province: string }
  geometry: { type: string; coordinates: number[][][][] }
}
type Geometry = { features: Feature[] }
const colors = ['#e1e9d9', '#b9ceb5', '#8aad94', '#598371', '#355e50']
export function ProvinceMap({
  rows,
  metric,
  onSelect,
  selected,
}: {
  rows: Row[]
  metric: string
  onSelect: (code: string) => void
  selected?: string
}) {
  const [geometry, setGeometry] = useState<Geometry | null>(null),
    [hover, setHover] = useState<Row | null>(null),
    [error, setError] = useState(false)
  useEffect(() => {
    const controller = new AbortController()
    fetch(`${import.meta.env.BASE_URL}data/spain.geojson`, { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw new Error()
        return r.json()
      })
      .then(setGeometry)
      .catch((e) => {
        if (e.name !== 'AbortError') setError(true)
      })
    return () => controller.abort()
  }, [])
  const values = rows.map((r) => number(r, metric)).filter((v): v is number => v != null),
    min = Math.min(...values),
    max = Math.max(...values)
  const project = (point: number[], island: boolean) =>
    island
      ? [(point[0] + 18.3) * 25 + 40, (29.8 - point[1]) * 32 + 345]
      : [(point[0] + 9.6) * 32 + 90, (44 - point[1]) * 40 + 30]
  function path(f: Feature) {
    const island = ['35', '38'].includes(f.properties.province_code),
      polygons =
        f.geometry.type === 'Polygon'
          ? [f.geometry.coordinates as unknown as number[][][]]
          : f.geometry.coordinates
    return polygons
      .map((poly) =>
        poly
          .map(
            (ring) =>
              ring
                .map((pt, i) => {
                  const [x, y] = project(pt, island)
                  return `${i ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)}`
                })
                .join(' ') + 'Z',
          )
          .join(' '),
      )
      .join(' ')
  }
  if (error)
    return (
      <p role="alert">No se pudo cargar el mapa. Los mismos datos están disponibles en la tabla.</p>
    )
  return (
    <div className="map">
      <svg
        viewBox="0 0 570 440"
        role="group"
        aria-label="Mapa de provincias. Selecciona una provincia para abrir su ficha."
      >
        <defs>
          <pattern id="no-data" patternUnits="userSpaceOnUse" width="6" height="6">
            <rect width="6" height="6" fill="#eee" />
            <path d="M0,6L6,0" stroke="#a1aba4" />
          </pattern>
        </defs>
        <rect x="29" y="330" width="165" height="83" fill="none" stroke="#cdd5c9" rx="6" />
        <text x="40" y="347" fontSize="10" fill="#54685b">
          CANARIAS · escala independiente
        </text>
        {geometry?.features.map((f) => {
          const row = rows.find((r) => r.province_code === f.properties.province_code),
            value = row ? number(row, metric) : null,
            color =
              value == null
                ? 'url(#no-data)'
                : colors[Math.min(4, Math.floor(((value - min) / (max - min || 1)) * 5))]
          return (
            <path
              key={f.properties.province_code}
              d={path(f)}
              fill={color}
              fillRule="evenodd"
              stroke={selected === f.properties.province_code ? '#a76026' : '#fffef8'}
              strokeWidth={selected === f.properties.province_code ? 2.5 : 1}
              tabIndex={0}
              role="button"
              aria-label={`${f.properties.province}: ${fmt(value, 2)}. Abrir ficha.`}
              onClick={() => onSelect(f.properties.province_code)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  onSelect(f.properties.province_code)
                }
              }}
              onMouseEnter={() => setHover(row ?? null)}
              onFocus={() => setHover(row ?? null)}
            >
              <title>
                {f.properties.province}: {fmt(value, 2)}
              </title>
            </path>
          )
        })}
        <text x="220" y="425" fontSize="10" fill="#54685b">
          Geometría derivada · © EuroGeographics / GISCO
        </text>
      </svg>
      <div className="map-readout" aria-live="polite">
        {hover ? (
          <>
            <strong>{hover.province}</strong>
            <span>{fmt(number(hover, metric), 2)}</span>
          </>
        ) : (
          <>
            <strong>Explora una provincia</strong>
            <span>Haz clic para abrir su ficha</span>
          </>
        )}
      </div>
      <div className="map-legend">
        <span>{fmt(min, 1)}</span>
        {colors.map((c) => (
          <i key={c} style={{ background: c }} />
        ))}
        <span>{fmt(max, 1)}</span>
        <span className="muted">Mayor tasa →</span>
      </div>
      <div className="map-cities">
        {rows
          .filter((r) => ['51', '52'].includes(String(r.province_code)))
          .map((r) => (
            <button
              key={String(r.province_code)}
              className="text-button"
              onClick={() => onSelect(String(r.province_code))}
            >
              {r.province} · {fmt(number(r, metric), 2)}
            </button>
          ))}
      </div>
    </div>
  )
}
