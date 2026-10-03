import { ArrowRight, Info } from 'lucide-react'
import { number } from '../data'
import { Panel, Note, DataTable, Lines, Export, metadata } from '../components'
import { type PageProps, SpainSource } from './shared'

export function Models({ data, f }: PageProps) {
  const metrics = data.tables.model_metrics,
    policy = data.tables.model_policy,
    pr = data.tables.model_pr_curve
      .filter((r) => r.model === 'hist_gradient_boosting')
      .map((r) => ({
        ...r,
        recall_pct: (number(r, 'recall') ?? 0) * 100,
        precision_pct: (number(r, 'precision') ?? 0) * 100,
      })),
    calibration = data.tables.model_calibration.filter((r) => r.model === 'hist_gradient_boosting')
  return (
    <>
      <SpainSource
        data={data}
        year={2024}
        scope="Gravedad condicionada a un siniestro ya registrado · evaluación temporal"
      />
      <div className="scope-banner">
        <Info size={20} />
        <div>
          <strong>Qué predice este modelo</strong>
          <p>
            Si un siniestro registrado incluye fallecidos o heridos hospitalizados. No estima tu
            probabilidad de tener un accidente ni permite inferir causas.
          </p>
        </div>
      </div>
      <div className="timeline">
        <span>
          <b>2022</b>Entrenamiento
        </span>
        <ArrowRight size={16} />
        <span>
          <b>2023</b>Selección y validación
        </span>
        <ArrowRight size={16} />
        <span>
          <b>2024</b>Evaluación original
        </span>
      </div>
      <Panel
        title="Comparación de modelos"
        subtitle="Evaluación de 2024 · baseline, regresión logística y boosting"
        action={
          <Export
            rows={metrics}
            title="Evaluación de modelos"
            metadata={metadata(
              data,
              f,
              'DGT; target gravedad de siniestro registrado; train2022 val2023 refit2022–2023 test2024',
            )}
          />
        }
      >
        <DataTable
          rows={metrics}
          caption="Métricas de modelos en 2024"
          columns={[
            { key: 'model', title: 'Modelo' },
            { key: 'roc_auc', title: 'ROC AUC', digits: 3 },
            { key: 'pr_auc', title: 'PR AUC', digits: 3 },
            { key: 'log_loss', title: 'Log loss', digits: 3 },
            { key: 'brier', title: 'Brier', digits: 3 },
            { key: 'precision', title: 'Precisión (umbral 0,5)', digits: 3 },
            { key: 'recall', title: 'Sensibilidad (0,5)', digits: 3 },
          ]}
        />
      </Panel>
      <div className="grid">
        <Panel title="Precisión y sensibilidad" subtitle="Curva de 2024 · boosting · porcentajes">
          <Lines
            rows={pr}
            xKey="recall_pct"
            series={[{ key: 'precision_pct', name: 'Precisión (%)' }]}
            title="Curva precisión sensibilidad"
            numericX
          />
          <details>
            <summary>Ver datos del gráfico</summary>
            <DataTable
              rows={pr}
              caption="Curva precisión sensibilidad"
              columns={[
                { key: 'recall_pct', title: 'Sensibilidad (%)', digits: 2 },
                { key: 'precision_pct', title: 'Precisión (%)', digits: 2 },
              ]}
            />
          </details>
        </Panel>
        <Panel title="Calibración" subtitle="Frecuencia observada frente a probabilidad predicha">
          <Lines
            rows={calibration}
            xKey="mean_prediction"
            series={[{ key: 'observed_frequency', name: 'Frecuencia observada' }]}
            title="Calibración de probabilidades"
            domain={[0, 1]}
            numericX
          />
          <DataTable
            rows={calibration}
            caption="Calibración del boosting"
            columns={[
              { key: 'mean_prediction', title: 'Predicción media', digits: 3 },
              { key: 'observed_frequency', title: 'Frecuencia observada', digits: 3 },
              { key: 'n', title: 'Siniestros' },
            ]}
          />
        </Panel>
      </div>
      <Panel
        title="Estudio exploratorio de umbrales"
        subtitle="Modelo entrenado solo en 2022 · umbral F2 elegido en 2023 · evaluación descriptiva en 2024"
      >
        <DataTable
          rows={policy}
          caption="Tradeoff de umbral de decisión"
          columns={[
            { key: 'policy', title: 'Política' },
            { key: 'threshold', title: 'Umbral', digits: 4 },
            { key: 'precision', title: 'Precisión', digits: 3 },
            { key: 'recall', title: 'Sensibilidad', digits: 3 },
            { key: 'fp', title: 'Falsos positivos' },
            { key: 'fn', title: 'Falsos negativos' },
          ]}
        />
        <Note>
          El umbral F2 recupera más casos graves a costa de muchos falsos positivos. Como 2024 ya
          había sido examinado en el proyecto, este estudio necesita un nuevo año reservado para
          validación confirmatoria. No sustituye los resultados del modelo original.
        </Note>
      </Panel>
      <Panel
        title="Interpretación del modelo"
        subtitle="Importancia por permutación y explicación local · asociaciones estadísticas"
      >
        <DataTable
          rows={data.tables.model_permutation_importance}
          caption="Importancia por permutación"
          columns={Object.keys(data.tables.model_permutation_importance[0] ?? {}).map((key) => ({
            key,
            title: key,
            digits: 3,
          }))}
        />
        <details>
          <summary>Ver resumen SHAP · casos reservados</summary>
          <img
            className="shap"
            src={`${import.meta.env.BASE_URL}figures/model_shap_summary.png`}
            alt="Resumen SHAP del modelo: contribuciones en log-odds de las variables observadas; no representa causalidad."
            loading="lazy"
          />
          <Note>
            400 siniestros reservados. SHAP describe contribuciones al score en log-odds, no efectos
            causales.
          </Note>
        </details>
      </Panel>
    </>
  )
}
