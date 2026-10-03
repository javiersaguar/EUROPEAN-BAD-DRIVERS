import { ArrowUpRight } from 'lucide-react'
import { label } from '../data'
import { Panel, Note, SourceNote, DataTable, Bars, Export, metadata } from '../components'
import { type PageProps, sort } from './shared'

export function Europe({ data, f, update }: PageProps) {
  const key = 'fatalities_per_million_population',
    rows = sort(
      data.tables.europe_history.filter((r) => r.year === f.year),
      key,
    )
  return (
    <>
      <SourceNote
        data={data}
        year={f.year}
        ids={['eurostat_fatalities_history', 'eurostat_population_history']}
        scope="27 países · muertes a 30 días · población a 1 enero"
      />
      <Panel
        title="Mortalidad vial en la Unión Europea"
        subtitle="Fallecidos por millón de habitantes · comparación descriptiva"
        action={
          <Export
            rows={rows}
            title="Mortalidad UE27"
            metadata={metadata(
              data,
              f,
              'Eurostat; fallecidos a 30 días / millón de habitantes; población a 1 enero; flags conservados',
            )}
            chartId="europe-chart"
          />
        }
      >
        <div id="europe-chart">
          <Bars
            rows={rows}
            valueKey={key}
            nameKey="country"
            title="Fallecidos por millón de habitantes"
            horizontal
          />
        </div>
        <DataTable
          rows={rows}
          caption="Mortalidad europea y comparabilidad"
          columns={[
            {
              key: 'country',
              title: 'País',
              render: (r) => (
                <button
                  className="text-button"
                  onClick={() => update({ country: label(r, 'geo'), page: 'trends' })}
                >
                  {r.country}
                  <ArrowUpRight size={12} />
                </button>
              ),
            },
            { key: 'fatalities', title: 'Fallecidos' },
            { key, title: 'Por millón', digits: 2 },
            { key: 'fatalities_status', title: 'Bandera fuente' },
            { key: 'population_status', title: 'Bandera población' },
          ]}
        />
      </Panel>
      <Note>
        La definición común de fallecimiento a 30 días facilita la comparación, pero persisten
        diferencias de registro y movilidad. No existe aquí una serie europea homogénea de golpes de
        chapa.
      </Note>
    </>
  )
}
