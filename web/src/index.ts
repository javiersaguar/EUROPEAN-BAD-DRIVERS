import { number, type Row, type Filters } from './data'
const reference = ['injury_crashes', 'urban_crashes', 'rear_lateral_crashes', 'fatalities']
export function normalize(values: number[], method: Filters['method']): number[] {
  if (!values.length) return []
  if (values.every((v) => v === values[0]))
    return values.map(() => (['minmax', 'percentile'].includes(method) ? 50 : 0))
  if (method === 'percentile')
    return values.map(
      (v) =>
        ((values.filter((x) => x < v).length + (values.filter((x) => x === v).length - 1) / 2) /
          (values.length - 1)) *
        100,
    )
  const min = Math.min(...values),
    max = Math.max(...values),
    mean = values.reduce((a, b) => a + b) / values.length
  const sd = Math.sqrt(values.reduce((s, v) => s + (v - mean) ** 2, 0) / values.length)
  if (method === 'minmax') return values.map((v) => ((v - min) / (max - min)) * 100)
  const median = (v: number[]) => {
    const s = [...v].sort((a, b) => a - b),
      m = Math.floor(s.length / 2)
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2
  }
  const center = method === 'robust_zscore' ? median(values) : mean
  const spread =
    method === 'robust_zscore' ? 1.4826 * median(values.map((v) => Math.abs(v - center))) || sd : sd
  return values.map((v) => (v - center) / spread)
}
export function composite(
  rows: Row[],
  weights: number[],
  method: Filters['method'],
  alternative = false,
): Row[] {
  const active = alternative ? [0.5, 0, 0, 0.5] : weights
  const sum = active.reduce((a, b) => a + b, 0)
  if (!sum || active.some((v) => !Number.isFinite(v) || v < 0)) return []
  const eligible = rows.filter(
    (r) =>
      (number(r, 'injury_crashes') ?? 0) >= 30 &&
      reference.every((c, i) => !active[i] || number(r, `${c}_per_100k_population`) != null),
  )
  const vectors = reference.map((c) =>
    normalize(
      eligible.map((r) => number(r, `${c}_per_100k_population`) ?? 0),
      method,
    ),
  )
  const scores = eligible.map((r, j) => ({
    ...r,
    index_score: active.reduce((s, w, i) => s + (w / sum) * vectors[i][j], 0),
  }))
  return scores
    .map((r) => ({
      ...r,
      index_rank:
        1 +
        scores.filter((x) => x.index_score > r.index_score).length +
        (scores.filter((x) => x.index_score === r.index_score).length - 1) / 2,
    }))
    .sort((a, b) => a.index_rank - b.index_rank)
}
