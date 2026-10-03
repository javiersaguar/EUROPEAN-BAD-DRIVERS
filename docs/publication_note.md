# Publication draft

Optional post text for Javier to edit and publish. No external post has been sent.

**¿Se puede medir dónde conducimos peor?**

He convertido esa pregunta en un proyecto reproducible con datos oficiales de DGT, INE y Eurostat: European Bad Drivers Index.

El nombre es provocador, pero el análisis mide siniestralidad registrada y carga territorial. Analicé 301.218 siniestros con víctimas de 2022–2024, comparé tasas por población, parque y permisos de conducir, y construí un laboratorio para cambiar indicadores, pesos y normalización.

En 2024, los rankings de tasas de siniestros y mortalidad tienen una correlación de −0,352. Y una provincia puede recorrer hasta 50 posiciones al cambiar los pesos entre 500 escenarios. La respuesta depende mucho de la pregunta que hacemos.

El proyecto incluye una capa de datos con hashes, validaciones, Parquet y DuckDB; intervalos y sensibilidad; un dashboard; notebooks ejecutados; y un modelo de gravedad condicionado a que el siniestro ya esté registrado, con evaluación temporal y SHAP. No calcula tu probabilidad anual de tener un accidente.

También investigué seguros y kilómetros recorridos. Las fuentes auditadas no ofrecen aquí un panel moderno y comparable con el denominador necesario, así que documenté esa limitación en vez de fabricar una comparación. La extensión a UE-27 se limita a mortalidad a 30 días por población.

Lo interesante no es proclamar quién conduce peor. Es mostrar qué mide realmente cada indicador y cómo las decisiones metodológicas cambian los resultados.

[Código, metodología y resultados](https://github.com/javiersaguar/EUROPEAN-BAD-DRIVERS)

## Suggested original figures

- `outputs/figures/weight_sensitivity.png`: methodological choice and rank movement.
- `outputs/figures/injury_vs_fatality.png`: different outcomes, different territorial burdens.
- `outputs/figures/dashboard_overview.png`: dashboard with definitions and actual totals.

Use the underlying counts/denominators and limitations when sharing charts. Weight scenario ranges are not confidence intervals. Do not state that insurance claims or vehicle-kilometres were combined into the modern index, or that the model identifies causal effects or individual driving risk.
