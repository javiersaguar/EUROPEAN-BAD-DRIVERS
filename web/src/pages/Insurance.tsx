import { ArrowUpRight, Info } from 'lucide-react'
import { number, type Filters } from '../data'
import { Panel, Note, SourceNote, DataTable, Bars, Export, metadata } from '../components'
import { type PageProps, sort } from './shared'

export function Insurance({ data, f, update }: PageProps) {
  const insured = data.tables.insurance_exposure ?? []
  const insuredYear = insured.some((r) => r.year === f.year)
    ? f.year
    : Math.max(...insured.map((r) => number(r, 'year')!))
  const insuredRows = insured.filter((r) => r.year === insuredYear)
  const rows = data.tables.insurance_municipal.filter(
      (r) => r.coverage === f.insurance && (f.selection === 'both' || r.selection === f.selection),
    ),
    sorted =
      f.selection === 'lower'
        ? sort(rows, 'relative_difference_pct').reverse()
        : sort(rows, 'relative_difference_pct'),
    scope = `UNESPA 2024; ${f.insurance}; ciudades > 50.000 hab.; diferencia relativa de frecuencia frente a España (%)`,
    meta = metadata(data, f, scope)
  return (
    <>
      <div className="filter-row">
        <label>
          Cobertura
          <select
            aria-label="Cobertura"
            value={f.insurance}
            onChange={(e) => update({ insurance: e.target.value as Filters['insurance'] })}
          >
            <option value="rc_material">Responsabilidad civil · daños materiales</option>
            <option value="rc_corporal">Responsabilidad civil · daños corporales</option>
          </select>
        </label>
        <label>
          Selección publicada
          <select
            aria-label="Selección publicada"
            value={f.selection}
            onChange={(e) => update({ selection: e.target.value as Filters['selection'] })}
          >
            <option value="higher">20 frecuencias más altas</option>
            <option value="lower">20 frecuencias más bajas</option>
            <option value="both">Ambas listas · 40 municipios</option>
          </select>
        </label>
      </div>
      <SourceNote
        data={data}
        year={2024}
        ids={['unespa_motor_2024']}
        scope="Seguro · municipios > 50.000 habitantes · listas parciales"
      />
      <div className="scope-banner">
        <Info size={20} />
        <div>
          <strong>Daños materiales del seguro</strong>
          <p>
            La cifra compara la frecuencia con la media española. +40 % significa una frecuencia un
            40 % mayor que esa media; no una probabilidad del 40 %. Las coberturas materiales y
            corporales pueden coexistir.
          </p>
        </div>
      </div>
      <div className="grid main-grid">
        <Panel
          title="Frecuencia relativa por municipio"
          subtitle="Diferencia frente a España · % · seguro de 2024"
          action={
            <Export
              rows={sorted}
              title="Daños del seguro por municipio"
              metadata={meta}
              chartId="insurance-chart"
            />
          }
        >
          <div id="insurance-chart">
            <Bars
              rows={sorted}
              valueKey="relative_difference_pct"
              nameKey="municipality"
              title="Diferencia relativa frente a España (%)"
              horizontal
            />
          </div>
        </Panel>
        <Panel title="Qué permite consultar la fuente" subtitle="Publicación agregada de UNESPA">
          <ul className="coverage-list">
            <li>
              Frecuencia relativa de daños materiales y corporales en los municipios publicados.
            </li>
            <li>Peso de cada cobertura y coste medio en el conjunto nacional.</li>
            <li>Recuentos provinciales del conjunto de coberturas, incluida asistencia.</li>
          </ul>
          <Note>
            La fuente pública no contiene recuentos completos de chapa por territorio ni
            vehículos-año asegurados. Ampliar esa comparación requiere una fuente autorizada con
            ambos datos y la misma cobertura.
          </Note>
          <a
            className="button"
            href="https://www.unespa.es/main-files/uploads/2026/02/NdP-Siniestros-del-seguro-de-auto-2024-FINAL.pdf"
            target="_blank"
            rel="noreferrer"
          >
            Consultar publicación
            <ArrowUpRight size={14} />
          </a>
        </Panel>
      </div>
      {data.tables.insurance_exposure?.length > 0 && (
        <Panel
          title="Panel asegurado con exposición compatible"
          subtitle="Fuente agregada autorizada · siniestros por 100 vehículos-año asegurados"
        >
          <label className="province-select">
            Año del panel asegurado
            <select
              value={
                data.tables.insurance_exposure.some((r) => r.year === f.year)
                  ? f.year
                  : Math.max(...data.tables.insurance_exposure.map((r) => number(r, 'year')!))
              }
              onChange={(e) => update({ year: Number(e.target.value) })}
            >
              {[...new Set(data.tables.insurance_exposure.map((r) => number(r, 'year')!))]
                .sort((a, b) => b - a)
                .map((year) => (
                  <option key={year}>{year}</option>
                ))}
            </select>
          </label>
          <Note>
            La exposición corresponde al mismo territorio, año, cobertura y cartera que los
            siniestros. Las coberturas se muestran por separado; esta frecuencia puede incluir
            varios siniestros por vehículo.
          </Note>
          <Export
            rows={insuredRows}
            title="Panel asegurado con exposición"
            metadata={metadata(
              data,
              { ...f, year: insuredYear },
              `Cartera agregada autorizada; año ${insuredYear}; siniestros / 100 vehículos-año asegurados; fuente y ámbito en cada fila`,
            )}
          />
          <DataTable
            rows={data.tables.insurance_exposure.filter(
              (r) =>
                r.year ===
                (data.tables.insurance_exposure.some((x) => x.year === f.year)
                  ? f.year
                  : Math.max(...data.tables.insurance_exposure.map((x) => number(x, 'year')!))),
            )}
            caption="Frecuencia asegurada con exposición compatible"
            columns={[
              { key: 'province_code', title: 'Código provincial' },
              { key: 'coverage', title: 'Cobertura' },
              { key: 'claims', title: 'Siniestros' },
              { key: 'insured_vehicle_years', title: 'Vehículos-año', digits: 1 },
              { key: 'claims_per_100_vehicle_years', title: 'Por 100 vehículos-año', digits: 2 },
              { key: 'publisher', title: 'Fuente' },
              {
                key: 'source_url',
                title: 'Publicación',
                render: (r) => (
                  <a href={String(r.source_url)} target="_blank" rel="noreferrer">
                    Fuente original
                  </a>
                ),
              },
            ]}
          />
        </Panel>
      )}
      <Panel
        title="Municipios de la selección"
        subtitle="La lista no representa a todos los municipios de España."
      >
        <DataTable
          rows={sorted}
          caption="Frecuencia municipal relativa del seguro"
          columns={[
            { key: 'municipality', title: 'Municipio' },
            { key: 'province_source', title: 'Provincia' },
            { key: 'relative_difference_pct', title: 'Diferencia frente a España (%)', digits: 2 },
            {
              key: 'selection',
              title: 'Lista',
              render: (r) => (r.selection === 'higher' ? 'Más alta' : 'Más baja'),
            },
          ]}
        />
      </Panel>
      <Panel
        title="Coberturas en el total nacional"
        subtitle="2024 · los siniestros de distintas coberturas no equivalen a accidentes únicos"
      >
        <DataTable
          rows={data.tables.insurance_coverage}
          limit={12}
          caption="Coberturas nacionales del seguro"
          columns={[
            { key: 'coverage', title: 'Cobertura' },
            { key: 'claims_share_pct', title: '% de siniestros', digits: 2 },
            { key: 'payments_share_pct', title: '% de pagos', digits: 2 },
            { key: 'mean_cost_eur', title: 'Coste medio (€)' },
          ]}
        />
      </Panel>
      <Panel
        title="Recuentos provinciales · todas las coberturas"
        subtitle="Incluyen asistencia, lunas y otras coberturas. No son un recuento de accidentes sin heridos."
        action={
          <Export
            rows={data.tables.insurance_provinces}
            title="Seguro todas las coberturas"
            metadata={metadata(
              data,
              f,
              'UNESPA 2024; 50 provincias; todas las coberturas; Ceuta/Melilla no publicadas',
            )}
          />
        }
      >
        <DataTable
          rows={data.tables.insurance_provinces}
          caption="Siniestros del seguro de todas las coberturas"
          columns={[
            { key: 'province_source', title: 'Provincia' },
            { key: 'all_coverage_claims', title: 'Siniestros de cobertura' },
            { key: 'all_coverage_payments_eur', title: 'Pagos (€)' },
          ]}
        />
        <Note>
          Las 50 provincias publicadas suman 11.053.508 siniestros frente a 11.071.215 nacionales.
          La diferencia se conserva sin atribuirla a territorios o causas.
        </Note>
      </Panel>
    </>
  )
}
