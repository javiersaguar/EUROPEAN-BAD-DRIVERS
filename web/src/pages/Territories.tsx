import { ArrowUpRight } from 'lucide-react'
import { fmt, nationalRate, denominators, metricKey, label } from '../data'
import { Panel, DataTable, Bars, Export, metadata } from '../components'
import { ProvinceMap } from '../Map'
import { type PageProps, rateCaption, spain, sort, SpainSource, MetricFilters, Rce } from './shared'

export function Territories({ data, f, update }: PageProps) {
  const rows = spain(data, f.year),
    key = metricKey(f.incident, f.denominator),
    ranked = sort(rows, key),
    meta = metadata(data, f, `${rateCaption(f)}; DGT + INE; año ${f.year}; intervalo Poisson 95 %`)
  return (
    <>
      <MetricFilters f={f} update={update} />
      <SpainSource data={data} year={f.year} />
      <div className="grid main-grid">
        <Panel
          title="Distribución por provincias"
          subtitle={rateCaption(f)}
          action={
            <Export
              rows={ranked}
              title="Tasas provinciales"
              metadata={meta}
              chartId="territory-map"
            />
          }
        >
          <div id="territory-map">
            <ProvinceMap
              rows={rows}
              metric={key}
              onSelect={(province) => update({ province, page: 'profile' })}
            />
          </div>
        </Panel>
        <Panel
          title="Las 10 tasas más altas"
          subtitle={`España: ${fmt(nationalRate(rows, f.incident, f.denominator), 2)} · ${f.year}`}
        >
          <Bars rows={ranked.slice(0, 10)} valueKey={key} title={rateCaption(f)} horizontal />
        </Panel>
      </div>
      <Panel
        title="Todas las provincias"
        subtitle="Los intervalos reflejan variación estadística del recuento, no errores de registro."
      >
        <DataTable
          rows={ranked}
          caption="Tasas provinciales e intervalos del 95 %"
          columns={[
            {
              key: 'province',
              title: 'Provincia',
              render: (r) => (
                <button
                  className="text-button"
                  onClick={() => update({ province: label(r, 'province_code'), page: 'profile' })}
                >
                  {r.province}
                  <ArrowUpRight size={12} />
                </button>
              ),
            },
            { key: f.incident, title: 'Recuento' },
            { key: f.denominator, title: denominators[f.denominator] },
            { key, title: 'Tasa / 100.000', digits: 2 },
            { key: `${key}_lower`, title: 'IC 95 % inferior', digits: 2 },
            { key: `${key}_upper`, title: 'IC 95 % superior', digits: 2 },
          ]}
        />
      </Panel>
      <Rce data={data} f={f} />
    </>
  )
}
