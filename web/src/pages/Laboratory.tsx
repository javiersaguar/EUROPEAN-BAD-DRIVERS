import { fmt, number, type Filters } from '../data'
import { composite } from '../index'
import { Panel, Note, DataTable, Bars, Export, metadata } from '../components'
import { type PageProps, spain, SpainSource } from './shared'

export function Laboratory({ data, f, update }: PageProps) {
  const rows = composite(spain(data, f.year), f.weights, f.method, f.indexMode === 'alternative'),
    baseline = composite(spain(data, f.year), [0.4, 0.25, 0.2, 0.15], f.method),
    stabilityPublished =
      f.year === 2024 &&
      f.indexMode === 'reference' &&
      f.method === 'percentile' &&
      f.weights.every((w, i) => Math.abs(w - [0.4, 0.25, 0.2, 0.15][i]) < 1e-10),
    joined = rows.map((r) => ({
      ...r,
      reference_rank: number(
        baseline.find((x) => x.province_code === r.province_code) ?? {},
        'index_rank',
      ),
      ...(stabilityPublished
        ? data.tables.sensitivity.find((x) => x.province_code === r.province_code)
        : {}),
    })),
    names = [
      'Siniestros con víctimas',
      'Siniestros urbanos',
      'Alcance / lateral',
      'Fallecidos a 30 días',
    ]
  return (
    <>
      <SpainSource
        data={data}
        year={f.year}
        scope="Índice descriptivo · tasas por población · no mide la habilidad individual"
      />
      <div className="grid laboratory-grid">
        <Panel
          title="Construye una lectura"
          subtitle="El índice expresa una combinación de criterios, no una verdad única."
        >
          <div className="filter-row stacked">
            <label>
              Definición
              <select
                aria-label="Definición"
                value={f.indexMode}
                onChange={(e) => update({ indexMode: e.target.value as Filters['indexMode'] })}
              >
                <option value="reference">Referencia · cuatro componentes</option>
                <option value="alternative">Alternativa · víctimas 50 % + mortalidad 50 %</option>
              </select>
            </label>
            <label>
              Normalización
              <select
                aria-label="Normalización"
                value={f.method}
                onChange={(e) => update({ method: e.target.value as Filters['method'] })}
              >
                <option value="percentile">Percentiles · escala 0–100</option>
                <option value="minmax">Mínimo–máximo · escala 0–100</option>
                <option value="zscore">Puntuación z · sin límite 0–100</option>
                <option value="robust_zscore">Z robusta · mediana / MAD</option>
              </select>
            </label>
          </div>
          {names.map((name, i) => (
            <label className="weight" key={name}>
              <span>
                {name}
                <strong>
                  {fmt((f.indexMode === 'alternative' ? [0.5, 0, 0, 0.5] : f.weights)[i] * 100)} %
                </strong>
              </span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                disabled={f.indexMode === 'alternative'}
                value={(f.indexMode === 'alternative' ? [0.5, 0, 0, 0.5] : f.weights)[i]}
                aria-label={`Peso ${name}`}
                onChange={(e) =>
                  update({
                    weights: f.weights.map((w, j) => (j === i ? Number(e.target.value) : w)),
                  })
                }
              />
            </label>
          ))}
          <button
            className="text-button"
            onClick={() =>
              update({
                weights: [0.4, 0.25, 0.2, 0.15],
                method: 'percentile',
                indexMode: 'reference',
              })
            }
          >
            Restablecer referencia
          </button>
          <Note>
            Los pesos activos se normalizan a suma 1. La alternativa elimina el peso extra de los
            subconjuntos urbanos y de colisiones; víctimas y mortalidad siguen relacionadas.
          </Note>
        </Panel>
        <Panel
          title="Resultado del escenario"
          subtitle={`${f.year} · ${f.method} · mayor puntuación = mayor tasa combinada`}
          action={
            <Export
              rows={joined}
              title="Escenario del índice"
              metadata={metadata(
                data,
                f,
                'Índice DGT + INE; tasas por población; ranking relativo; pesos normalizados',
              )}
              chartId="index-chart"
            />
          }
        >
          {!rows.length ? (
            <p role="alert">Activa al menos un peso para calcular el índice.</p>
          ) : (
            <div id="index-chart">
              <Bars
                rows={rows.slice(0, 10)}
                valueKey="index_score"
                title="Puntuación del índice"
                horizontal
              />
            </div>
          )}
        </Panel>
      </div>
      <Panel
        title="Posiciones y sensibilidad"
        subtitle={
          stabilityPublished
            ? '500 combinaciones de pesos + 24 escenarios · 200 bootstrap Poisson · 2024'
            : 'Este escenario cambia la posición; los intervalos publicados corresponden a la referencia de 2024.'
        }
      >
        <DataTable
          rows={joined}
          caption="Ranking del índice y sensibilidad"
          columns={[
            { key: 'index_rank', title: 'Posición', digits: 1 },
            { key: 'province', title: 'Provincia' },
            { key: 'index_score', title: 'Puntuación', digits: 2 },
            { key: 'reference_rank', title: 'Posición referencia', digits: 1 },
            ...(stabilityPublished
              ? [
                  { key: 'weight_rank_p05', title: 'Pesos p5' },
                  { key: 'weight_rank_p95', title: 'Pesos p95' },
                  { key: 'bootstrap_rank_lower', title: 'Recuento IC inferior' },
                  { key: 'bootstrap_rank_upper', title: 'Recuento IC superior' },
                ]
              : []),
          ]}
        />
      </Panel>
    </>
  )
}
