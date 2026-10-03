import { fmt, pct, number, type Row } from '../data'
import { Stat, Note, SourceNote } from '../components'
import type { PageProps } from './shared'
import { sort } from './shared'
import { Evidence, Select } from './evidence'

export function Circumstances({ data, f, update }: PageProps) {
  const rows = data.tables.collision_analysis.filter(
      (r) => r.year === f.year && r.zone === f.zone && !r.is_total,
    ),
    parent = data.tables.collision_analysis.find(
      (r) => r.year === f.year && r.zone === f.zone && r.is_total,
    )!,
    types = data.tables.vehicle_age_analysis,
    zone =
      f.zone === 'Total' ? 'Total' : f.zone === 'Urbana' ? 'Vías urbanas' : 'Vías interurbanas',
    ageRows = types.filter(
      (r) => r.year === f.year && r.zone === zone && r.category === f.vehicle && r.age !== 'Total',
    ),
    vehicleTypes = [...new Set(types.map((r) => String(r.category)))],
    old = ageRows.find((r) => r.age === 'Más de 15 años'),
    unknown = ageRows.find((r) => r.age === 'Se desconoce'),
    ageTrend: Row[] = [2022, 2023, 2024].map((year) => ({
      year,
      older: number(
        types.find(
          (r) =>
            r.year === year &&
            r.zone === zone &&
            r.category === f.vehicle &&
            r.age === 'Más de 15 años',
        ) ?? {},
        'share_all_pct',
      ),
      unknown: number(
        types.find(
          (r) =>
            r.year === year &&
            r.zone === zone &&
            r.category === f.vehicle &&
            r.age === 'Se desconoce',
        ) ?? {},
        'share_all_pct',
      ),
    })),
    source = [`dgt_demographics_${f.year}`]
  return (
    <>
      <div className="filter-row">
        <Select
          title="Zona del accidente"
          value={f.zone}
          options={['Total', 'Urbana', 'Interurbana']}
          onChange={(v) => update({ zone: v })}
        />
        <Select
          title="Vehículos en el análisis de antigüedad"
          value={f.vehicle}
          options={vehicleTypes}
          onChange={(v) => update({ vehicle: v })}
        />
      </div>
      <SourceNote
        data={data}
        ids={source}
        year={f.year}
        scope={`España · ${f.zone} · tabla 1.3 de accidentes y tabla 8.3 de vehículos`}
      />
      <div className="stats">
        <Stat
          label="Siniestros con víctimas"
          value={fmt(number(parent, 'crashes'))}
          detail={`${f.year} · ${f.zone} · 21 categorías excluyentes`}
        />
        <Stat
          label="Accidentes mortales"
          value={fmt(number(parent, 'fatal_crashes'))}
          detail="Un accidente mortal puede tener varias víctimas"
        />
        <Stat
          label="Fracción mortal del registro"
          value={pct(number(parent, 'fatal_crash_pct'), 2)}
          detail="Accidentes mortales / accidentes con víctimas"
        />
      </div>
      <div className="grid equal-grid">
        <Evidence
          data={data}
          f={f}
          id="collision-volume"
          title="Qué tipos concentran los accidentes"
          unit={`Siniestros con víctimas · España ${f.year} · ${f.zone}`}
          rows={sort(rows, 'crashes')}
          xKey="category"
          valueKey="crashes"
          horizontal
          sources={source}
          interpretation="Las 21 categorías suman exactamente el Total publicado; se muestran sin duplicar ese Total. El volumen explica la contribución al registro, pero no el riesgo de encontrarse con ese tipo de accidente durante un viaje."
          columns={[
            { key: 'category', title: 'Tipo' },
            { key: 'crashes', title: 'Siniestros' },
            { key: 'crash_share_pct', title: 'Cuota (%)', digits: 2 },
          ]}
        />
        <Evidence
          data={data}
          f={f}
          id="collision-severity"
          title="Gravedad condicional al tipo de accidente"
          unit={`Accidentes mortales / siniestros con víctimas · % · ${f.zone} ${f.year}`}
          rows={sort(rows, 'fatal_crash_pct')}
          xKey="category"
          valueKey="fatal_crash_pct"
          horizontal
          sources={source}
          interpretation="Una categoría puede tener poco volumen y una fracción mortal alta. Se informa del denominador y del intervalo Wilson del 95 %; las celdas con menos de 100 accidentes requieren especial cautela. Esta fracción condiciona a que ya ocurrió un accidente con víctimas."
          columns={[
            { key: 'category', title: 'Tipo' },
            { key: 'crashes', title: 'Denominador' },
            { key: 'fatal_crashes', title: 'Mortales' },
            { key: 'fatal_crash_pct', title: 'Fracción mortal (%)', digits: 2 },
            { key: 'lower', title: 'Wilson inferior', digits: 2 },
            { key: 'upper', title: 'Wilson superior', digits: 2 },
            { key: 'small_sample', title: 'Menos de 100' },
          ]}
        />
      </div>
      <Note>
        El tipo de accidente no contiene sexo: la información de personas se analiza en «Personas y
        sexo». No se crea un cruce individual entre tablas agregadas. Los intervalos describen un
        modelo condicional, no una duda sobre los totales enumerados.
      </Note>
      <div className="section-heading">
        <span className="eyebrow">Vehículos implicados · España</span>
        <h2>Antigüedad y calidad del registro</h2>
        <p>
          Vehículos de motor en accidentes con víctimas. Cada vehículo implicado cuenta una vez en
          la tabla; varios pueden pertenecer al mismo accidente.
        </p>
      </div>
      <div className="stats">
        <Stat
          label="Más de 15 años"
          value={fmt(number(old ?? {}, 'vehicles'))}
          detail={`${f.vehicle} · ${zone} · ${f.year}`}
        />
        <Stat
          label="Cuota de vehículos de más de 15 años"
          value={pct(number(old ?? {}, 'share_all_pct'), 2)}
          detail="Incluye edad desconocida en el denominador"
        />
        <Stat
          label="Edad desconocida"
          value={pct(number(unknown ?? {}, 'share_all_pct'), 2)}
          detail="Se informa y no se reparte entre edades"
        />
      </div>
      <div className="grid equal-grid">
        <Evidence
          data={data}
          f={f}
          id="vehicle-age"
          title="Antigüedad de los vehículos implicados"
          unit={`Vehículos de motor · ${f.vehicle} · ${zone} · ${f.year}`}
          rows={ageRows}
          xKey="age"
          valueKey="vehicles"
          horizontal
          sources={source}
          interpretation="Esta distribución usa todas las edades publicadas, incluida la desconocida. Para medir riesgo por antigüedad se necesitaría la flota o los kilómetros de cada grupo de edad; el recuento de vehículos implicados no proporciona ese denominador."
          columns={[
            { key: 'age', title: 'Antigüedad' },
            { key: 'vehicles', title: 'Vehículos' },
            { key: 'share_all_pct', title: 'Cuota con desconocidos (%)', digits: 2 },
          ]}
        />
        <Evidence
          data={data}
          f={f}
          id="vehicle-age-trend"
          title="Vehículos antiguos y edades desconocidas"
          unit={`% de vehículos implicados · ${f.vehicle} · ${zone} · 2022–2024`}
          rows={ageTrend}
          xKey="year"
          series={[
            { key: 'older', name: 'Más de 15 años' },
            { key: 'unknown', name: 'Edad desconocida' },
          ]}
          sources={['dgt_demographics_2022', 'dgt_demographics_2023', 'dgt_demographics_2024']}
          interpretation="La lectura temporal debe considerar el porcentaje de edades desconocidas: un cambio en la completitud puede modificar la distribución observada. Estas series no prueban un efecto causal de la edad del vehículo sobre los accidentes."
        />
      </div>
      {f.year === 2024 && (
        <Note>
          La tabla 8.3 de 2024 contiene una columna numérica sin etiqueta. El Total supera a los
          tipos etiquetados en 87 vehículos de edad desconocida: 24 interurbanos y 63 urbanos. Se
          conserva el Total publicado y no se inventa un tipo de vehículo para cubrir la diferencia.
        </Note>
      )}
    </>
  )
}
