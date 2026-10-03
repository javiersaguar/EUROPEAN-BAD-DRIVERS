import type { ReactNode } from 'react'
import { fmt, number, total, type Row } from '../data'
import {
  Bars,
  Lines,
  GroupedBars,
  Panel,
  DataTable,
  Export,
  SourceNote,
  type Column,
} from '../components'
import type { PageProps } from './shared'

export const sexes: Record<string, string> = {
  T: 'Todos los sexos',
  M: 'Hombres',
  F: 'Mujeres',
  UNK: 'Sexo desconocido',
}
export const ages = ['0–17', '18–24', '25–44', '45–64', '65+', 'Desconocida']
export function group(rows: Row[], dimension: string, measure: string): Row[] {
  return [...new Set(rows.map((r) => String(r[dimension])))].map((name) => ({
    [dimension]: name,
    [measure]: total(
      rows.filter((r) => String(r[dimension]) === name),
      measure,
    ),
  }))
}
export function change(current: number | null, previous: number | null): string {
  return current == null || previous == null || previous <= 0
    ? 'Sin comparación disponible'
    : `${fmt((current / previous - 1) * 100, 1)} % frente a 2019`
}
export function Select({
  title,
  value,
  options,
  onChange,
}: {
  title: string
  value: string | number
  options: string[] | Record<string, string>
  onChange: (value: string) => void
}) {
  const pairs = Array.isArray(options) ? options.map((v) => [v, v]) : Object.entries(options)
  return (
    <label>
      {title}
      <select aria-label={title} value={value} onChange={(e) => onChange(e.target.value)}>
        {pairs.map(([k, v]) => (
          <option key={k} value={k}>
            {v}
          </option>
        ))}
      </select>
    </label>
  )
}
export function Evidence({
  data,
  f,
  id,
  title,
  unit,
  rows,
  xKey,
  valueKey,
  series,
  sources,
  interpretation,
  columns,
  scopeYear,
  horizontal = false,
  grouped = false,
}: Pick<PageProps, 'data' | 'f'> & {
  id: string
  title: string
  unit: string
  rows: Row[]
  xKey: string
  valueKey?: string
  series?: { key: string; name: string }[]
  sources: string[]
  interpretation: ReactNode
  columns?: Column[]
  scopeYear?: number
  horizontal?: boolean
  grouped?: boolean
}) {
  const fields = series ?? [{ key: valueKey!, name: unit }]
  const meta = [
    `Observatorio europeo · Javier Saguar · v${data.release}`,
    `Corte ${data.audit_date} · ${title}`,
    unit,
    `Filtros: ${JSON.stringify(f)}`,
    ...data.sources
      .filter((s) => sources.includes(s.id))
      .map((s) => `Fuente: ${s.organization} · ${s.page_url || s.url}`),
    'Datos ausentes no equivalen a cero. Consulte interpretación y cobertura en la aplicación.',
  ]
  return (
    <Panel
      title={title}
      subtitle={unit}
      action={<Export rows={rows} title={title} metadata={meta} chartId={id} />}
    >
      <div id={id}>
        {series ? (
          grouped ? (
            <GroupedBars rows={rows} xKey={xKey} series={series} title={unit} />
          ) : (
            <Lines rows={rows} xKey={xKey} series={series} title={unit} />
          )
        ) : (
          <Bars
            rows={rows}
            nameKey={xKey}
            valueKey={valueKey!}
            title={unit}
            horizontal={horizontal}
          />
        )}
      </div>
      <div className="evidence-reading">
        <span className="eyebrow">Lectura del gráfico</span>
        <p>{interpretation}</p>
      </div>
      <SourceNote
        data={data}
        ids={sources}
        scope={unit}
        year={
          scopeYear ??
          (xKey === 'year'
            ? `${rows[0]?.year ?? '—'}–${rows.at(-1)?.year ?? '—'}`
            : f.page === 'material'
              ? f.historyYear
              : f.year)
        }
      />
      <details className="evidence-table">
        <summary>Datos del gráfico y valores ausentes</summary>
        <DataTable
          rows={rows}
          caption={title}
          columns={
            columns ?? [
              { key: xKey, title: xKey === 'year' ? 'Año' : 'Categoría' },
              ...fields.map((s) => ({ key: s.key, title: s.name, digits: 2 })),
            ]
          }
          limit={30}
        />
      </details>
    </Panel>
  )
}
export function UnknownNote({ rows, keyName }: { rows: Row[]; keyName: string }) {
  const missing = rows.filter((r) => number(r, keyName) == null).length
  return missing ? (
    <span className="note">
      {missing} {missing === 1 ? 'celda' : 'celdas'} sin dato en esta selección. Las barras ausentes
      se identifican en la tabla; no se reconstruyen ni se convierten en ceros.
    </span>
  ) : null
}
