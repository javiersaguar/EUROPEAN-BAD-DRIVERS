import { fmt, pct, number, total, type Row } from '../data'
import { Panel, Stat, Note, SourceNote, DataTable } from '../components'
import type { PageProps } from './shared'
import { Evidence, Select, sexes, ages, group, UnknownNote } from './evidence'

const roles = {
  all_victims: 'Todas las víctimas',
  drivers_victims: 'Conductores víctimas',
  drivers_involved: 'Conductores implicados',
}
const outcomes = {
  fatalities: 'Fallecidos a 30 días',
  hospitalized: 'Heridos hospitalizados',
  non_hospitalized: 'Heridos no hospitalizados',
  casualties: 'Todas las víctimas',
}
const euRoles = {
  TOTAL: 'Todos los usuarios',
  DRIV: 'Conductores',
  PAS: 'Pasajeros',
  PED: 'Peatones',
  UNK: 'Usuario desconocido',
}
const users = [
  'Total',
  'Peatón',
  'Bicicleta',
  'VMP',
  'Ciclomotor',
  'Motocicleta',
  'Turismo',
  'Furgoneta',
  'Vehículo pesado',
  'Autobús',
  'Otros',
  'Desconocido',
]
export function Persons({ data, f, update }: PageProps) {
  const measure = f.personRole === 'drivers_involved' ? 'involved' : f.outcome,
    caption =
      measure === 'involved'
        ? 'Conductores implicados'
        : outcomes[measure as keyof typeof outcomes],
    base = data.tables.dgt_demographics.filter(
      (r) =>
        r.year === f.year &&
        r.role === f.personRole &&
        (f.zone === 'Total' || r.zone === f.zone) &&
        (f.age === 'Todas' || r.age_band === f.age),
    ),
    selected = base.filter((r) => r.category === f.user && (f.sex === 'T' || r.sex === f.sex)),
    sexRows = group(selected, 'sex', measure).map((r) => ({ ...r, name: sexes[String(r.sex)] })),
    ageRows = group(selected, 'age_band', measure).sort(
      (a, b) => ages.indexOf(String(a.age_band)) - ages.indexOf(String(b.age_band)),
    ),
    userRows = group(
      base.filter(
        (r) =>
          r.category !== 'Total' &&
          (f.user === 'Total' || r.category === f.user) &&
          (f.sex === 'T' || r.sex === f.sex),
      ),
      'category',
      measure,
    ),
    n = total(selected, measure),
    unknown = total(
      selected.filter((r) => r.sex === 'UNK'),
      measure,
    ),
    allSex = total(
      base.filter((r) => r.category === f.user),
      measure,
    ),
    trends = [2022, 2023, 2024].map((year) => ({
      year,
      value: total(
        data.tables.dgt_demographics.filter(
          (r) =>
            r.year === year &&
            r.role === f.personRole &&
            r.category === f.user &&
            (f.zone === 'Total' || r.zone === f.zone) &&
            (f.age === 'Todas' || r.age_band === f.age) &&
            (f.sex === 'T' || r.sex === f.sex),
        ),
        measure,
      ),
    })),
    spainSources = [`dgt_demographics_${f.year}`],
    rates = data.tables.spain_sex_rates.filter((r) => r.year === f.year),
    ageRates = ages
      .filter((a) => a !== 'Desconocida')
      .map((age) => ({
        age,
        M: number(
          data.tables.spain_age_sex_rates.find(
            (r) => r.year === f.year && r.sex === 'M' && r.age_band === age,
          ) ?? {},
          'fatalities_per_million',
        ),
        F: number(
          data.tables.spain_age_sex_rates.find(
            (r) => r.year === f.year && r.sex === 'F' && r.age_band === age,
          ) ?? {},
          'fatalities_per_million',
        ),
      })),
    standardRates = rates.map((r) => ({ ...r, name: sexes[String(r.sex)] })),
    standardizedM = number(rates.find((r) => r.sex === 'M') ?? {}, 'age_standardized_per_million'),
    standardizedF = number(rates.find((r) => r.sex === 'F') ?? {}, 'age_standardized_per_million'),
    eu = data.tables.europe_sex_users,
    euCountries = Object.fromEntries(
      eu
        .filter((r) => r.year === f.historyYear && r.sex === 'T' && r.pers_cat === 'TOTAL')
        .map((r) => [String(r.geo), String(r.country)]),
    ),
    euCurrent = eu.filter(
      (r) => r.geo === f.country && r.year === f.historyYear && r.pers_cat === f.euRole,
    ),
    euSelected = euCurrent.find((r) => r.sex === f.sex),
    euHistory = Array.from({ length: 15 }, (_, i) => 2010 + i).map((year) => ({
      year,
      ...Object.fromEntries(
        ['M', 'F', 'T'].map((sex) => [
          sex,
          number(
            eu.find(
              (r) =>
                r.geo === f.country && r.year === year && r.sex === sex && r.pers_cat === f.euRole,
            ) ?? {},
            'fatalities_per_million',
          ),
        ]),
      ),
    })),
    euRanking = eu
      .filter((r) => r.year === f.historyYear && r.sex === f.sex && r.pers_cat === f.euRole)
      .sort(
        (a, b) =>
          (number(b, 'fatalities_per_million') ?? -1) - (number(a, 'fatalities_per_million') ?? -1),
      )
  return (
    <>
      <SourceNote
        data={data}
        ids={spainSources}
        year={f.year}
        scope="España nacional · tablas administrativas de personas · vías urbanas e interurbanas"
      />
      <div className="filter-row">
        <Select
          title="Población analizada"
          value={f.personRole}
          options={roles}
          onChange={(v) =>
            update({
              personRole: v,
              user: v !== 'all_victims' && f.user === 'Peatón' ? 'Total' : f.user,
            })
          }
        />
        {f.personRole !== 'drivers_involved' && (
          <Select
            title="Resultado de las víctimas"
            value={f.outcome}
            options={outcomes}
            onChange={(v) => update({ outcome: v })}
          />
        )}
        <Select
          title="Sexo registrado"
          value={f.sex}
          options={sexes}
          onChange={(v) => update({ sex: v })}
        />
        <Select
          title="Edad de las personas"
          value={f.age}
          options={['Todas', ...ages]}
          onChange={(v) => update({ age: v })}
        />
        <Select
          title="Zona española"
          value={f.zone}
          options={['Total', 'Urbana', 'Interurbana']}
          onChange={(v) => update({ zone: v })}
        />
        <Select
          title="Tipo de usuario español"
          value={f.user}
          options={users.filter((v) => f.personRole === 'all_victims' || v !== 'Peatón')}
          onChange={(v) => update({ user: v })}
        />
      </div>
      <div className="stats">
        <Stat
          label={caption}
          value={fmt(n)}
          detail={`${roles[f.personRole as keyof typeof roles]} · ${f.year} · ${f.zone}`}
        />
        <Stat
          label="Selección entre todos los sexos"
          value={n == null || allSex == null || allSex === 0 ? 'Sin dato' : pct((n / allSex) * 100)}
          detail="Misma edad, zona, usuario y resultado"
        />
        <Stat
          label="Sexo desconocido · selección"
          value={fmt(unknown)}
          detail="Desconocido se conserva como categoría, sin asignación"
        />
      </div>
      <Note>
        La unidad es una persona, no un accidente. Un accidente puede incluir personas de varios
        sexos. «Implicado» no significa responsable y no permite asignar culpa. El sexo procede del
        registro administrativo; los recuentos no ajustan por cuánto conduce cada grupo.
      </Note>
      <div className="grid equal-grid">
        <Evidence
          data={data}
          f={f}
          id="persons-sex"
          title="Composición por sexo registrado"
          unit={`${caption} · ${f.user} · ${f.age} · ${f.zone} · ${f.year}`}
          rows={sexRows}
          xKey="name"
          valueKey={measure}
          sources={spainSources}
          interpretation={`${fmt(n)} personas en la selección. Los recuentos reflejan exposición, composición y gravedad; no identifican quién conduce mejor. La categoría desconocida participa en el total cuando se seleccionan todos los sexos.`}
        />
        <Evidence
          data={data}
          f={f}
          id="persons-age"
          title="Distribución por edad"
          unit={`${caption} · ${sexes[f.sex]} · ${f.user} · ${f.zone} · ${f.year}`}
          rows={ageRows}
          xKey="age_band"
          valueKey={measure}
          sources={spainSources}
          interpretation="Las cinco bandas conocidas no se solapan. La edad desconocida se conserva y no se reparte entre grupos. Un volumen mayor puede corresponder a una población o a una exposición mayor; se muestran tasas poblacionales en la sección siguiente."
        />
        <Evidence
          data={data}
          f={f}
          id="persons-user"
          title="Tipo de usuario y vehículo"
          unit={`${caption} · ${sexes[f.sex]} · ${f.age} · ${f.zone} · ${f.year}`}
          rows={userRows}
          xKey="category"
          valueKey={measure}
          horizontal
          sources={spainSources}
          interpretation={
            <>
              Los usuarios se agrupan a partir de las categorías publicadas. El Total se utiliza por
              separado y nunca se suma a sus componentes.
              <UnknownNote rows={userRows} keyName={measure} />
            </>
          }
        />
        <Evidence
          data={data}
          f={f}
          id="persons-trend"
          title="La misma selección a lo largo del tiempo"
          unit={`${caption} · ${sexes[f.sex]} · ${f.age} · ${f.user} · ${f.zone}`}
          rows={trends}
          xKey="year"
          series={[{ key: 'value', name: caption }]}
          sources={['dgt_demographics_2022', 'dgt_demographics_2023', 'dgt_demographics_2024']}
          interpretation="Se mantiene la misma definición y los mismos filtros en los tres años. Tres puntos describen evolución observada; no bastan para atribuir causas ni estimar una tendencia estable. Los valores ausentes interrumpen la línea."
        />
      </div>
      {f.year === 2024 && (
        <Panel
          title="Incidencias de la tabla original de 2024"
          subtitle="Los valores publicados no se sustituyen"
        >
          <p>
            En víctimas urbanas faltan todas las celdas de bicicleta. En conductores víctimas
            interurbanos, los componentes por vehículo superan al Total en 5 fallecidos, 5
            hospitalizados y 13 no hospitalizados. Los desgloses y el Total se conservan sin forzar
            porcentajes que sumen 100 %.
          </p>
          <Note>
            Falta además una celda Total de conductores de motocicleta implicados de 70–74 años en
            vías interurbanas. Los recuentos por sexo de esa celda están publicados; el Total
            ausente no se reconstruye. Los detalles y diferencias auditadas están documentados en el
            repositorio.
          </Note>
        </Panel>
      )}
      <div className="section-heading">
        <span className="eyebrow">Carga de mortalidad · España</span>
        <h2>Tasas por sexo y ajuste por edad</h2>
        <p>
          España completa · todas las víctimas fallecidas · {f.year}. Esta sección mantiene un
          ámbito fijo, independiente de los filtros de recuentos anteriores.
        </p>
      </div>
      <div className="grid equal-grid">
        <Evidence
          data={data}
          f={f}
          id="spain-age-rate"
          grouped
          title="Mortalidad por edad y sexo"
          unit={`Fallecidos / millón de habitantes de la misma edad y sexo · España ${f.year}`}
          rows={ageRates}
          xKey="age"
          series={[
            { key: 'M', name: 'Hombres' },
            { key: 'F', name: 'Mujeres' },
          ]}
          sources={[...spainSources, 'eurostat_es_age_population']}
          interpretation="Estas tasas ajustan por el tamaño poblacional de cada celda. Siguen sin medir riesgo por kilómetro ni distinguir intensidad de conducción. La edad desconocida se excluye de estas celdas y se informa en la tabla de tasas nacionales."
        />
        <Evidence
          data={data}
          f={f}
          id="spain-standard"
          grouped
          title="Bruta y ajustada: una estructura de edad común"
          unit={`Fallecidos / millón · estándar fijo España 2024 · año ${f.year}`}
          rows={standardRates}
          xKey="name"
          series={[
            { key: 'crude_per_million', name: 'Bruta' },
            { key: 'age_standardized_per_million', name: 'Ajustada por edad' },
          ]}
          sources={[...spainSources, 'eurostat_es_age_population']}
          interpretation={`La razón hombres/mujeres ajustada es ${fmt(standardizedM != null && standardizedF != null && standardizedF > 0 ? standardizedM / standardizedF : null, 2)}. El ajuste aplica a ambos sexos los mismos pesos poblacionales de cinco edades de 2024; controla esa composición, pero no kilómetros, ocupación del vehículo ni otros factores. El ajuste es una estimación puntual y excluye edad desconocida.`}
          columns={[
            { key: 'name', title: 'Sexo' },
            { key: 'fatalities', title: 'Fallecidos' },
            { key: 'population', title: 'Habitantes' },
            { key: 'crude_per_million', title: 'Bruta / millón', digits: 2 },
            { key: 'lower', title: 'IC Poisson inf.', digits: 2 },
            { key: 'upper', title: 'IC Poisson sup.', digits: 2 },
            { key: 'age_standardized_per_million', title: 'Ajustada / millón', digits: 2 },
            { key: 'unknown_age_deaths', title: 'Edad desconocida' },
          ]}
        />
      </div>
      <div className="section-heading">
        <span className="eyebrow">Perspectiva europea · 27 países</span>
        <h2>Sexo y papel de la persona en el accidente</h2>
        <p>
          Eurostat · 2010–2024 · fallecidos a 30 días. «Usuario» aquí distingue conductor, pasajero
          y peatón; no el tipo de vehículo. El sexo usa el filtro compartido de esta página.
        </p>
      </div>
      <div className="filter-row">
        <Select
          title="País del análisis por sexo"
          value={f.country}
          options={euCountries}
          onChange={(v) => update({ country: v })}
        />
        <Select
          title="Año europeo por sexo"
          value={f.historyYear}
          options={Array.from({ length: 15 }, (_, i) => String(2024 - i))}
          onChange={(v) => update({ historyYear: Number(v) })}
        />
        <Select
          title="Papel de la persona en Europa"
          value={f.euRole}
          options={euRoles}
          onChange={(v) => update({ euRole: v })}
        />
      </div>
      <div className="stats">
        <Stat
          label={`${euCountries[f.country]} · ${f.historyYear}`}
          value={fmt(number(euSelected ?? {}, 'fatalities'))}
          unit="fallecidos a 30 días"
          detail={`${euRoles[f.euRole as keyof typeof euRoles]} · ${sexes[f.sex]}`}
        />
        <Stat
          label="Tasa poblacional europea"
          value={fmt(number(euSelected ?? {}, 'fatalities_per_million'), 2)}
          unit="fallecidos / millón de habitantes del sexo"
          detail={
            f.sex === 'UNK'
              ? 'Sexo desconocido: no hay denominador poblacional'
              : 'Todas las edades; tasa bruta'
          }
        />
        <Stat
          label="Celdas con tasa disponible"
          value={`${euRanking.filter((r) => r.included).length} / 27`}
          detail="Países de este año, sexo y papel; no se imputan ausencias"
        />
      </div>
      <div className="grid equal-grid">
        <Evidence
          data={data}
          f={f}
          id="eu-sex-trend"
          title="Quince años por sexo: mismo país y papel"
          unit={`${euCountries[f.country]} · ${euRoles[f.euRole as keyof typeof euRoles]} · fallecidos / millón de habitantes del sexo`}
          rows={euHistory}
          xKey="year"
          series={[
            { key: 'M', name: 'Hombres' },
            { key: 'F', name: 'Mujeres' },
            { key: 'T', name: 'Total' },
          ]}
          sources={['eurostat_sex_users', 'eurostat_sex_population']}
          interpretation="Las líneas usan población del mismo sexo y año. El Total es un cociente propio y no el promedio de las tasas de hombres y mujeres. Las tasas brutas entre países no están ajustadas por edad ni por movilidad; las ausencias interrumpen la serie."
        />
        <Evidence
          data={data}
          f={f}
          scopeYear={f.historyYear}
          id="eu-sex-country"
          title="Comparación europea con cobertura visible"
          unit={`${f.historyYear} · ${sexes[f.sex]} · ${euRoles[f.euRole as keyof typeof euRoles]} · fallecidos / millón`}
          rows={euRanking}
          xKey="country"
          valueKey="fatalities_per_million"
          horizontal
          sources={['eurostat_sex_users', 'eurostat_sex_population']}
          interpretation="La comparación describe carga poblacional de mortalidad. Los protocolos nacionales, el registro y la composición pueden afectar a las diferencias. Una celda sin exposición compatible no recibe tasa; sus recuentos y banderas originales siguen en la descarga."
          columns={[
            { key: 'country', title: 'País' },
            { key: 'fatalities', title: 'Fallecidos' },
            { key: 'population', title: 'Población del sexo' },
            { key: 'fatalities_per_million', title: 'Tasa / millón', digits: 2 },
            { key: 'lower', title: 'IC inferior', digits: 2 },
            { key: 'upper', title: 'IC superior', digits: 2 },
            { key: 'fatalities_status', title: 'Bandera fallecidos' },
            { key: 'population_status', title: 'Bandera población' },
          ]}
        />
      </div>
      <Panel
        title="Recuentos europeos, incluido sexo desconocido"
        subtitle={`${euCountries[f.country]} · ${f.historyYear} · ${euRoles[f.euRole as keyof typeof euRoles]}`}
      >
        <DataTable
          rows={euCurrent.map((r: Row) => ({ ...r, name: sexes[String(r.sex)] }))}
          caption="Recuentos y exposición europeos por sexo"
          columns={[
            { key: 'name', title: 'Sexo' },
            { key: 'fatalities', title: 'Fallecidos' },
            { key: 'population', title: 'Habitantes del sexo' },
            { key: 'fatalities_per_million', title: 'Tasa / millón', digits: 2 },
            { key: 'fatalities_status', title: 'Bandera original' },
          ]}
        />
        <Note>
          Los componentes de usuario y sexo están anidados en sus Totales; nunca se suman con ellos.
          Los intervalos de Poisson del 95 % corresponden a un modelo de recuentos y no a errores de
          medición del censo administrativo.
        </Note>
      </Panel>
    </>
  )
}
