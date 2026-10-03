import { fmt, number, incidents, denominators, metricKey, label, type Row } from '../data'
import { Panel, Stat, Note, DataTable, Lines, Export, metadata } from '../components'
import { type PageProps, rateCaption, spain, SpainSource, MetricFilters } from './shared'

export function Compare({ data, f, update }: PageProps) {
  const rows = spain(data, f.year),
    chosen = rows.filter((r) => f.compare.includes(label(r, 'province_code'))),
    key = metricKey(f.incident, f.denominator),
    series = chosen.map((r) => ({ key: label(r, 'province_code'), name: String(r.province) })),
    history = [2022, 2023, 2024].map((year) => {
      const r: Row = { year }
      f.compare.forEach((c) => {
        r[c] = number(
          data.tables.spain_metrics.find((p) => p.year === year && p.province_code === c) ?? {},
          key,
        )
      })
      return r
    })
  const toggle = (code: string) => {
    if (f.compare.includes(code)) update({ compare: f.compare.filter((c) => c !== code) })
    else if (f.compare.length < 3) update({ compare: [...f.compare, code] })
  }
  return (
    <>
      <MetricFilters f={f} update={update} />
      <details className="comparison-picker">
        <summary className="button">Elegir provincias · {f.compare.length} / 3</summary>
        <fieldset>
          <legend>Selecciona entre dos y tres provincias</legend>
          <div>
            {rows.map((r) => (
              <label key={label(r, 'province_code')}>
                <input
                  type="checkbox"
                  checked={f.compare.includes(label(r, 'province_code'))}
                  disabled={
                    f.compare.length === 3 && !f.compare.includes(label(r, 'province_code'))
                  }
                  onChange={() => toggle(label(r, 'province_code'))}
                />
                {r.province}
              </label>
            ))}
          </div>
        </fieldset>
      </details>
      <SpainSource data={data} year={f.year} />
      {chosen.length < 2 && <Note>Selecciona al menos dos provincias para comparar.</Note>}
      <div className="stats">
        {chosen.map((r) => (
          <Stat
            key={label(r, 'province_code')}
            label={String(r.province)}
            value={fmt(number(r, key), 2)}
            unit="por 100.000"
            detail={`${fmt(number(r, f.incident))} ${incidents[f.incident].toLowerCase()}`}
          />
        ))}
      </div>
      <Panel
        title="Evolución con el mismo denominador"
        subtitle={rateCaption(f)}
        action={
          <Export
            rows={chosen}
            title="Comparación territorial"
            metadata={metadata(data, f, `DGT + INE; ${rateCaption(f)}; IC Poisson 95 %`)}
            chartId="compare-chart"
          />
        }
      >
        <div id="compare-chart">
          <Lines rows={history} series={series} title="Comparación de provincias 2022–2024" />
        </div>
        <DataTable
          rows={chosen}
          caption="Comparación territorial"
          columns={[
            { key: 'province', title: 'Provincia' },
            { key: f.incident, title: 'Recuento' },
            { key: f.denominator, title: denominators[f.denominator] },
            { key, title: 'Tasa / 100.000', digits: 2 },
            { key: `${key}_lower`, title: 'IC inferior', digits: 2 },
            { key: `${key}_upper`, title: 'IC superior', digits: 2 },
          ]}
        />
      </Panel>
    </>
  )
}
