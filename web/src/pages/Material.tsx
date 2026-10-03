import { fmt, pct, number, type Row } from '../data'
import { Panel, Stat, Note, SourceNote, DataTable } from '../components'
import type { PageProps } from './shared'
import { sort } from './shared'
import { Evidence, Select, change } from './evidence'

const claimTypes = [
  'Daños materiales',
  'Daños propios por accidente',
  'Daños materiales a terceros',
  'Lunas',
  'Incendio y robo',
  'Lesiones',
  'Total',
]
const pureDamage = [
  'Daños propios por accidente',
  'Daños materiales a terceros',
  'Lunas',
  'Incendio y robo',
]
const irish = ['ncid_motor_2024', 'ncid_methodology', 'eurostat_ie_hicp']
const german = ['destatis_damage_history', 'destatis_damage_2024']

export function Material({ data, f, update }: PageProps) {
  const settled = f.claimBasis === 'settled',
    availableTypes = settled
      ? claimTypes.filter((v) => !['Lesiones', 'Total'].includes(v))
      : claimTypes,
    claim = availableTypes.includes(f.claim) ? f.claim : 'Daños materiales',
    all = data.tables[settled ? 'ncid_settled' : 'ncid_ultimate'],
    series = all
      .filter((r) => r.category === claim)
      .sort((a, b) => Number(a.year) - Number(b.year)),
    actualYear = settled ? Math.max(2015, f.historyYear) : f.historyYear,
    current = series.find((r) => r.year === actualYear),
    prior = series.find((r) => r.year === 2019),
    count = settled ? 'settled_claims' : 'ultimate_claims',
    mix = all.filter((r) => r.year === actualYear && pureDamage.includes(String(r.category))),
    frequency = number(current ?? {}, 'frequency_per_1000_all_policies'),
    history = data.tables.material_history,
    last = history.find((r) => r.year === f.historyYear)!,
    deStates = data.tables.material_states.filter(
      (r) => r.state !== 'Deutschland' && r.location === f.germanLocation,
    ),
    deTotal = data.tables.material_states.find(
      (r) => r.state === 'Deutschland' && r.location === f.germanLocation,
    )!
  const values: Row[] = series.map((r) => ({ ...r }))
  return (
    <>
      <div className="scope-banner">
        <div>
          <strong>Dos fuentes completas dentro de su ámbito</strong>
          <p>
            Irlanda: reclamaciones de seguros privados de automóvil. Alemania: accidentes
            registrados por la policía, incluidos los que solo causaron daños materiales. Se
            analizan por separado, con series y categorías propias.
          </p>
        </div>
      </div>
      <div className="filter-row">
        <Select
          title="Año histórico"
          value={f.historyYear}
          options={Array.from({ length: 15 }, (_, i) => String(2024 - i))}
          onChange={(v) => update({ historyYear: Number(v) })}
        />
        <Select
          title="Base de reclamaciones"
          value={f.claimBasis}
          options={{
            ultimate: 'Año de ocurrencia · estimación final',
            settled: 'Año de liquidación · pagadas',
          }}
          onChange={(v) =>
            update({
              claimBasis: v,
              claim:
                v === 'settled' && ['Lesiones', 'Total'].includes(f.claim)
                  ? 'Daños materiales'
                  : f.claim,
            })
          }
        />
        <Select
          title="Tipo de reclamación"
          value={claim}
          options={availableTypes}
          onChange={(v) => update({ claim: v })}
        />
      </div>
      {settled && f.historyYear < 2015 && (
        <Note>
          El anexo de liquidaciones empieza en 2015. La selección irlandesa muestra 2015; el año
          alemán sigue siendo {f.historyYear}.
        </Note>
      )}
      <SourceNote
        data={data}
        ids={irish}
        year={actualYear}
        scope={`Irlanda · ${claim} · ${settled ? 'liquidación final' : 'estimación por ocurrencia, incluye nulos'}`}
      />
      <div className="stats">
        <Stat
          label={`${settled ? 'Reclamaciones liquidadas' : 'Reclamaciones estimadas'} · ${actualYear}`}
          value={fmt(number(current ?? {}, count), settled ? 0 : 1)}
          detail={`${claim} · ${change(number(current ?? {}, count), number(prior ?? {}, count))}`}
        />
        <Stat
          label={settled ? 'Coste medio liquidado' : 'Frecuencia en la cartera'}
          value={fmt(settled ? number(current ?? {}, 'mean_cost_eur') : frequency, 2)}
          unit={settled ? '€/reclamación' : 'reclamaciones / 1.000 pólizas-año'}
          detail={
            settled
              ? 'Sin denominador de exposición comparable'
              : 'La misma cartera UltData en numerador y exposición'
          }
        />
        <Stat
          label="Coste medio"
          value={fmt(number(current ?? {}, 'mean_cost_eur'), 2)}
          unit="euros nominales / reclamación"
          detail={
            change(
              number(current ?? {}, 'mean_cost_2024_eur'),
              number(prior ?? {}, 'mean_cost_2024_eur'),
            ) + ' en euros de 2024'
          }
        />
      </div>
      <Note>
        {settled
          ? 'Las reclamaciones liquidadas pueden proceder de accidentes de años anteriores. No se dividen por las pólizas del año de pago ni se comparan como si fueran la misma cohorte de las estimaciones.'
          : 'Las cifras finales son estimaciones actuariales revisables, incluyen reclamaciones sin indemnización y pueden ser fraccionarias. No llevan intervalos de Poisson. La frecuencia de cartera puede incluir más de una reclamación por póliza y no es una probabilidad individual.'}{' '}
        La cobertura del mercado de 2024 es del {settled ? '88' : '94'} % de las primas devengadas;
        no del número de conductores.
      </Note>
      <div className="grid equal-grid">
        <Evidence
          data={data}
          f={f}
          id="claim-count"
          title="Evolución de las reclamaciones"
          unit={`Irlanda · ${claim} · ${settled ? 'recuentos por liquidación' : 'estimaciones por ocurrencia'}`}
          rows={values}
          xKey="year"
          series={[{ key: count, name: 'Reclamaciones' }]}
          sources={irish}
          interpretation={`${actualYear}: ${fmt(number(current ?? {}, count), settled ? 0 : 1)} reclamaciones; ${change(number(current ?? {}, count), number(prior ?? {}, count))}. El volumen combina exposición, frecuencia y cobertura del registro; por sí solo no mide riesgo.`}
        />
        <Evidence
          data={data}
          f={f}
          id="claim-cost"
          title="Costes nominales y poder adquisitivo"
          unit={`Irlanda · ${claim} · euros por reclamación`}
          rows={values}
          xKey="year"
          series={[
            { key: 'mean_cost_eur', name: 'Euros nominales' },
            { key: 'mean_cost_2024_eur', name: 'Euros de 2024' },
          ]}
          sources={irish}
          interpretation={`El coste en euros constantes cambia ${change(number(current ?? {}, 'mean_cost_2024_eur'), number(prior ?? {}, 'mean_cost_2024_eur'))}. El deflactor es el HICP general de Irlanda; no identifica cuánto de la variación procede de piezas, mano de obra o cambios en la mezcla de daños.`}
        />
      </div>
      {!settled && (
        <div className="grid equal-grid">
          <Evidence
            data={data}
            f={f}
            id="claim-frequency"
            title="Frecuencia con exposición compatible"
            unit="Reclamaciones estimadas / 1.000 pólizas-año de cartera"
            rows={values}
            xKey="year"
            series={[{ key: 'frequency_per_1000_all_policies', name: 'Cartera completa' }]}
            sources={irish}
            interpretation={`${actualYear}: ${fmt(frequency, 2)} por 1.000 pólizas-año; ${change(frequency, number(prior ?? {}, 'frequency_per_1000_all_policies'))}. Se usa la exposición del propio UltData, sin mezclarla con PremData. ${claim === 'Daños propios por accidente' ? `La frecuencia por pólizas comprehensive es ${fmt(number(current ?? {}, 'frequency_per_1000_comprehensive'), 2)} por 1.000.` : 'El anexo solo permite exposición de cobertura específica para daños propios; el resto se analiza por cartera completa.'}`}
          />
          <Evidence
            data={data}
            f={f}
            id="claim-burden"
            title="Coste agregado por póliza de cartera"
            unit="Euros nominales estimados / póliza-año · incluye reclamaciones nulas"
            rows={values}
            xKey="year"
            series={[{ key: 'cost_per_policy_eur', name: 'Coste por póliza-año' }]}
            sources={irish}
            interpretation={`En ${actualYear}, ${fmt(number(current ?? {}, 'cost_per_policy_eur'), 2)} €/póliza-año. El coste equivale a frecuencia × coste medio; describe la carga de siniestros de la cartera y no la prima comercial ni un precio de reparación.`}
          />
        </div>
      )}
      <div className="grid equal-grid">
        <Evidence
          data={data}
          f={{ ...f, historyYear: actualYear }}
          id="damage-mix"
          title="Composición de los daños materiales"
          unit={`Irlanda ${actualYear} · ${settled ? 'reclamaciones liquidadas' : 'estimaciones por ocurrencia'} · cuatro categorías excluyentes`}
          rows={mix}
          xKey="category"
          valueKey={count}
          horizontal
          sources={irish}
          interpretation="Daños propios y daños a terceros aproximan mejor las colisiones de chapa. Lunas, incendio y robo se mantienen separados porque no todos proceden de una colisión. Una colisión puede generar varias reclamaciones; no son accidentes únicos."
        />
        <Panel
          title="Auditoría de los anexos"
          subtitle="Totales conservados y diferencias documentadas"
        >
          <p>
            En 2024, la tabla 14 registra 139.433 liquidaciones materiales y coincide con la tabla
            11. El resumen de la tabla 12 presenta 139.415: una diferencia de 18 que se conserva y
            documenta.
          </p>
          <Note>
            Las bandas de coste de lesiones no particionan exactamente el total estimado. El total
            de lesiones se toma de la fila publicada y no de la suma de sus bandas. Las
            reclamaciones de lesiones permanecen separadas de los daños materiales.
          </Note>
          <DataTable
            rows={mix}
            caption="Tipos de daños asegurados"
            columns={[
              { key: 'category', title: 'Tipo' },
              { key: count, title: 'Reclamaciones', digits: settled ? 0 : 1 },
              { key: 'mean_cost_eur', title: 'Coste medio (€)', digits: 2 },
            ]}
          />
        </Panel>
      </div>
      <div className="section-heading">
        <span className="eyebrow">Accidentes policiales · Alemania</span>
        <h2>Accidentes sin víctimas, con daños materiales</h2>
        <p>
          La unidad aquí es el accidente registrado por la policía. Se excluyen los daños que no
          llegaron a ese registro.
        </p>
      </div>
      <div className="stats">
        <Stat
          label={`Solo daños materiales · ${f.historyYear}`}
          value={fmt(number(last, 'property_only_crashes'))}
          detail="Alemania · todos los tipos de daño policial"
        />
        <Stat
          label="Peso entre accidentes registrados"
          value={pct(number(last, 'property_only_share_pct'), 2)}
          detail="Denominador: todos los accidentes registrados"
        />
        <Stat
          label="Con víctimas"
          value={fmt(number(last, 'injury_crashes'))}
          detail="Categoría separada y excluyente respecto a solo daños"
        />
      </div>
      <div className="grid equal-grid">
        <Evidence
          data={data}
          f={f}
          id="german-count"
          title="Daños materiales y accidentes con víctimas"
          unit="Alemania · accidentes registrados por la policía · 2010–2024"
          rows={history}
          xKey="year"
          series={[
            { key: 'property_only_crashes', name: 'Solo daños materiales' },
            { key: 'injury_crashes', name: 'Con víctimas' },
          ]}
          sources={german}
          interpretation={`En ${f.historyYear}, ${fmt(number(last, 'property_only_crashes'))} accidentes causaron solo daños materiales. Las dos categorías suman el total policial; su escala depende también de la propensión a denunciar y de las reglas de registro.`}
        />
        <Evidence
          data={data}
          f={f}
          id="german-share"
          title="Peso de los accidentes sin víctimas"
          unit="% de accidentes policiales con solo daños materiales · Alemania"
          rows={history}
          xKey="year"
          series={[{ key: 'property_only_share_pct', name: 'Solo daños / total registrado (%)' }]}
          sources={german}
          interpretation={`${pct(number(last, 'property_only_share_pct'), 2)} del registro policial corresponde a solo daños en ${f.historyYear}. Una cuota elevada no significa que conducir allí sea más seguro: depende de ambos recuentos y de la cobertura administrativa.`}
        />
      </div>
      <div className="filter-row">
        <Select
          title="Localización alemana · 2024"
          value={f.germanLocation}
          options={['Total', 'Urbana', 'Interurbana sin autopistas', 'Autopista']}
          onChange={(v) => update({ germanLocation: v })}
        />
      </div>
      <div className="grid equal-grid">
        <Evidence
          data={data}
          f={{ ...f, historyYear: 2024 }}
          id="german-states"
          title="Daños materiales por estado federal"
          unit={`Alemania 2024 · ${f.germanLocation} · accidentes con solo daños`}
          rows={sort(deStates, 'property_only_crashes')}
          xKey="state"
          valueKey="property_only_crashes"
          horizontal
          sources={german}
          interpretation="Los recuentos miden volumen, sin ajustar por kilómetros, flota o población. Berlín no publica la localización interurbana sin autopistas: se muestra como ausente en la tabla y nunca se convierte en cero."
          columns={[
            { key: 'state', title: 'Estado' },
            { key: 'property_only_crashes', title: 'Solo daños' },
            { key: 'total_crashes', title: 'Total registrado' },
            { key: 'property_only_share_pct', title: 'Cuota solo daños (%)', digits: 2 },
          ]}
        />
        <Evidence
          data={data}
          f={{ ...f, historyYear: 2024 }}
          id="german-types"
          horizontal
          title="Clases de daños en el registro policial"
          unit={`Alemania 2024 · ${f.germanLocation} · categorías excluyentes`}
          rows={[
            { category: 'Daños graves', count: number(deTotal, 'serious_property_crashes') },
            {
              category: 'Otros bajo intoxicantes',
              count: number(deTotal, 'intoxicant_property_crashes'),
            },
            {
              category: 'Otros daños materiales',
              count: number(deTotal, 'other_property_crashes'),
            },
          ]}
          xKey="category"
          valueKey="count"
          sources={german}
          interpretation="Las tres clases suman todos los accidentes con solo daños de esta localización. La clasificación de daños graves de Destatis no representa víctimas graves. Estas cifras no se extrapolan a España ni se mezclan con la frecuencia aseguradora irlandesa."
        />
      </div>
      <Note>
        España sigue teniendo la selección municipal de UNESPA en «Golpes de chapa». Estas fuentes
        amplían el análisis europeo, pero no aportan una serie completa de chapa por provincia
        española, sexo del conductor o kilómetros recorridos.
      </Note>
    </>
  )
}
