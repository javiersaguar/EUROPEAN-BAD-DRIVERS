import { ArrowUpRight, Info } from 'lucide-react'
import { fmt, type Row } from '../data'
import { Panel, Stat, Note, Export, metadata } from '../components'
import { type PageProps } from './shared'

export function Sources({ data, f }: PageProps) {
  const groups = [
    { label: 'España', keys: ['dgt', 'ine', 'gisco'] },
    { label: 'Europa', keys: ['eurostat', 'erso'] },
    { label: 'Seguro y movilidad', keys: ['unespa', 'transport', 'insurance'] },
  ]
  return (
    <>
      <div className="stats">
        <Stat
          label="Fuentes registradas"
          value={fmt(data.sources.length)}
          detail="Descargas originales con hash y metadatos"
        />
        <Stat
          label="Panel provincial"
          value="156 filas"
          detail="52 provincias × 3 años · denominadores completos"
        />
        <Stat
          label="Versión publicada"
          value={data.release}
          detail={`Corte de verificación: ${data.audit_date}`}
        />
      </div>
      <div className="scope-banner">
        <Info size={20} />
        <div>
          <strong>Tres ámbitos, tres lecturas</strong>
          <p>
            DGT: siniestros con víctimas en España. Eurostat: mortalidad vial europea. UNESPA:
            siniestros por coberturas del seguro. La procedencia y las unidades aparecen antes de
            cada gráfico.
          </p>
        </div>
      </div>
      {groups.map((g) => (
        <Panel
          key={g.label}
          title={g.label}
          subtitle="Acceso a publicaciones originales y condiciones de uso"
        >
          <div className="source-cards">
            {data.sources
              .filter((s) => g.keys.some((k) => s.id.startsWith(k)))
              .map((s) => (
                <article key={s.id}>
                  <span className="eyebrow">
                    {s.organization} ·{' '}
                    {s.years.length > 4 ? `${s.years[0]}–${s.years.at(-1)}` : s.years.join(', ')}
                  </span>
                  <h3>{s.dataset_title}</h3>
                  {!s.enabled && (
                    <span className="badge">Registrada · no utilizada en el panel actual</span>
                  )}
                  <p>
                    {s.geographic_level} · {s.observation_unit}
                  </p>
                  <a href={s.page_url || s.url} target="_blank" rel="noreferrer">
                    Publicación original
                    <ArrowUpRight size={13} />
                  </a>
                  <details>
                    <summary>Definición, cobertura y licencia</summary>
                    <p>
                      <b>Denominador:</b> {s.denominator}
                    </p>
                    <p>{s.known_limitations}</p>
                    <a href={s.license_url || s.page_url || s.url} target="_blank" rel="noreferrer">
                      Condiciones de reutilización
                    </a>
                    <p className="hash">SHA-256: {s.sample_sha256}</p>
                    <p>Verificado: {s.sample_retrieved_at}</p>
                  </details>
                </article>
              ))}
          </div>
        </Panel>
      ))}
      <Panel
        title="Calidad y trazabilidad"
        subtitle="Los nuevos originales se ponen en cuarentena si cambia el contrato."
      >
        <p>
          Los datos publicados son agregados. Los valores ausentes se mantienen como ausentes; los
          cocientes nacionales se calculan con los totales.
        </p>
        <details>
          <summary>Auditorías de cobertura y reconciliación</summary>
          <pre>
            {JSON.stringify(
              { spain: data.data_quality, insurance: data.insurance_quality },
              null,
              2,
            )}
          </pre>
        </details>
        <Export
          rows={data.sources as unknown as Row[]}
          title="Catálogo de fuentes"
          metadata={metadata(data, f, 'Catálogo verificado; hashes de fuente y cobertura')}
        />
        <p>
          <a
            href="https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS"
            target="_blank"
            rel="noreferrer"
          >
            Código, metodología y versiones
            <ArrowUpRight size={13} />
          </a>
        </p>
        <Note>
          Cartografía derivada de GISCO · © EuroGeographics. El repositorio documenta los contratos,
          las transformaciones y las limitaciones de cada publicación.
        </Note>
      </Panel>
    </>
  )
}
