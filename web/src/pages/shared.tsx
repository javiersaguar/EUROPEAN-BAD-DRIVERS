import { number, incidents, denominators, type Dataset, type Filters, type Row } from '../data'
import { Panel, Note, SourceNote, DataTable, Export, metadata } from '../components'

export type PageProps = { data: Dataset; f: Filters; update: (patch: Partial<Filters>) => void }

export const rateCaption = (f: Filters) =>
  `${incidents[f.incident]} / 100.000 ${denominators[f.denominator].toLowerCase()}`

export const spain = (data: Dataset, year: number) =>
  data.tables.spain_metrics.filter((r) => r.year === year)

export const sort = (rows: Row[], key: string) =>
  [...rows].sort((a, b) => (number(b, key) ?? -Infinity) - (number(a, key) ?? -Infinity))

export function SpainSource({
  data,
  year,
  scope,
}: {
  data: Dataset
  year: number
  scope?: string
}) {
  return (
    <SourceNote
      data={data}
      year={year}
      ids={[
        `dgt_accidents_${year}`,
        'ine_population_67988',
        `dgt_vehicles_${year}`,
        `dgt_drivers_${year}`,
      ]}
      scope={scope ?? '52 provincias · siniestros con víctimas · tasas por exposición registrada'}
    />
  )
}

export function MetricFilters({ f, update }: { f: Filters; update: PageProps['update'] }) {
  return (
    <div className="filter-row">
      <label>
        Indicador
        <select
          value={f.incident}
          onChange={(e) => update({ incident: e.target.value as Filters['incident'] })}
        >
          {Object.entries(incidents).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
      </label>
      <label>
        Denominador
        <select
          value={f.denominator}
          onChange={(e) => update({ denominator: e.target.value as Filters['denominator'] })}
        >
          {Object.entries(denominators).map(([k, v]) => (
            <option key={k} value={k}>
              Por 100.000 {v.toLowerCase()}
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}

export function Rce({ data, f }: Pick<PageProps, 'data' | 'f'>) {
  const rows = data.tables.rce_exposure.filter((r) => r.matched_exposure),
    key = 'rce_crashes_per_100m_vkm'
  return (
    <Panel
      title="Exposición por kilómetros · red estatal"
      subtitle="2022 · siniestros en vías de titularidad estatal / 100 millones de vehículos-km"
    >
      <SourceNote
        data={data}
        year={2022}
        ids={['transport_rce_2022', 'dgt_accidents_2022']}
        scope="44 provincias con tráfico RCE · todos los vehículos · solo red estatal"
      />
      <Note>
        La clasificación administrativa de DGT y el inventario RCE pueden diferir. Esta tasa se
        presenta por separado y no entra en el índice. Las provincias sin exposición se conservan
        como «Sin dato».
      </Note>
      <Export
        rows={data.tables.rce_exposure}
        title="Red estatal 2022"
        metadata={metadata(
          data,
          f,
          'DGT titularidad estatal + tráfico RCE 2022; tasa / 100 millones de vehículos-km',
        )}
      />
      <DataTable
        rows={sort(rows, key)}
        caption="Tasas en la red estatal de 2022"
        columns={[
          { key: 'province', title: 'Provincia' },
          { key: 'vehicle_km_million', title: 'Millones vehículo-km', digits: 1 },
          { key: 'rce_injury_crashes', title: 'Siniestros con víctimas' },
          { key, title: 'Tasa / 100 M vkm', digits: 2 },
          { key: 'lower', title: 'IC inferior', digits: 2 },
          { key: 'upper', title: 'IC superior', digits: 2 },
        ]}
      />
    </Panel>
  )
}
