# Project: FireBridge — Harmonized MODIS + VIIRS Burning Activity Calendar (NASA Space Apps 2026)

You are building a complete, judge-ready entry for the NASA Space Apps 2026 challenge
**"Harmonization of MODIS and VIIRS Hot Spots"** (author: CONAE, Argentina's space agency).
Read this whole file and `docs/challenge.md` before doing anything. This file is the single
source of truth for how we build; `docs/challenge.md` holds the **official challenge text**
and the requirements checklist **R1–R18**. If they ever disagree, the official text wins:
tell us and update this file.

## 1. What we're building

The official objective: *"develop a harmonized burning activity calendar based on active fire
hotspots in a web application, combining the extensive historical series of MODIS with the
continuity and greater detail of VIIRS to provide a consistent time series of hotspot
activity."* Two parts:

1. **Harmonization**: MODIS + VIIRS FIRMS hotspots → one consistent record, so that "the
   sensor of origin no longer matters and the patterns, trends, and anomalies become the focus."
2. **Web app** on top of the harmonized data. A user selects a region (draw on a map **or**
   type lat/lon) and a date range, then sees and downloads analytics and visualizations:
   - a **burning activity calendar**: number of hotspots per month, early 2000s → present
   - **which periods of the year** see more fires, **which years** had more burning
   - **how the current month compares with the historical median**
   - **anomalies against multi-year averages**
   - accessible color ramps; **CSV of the hotspots** found in the search; downloadable charts

Audience: early-warning and emergency responders, scientists, land managers, firefighters.
Every screen should make sense to a fire manager in 10 seconds.

How we win: judging is Impact, Creativity, Validity, Relevance, Presentation. Many teams have
public repos for this same challenge. We stand out by (1) **rigorous, honest validation with
numbers** (temporal holdout + NOAA-20 transfer test), (2) treating missing data as missing,
not zero, (3) covering every R1–R18 item visibly, and (4) a polished, plain-language app.

## 2. Ground rules for you (Claude Code)

- Plan before coding. Keep a task list and tick items off.
- Work in milestone order (§8). Each milestone ends with a runnable command and a check.
- **Never invent numbers.** Every metric in the README, video, UI text or summaries must come
  from `results/metrics.json` or from the app's computed output. If not computed yet: `TBD`.
- Simple, readable, commented code a high-school team can explain to judges.
- Pipeline scripts are idempotent and run from the repo root: `python -m pipeline.<name>`.
- Commit after each milestone with a clear message, then `git push origin main`.
- Memory: raw CSVs reach ~850 MB. Read with `usecols`, explicit dtypes, chunking, or DuckDB.
  Never load all regions' raw CSVs at once.
- If the data contradicts this file, trust the data, tell us, and update this file.
- Never commit data/raw, .env, or any file over 50 MB.

## 3. Data

### 3.1 FIRMS hotspots (the core data, NASA Earthdata FIRMS)

Raw archive zips, provided in Prompt 0 as a folder path, sorted into `data/raw/<region>/` by ID:

| Region | Box (W,S,E,N) | MODIS C6.1 | VIIRS S-NPP | VIIRS NOAA-20 |
|---|---|---|---|---|
| texas | -107, 25, -93, 37 | DL_FIRE_M-C61_845957.zip | DL_FIRE_SV-C2_845959.zip | DL_FIRE_J1V-C2_845958.zip |
| amazon | -65, -15, -45, -5 | DL_FIRE_M-C61_845966.zip | DL_FIRE_SV-C2_845968.zip | DL_FIRE_J1V-C2_845967.zip |
| australia | 120, -20, 150, -10 | DL_FIRE_M-C61_845970.zip | DL_FIRE_SV-C2_845972.zip | DL_FIRE_J1V-C2_845971.zip |

Region boxes also live in `data/regions/*.geojson`: the single source for region definitions.

Each zip holds `fire_archive_*.csv` (standard processing, science quality, through
~2026-08-31; verify) and `fire_nrt_*.csv` (near-real-time, ~Sep–Oct 2026).
- **Archive only** for calibration and validation.
- NRT extends the app toward the present, flagged **provisional**.
- **Live mode** (needed for R9, "current month"): `FIRMS_MAP_KEY` in `.env`; the FIRMS area API
  `/api/area/csv/{key}/{source}/{W,S,E,N}/{days≤10}/{date}` with `VIIRS_NOAA20_NRT`,
  `VIIRS_NOAA21_NRT`, `MODIS_NRT` fills the gap from the end of the zips' NRT data to today.
  Cache responses to disk; respect the rate limit; app must still work if the API is down.

MODIS columns (verified, texas): latitude, longitude, brightness, scan, track, acq_date,
acq_time, satellite (T/A), instrument, confidence (0–100), version, bright_t31, frp, daynight,
type. VIIRS: bright_ti4/bright_ti5 instead of brightness/bright_t31; confidence l/n/h. Check
real headers in code.

`type`: 0 vegetation fire, 1 volcano, 2 other static land source, 3 offshore. **Keep type 0.**
(Texas MODIS: ~94% type 0.) NRT files may lack `type`; if so, drop detections that fall on
static-source cells identified from the archive (cells with type 2 detections) and say so.

Coverage: Terra from 2000-11, Aqua from 2002-07; S-NPP 2012-01-20 → 2026-11-02 (FIRMS form);
NOAA-20 from 2018-04-01. NASA plans to end Terra MODIS collection Jan 2027 and Aqua ~Sep 2027.

### 3.2 Optional extras (use if present; the project must work without them)
- `data/raw/appeears/<region>/`: MCD12Q1.061 LC_Type1 (yearly land cover) and MCD64A1.061
  Burn_Date (monthly burned area) GeoTIFFs (Australia may be missing; handle that).
- `data/raw/missing_dates.csv`: FIRMS missing-data dates. If absent, infer per-sensor gaps
  (days with zero detections region-wide while the other sensor has many) and flag them.
- **A missing-data day is NaN, never zero.**

## 4. Harmonization (R1, R2)

Why the records differ: pixel size (1 km vs 375 m: VIIRS sees smaller/cooler fires and splits
one fire into several detections), overpass times (Terra ~10:30/22:30; Aqua, S-NPP, NOAA-20
~13:30/01:30), confidence scales, FRP sensitivity. Terra/Aqua orbits drift in recent years:
plot `acq_time` by year and satellite and report it.

### 4.1 Grids
- Calibration: **0.25° cells, monthly**. App: **0.1° cells, daily**.
- Per cell-period, per satellite, split day/night: `n_det`, `frp_sum`, `frp_mean`.

### 4.2 Harmonized unit: hotspot count on the MODIS scale
The challenge centers on **number of hotspots**. Primary output: `mec`, **MODIS-equivalent
hotspot count**, so 2001–2011 (MODIS only) and the VIIRS era form one continuous series.
Secondary: `mefrp`, MODIS-equivalent FRP sum (MW). Label this clearly in the UI
("hotspots, harmonized to MODIS scale").

### 4.3 Calibration pair
**MODIS Aqua vs VIIRS S-NPP** (same ~13:30 overpass), 2012-01-20 → archive end, same-day and
same-overpass only.

### 4.4 Methods (implement both, pick the winner by validation)
- **A, detection-limit matching**: per region × land-cover group, find VIIRS FRP threshold τ so
  VIIRS detections with frp ≥ τ best match MODIS Aqua totals; then a fitted pixel-size ratio.
- **B, statistical mapping**: per region × land-cover group × day/night, `log1p(MODIS) ~
  log1p(VIIRS)` (OLS) and quantile mapping, on 0.25° monthly cells.
- Baselines to beat: **raw VIIRS** and **one global ratio**.
- Land-cover groups (MCD12Q1 majority per 0.25° cell-year): forest 1–5, shrub 6–7, savanna 8–9,
  grassland 10, cropland 12/14, other. Without land cover: per region only, and say so.
- Confidence: MODIS <30 low, 30–79 nominal, ≥80 high (to match VIIRS l/n/h). Main run on all
  confidences + a sensitivity run excluding low.
- Combining sensors in the final record: before VIIRS → MODIS (Terra+Aqua); VIIRS era →
  harmonized VIIRS (S-NPP + NOAA-20 + NOAA-21 where available, de-duplicated so overlapping
  satellites aren't double-counted; document the rule). Show sensor source per day.

### 4.5 Validation (what judges check)
- **Temporal holdout**: fit 2012–2018, test 2019 → end.
- **Transfer test**: S-NPP-fitted mapping applied to **NOAA-20** (never used in fitting) vs MODIS
  Aqua, 2018-04 → end.
- Per region and overall, monthly regional totals AND per cell: R², bias %, RMSE, Pearson r,
  raw vs harmonized.
- **Continuity check**: 2001 → present monthly series per region, raw (jump at 2012) vs
  harmonized (no jump), switch date marked.
- Optional: monthly harmonized activity vs MCD64A1 burned area (independent check).
- Write `results/metrics.json` and `results/figures/*.png` (titles, axis labels with units,
  legends, colorblind-safe).

## 5. Analytics for a selected area (computed on the fly for the user's polygon)

Sum harmonized `mec` over 0.1° cells whose centers fall inside the polygon → daily series
(NaN on missing days). Default baseline: 2003–2022 (user-selectable). Report counts as both
the **median** and the mean, since the brief asks for the median.

### 5.1 Anomalies (R10)
Smoothed day-of-year climatology (±15 days): mean, median, std. Per day, week and month:
value, % of median, difference from mean, z-score.

### 5.2 Patterns and critical periods (R6, R7, R8)
- **Month × year calendar**: hotspots per month for every year since 2001 (the centerpiece).
- **Which years**: yearly totals, ranked; top 3 called out.
- **Which periods of the year**: monthly median across years; **fire season** = contiguous
  window holding 80% of typical activity (start, peak, end); **high-risk months/weeks** = top 20%.
- **Chance of an unusual month**: share of baseline years in which each month was above its
  normal (z > 1). Label as historical frequency, not a forecast.

### 5.3 Current month vs history (R9)
Current month to date (archive + NRT + live, flagged provisional) vs the historical median
for the same days of that month, as "X hotspots so far vs a typical Y (Z% of median)", plus its
rank among all years. Also: pick any past event/date range and compare it the same way.

## 6. Web app (R3–R5, R11–R15)

Stack: **FastAPI + DuckDB** over Parquet; static frontend (plain HTML/JS, Leaflet +
Leaflet.draw, D3 for calendars, Chart.js or D3 for charts). No build step.

Endpoints:
- `GET /api/regions`: regions and date coverage
- `POST /api/summary`: polygon, date range, baseline → key figures, plain-language summary
- `POST /api/calendar`: polygon, range, baseline, mode (`harmonized` | `modis_only` |
  `viirs_raw`), granularity (day | month) → values + anomalies
- `POST /api/patterns`: polygon, baseline → month×year grid, yearly ranking, fire season,
  high-risk months, chance of unusual month
- `POST /api/current`: polygon → current month vs median (§5.3)
- `POST /api/timeseries`: polygon → monthly 2001 → present, all three modes
- `POST /api/export/series.csv`: the analytics table (date, value, median, mean, std, z,
  pct_of_median, source_sensor, provisional_flag, missing_flag)
- `POST /api/export/hotspots.csv`: **the hotspot points in the polygon and date range** (lat,
  lon, datetime UTC, satellite, sensor, frp, confidence, day/night, provisional), plus the
  harmonized weight each point contributes. Stream it; cap with a clear message if huge.

UI (one page, three tabs named after the brief, plus a Methods page):
- **Area**: draw rectangle/polygon on the map, **or type lat/lon** (box or point + radius km),
  or click a preset (pick presets from the data's actual biggest anomalies; don't guess).
  Regions outlined; warn if the area falls outside our data.
- **Date range** picker; **baseline years** selector; mode toggle (harmonized / MODIS only /
  raw VIIRS) so judges SEE the 2012 jump disappear.
- **Key figures strip** (R11): total hotspots in range, % of median, busiest month, busiest
  year, fire season dates.
- **Plain-language summary** for responders, generated from computed numbers only.
- Tab **Burning calendar** (R6, R12): month × year heatmap, 2001 → present, with a
  **sequential accessible color ramp** (e.g. viridis/cividis) for counts, toggle to a
  **diverging accessible ramp** for anomaly vs median. Click a month → daily calendar.
  Grey = missing data, hatched = provisional.
- Tab **Patterns & critical periods** (R7, R8): monthly median bars with the fire season shaded,
  yearly totals ranked, chance-of-unusual-month row.
- Tab **Now vs history** (R9, R10): current month vs median gauge + daily anomaly calendar.
- Long-term chart: raw vs harmonized, sensor switches marked.
- **Exports** (R13, R14): hotspots CSV, analytics CSV, and **PNG download of every chart**.
- Accessible: keyboard usable, ARIA labels, colorblind-safe ramps, legends and units everywhere,
  readable on a phone.
- **Methods page**: how harmonization works, validation figures and numbers from
  `results/metrics.json`, data sources and DOIs, limitations, AI-use note.

## 7. Repo layout

```
data/raw/<region>/*.zip, data/raw/appeears/, data/raw/missing_dates.csv   # gitignored
data/regions/*.geojson                                                     # committed
data/processed/                                                            # gitignored
data/app/                       # final app parquet (small; build in deploy or host externally)
pipeline/ingest.py              # zips → clean parquet per region × sensor (+ points table)
pipeline/grid.py                # 0.1° daily, 0.25° monthly, missing-data mask
pipeline/landcover.py           # optional
pipeline/harmonize.py           # Methods A/B, winner, coefficients
pipeline/validate.py            # metrics.json + figures
pipeline/live.py                # FIRMS API fetch + cache for recent days
pipeline/build_app_data.py      # app parquet: harmonized daily cells + slim hotspot points
pipeline/run_all.py
app/main.py, app/analytics.py   # FastAPI + §5 math
app/static/                     # index.html, methods.html, js/, css/
results/metrics.json, results/figures/
tests/
scripts/record_demo.py          # Playwright + ffmpeg → docs/demo.mp4
docs/challenge.md, docs/AI_USE.md, docs/video_script.md, docs/video_subtitles.srt,
docs/submission_text.md, docs/screenshots/
README.md, Dockerfile, Makefile, requirements.txt
```

## 8. Milestones (hackathon Sat Nov 14 – Sun Nov 15; submission closes Sun 11:59 pm local)

| # | When | Milestone | Check |
|---|---|---|---|
| M0 | Sat 9:00 | Data in place, scaffold, plan | 9 zips valid, imports work |
| M1 | Sat 10:30 | Ingest | row counts by region × sensor × year; no nulls in keys |
| M2 | Sat 12:00 | Grid + missing mask + overpass figure | grid totals = row counts |
| M3 | Sat 17:00 | Harmonize + validate | metrics.json; harmonized beats raw on test set (or honest explanation) |
| M4 | Sat 22:00 | Analytics + API + live data | pytest passes; endpoints < 2 s on a Texas-size polygon |
| M5 | Sun 11:00 | Frontend | full flow works; every R1–R18 visible |
| M6 | Sun 14:00 | Deploy | public URL, no login |
| M7 | Sun 18:00 | Video + README + submission text | demo.mp4 ≤ 30 s with subtitles |
| M8 | Sun 20:00 | Fresh-eyes review + fixes | judge checklist all green |

If behind schedule, cut in this order: land cover → Method A (keep B) → daily drill-down →
live API (keep NRT from zips) → Australia region. Never cut validation or R6/R9/R14.

## 9. Submission requirements

- Uses NASA data; describe which and how it shaped the project (FIRMS MODIS C6.1, VIIRS S-NPP,
  NOAA-20, NOAA-21 NRT; MCD12Q1/MCD64A1 if used), with DOIs.
- **Demo = video**, ≤ 30 s, English subtitles, public link (YouTube Unlisted). Over the limit
  = ineligible for Global Judging. (Verify against the 2026 Submission Guide.)
- All links public, no login. All content in English.
- **AI disclosure**: we use Claude Code. README + `docs/AI_USE.md` + submission text say where
  and how (code, debugging, writing). No AI-generated images/video without a visible watermark.
  No NASA logos or mission branding.
- Repo: https://github.com/jonahgigi534-wq/NASA-SpaceApps (`main`).
