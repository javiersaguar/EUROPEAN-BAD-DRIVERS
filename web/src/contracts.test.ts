import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import {
  defaults,
  readFilters,
  serializeFilters,
  nationalRate,
  total,
  fmt,
  type Dataset,
} from './data'
import { normalize, composite } from './index'
import { csvText } from './components'
const data = JSON.parse(
  readFileSync(new URL('../public/data/observatory.json', import.meta.url), 'utf8'),
) as Dataset
describe('published analytical contract', () => {
  it('reproduces every reference and alternative provincial score and rank', () => {
    for (const year of [2022, 2023, 2024])
      for (const alternative of [false, true]) {
        const actual = composite(
          data.tables.spain_metrics.filter((r) => r.year === year),
          defaults.weights,
          'percentile',
          alternative,
        )
        const published = data.tables[alternative ? 'index_alternative' : 'index'].filter(
          (r) => r.year === year,
        )
        expect(actual).toHaveLength(52)
        for (const row of actual) {
          const expected = published.find((r) => r.province_code === row.province_code)!
          expect(row.index_score).toBeCloseTo(Number(expected.index_score), 9)
          expect(row.index_rank).toBe(Number(expected.index_rank))
        }
      }
  })
  it('uses ratios of totals and retains missing exposure', () => {
    const rows = data.tables.spain_metrics.filter((r) => r.year === 2023)
    expect(total(rows, 'registered_vehicles')).toBe(36075238)
    expect(total(rows, 'licensed_drivers')).toBe(27910056)
    expect(nationalRate(rows, 'injury_crashes', 'population')).toBeCloseTo(
      (101306 / Number(total(rows, 'population'))) * 100000,
    )
    expect(
      nationalRate([{ injury_crashes: 10, population: null }], 'injury_crashes', 'population'),
    ).toBeNull()
  })
  it('retains all 405 historic observations and eight missing network exposures', () => {
    expect(data.tables.europe_history).toHaveLength(405)
    expect(data.tables.rce_exposure.filter((r) => r.vehicle_km_million === null)).toHaveLength(8)
    expect(JSON.stringify(data)).not.toContain('NaN')
  })
})
describe('normalization and URL state', () => {
  it('uses average ties and neutral constants', () => {
    expect(normalize([1, 1, 3], 'percentile')).toEqual([25, 25, 100])
    expect(normalize([5, 5], 'minmax')).toEqual([50, 50])
    expect(normalize([5, 5], 'robust_zscore')).toEqual([0, 0])
    expect(normalize([1, 2, 3], 'zscore')[1]).toBe(0)
    expect(composite(data.tables.spain_metrics, [0, 0, 0, 0], 'percentile')).toEqual([])
  })
  it('roundtrips all filters and rejects invalid values', () => {
    const f = {
      ...defaults,
      page: 'insurance' as const,
      year: 2023,
      compare: ['08', '52'],
      weights: [0, 0, 0.2, 0.8],
      selection: 'both' as const,
      insurance: 'rc_corporal' as const,
      method: 'robust_zscore' as const,
      indexMode: 'alternative' as const,
    }
    expect(readFilters(serializeFilters(f))).toEqual(f)
    const invalid = readFilters('?page=wrong&year=2030&province=99&country=XX&weights=-1,NaN,5,1')
    expect(invalid).toEqual(defaults)
    expect(readFilters(serializeFilters({ ...defaults, compare: [] })).compare).toEqual([])
  })
  it('formats Spanish numbers and escapes spreadsheet expressions and quotes', () => {
    expect(fmt(null)).toBe('Sin dato')
    expect(fmt(101996)).toBe('101.996')
    const text = csvText(
      [{ name: '=SUM(A1:A2)', note: 'He said "hola"', value: null }],
      ['Source: audited'],
    )
    expect(text).toContain("'=")
    expect(text).toContain('""hola""')
    expect(text).toContain('# Source: audited')
  })
})
