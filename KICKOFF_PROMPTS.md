# Claude Code prompts, in order

Paste one at a time. Run `/clear` between milestones so each starts fresh
(CLAUDE.md is reloaded automatically). Don't move on until the milestone's check passes.

---

## Prompt 0: setup and plan (Sat morning, first thing)

Read CLAUDE.md and docs/challenge.md completely. Then:
1. Inspect data/raw/: list every file and size, open each zip's CSV header and first 3 rows
   (don't unzip everything to disk if not needed), and confirm the column names and date
   ranges against CLAUDE.md. Report any differences.
2. Set up the repo: the layout from CLAUDE.md section 7, requirements.txt (pandas, pyarrow,
   duckdb, numpy, scipy, statsmodels, shapely, rasterio, matplotlib, fastapi, uvicorn,
   python-dotenv, pytest), .gitignore (data/raw, data/processed, .env), a Makefile.
3. Write a task list covering milestones M1–M7.
Use plan mode: show me the plan and wait for my OK before writing pipeline code.

## Prompt 1: M1 ingest

Implement pipeline/ingest.py per CLAUDE.md. Stream from the zips, keep type == 0, normalize
the schema across MODIS and VIIRS (sensor, satellite, datetime UTC, lat, lon, frp, confidence
mapped to low/nominal/high, daynight, is_provisional), write
data/processed/fires_<region>_<sensor>.parquet. Then print a table of row counts by
region × sensor × year and the share of each `type` that was removed. Flag anything odd.
Add pytest tests for the confidence mapping and schema.

## Prompt 2: M2 grid

Implement pipeline/grid.py: the 0.1° daily and 0.25° monthly aggregates from CLAUDE.md 4.1,
split by satellite and day/night. Build the missing-data mask (CLAUDE.md section 3) and store
missing days as NaN. Verify detection totals are preserved after gridding and write a test
for it. Also produce results/figures/overpass_times.png: acq_time distribution by year for
Terra, Aqua, S-NPP and NOAA-20 (orbit drift check).

## Prompt 3: M3 harmonize and validate (most important, take your time)

Implement pipeline/harmonize.py and pipeline/validate.py exactly per CLAUDE.md section 4:
Methods A and B, baselines (raw VIIRS, single global ratio), fit on 2012–2018, test on
2019 → end, NOAA-20 transfer test, continuity plot 2001 → present per region (raw vs
harmonized, sensor-switch date marked), and land-cover groups if data/raw/appeears exists.
Write results/metrics.json and the figures. Then give me a plain-English summary: which
method won, by how much, in which regions it struggles, and why. If harmonization doesn't
beat the baselines somewhere, say so and propose a fix. Don't hide it.

## Prompt 4: M4 backend

Implement pipeline/build_app_data.py (final harmonized 0.1° daily parquet, all three modes)
and app/main.py with the endpoints in CLAUDE.md section 6, using DuckDB over Parquet and
shapely for polygon-cell selection. Anomaly math per CLAUDE.md section 5. pytest tests for:
polygon selection, the anomaly z-score on a synthetic series, NaN propagation for missing
days, CSV columns. Make every endpoint respond in <2 s for a Texas-sized polygon.

## Prompt 5: M5 frontend

Build app/static/index.html and methods.html per CLAUDE.md section 6. No build step. Clean,
modern, readable design; colorblind-safe diverging palette; legends and tooltips; works
on a laptop screen and a phone. Add 3 preset events that the data actually shows as big
anomalies (find them from the data, don't guess). Then run the app and test the full flow:
draw → dates → calendar → mode toggle → long-term chart → CSV download. Fix anything broken.

## Prompt 6: M6 deploy

Make the app deployable as a single Docker container (Dockerfile, small app data, port from
$PORT). Give me exact click-by-click steps to deploy on Render (or Hugging Face Spaces) so
the URL is public with no login. After I deploy, help me smoke-test the live URL.

## Prompt 7: M7 submission assets

Using only numbers from results/metrics.json, write:
1. README.md: problem, NASA data used and how, method, validation results table, how to run,
   live link, AI-use disclosure, team.
2. docs/AI_USE.md: specific disclosure of how Claude Code was used.
3. A 7-slide outline (title; problem; why sensors disagree; our method; validation
   proof with the before/after figure; app demo screenshots; impact and next steps), with
   speaker notes.
4. A 30-second video script with on-screen subtitles, as an alternative.
5. The project-page text for the Space Apps submission form (summary, data used, how we used it).
