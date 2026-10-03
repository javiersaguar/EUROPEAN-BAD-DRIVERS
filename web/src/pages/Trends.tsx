import { fmt, pct, number, label } from '../data'
import { Panel, Stat, Note, SourceNote, DataTable, Lines, Export, metadata } from '../components'
import { type PageProps } from './shared'

export function Trends({ data, f, update }: PageProps) {
  const countries = data.tables.europe_history.filter((r) => r.year === 2024),
    rows = data.tables.europe_history.filter((r) => r.geo === f.country),
    country = String(rows[0]?.country ?? ''),
    key = 'fatalities_per_million_population',
    first = number(rows[0] ?? {}, key),
    last = number(rows.at(-1) ?? {}, key)
  return (
    <>
      <label className="province-select">
        País
        <select
          aria-label="País"
          value={f.country}
          onChange={(e) => update({ country: e.target.value })}
        >
          {countries.map((r) => (
            <option key={label(r, 'geo')} value={label(r, 'geo')}>
              {r.country}
            </option>
          ))}
        </select>
      </label>
      <SourceNote
        data={data}
        year="2010–2024"
        ids={['eurostat_fatalities_history', 'eurostat_population_history']}
        scope="UE-27 actual · fallecidos a 30 días / millón de habitantes"
      />
      <div className="stats">
        <Stat
          label={`${country} · 2024`}
          value={fmt(last, 1)}
          unit="fallecidos / millón de habitantes"
        />
        <Stat
          label="Cambio de la tasa desde 2010"
          value={pct(first && last != null ? (last / first - 1) * 100 : null)}
          detail="Comparación de extremos, sin atribución causal"
        />
        <Stat
          label="Longitud de la serie"
          value="15 años"
          detail="2010–2024 · banderas de Eurostat conservadas"
        />
      </div>
      <Panel
        title={`Mortalidad vial · ${country}`}
        subtitle="Fallecidos a 30 días / millón de habitantes"
        action={
          <Export
            rows={rows}
            title={`Historia ${country}`}
            metadata={metadata(
              data,
              f,
              'Eurostat tran_sf_roadus + demo_pjan; 2010–2024; población a 1 enero; muertes a 30 días / millón',
            )}
            chartId="history-chart"
          />
        }
      >
        <div id="history-chart">
          <Lines rows={rows} series={[{ key, name: country }]} title="Mortalidad vial histórica" />
        </div>
        <Note>
          2020 incluye una alteración excepcional de la movilidad. La serie muestra resultados
          observados; por sí sola no identifica las causas del cambio.
        </Note>
        <DataTable
          rows={rows}
          caption="Mortalidad histórica y banderas de publicación"
          columns={[
            { key: 'year', title: 'Año' },
            { key: 'fatalities', title: 'Fallecidos' },
            { key: 'population', title: 'Población' },
            { key, title: 'Por millón', digits: 2 },
            { key: 'lower', title: 'IC inferior', digits: 2 },
            { key: 'upper', title: 'IC superior', digits: 2 },
            { key: 'fatalities_status', title: 'Bandera mortalidad' },
            { key: 'population_status', title: 'Bandera población' },
          ]}
        />
      </Panel>
      <Note>
        La cohorte usa los 27 miembros actuales también antes de sus adhesiones. Los siniestros con
        víctimas en España siguen cubriendo 2022–2024; esta ampliación histórica corresponde a
        mortalidad europea.
      </Note>
    </>
  )
}
