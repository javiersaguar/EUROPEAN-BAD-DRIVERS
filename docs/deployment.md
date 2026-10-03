# Publication and operations

The product is a static React application. Python computes and validates aggregate releases offline; no participant-level data, Python model service, API credentials or admin toolbar are delivered to the browser.

## Local product

Node 24 and the committed npm lock:

```sh
cd web
npm ci --ignore-scripts
npm run dev -- --port 8501
```

For production artifacts: `npm run build`. `npm run preview` is for local inspection, not a production server. Streamlit remains available separately with `uv run ebdi dashboard` for research compatibility.

## HTTPS publication

GitHub Pages uses the workflow in `.github/workflows/pages.yml`, repository source **GitHub Actions**, base `/EUROPEAN-BAD-DRIVERS/`, and environment `github-pages`. It installs from the lock, runs frontend checks and desktop/mobile browser verification before publishing. The project URL is:

https://javiersaguar.github.io/EUROPEAN-BAD-DRIVERS/

The site deploys only static aggregates and local assets. No paid hosting or domain is required. An owned custom domain can be configured later; the project does not assume or purchase one. Public Pages adds HTTPS. The production build embeds a content policy; fonts are local, and no analytics SDK or error-data collection service receives visitor data.

## Container

```sh
docker build -t ebdi-observatory .
docker run --rm --read-only --tmpfs /tmp --tmpfs /var/cache/nginx -p 8080:8080 ebdi-observatory
```

The multi-stage image builds with Node and serves through unprivileged Nginx, user 101, port 8080, with healthcheck, cache controls and security headers. HTTPS termination belongs to the deployment platform/reverse proxy. Mutable base-image tags are checked by Dependabot; pin approved digests if a deployment requires bit-for-bit image reproducibility. `Dockerfile.research` retains the optional legacy Python research dashboard.

## Checks and monitoring

- `web.yml`: frontend lint/format/unit/build, dependency audit, Chromium desktop/mobile and axe tests, downloads and error states; container build/read-only smoke.
- `ci.yml`: Python checks on Linux/Windows and executed notebooks.
- `monitor.yml`: weekly Monday 06:17 UTC upstream hash/structure checks and HTTPS availability/aggregate-contract check. Failures and quarantined originals are workflow artifacts; changed data are never activated automatically.
- `uv run ebdi monitor`: manual upstream checks, report `outputs/tables/source_monitor.json`.
- `python scripts/check_site.py <HTTPS-site-url>`: report `outputs/tables/site_monitor.json`.

Monitoring requires GitHub Actions to remain enabled. Scheduled public-repository workflows may stop after repository inactivity according to platform policy; inspect workflow status during maintenance. A failed download is logged as unavailable, not interpreted as a data revision. There is no automatic model retraining or silent release overwrite.

To approve a source revision: inspect quarantine, verify definitions/schema, reconcile totals, add/adjust the contract tests, update source hash/retrieval metadata explicitly, regenerate aggregates, run all checks, then publish a new release. Keep the old Git tag and aggregate version for comparison and rollback.
