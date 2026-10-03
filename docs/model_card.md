# Conditional-severity model card

**Target:** whether a recorded injury crash includes a fatality or hospitalized injured person at 30 days.
**This is not P(accident | person) and not personal annual risk.**

Training: 2022 (97,916 records); validation: 2023 (101,306); test: 2024 (101,996).
Select by validation log loss, then refit on 2022–2023. The holdout is untouched during model and threshold selection.
Selected model: `hist_gradient_boosting`. Test ROC-AUC 0.703, PR-AUC 0.234,
log loss 0.2957, Brier score 0.0831.
All candidate results, prevalence, sample sizes and confusion matrices are in `outputs/tables/model_metrics.csv`.

The three baselines are a prior-frequency dummy, logistic regression and histogram gradient boosting.
Boosting is tested against simpler baselines without adding a heavyweight XGBoost dependency. There is no hyperparameter
search on 2024. A fixed 0.5 threshold is reported for completeness; it is not an operational recommendation.

Predictors: recorded province, urban/interurban environment, road and collision type, junction, weather, lighting,
surface, weekday and cyclic hour/month encodings. No victim totals, fatality-by-category counts, IDs or outcome-derived
variables are predictors. Unknown codes remain explicit categories. Driver demographics and vehicle ages do not exist here.
Some attributes are recorded or reconstructed after the crash; this is a descriptive research model, not a live forecast.

Explainability uses reproducible holdout permutation importance (5,000 rows; three repeats), with standard deviations.
Correlated predictors can dilute importance. Calibration bins include sample sizes; sparse bins are unstable.
Optional TreeSHAP explains a seeded 400-row 2024 sample in raw log-odds. Run `uv run --extra explain ebdi explain`;
the explanation command verifies additivity against the fitted model and publishes a beeswarm, grouped importance
and metadata. Tree-path-dependent attributions depend on the fitted representation and correlated predictors;
they do not identify causal effects. SHAP is an optional dependency so the core pipeline stays smaller.
No causal claim, personalized insurance recommendation or real-world individual risk calculator is supported.

The fitted model is saved locally to `outputs/models/conditional_severity.joblib` with source hashes in the JSON model card.
Do not load untrusted pickle/joblib files. Git excludes model binaries; regenerate with `uv run ebdi model`.
