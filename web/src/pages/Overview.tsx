import { ArrowRight, ArrowUpRight } from 'lucide-react'
import { fmt, pct, number, total, nationalRate, metricKey, label } from '../data'
import { Panel, Stat, Note, Lines, ValueTable } from '../components'
import { ProvinceMap } from '../Map'
import { type PageProps, spain, sort, SpainSource } from './shared'

export function Overview({ data, f, update }: PageProps) {
  const rows = spain(data, f.year),
    key = metricKey('injury_crashes', 'population'),
    ranked = sort(rows, key),
    national = nationalRate(rows, 'injury_crashes', 'population'),
    trend = [2022, 2023, 2024].map((year) => ({
      year,
      rate: nationalRate(spain(data, year), 'injury_crashes', 'population'),
    })),
    older = spain(data, 2022),
    change = (total(rows, 'injury_crashes')! / total(older, 'injury_crashes')! - 1) * 100
  return (
    <>
      <SpainSource data={data} year={f.year} />
      <div className="stats">
        <Stat
          label="Siniestros con víctimas"
          value={fmt(total(rows, 'injury_crashes'))}
          detail={`${pct(change)} frente a 2022`}
        />
        <Stat
          label="Fallecidos a 30 días"
          value={fmt(total(rows, 'fatalities'))}
          detail="Personas, todas las vías y usuarios"
        />
        <Stat
          label="Tasa nacional"
          value={fmt(national, 1)}
          unit="siniestros / 100.000 habitantes"
          detail="Cociente de totales, sin promediar provincias"
        />
      </div>
      <div className="grid main-grid">
        <Panel
          title="Una lectura territorial"
          subtitle="Siniestros con víctimas por 100.000 habitantes"
          action={
            <button className="text-button" onClick={() => update({ page: 'territories' })}>
              Explorar
              <ArrowRight size={14} />
            </button>
          }
        >
          <ProvinceMap
            rows={rows}
            metric={key}
            onSelect={(province) => update({ province, page: 'profile' })}
          />
        </Panel>
        <Panel title="Dónde se concentra la tasa" subtitle={`Primeras 6 provincias · ${f.year}`}>
          <div className="rank-list">
            {ranked.slice(0, 6).map((r, i) => (
              <button
                key={label(r, 'province_code')}
                onClick={() => update({ province: label(r, 'province_code'), page: 'profile' })}
              >
                <span className="rank-number">{i + 1}</span>
                <span>{r.province}</span>
                <strong>{fmt(number(r, key), 1)}</strong>
                <ArrowUpRight size={14} />
              </button>
            ))}
          </div>
          <div className="national-benchmark">
            <span>Referencia España</span>
            <strong>{fmt(national, 1)}</strong>
          </div>
          <Note>
            La tasa describe dónde se registran los siniestros. La movilidad y el registro afectan a
            la comparación.
          </Note>
        </Panel>
      </div>
      <div className="insights">
        <button onClick={() => update({ page: 'material' })}>
          <span className="eyebrow">01 · Daños materiales</span>
          <h2>Los golpes de chapa tienen su propio panel.</h2>
          <p>Irlanda y Alemania: series 2010–2024, categorías de daños y costes.</p>
          <ArrowRight size={19} />
        </button>
        <button onClick={() => update({ page: 'persons' })}>
          <span className="eyebrow">02 · Personas y categorías</span>
          <h2>Sexo, edad y usuarios: recuentos con contexto.</h2>
          <p>España y UE27, con mortalidad poblacional y ajuste por edad.</p>
          <ArrowRight size={19} />
        </button>
        <button onClick={() => update({ page: 'circumstances' })}>
          <span className="eyebrow">03 · Tipos de accidente</span>
          <h2>Volumen y gravedad responden a preguntas distintas.</h2>
          <p>21 categorías de accidente y antigüedad de vehículos implicados.</p>
          <ArrowRight size={19} />
        </button>
      </div>
      <Panel
        title="Evolución en España"
        subtitle="Tasa de siniestros con víctimas / 100.000 habitantes · 2022–2024"
      >
        <Lines
          rows={trend}
          series={[{ key: 'rate', name: 'España' }]}
          title="Tasa nacional 2022–2024"
        />
        <ValueTable
          rows={trend}
          keyName="rate"
          nameKey="year"
          caption="Tasa por 100.000 habitantes"
        />
      </Panel>
    </>
  )
}
