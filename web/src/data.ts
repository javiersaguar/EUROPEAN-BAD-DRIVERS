export type Row = Record<string, string | number | boolean | null>
export type Source = {
  id: string
  organization: string
  dataset_title: string
  years: number[]
  url: string
  page_url: string
  geographic_level: string
  observation_unit: string
  denominator: string
  known_limitations: string
  sample_retrieved_at: string
  sample_sha256: string
  license_url: string
  enabled: boolean
}
export type Dataset = {
  schema_version: number
  release: string
  audit_date: string
  author: string
  tables: Record<string, Row[]>
  sources: Source[]
  table_hashes: Record<string, string>
  data_quality: Record<string, unknown>
  insurance_quality: Record<string, unknown>
  model_policy: Record<string, unknown>
  model_card: Record<string, unknown>
}
export const number = (row: Row, key: string): number | null =>
  typeof row[key] === 'number' && Number.isFinite(row[key]) ? (row[key] as number) : null
export const fmt = (value: number | null | undefined, digits = 0) =>
  value == null || !Number.isFinite(value)
    ? 'Sin dato'
    : new Intl.NumberFormat('es-ES', {
        maximumFractionDigits: digits,
        minimumFractionDigits: digits,
        useGrouping: 'always',
      }).format(value)
export const pct = (value: number | null | undefined, digits = 1) =>
  value == null ? 'Sin dato' : `${fmt(value, digits)} %`
export const label = (row: Row, key = 'province') => String(row[key] ?? '')
export const total = (rows: Row[], key: string): number | null =>
  rows.length && rows.every((r) => number(r, key) != null)
    ? rows.reduce((sum, r) => sum + (number(r, key) ?? 0), 0)
    : null
export const incidents = {
  injury_crashes: 'Siniestros con víctimas',
  fatalities: 'Fallecidos a 30 días',
  severe_crashes: 'Siniestros graves',
  urban_crashes: 'Siniestros urbanos',
  rear_lateral_crashes: 'Colisiones de alcance / lateral',
} as const
export const denominators = {
  population: 'Habitantes',
  registered_vehicles: 'Vehículos registrados',
  licensed_drivers: 'Titulares de permisos',
} as const
export type Incident = keyof typeof incidents
export type Denominator = keyof typeof denominators
export const metricKey = (incident: Incident, denominator: Denominator) =>
  `${incident}_per_100k_${denominator}`
export const nationalRate = (
  rows: Row[],
  incident: Incident,
  denominator: Denominator,
): number | null => {
  const numerator = total(rows, incident),
    exposure = total(rows, denominator)
  return numerator != null && exposure != null && exposure > 0
    ? (numerator / exposure) * 100000
    : null
}
export type Page =
  | 'overview'
  | 'territories'
  | 'profile'
  | 'compare'
  | 'insurance'
  | 'trends'
  | 'europe'
  | 'laboratory'
  | 'models'
  | 'sources'
export type Filters = {
  page: Page
  year: number
  province: string
  compare: string[]
  incident: Incident
  denominator: Denominator
  insurance: 'rc_material' | 'rc_corporal'
  selection: 'higher' | 'lower' | 'both'
  country: string
  method: 'percentile' | 'minmax' | 'zscore' | 'robust_zscore'
  weights: number[]
  indexMode: 'reference' | 'alternative'
}
export const defaults: Filters = {
  page: 'overview',
  year: 2024,
  province: '28',
  compare: ['28', '08', '41'],
  incident: 'injury_crashes',
  denominator: 'population',
  insurance: 'rc_material',
  selection: 'higher',
  country: 'ES',
  method: 'percentile',
  weights: [0.4, 0.25, 0.2, 0.15],
  indexMode: 'reference',
}
const pages: Page[] = [
  'overview',
  'territories',
  'profile',
  'compare',
  'insurance',
  'trends',
  'europe',
  'laboratory',
  'models',
  'sources',
]
export function readFilters(search: string): Filters {
  const p = new URLSearchParams(search),
    result = { ...defaults, compare: [...defaults.compare], weights: [...defaults.weights] }
  if (pages.includes(p.get('page') as Page)) result.page = p.get('page') as Page
  if ([2022, 2023, 2024].includes(Number(p.get('year')))) result.year = Number(p.get('year'))
  if (
    /^\d{2}$/.test(p.get('province') ?? '') &&
    Number(p.get('province')) >= 1 &&
    Number(p.get('province')) <= 52
  )
    result.province = p.get('province')!
  const comparison = [
    ...new Set(
      (p.get('compare') ?? '')
        .split(',')
        .filter((s) => /^\d{2}$/.test(s) && Number(s) >= 1 && Number(s) <= 52),
    ),
  ].slice(0, 3)
  if (p.has('compare') && (comparison.length || p.get('compare') === ''))
    result.compare = comparison
  if (p.get('incident')! in incidents) result.incident = p.get('incident') as Incident
  if (p.get('denominator')! in denominators)
    result.denominator = p.get('denominator') as Denominator
  if (['rc_material', 'rc_corporal'].includes(p.get('insurance') ?? ''))
    result.insurance = p.get('insurance') as Filters['insurance']
  if (['higher', 'lower', 'both'].includes(p.get('selection') ?? ''))
    result.selection = p.get('selection') as Filters['selection']
  if (
    [
      'AT',
      'BE',
      'BG',
      'HR',
      'CY',
      'CZ',
      'DK',
      'EE',
      'FI',
      'FR',
      'DE',
      'EL',
      'HU',
      'IE',
      'IT',
      'LV',
      'LT',
      'LU',
      'MT',
      'NL',
      'PL',
      'PT',
      'RO',
      'SK',
      'SI',
      'ES',
      'SE',
    ].includes(p.get('country') ?? '')
  )
    result.country = p.get('country')!
  if (['percentile', 'minmax', 'zscore', 'robust_zscore'].includes(p.get('method') ?? ''))
    result.method = p.get('method') as Filters['method']
  if (p.get('indexMode') === 'alternative') result.indexMode = 'alternative'
  const weights = (p.get('weights') ?? '').split(',').map(Number)
  if (weights.length === 4 && weights.every((v) => Number.isFinite(v) && v >= 0 && v <= 1))
    result.weights = weights
  return result
}
export function serializeFilters(f: Filters): string {
  return new URLSearchParams({
    ...f,
    year: String(f.year),
    compare: f.compare.join(','),
    weights: f.weights.join(','),
  }).toString()
}
export const chartColors = ['#355e50', '#b87736', '#557b94']
