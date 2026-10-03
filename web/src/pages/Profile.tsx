import { ArrowRight } from 'lucide-react'
import { fmt, pct, number, nationalRate, incidents, denominators, metricKey, label } from '../data'
import { Panel, Stat, Note, Lines, Export, ValueTable, metadata } from '../components'
import { type PageProps, rateCaption, spain, SpainSource, MetricFilters } from './shared'

export function Profile({ data, f, update }: PageProps) {
  const rows = spain(data, f.year),
    r = rows.find((r) => r.province_code === f.province)!,
    key = metricKey(f.incident, f.denominator),
    value = number(r, key),
    national = nationalRate(rows, f.incident, f.denominator),
    history = data.tables.spain_metrics.filter((r) => r.province_code === f.province),
    rank = data.tables.index.find((r) => r.year === f.year && r.province_code === f.province),
    sensitivity = data.tables.sensitivity.find((r) => r.province_code === f.province)
  return (
    <>
      <label className="province-select">
        Provincia
        <select
          aria-label="Provincia"
          value={f.province}
          onChange={(e) => update({ province: e.target.value })}
        >
          {rows.map((r) => (
            <option key={label(r, 'province_code')} value={label(r, 'province_code')}>
              {r.province}
            </option>
          ))}
        </select>
      </label>
      <MetricFilters f={f} update={update} />
      <SpainSource data={data} year={f.year} />
      <div className="profile-heading">
        <h2>{r.province}</h2>
        <span className="badge">
          {r.community} · {f.year}
        </span>
      </div>
      <div className="stats">
        <Stat
          label={incidents[f.incident]}
          value={fmt(number(r, f.incident))}
          detail={`${fmt(number(r, f.denominator))} ${denominators[f.denominator].toLowerCase()}`}
        />
        <Stat
          label="Tasa por 100.000"
          value={fmt(value, 2)}
          detail={`IC 95 %: ${fmt(number(r, `${key}_lower`), 2)}–${fmt(number(r, `${key}_upper`), 2)}`}
        />
        <Stat
          label="Frente a España"
          value={pct(value != null && national ? (value / national - 1) * 100 : null)}
          detail={`Referencia nacional: ${fmt(national, 2)}`}
        />
      </div>
      <div className="grid">
        <Panel
          title="Trayectoria de la provincia"
          subtitle={rateCaption(f)}
          action={
            <Export
              rows={history}
              title={`Ficha ${r.province}`}
              metadata={metadata(data, f, `DGT + INE; ${rateCaption(f)}; 2022–2024`)}
              chartId="profile-chart"
            />
          }
        >
          <div id="profile-chart">
            <Lines
              rows={history}
              series={[{ key, name: String(r.province) }]}
              title="Evolución provincial"
            />
          </div>
          <ValueTable rows={history} keyName={key} nameKey="year" caption="Tasa por 100.000" />
        </Panel>
        <Panel
          title="Posición y estabilidad"
          subtitle="Índice de referencia · percentiles · exposición por población"
        >
          <Stat
            label="Posición del índice"
            value={`${fmt(number(rank ?? {}, 'index_rank'))} / 52`}
            detail={`Puntuación: ${fmt(number(rank ?? {}, 'index_score'), 1)} / 100`}
          />
          {f.year === 2024 && sensitivity ? (
            <>
              <div className="stability">
                <p>
                  <strong>Pesos alternativos</strong>
                  <span>
                    Posiciones {fmt(number(sensitivity, 'weight_rank_p05'))}–
                    {fmt(number(sensitivity, 'weight_rank_p95'))} · percentiles 5–95
                  </span>
                </p>
                <p>
                  <strong>Variación del recuento</strong>
                  <span>
                    Posiciones {fmt(number(sensitivity, 'bootstrap_rank_lower'))}–
                    {fmt(number(sensitivity, 'bootstrap_rank_upper'))} · bootstrap Poisson 95 %
                  </span>
                </p>
              </div>
              <Note>
                La sensibilidad a los pesos y la incertidumbre del recuento responden a preguntas
                distintas. El índice incluye subconjuntos solapados.
              </Note>
            </>
          ) : (
            <Note>
              La auditoría de estabilidad publicada corresponde a 2024. No se traslada a otros años.
            </Note>
          )}
          <button className="button" onClick={() => update({ page: 'laboratory' })}>
            Explorar el método
            <ArrowRight size={14} />
          </button>
        </Panel>
      </div>
    </>
  )
}
