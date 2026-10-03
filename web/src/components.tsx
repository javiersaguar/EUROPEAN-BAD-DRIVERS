import { useRef, useState, type ReactNode } from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { Download, ChevronDown, ArrowUpRight } from 'lucide-react'
import { fmt, number, chartColors, type Row, type Dataset, type Filters } from './data'

export function Panel({
  title,
  subtitle,
  children,
  action,
  className = '',
}: {
  title: string
  subtitle?: string
  children: ReactNode
  action?: ReactNode
  className?: string
}) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-heading">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </section>
  )
}
export function Stat({
  label: caption,
  value,
  unit,
  detail,
}: {
  label: string
  value: string
  unit?: string
  detail?: string
}) {
  return (
    <article className="stat">
      <span>{caption}</span>
      <strong>{value}</strong>
      {unit && <span className="unit">{unit}</span>}
      {detail && <p>{detail}</p>}
    </article>
  )
}
export function Note({ children }: { children: ReactNode }) {
  return <p className="note">{children}</p>
}
export function SourceNote({
  data,
  ids,
  scope,
  year,
}: {
  data: Dataset
  ids: string[]
  scope: string
  year: string | number
}) {
  const sources = data.sources.filter((s) => ids.includes(s.id))
  return (
    <div className="source-note">
      <span className="source-label">Cobertura</span>
      <span>
        {year} · {scope}
      </span>
      <span className="source-links">
        {sources.map((s) => (
          <a key={s.id} href={s.page_url || s.url} target="_blank" rel="noreferrer">
            {s.organization}
            <ArrowUpRight size={12} />
          </a>
        ))}
      </span>
      <span>Verificado {data.audit_date.split('-').reverse().join('/')}</span>
    </div>
  )
}
export type Column = {
  key: string
  title: string
  digits?: number
  render?: (row: Row) => ReactNode
}
export function DataTable({
  rows,
  columns,
  caption,
  limit = 12,
}: {
  rows: Row[]
  columns: Column[]
  caption: string
  limit?: number
}) {
  const [expanded, setExpanded] = useState(false)
  const visible = expanded ? rows : rows.slice(0, limit)
  return (
    <>
      <div className="table-scroll" tabIndex={0} role="region" aria-label={caption}>
        <table>
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c.key} scope="col">
                  {c.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visible.map((r, i) => (
              <tr key={`${r.province_code ?? r.geo ?? r.municipality ?? i}-${i}`}>
                {columns.map((c) => (
                  <td key={c.key}>
                    {c.render
                      ? c.render(r)
                      : c.key === 'year'
                        ? String(r[c.key])
                        : typeof r[c.key] === 'number'
                          ? fmt(number(r, c.key), c.digits ?? 0)
                          : r[c.key] == null || r[c.key] === ''
                            ? '—'
                            : String(r[c.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {!rows.length && <p className="empty">No hay datos para esta selección.</p>}
      </div>
      {rows.length > limit && (
        <button className="text-button table-toggle" onClick={() => setExpanded(!expanded)}>
          {expanded ? 'Mostrar menos' : `Ver las ${fmt(rows.length)} filas`}
          <ChevronDown size={14} />
        </button>
      )}
    </>
  )
}
const tooltipStyle = {
  borderRadius: 8,
  border: '1px solid #ced7cf',
  color: '#263b32',
  background: '#fffef8',
  fontSize: 12,
}
export function Bars({
  rows,
  valueKey,
  nameKey = 'province',
  title,
  horizontal = false,
}: {
  rows: Row[]
  valueKey: string
  nameKey?: string
  title: string
  horizontal?: boolean
}) {
  return (
    <div className="chart" role="img" aria-label={title}>
      <ResponsiveContainer width="100%" height={horizontal ? Math.max(260, rows.length * 28) : 260}>
        <BarChart
          data={rows}
          layout={horizontal ? 'vertical' : 'horizontal'}
          margin={{ left: horizontal ? 12 : 0, right: 20, top: 12, bottom: 5 }}
          accessibilityLayer
        >
          <CartesianGrid stroke="#e5e9df" horizontal={!horizontal} vertical={horizontal} />
          {horizontal ? (
            <>
              <XAxis type="number" tickFormatter={(v) => fmt(v)} fontSize={11} />
              <YAxis
                dataKey={nameKey}
                type="category"
                width={105}
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />
            </>
          ) : (
            <>
              <XAxis dataKey={nameKey} fontSize={11} tickLine={false} />
              <YAxis fontSize={11} tickFormatter={(v) => fmt(v)} />
            </>
          )}
          <Tooltip formatter={(v) => fmt(Number(v), 2)} contentStyle={tooltipStyle} />
          <Bar
            dataKey={valueKey}
            name={title}
            fill={chartColors[0]}
            radius={horizontal ? [0, 3, 3, 0] : [3, 3, 0, 0]}
            isAnimationActive={false}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
export function Lines({
  rows,
  series,
  xKey = 'year',
  title,
  domain,
  numericX = false,
}: {
  rows: Row[]
  series: { key: string; name: string }[]
  xKey?: string
  title: string
  domain?: [number, number]
  numericX?: boolean
}) {
  return (
    <div className="chart" role="img" aria-label={title}>
      <ResponsiveContainer width="100%" height={270}>
        <LineChart
          data={rows}
          margin={{ top: 12, right: 18, left: 0, bottom: 5 }}
          accessibilityLayer
        >
          <CartesianGrid stroke="#e5e9df" vertical={false} />
          <XAxis
            dataKey={xKey}
            fontSize={11}
            tickLine={false}
            type={numericX ? 'number' : 'category'}
            domain={numericX && domain ? domain : undefined}
            tickFormatter={numericX ? (v) => fmt(Number(v), domain ? 1 : 0) : undefined}
          />
          <YAxis domain={domain} fontSize={11} tickFormatter={(v) => fmt(v, 1)} />
          <Tooltip formatter={(v) => fmt(Number(v), 2)} contentStyle={tooltipStyle} />
          {series.map((s, i) => (
            <Line
              key={s.key}
              dataKey={s.key}
              name={s.name}
              stroke={chartColors[i % 3]}
              strokeWidth={2}
              dot={{ r: 3 }}
              connectNulls={false}
              isAnimationActive={false}
            />
          ))}
          {domain && (
            <ReferenceLine
              segment={[
                { x: 0, y: 0 },
                { x: 1, y: 1 },
              ]}
              stroke="#899b91"
              strokeDasharray="4 4"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      <div className="legend">
        {series.map((s, i) => (
          <span key={s.key}>
            <i style={{ background: chartColors[i % 3] }} />
            {s.name}
          </span>
        ))}
      </div>
    </div>
  )
}

function save(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob),
    a = document.createElement('a')
  a.href = url
  a.download = name
  a.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
export function csvText(rows: Row[], metadata: string[]): string {
  const quote = (v: unknown) => `"${String(v ?? '').replaceAll('"', '""')}"`
  const keys = Object.keys(rows[0] ?? {})
  return (
    '\uFEFF' +
    metadata.map((s) => `# ${s}`).join('\r\n') +
    '\r\n' +
    [
      keys.map(quote).join(','),
      ...rows.map((r) =>
        keys
          .map((k) =>
            quote(typeof r[k] === 'string' && /^[=+@-]/.test(r[k] as string) ? `'${r[k]}` : r[k]),
          )
          .join(','),
      ),
    ].join('\r\n')
  )
}
async function exportSvg(svg: SVGSVGElement, metadata: string[]): Promise<string> {
  const clone = svg.cloneNode(true) as SVGSVGElement
  const originals = [svg, ...svg.querySelectorAll('*')],
    copies = [clone, ...clone.querySelectorAll('*')]
  originals.forEach((el, i) => {
    const style = getComputedStyle(el)
    ;['fill', 'stroke', 'font-family', 'font-size', 'color', 'opacity', 'background-color'].forEach(
      (k) => (copies[i] as SVGElement).style.setProperty(k, style.getPropertyValue(k)),
    )
  })
  const box = svg.getBoundingClientRect()
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  clone.setAttribute('width', String(box.width))
  clone.setAttribute('height', String(box.height + 52))
  clone.setAttribute('viewBox', `0 0 ${box.width} ${box.height + 52}`)
  // Preserve a map's existing coordinate system instead of flattening its projection.
  if (svg.hasAttribute('viewBox')) {
    clone.setAttribute('viewBox', svg.getAttribute('viewBox')!)
    const meta = document.createElementNS('http://www.w3.org/2000/svg', 'metadata')
    meta.textContent = metadata.join('\n')
    clone.prepend(meta)
  } else {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text')
    text.setAttribute('x', '12')
    text.setAttribute('y', String(box.height + 20))
    text.setAttribute('font-size', '10')
    text.setAttribute('fill', '#263b32')
    text.textContent = metadata.slice(0, 2).join(' · ')
    clone.append(text)
  }
  return new XMLSerializer().serializeToString(clone)
}
export function Export({
  rows,
  title,
  metadata,
  chartId,
}: {
  rows: Row[]
  title: string
  metadata: string[]
  chartId?: string
}) {
  const [busy, setBusy] = useState(false),
    [status, setStatus] = useState(''),
    [failed, setFailed] = useState(false)
  const menu = useRef<HTMLDetailsElement>(null)
  async function run(format: 'csv' | 'svg' | 'png' | 'pdf') {
    setBusy(true)
    setStatus(`Preparando ${format.toUpperCase()}…`)
    setFailed(false)
    try {
      const name = title
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/[^a-z0-9]+/g, '-')
      if (format === 'csv')
        save(new Blob([csvText(rows, metadata)], { type: 'text/csv;charset=utf-8' }), `${name}.csv`)
      else if (format === 'pdf') {
        const { jsPDF } = await import('jspdf')
        const doc = new jsPDF()
        doc.setProperties({ author: 'Javier Saguar', title, subject: metadata.join(' · ') })
        doc.setFont('helvetica', 'bold')
        doc.setFontSize(17)
        doc.text('Observatorio europeo', 14, 20)
        doc.setFontSize(12)
        doc.text(title, 14, 30)
        doc.setFont('helvetica', 'normal')
        doc.setFontSize(9)
        let y = 40
        const add = (text: string) => {
          for (const line of doc.splitTextToSize(text, 180) as string[]) {
            if (y > 280) {
              doc.addPage()
              y = 20
            }
            doc.text(line, 14, y)
            y += 5
          }
        }
        metadata.forEach(add)
        y += 5
        rows.forEach((r, i) => {
          add(
            `${i + 1}. ${Object.entries(r)
              .map(([k, v]) => `${k}: ${typeof v === 'number' ? fmt(v, 2) : (v ?? 'Sin dato')}`)
              .join(' | ')}`,
          )
          y += 2
        })
        doc.save(`${name}.pdf`)
      } else {
        const svg = document.getElementById(chartId ?? '')?.querySelector('svg')
        if (!svg) throw new Error('Esta vista no contiene un gráfico exportable.')
        const xml = await exportSvg(svg as SVGSVGElement, metadata)
        if (format === 'svg') save(new Blob([xml], { type: 'image/svg+xml' }), `${name}.svg`)
        else {
          const url = URL.createObjectURL(new Blob([xml], { type: 'image/svg+xml' }))
          try {
            const img = new Image()
            await new Promise<void>((resolve, reject) => {
              img.onload = () => resolve()
              img.onerror = () => reject(new Error('No se pudo renderizar la imagen.'))
              img.src = url
            })
            const canvas = document.createElement('canvas')
            canvas.width = img.width * 2
            canvas.height = img.height * 2 + 100
            const ctx = canvas.getContext('2d')!
            ctx.fillStyle = '#fffef8'
            ctx.fillRect(0, 0, canvas.width, canvas.height)
            ctx.drawImage(img, 0, 0, img.width * 2, img.height * 2)
            ctx.fillStyle = '#263b32'
            ctx.font = '20px Arial'
            metadata
              .slice(0, 3)
              .forEach((s, i) => ctx.fillText(s, 20, img.height * 2 + 24 + i * 24))
            const blob = await new Promise<Blob | null>((r) => canvas.toBlob(r, 'image/png'))
            if (blob) save(blob, `${name}.png`)
          } finally {
            URL.revokeObjectURL(url)
          }
        }
      }
      setStatus(`Archivo ${format.toUpperCase()} preparado.`)
      if (menu.current) menu.current.open = false
    } catch (error) {
      setFailed(true)
      setStatus(error instanceof Error ? error.message : 'Error al exportar.')
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="export">
      <details ref={menu}>
        <summary className="button">
          <Download size={15} />
          Exportar
          <ChevronDown size={12} />
        </summary>
        <div className="export-menu">
          {(
            ['csv', 'pdf', ...(chartId ? ['svg', 'png'] : [])] as ('csv' | 'pdf' | 'svg' | 'png')[]
          ).map((f) => (
            <button key={f} disabled={busy} onClick={() => void run(f)}>
              {f.toUpperCase()} ·{' '}
              {f === 'pdf' ? 'Informe' : f === 'csv' ? 'Datos filtrados' : 'Gráfico'}
            </button>
          ))}
        </div>
      </details>
      <span className="sr-only" role="status">
        {status}
      </span>
      {failed && <p role="alert">{status}</p>}
    </div>
  )
}
export function metadata(data: Dataset, filters: Filters, scope: string) {
  const ids = /UNESPA/i.test(scope)
    ? ['unespa_motor_2024']
    : /Eurostat/i.test(scope)
      ? ['eurostat_fatalities_history', 'eurostat_population_history']
      : /RCE/i.test(scope)
        ? ['transport_rce_2022', 'dgt_accidents_2022']
        : [
            `dgt_accidents_${filters.year}`,
            'ine_population_67988',
            `dgt_vehicles_${filters.year}`,
            `dgt_drivers_${filters.year}`,
          ]
  return [
    'Observatorio europeo de siniestralidad vial',
    `Versión ${data.release} · corte verificado ${data.audit_date}`,
    scope,
    ...data.sources
      .filter((s) => ids.includes(s.id))
      .map((s) => `Fuente: ${s.organization} · ${s.page_url || s.url}`),
    `Filtros: ${JSON.stringify(filters)}`,
    'Fuentes y unidades: consulte Fuentes en la aplicación; no es una probabilidad individual.',
  ]
}
export function ValueTable({
  rows,
  keyName,
  nameKey = 'province',
  caption,
}: {
  rows: Row[]
  keyName: string
  nameKey?: string
  caption: string
}) {
  return (
    <DataTable
      rows={rows}
      caption={caption}
      columns={[
        { key: nameKey, title: nameKey === 'year' ? 'Año' : 'Territorio' },
        { key: keyName, title: caption, digits: 2 },
      ]}
    />
  )
}
