# Project: FireBridge — Harmonized MODIS + VIIRS Fire Activity (NASA Space Apps 2026)

You are building a complete, judge-ready entry for the NASA Space Apps 2026 challenge
"Harmonization of MODIS and VIIRS Hot Spots". Read this whole file before doing anything.
It is the single source of truth for the project. Keep it updated if decisions change.

## 1. The challenge (paste the official text into docs/challenge.md and re-read it)

MODIS has 20+ years of active-fire hotspot data but is aging out. VIIRS has better resolution
(375 m vs 1 km) but different sensitivity and overpass schedule, so the two records cannot be
compared directly. Two deliverables:

1. **Harmonize** the MODIS and VIIRS FIRMS datasets so the source sensor stops mattering.
2. **Web app** with a "burning activity calendar": the user draws an area, picks dates, and gets
   fire-activity anomalies against multi-year averages, plus a CSV download.

Judging criteria: Impact, Creativity, Validity, Relevance, Presentation. **Validity is where we
win**: every claim about the harmonization must be backed by a number we computed and saved.

## 2. Ground rules for you (Claude Code)

- Plan before coding. Keep a task list and tick items off.
- Work in the milestone order below. Each milestone ends with a runnable command and a check.
- **Never invent numbers.** Every metric in the README, slides, or UI must come from
  `results/metrics.json`, written by code. If a number isn't computed yet, write `TBD`.
- Prefer simple, readable code a high-school team can explain to judges. Use comments.
- Every pipeline script is idempotent and runnable from the repo root: `python -m pipeline.<name>`.
- Commit after each milestone with a clear message.
- Memory: the big CSVs are up to ~850 MB. Read with `usecols`, explicit dtypes, and chunking
  or DuckDB. Never load all regions' raw CSVs at once.
- If something in the data contradicts this file, trust the data, tell us, and update this file.

## 3. The data we already have

Raw FIRMS archive zips (downloaded Nov 13). The team provides them in Prompt 0 as a folder
path; sort them into `data/raw/<region>/` by ID:

| Region | Bounding box (W,S,E,N) | MODIS C6.1 | VIIRS S-NPP | VIIRS NOAA-20 |
|---|---|---|---|---|
| texas | -107, 25, -93, 37 | DL_FIRE_M-C61_845957.zip | DL_FIRE_SV-C2_845959.zip | DL_FIRE_J1V-C2_845958.zip |
| amazon | -65, -15, -45, -5 | DL_FIRE_M-C61_845966.zip | DL_FIRE_SV-C2_845968.zip | DL_FIRE_J1V-C2_845967.zip |
| australia | 120, -20, 150, -10 | DL_FIRE_M-C61_845970.zip | DL_FIRE_SV-C2_845972.zip | DL_FIRE_J1V-C2_845971.zip |

Each zip has `fire_archive_*.csv` (science-quality standard processing, through ~2026-08-31,
verify) and `fire_nrt_*.csv` (near-real-time, ~Sep–Oct 2026). Use **archive only** for
calibration and validation. NRT may be used only to extend the app's most recent dates, and
must be flagged as provisional.

MODIS columns (verified on texas): latitude, longitude, brightness, scan, track, acq_date,
acq_time, satellite (T=Terra, A=Aqua), instrument, confidence (0–100), version, bright_t31,
frp, daynight, type. VIIRS is similar but uses bright_ti4/bright_ti5 and confidence is
l/n/h. Check actual headers in code; don't assume.

`type`: 0 = presumed vegetation fire, 1 = volcano, 2 = other static land source,
3 = offshore. **Keep only type == 0.** (Texas MODIS: ~94% are type 0.)

Coverage: MODIS Terra from 2000-11, Aqua from 2002-07; S-NPP 2012-01-20 to 2026-11-02 (the
FIRMS form shows S-NPP ending 2026-11-02); NOAA-20 from 2018-04-01.

Optional, may arrive later in `data/raw/appeears/<region>/` as GeoTIFFs:
- MCD12Q1.061 LC_Type1 (yearly IGBP land cover, 500 m)
- MCD64A1.061 Burn_Date (monthly burned area, 500 m)
The project must work without these. Use them if present.

Missing-satellite-data dates: `data/raw/missing_dates.csv` if present (from
firms.modaps.eosdis.nasa.gov/api/missing_data/). If absent, infer gaps per sensor as dates
with zero detections across an entire region while the other sensor has many, and flag them.
**A missing-data day is NaN, never zero.**

FIRMS MAP_KEY lives in `.env` as `FIRMS_MAP_KEY` (gitignored). Only needed for the optional
live-update feature.

## 4. Science plan: the harmonization (the core of the project)

Why the records differ: pixel size (1 km vs 375 m, so VIIRS sees small or cool fires MODIS
misses and splits one fire into several detections); overpass times (Terra ~10:30/22:30,
Aqua and S-NPP and NOAA-20 ~13:30/01:30); different confidence scales; different FRP
sensitivity. Also: Terra and Aqua orbits have been drifting in recent years, so check the
`acq_time` distribution by year and satellite and report it.

### 4.1 Common grid
- Calibration grid: **0.25° cells, monthly** (less noise).
- App grid: **0.1° cells, daily**.
- Per cell-period and per sensor/satellite: `n_det`, `frp_sum`, `frp_mean`, split by
  day/night. Keep day and night separate during calibration.

### 4.2 Harmonized unit
Output a **MODIS-equivalent** record: VIIRS is mapped onto the MODIS scale, so the 2001–2011
MODIS-only era and the VIIRS era form one continuous series. Report both:
- `mec`: MODIS-equivalent detection count
- `mefrp`: MODIS-equivalent FRP sum (MW)

### 4.3 Calibration pair
Primary: **MODIS Aqua vs VIIRS S-NPP** (same ~13:30 overpass), over the overlap
2012-01-20 → archive end. Same-day and same-overpass pairs only.

### 4.4 Methods (implement both, compare, pick the winner by validation score)
- **Method A, detection-limit matching**: for each region × land-cover group, find the VIIRS
  FRP threshold τ such that VIIRS detections with frp ≥ τ, re-aggregated, best match MODIS Aqua
  totals. Then scale for pixel size with a fitted ratio.
- **Method B, statistical mapping**: per region × land-cover group × day/night, fit
  `log1p(MODIS) ~ log1p(VIIRS)` (OLS, plus quantile mapping as an alternative) on the
  0.25° monthly cells.
- Baseline to beat: **raw VIIRS** with no adjustment, and **a single global ratio**.

Land-cover groups (if MCD12Q1 is available, majority class per 0.25° cell per year):
forest (IGBP 1–5), shrubland (6–7), savanna (8–9), grassland (10), cropland (12, 14),
other. Without land cover, calibrate per region only and say so.

Confidence harmonization: map MODIS confidence <30 → low, 30–79 → nominal, ≥80 → high to
match VIIRS l/n/h. Run the main analysis on all confidences, plus a sensitivity check
excluding low.

### 4.5 Validation (this is what judges will look at)
- **Temporal holdout**: fit on 2012–2018, test on 2019 → archive end.
- **Transfer test**: apply the S-NPP-fitted mapping to **NOAA-20** (never used in fitting) vs
  MODIS Aqua, 2018-04 → end.
- Metrics per region and overall, on monthly regional totals AND per-cell: R², bias (%),
  RMSE, Pearson r. Before (raw VIIRS) vs after (harmonized) for each.
- **Continuity check**: plot the 2001 → present regional monthly series. Raw switching from
  MODIS to VIIRS should show a jump. Harmonized should not.
- Optional, if MCD64A1 present: correlate monthly harmonized fire activity with burned area
  per region (an independent check).
- Write everything to `results/metrics.json` and figures to `results/figures/*.png`.
  Figures must have titles, axis labels with units, and legends.

## 5. Anomalies ("burning activity calendar")

Computed **on the fly for the user's polygon**, not per cell (per-cell climatologies are too
noisy):
1. Sum harmonized `mec` (and `mefrp`) over cells whose centers fall inside the polygon → daily series.
2. Baseline: same polygon, baseline years (default 2003–2022, user-selectable), smoothed
   day-of-year climatology (±15-day window): mean and std.
3. Anomaly per day: z-score, % of normal, and absolute difference. Missing-data days → NaN.
4. Also offer weekly and monthly aggregation.

## 6. Web app

Stack: **FastAPI + DuckDB** backend reading Parquet; static frontend (plain HTML/JS, Leaflet +
Leaflet.draw, a calendar heatmap with D3 or Cal-Heatmap, Chart.js or D3 for line charts).
No build step needed.

Endpoints:
- `GET /api/regions`: available regions and their date coverage
- `POST /api/calendar`: polygon GeoJSON, start, end, baseline years, mode
  (`harmonized` | `modis_only` | `viirs_raw`), metric (`count` | `frp`) → daily values + anomalies
- `POST /api/timeseries`: same inputs → monthly series 2001 → present, all three modes
- `POST /api/csv`: same inputs → CSV download (date, value, baseline_mean, baseline_std,
  z, pct_of_normal, source_sensor, provisional_flag, missing_flag)

UI:
- Map with the three regions outlined. Draw a rectangle or polygon, or click a preset
  (e.g. "2011 Texas drought fires", "2019–20 Black Summer", "2019 Amazon fires", whatever
  the data actually shows as notable; verify in data).
- Date range picker. Mode toggle (harmonized / MODIS only / raw VIIRS) so judges can SEE the
  sensor jump disappear.
- Calendar heatmap with a diverging color scale (below normal → normal → above normal), grey
  for missing data, hatched for provisional NRT. Tooltip: date, value, normal, z.
- Long-term line chart: raw vs harmonized, with the sensor-switch dates marked.
- "Download CSV" button.
- **Methods page** showing the validation figures and metrics from `results/metrics.json`.
- Accessible: keyboard usable, colorblind-safe palette, legends everywhere.

Stretch (only after everything else works): live mode using the FIRMS API (VIIRS NOAA-20
NRT) to append the last 7 days, clearly flagged provisional.

## 7. Repo layout

```
data/raw/<region>/*.zip        # gitignored
data/raw/appeears/...          # gitignored
data/processed/*.parquet       # gitignored (but small app parquet may be committed or built in deploy)
pipeline/ingest.py             # zips → clean parquet per region × sensor (type==0, dtypes, datetime)
pipeline/grid.py               # → 0.1° daily and 0.25° monthly aggregates
pipeline/landcover.py          # optional, GeoTIFF → cell land-cover group
pipeline/harmonize.py          # fit Methods A and B, choose winner, write coefficients
pipeline/validate.py           # metrics.json + figures
pipeline/build_app_data.py     # final harmonized 0.1° daily parquet for the app
app/main.py                    # FastAPI
app/static/                    # index.html, methods.html, js, css
results/metrics.json, results/figures/
tests/                         # pytest: gridding, polygon aggregation, anomaly math, NaN handling
scripts/record_demo.py         # Playwright + ffmpeg → docs/demo.mp4 (≤30 s, subtitles burned in)
docs/challenge.md, docs/AI_USE.md, docs/video_script.md, docs/video_subtitles.srt
README.md
```

Single entry point: `make all` (or `python -m pipeline.run_all`) rebuilds everything.

## 8. Milestones (hackathon is Nov 14–15; submission closes Sun 11:59 pm local)

1. **M1 Ingest (Sat AM)**: clean Parquet for all 9 files. Print row counts by region ×
   sensor × year and type breakdown. Check: counts look plausible, no nulls in key fields.
2. **M2 Grid (Sat AM)**: both grids built. Check: totals preserved (sum of grid = row count).
3. **M3 Harmonize + validate (Sat PM)**: both methods, holdout, NOAA-20 transfer,
   continuity plots, metrics.json. Check: harmonized beats raw on test-set bias and R²
   in every region (if not, report honestly and explain).
4. **M4 App backend (Sat night)**: endpoints work with tests.
5. **M5 App frontend (Sun AM)**: full flow works in browser end to end.
6. **M6 Deploy (Sun midday)**: public URL with no login (Render, Fly.io, or Hugging Face Spaces
   Docker). Keep app data small (<200 MB).
7. **M7 Submission assets (Sun PM)**: README, docs/AI_USE.md, and the demo **video** (we chose
   video: ≤30 s, English subtitles burned in): docs/video_script.md, docs/video_subtitles.srt,
   scripts/record_demo.py (Playwright + ffmpeg) → docs/demo.mp4, docs/submission_text.md.
   Upload to YouTube as Unlisted for a public no-login link.

Repo: https://github.com/jonahgigi534-wq/NASA-SpaceApps (branch `main`). Region boxes live in
`data/regions/*.geojson` and are the single source for region definitions.

## 9. Submission requirements to respect

- Must use NASA data and describe which data and how it shaped the project (FIRMS MODIS C6.1,
  VIIRS S-NPP and NOAA-20; MCD12Q1 and MCD64A1 if used).
- Demo: **we're submitting a video**, ≤30 s with English subtitles, hosted publicly (YouTube
  Unlisted). Going over the limit makes us ineligible for Global Judging. (Verify the limit
  against the 2026 Submission Guide.)
- All links public, no login.
- **AI disclosure**: we are using Claude Code. `docs/AI_USE.md` and the README must state
  clearly where and how AI was used (code generation, debugging, writing). No AI-generated
  images without a visible watermark. Don't use NASA logos or branding.
