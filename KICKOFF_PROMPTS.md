# Claude Code prompts, in order

Paste one at a time. Run `/clear` between milestones so each starts fresh
(CLAUDE.md is reloaded automatically). Don't move on until the milestone's check passes.

## Before Prompt 0 (about 5 minutes)

1. Clone the repo: `git clone https://github.com/jonahgigi534-wq/NASA-SpaceApps` and `cd` into it.
2. Put all the data you have in one folder you can point to (for example `~/Downloads/firms`):
   the 9 FIRMS zips, plus the AppEEARS GeoTIFFs and missing-dates table if you have them.
   Prompt 0 sorts them into place, so you don't need to.
3. Have the official challenge text copied and ready to paste.
4. Start Claude Code in the repo folder (`claude`), then press Shift+Tab until plan mode is on.

Already in the repo, so don't recreate it: `CLAUDE.md`, this file, `.gitignore`,
`data/raw/README.md`, `data/regions/*.geojson` (the three region boxes), `docs/challenge.md`.

---

## Prompt 0: data, setup and plan (Sat morning, first thing)

Fill in the three blanks, then paste the whole thing.

> All our data is in: `<PATH TO YOUR DATA FOLDER>`
> Our FIRMS MAP_KEY is: `<YOUR KEY>`
> The official challenge text is:
> `<PASTE THE CHALLENGE TEXT HERE>`

Read CLAUDE.md completely. Then:
1. **Data.** Copy every file from that folder into the repo. Use the table in CLAUDE.md
   section 3 and data/raw/README.md to route each FIRMS zip by its ID to
   data/raw/texas/, data/raw/amazon/ or data/raw/australia/. AppEEARS GeoTIFFs go to
   data/raw/appeears/<region>/ (match the region from the file or folder name; ask if unclear).
   A missing-dates table goes to data/raw/missing_dates.csv. Then verify: all 9 FIRMS zips
   present, each opens as a valid zip, and each contains a fire_archive_*.csv. If any is
   missing or broken, stop and tell me which. Don't commit any data (it's gitignored; confirm
   with `git status`).
2. **Key.** Write `FIRMS_MAP_KEY=<key>` to .env and confirm .env is gitignored.
3. **Challenge.** Replace the placeholder in docs/challenge.md with the challenge text above.
   Compare it against CLAUDE.md: list anything the challenge asks for that CLAUDE.md doesn't
   cover, and propose an update to CLAUDE.md.
4. **Inspect.** For each zip, read the CSV header and first 3 rows (don't unzip everything to
   disk) and the min/max acq_date. Confirm column names and date ranges against CLAUDE.md
   and report any differences.
5. **Scaffold.** The repo already has .gitignore, data/raw/README.md, data/regions/*.geojson
   and docs/challenge.md. Keep those. Add the rest of the layout from CLAUDE.md section 7
   (pipeline/, app/static/, results/figures/, tests/), plus requirements.txt (pandas, pyarrow,
   duckdb, numpy, scipy, statsmodels, shapely, rasterio, matplotlib, fastapi, uvicorn,
   python-dotenv, pytest, playwright) and a Makefile. Use data/regions/*.geojson as the region
   definitions everywhere (map outlines, presets, clipping); don't hardcode the boxes twice.
6. Create a virtual environment (.venv), install requirements, and confirm the imports work.
   Check that ffmpeg is installed (needed for the demo video at the end); if not, tell me
   how to install it on my OS.
7. Write a task list covering milestones M1–M7.
Show me the plan and wait for my OK before writing pipeline code. After I approve, commit
the scaffolding and push to origin main.

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

We're submitting a **video** as our demo: **30 seconds max, English subtitles** (check the
2026 Submission Guide in case the limit changed; going over makes us ineligible for Global
Judging). Using only numbers from results/metrics.json, make:
1. README.md: problem, NASA data used and how, method, validation results table, how to run,
   live link, demo video link (placeholder until uploaded), AI-use disclosure, team.
2. docs/AI_USE.md: specific disclosure of how Claude Code was used.
3. docs/video_script.md: a shot-by-shot storyboard that fits in **27 seconds** (leave a
   buffer). Suggested beats: 0–4 s the problem (MODIS aging out, VIIRS doesn't match);
   4–10 s the raw-vs-harmonized long-term chart with the jump disappearing; 10–14 s one
   key validation number; 14–24 s the app: draw an area, pick dates, calendar lights up,
   flip the mode toggle, download the CSV; 24–27 s name, live URL, "built on NASA FIRMS data".
   For each shot: start/end time, what's on screen, subtitle text (short enough to read).
4. docs/video_subtitles.srt matching the script exactly.
5. scripts/record_demo.py: a Playwright script that runs the deployed app (or local if no
   URL yet) through the storyboard's app shots and records video at 1920×1080. Also render
   the chart/metric shots as short clips from results/figures/. Then use ffmpeg to join the
   clips, **burn in the subtitles**, add a small "Made with NASA FIRMS data" credit, and write
   docs/demo.mp4. Verify with ffprobe that it's ≤30.0 s and 1080p, and tell me its exact
   duration. No AI-generated imagery and no NASA logos.
6. docs/submission_text.md: the project-page text for the Space Apps form (summary, NASA data
   used and how it shaped the project, AI-use statement), plus the steps to upload demo.mp4
   to YouTube as Unlisted (public link, no login) so we can paste the link in.
Commit and push everything except demo.mp4 if it's over 50 MB.
