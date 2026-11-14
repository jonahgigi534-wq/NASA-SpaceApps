# FireBridge: Claude Code prompts, start to finish

Nine prompts, one per milestone. Paste them in order. Each one is in a code block so you can
copy it exactly.

**How to run them**
- Start Claude Code in the repo folder: `cd NASA-SpaceApps` then `claude`.
- Use **plan mode** (Shift+Tab) for Prompts 0 and 3. Read the plan before approving.
- After each prompt finishes and its check passes, type `/clear` before the next one.
  CLAUDE.md and docs/challenge.md reload automatically, so nothing is lost.
- Don't skip ahead. If a check fails, use the "If something goes wrong" prompts at the bottom.
- One person drives Claude Code. Everyone else reviews outputs, charts and the app.

Target times (Central): M0 Sat 9:00 · M1 10:30 · M2 12:00 · M3 17:00 · M4 22:00 ·
M5 Sun 11:00 · M6 14:00 · M7 18:00 · M8 20:00 · **submit by 22:00** (deadline 23:59).

---

## Before Prompt 0 (5 minutes, by hand)

1. `git clone https://github.com/jonahgigi534-wq/NASA-SpaceApps` and `cd NASA-SpaceApps`
2. Put all data in one folder on this laptop (for example `~/Downloads/firms`): the 9 FIRMS zips,
   and if you have them, the AppEEARS files (Texas, Amazon, Australia) and missing-dates table.
3. Open the challenge page's **Resources tab** and copy any new links or notes.
4. Have your FIRMS MAP_KEY handy.

---

## Prompt 0: data, setup, plan (M0)

Fill in the blanks, then paste.

```
Data folder: <PATH, e.g. ~/Downloads/firms>
FIRMS MAP_KEY: <KEY>
Anything new on the challenge Resources tab: <PASTE, or "nothing new">

Read CLAUDE.md and docs/challenge.md completely before doing anything.

1. Data. Copy every file from the data folder into the repo. Route each FIRMS zip by its ID to
   data/raw/texas/, data/raw/amazon/ or data/raw/australia/ using CLAUDE.md §3.1. AppEEARS
   files go to data/raw/appeears/<region>/. Warning: the three regions' AppEEARS GeoTIFFs have
   identical file names, so the browser saved duplicates as "name (1).tif", "name (2).tif" in
   unpredictable order. Do NOT route them by file name: open each .tif with rasterio, read its
   bounds, and assign it to the region whose box in data/regions/*.geojson contains its center.
   Rename to the original name (strip " (n)"). Expect per region: 25 MCD12Q1 LC_Type1 files and
   300 MCD64A1 Burn_Date files plus QA layers; report counts per region and anything missing.
   Region-prefixed files (texas-landcover-*, Amazon-landcover-*, aussie-landcover-*) route by
   prefix; skip the duplicate-named statistics CSVs (we don't need them). A missing-dates table goes to data/raw/missing_dates.csv. Verify all 9 FIRMS zips
   exist, open as valid zips, and contain a fire_archive_*.csv. If anything is missing or
   broken, stop and tell me exactly which file.
2. Key. Write FIRMS_MAP_KEY=<key> to .env. Confirm .env and data/raw are gitignored with
   git status.
3. Inspect. For each zip, print the CSV headers, first 3 rows, row count estimate, and min/max
   acq_date for both the archive and NRT files (stream from the zip; don't extract everything).
   Confirm against CLAUDE.md §3 and list every difference. Make one real FIRMS API call with
   the key for a small Texas box to confirm live mode works.
4. Resources. If I pasted anything from the Resources tab, check it against docs/challenge.md
   and CLAUDE.md, add new R-rows to the checklist if needed, and propose CLAUDE.md updates.
5. Scaffold. Keep the existing files (CLAUDE.md, KICKOFF_PROMPTS.md, .gitignore,
   data/raw/README.md, data/regions/*.geojson, docs/challenge.md). Create the rest of the
   layout in CLAUDE.md §7, requirements.txt (pandas, pyarrow, duckdb, numpy, scipy,
   statsmodels, shapely, rasterio, matplotlib, fastapi, uvicorn, httpx, python-dotenv, pytest,
   playwright), a Makefile with targets for each pipeline step plus `all`, `test`, `app`.
6. Environment. Create .venv, install requirements, run `playwright install chromium`, confirm
   all imports work. Check ffmpeg is installed; if not, give me the one install command for my OS.
7. Plan. Write a task list for milestones M1–M8 mapped to requirements R1–R18 (every R must
   map to at least one task).

Show me the plan and wait for my OK. After I approve, commit the scaffold and push to origin main.
```

**Check:** all 9 zips valid, the API call worked, imports pass, and every R1–R18 appears in the plan.

---

## Prompt 1: ingest (M1)

```
Implement pipeline/ingest.py per CLAUDE.md §3.

- Stream each zip's archive and NRT CSVs with usecols and explicit dtypes (chunked or DuckDB).
- Keep type == 0 (for NRT without `type`, follow CLAUDE.md §3.1).
- Normalize MODIS and VIIRS to one schema: region, sensor (MODIS/VIIRS), satellite
  (Terra/Aqua/S-NPP/NOAA-20/NOAA-21), datetime_utc, acq_date, lat, lon, frp, confidence_class
  (low/nominal/high per CLAUDE.md §4.4), confidence_raw, daynight, is_provisional.
- Write data/processed/fires_<region>_<sensor>.parquet (zstd, sorted by date).
- Print: rows by region × sensor × satellite × year; share of each `type` removed; null counts in
  key columns; archive end date and NRT start/end date per file.
- pytest: confidence mapping, schema and dtypes, type filter, no nulls in keys.

Flag anything odd (gaps, sudden drops, duplicate rows). Then run the tests, commit and push.
```

**Check:** counts look plausible, nothing null, tests pass.

---

## Prompt 2: grid, missing data, overpass check (M2)

```
Implement pipeline/grid.py per CLAUDE.md §4.1 and §3.2.

- 0.1° daily and 0.25° monthly aggregates per region × satellite × day/night: n_det,
  frp_sum, frp_mean.
- Missing-data mask: use data/raw/missing_dates.csv if present, otherwise infer per CLAUDE.md
  §3.2. Store missing days as NaN, never 0. Print how many missing days per satellite.
- Assert grid totals equal ingested row counts (pytest).
- results/figures/overpass_times.png: acq_time distribution by year for Terra, Aqua, S-NPP,
  NOAA-20 (orbit-drift check). Tell me in one paragraph what it shows.

Run tests, commit and push.
```

**Check:** totals match, missing days counted, overpass figure looks sensible.

---

## Prompt 3: harmonize and validate (M3, the most important prompt; use plan mode)

```
Implement pipeline/harmonize.py, pipeline/validate.py and (if AppEEARS data exists)
pipeline/landcover.py, exactly per CLAUDE.md §4.

- Calibration pair: MODIS Aqua vs VIIRS S-NPP, same day and overpass, 0.25° monthly cells.
- Method A (detection-limit matching) and Method B (log-log OLS + quantile mapping), per
  region (× land-cover group if available) × day/night.
- Baselines: raw VIIRS and one global ratio.
- Fit on 2012–2018, test on 2019 → archive end. Transfer test on NOAA-20 (never used in fitting).
- Sensitivity run excluding low-confidence detections.
- Pick the winning method by test-set score; save coefficients to data/processed/.
- Build the final harmonized record per CLAUDE.md §4.4 (sensor combining and de-duplication rule
  documented in code comments and in metrics.json).
- results/metrics.json: every metric (R², bias %, RMSE, Pearson r) per region and overall,
  monthly totals and per cell, raw vs harmonized, holdout and transfer.
- Figures: continuity plot per region 2001 → present (raw vs harmonized, switch dates marked),
  scatter MODIS vs VIIRS before/after, bar chart of bias before/after, optional burned-area check.

Show me the plan first. After it runs, give me a plain-English summary: which method won, by
how much, where it struggles and why, and the 3 numbers I should put in the video. If
harmonization doesn't beat the baselines somewhere, say so and propose a fix. Don't hide it.
Commit and push.
```

**Check:** read `results/metrics.json` and open the continuity plots yourself. The jump in 2012 should be gone in the harmonized line.

---

## Prompt 4: analytics, live data, backend (M4)

```
Implement pipeline/live.py, pipeline/build_app_data.py, app/analytics.py and app/main.py per
CLAUDE.md §3.1, §5 and §6.

- live.py: fetch recent days from the FIRMS area API (VIIRS_NOAA20_NRT, VIIRS_NOAA21_NRT,
  MODIS_NRT) for each region, from the end of the zips' NRT data to today, in ≤10-day chunks,
  cached to disk, respecting the rate limit. The app must still work offline from the cache.
- build_app_data.py: harmonized 0.1° daily cells (all three modes, missing + provisional flags)
  and a slim hotspot points table for CSV export, in data/app/ (zstd parquet). Report total size;
  keep under 200 MB if possible, otherwise propose where to host the points file.
- analytics.py: all of §5. Polygon → cells (shapely, cell centers), daily series with NaN for
  missing days, climatology (median, mean, std; ±15-day smoothing), anomalies, month×year
  grid, yearly ranking, fire season, high-risk months, chance of unusual month, current month
  vs median, and the plain-language summary built only from computed numbers.
- main.py: every endpoint in CLAUDE.md §6 including /api/export/hotspots.csv (streamed) and
  /api/export/series.csv. Accept a polygon OR a lat/lon box OR a point + radius km.
- pytest: polygon selection, lat/lon and radius input, z-score and % of median on a synthetic
  series, NaN propagation, fire-season window on a synthetic seasonal curve, CSV columns,
  endpoint response time < 2 s for a Texas-sized polygon.

Run the server, call each endpoint with curl for a Texas polygon, show me the outputs, then
commit and push.
```

**Check:** tests pass, every endpoint answers fast, hotspots CSV opens in Excel.

---

## Prompt 5: frontend (M5)

```
Build app/static/ (index.html, methods.html, js/, css/) per CLAUDE.md §6. Plain HTML/JS, no
build step. Use the frontend-design skill if available.

- Layout: map + area tools (draw, lat/lon box, point + radius, presets) on the left; key
  figures strip, plain-language summary, and the three tabs (Burning calendar, Patterns &
  critical periods, Now vs history) on the right; long-term raw-vs-harmonized chart below.
- Burning calendar: month × year heatmap 2001 → present, sequential accessible ramp for counts,
  toggle to a diverging accessible ramp for anomaly vs median, legend with units, grey for
  missing, hatching for provisional; click a month for the daily view.
- Mode toggle harmonized / MODIS only / raw VIIRS on the calendar and long-term chart.
- Exports: hotspots CSV, analytics CSV, PNG download for every chart.
- Presets: find the 3–4 biggest anomalies in the data (e.g. Texas 2011, Amazon 2019/2024,
  Australia 2019–20 if the data shows them) and use those; don't guess.
- Methods page: harmonization explained simply, validation figures and numbers loaded from
  results/metrics.json, data sources with DOIs, limitations, AI-use note.
- Accessibility: keyboard navigation, ARIA labels, colorblind-safe colors, works on a phone.

Then run the app and test the full flow with Playwright: draw → date range → calendar → click a
month → patterns → now vs history → mode toggle → each export. Screenshot each step into
docs/screenshots/. Finally, go through docs/challenge.md R1–R18 one by one and tell me where
each is visible in the app; fix anything missing. Commit and push.
```

**Check:** open the app yourself, try a preset and a hand-drawn area, download both CSVs.

---

## Prompt 6: deploy (M6)

```
Make the app deployable as one Docker container: Dockerfile, data/app included or downloaded
at build time, port from $PORT, health check at /api/regions. Live mode should use the cache and
refresh in the background with FIRMS_MAP_KEY from an environment variable (never baked into the
image). Test the container locally.

Then give me exact click-by-click steps to deploy on Render (fallback: Hugging Face Spaces,
Docker type) so the URL is public with no login, including where to set FIRMS_MAP_KEY. After I
paste the live URL, run the Playwright flow from Prompt 5 against it and report any failures.
Put the live URL in README.md. Commit and push.
```

**Check:** the public URL works in a private/incognito window on a phone.

---

## Prompt 7: video, README, submission text (M7)

```
Demo is a VIDEO: max 30 seconds, English subtitles (check the 2026 Submission Guide; going over
makes us ineligible for Global Judging). Use only numbers from results/metrics.json and the app.

1. docs/video_script.md: a storyboard that fits in 27 seconds. Beats: 0–4 s the problem (MODIS
   ending, VIIRS doesn't match, 2012 jump); 4–9 s raw vs harmonized long-term chart, jump
   disappears; 9–12 s one validation number; 12–24 s the app on the live URL: draw an area,
   burning calendar appears, current month vs median, download hotspots CSV; 24–27 s app name,
   URL, "Built on NASA FIRMS MODIS + VIIRS data". For each shot: start/end, on-screen action,
   subtitle (max ~8 words).
2. docs/video_subtitles.srt matching the script.
3. scripts/record_demo.py: Playwright records the app shots at 1920×1080 against the live URL;
   chart and title shots are rendered from results/figures/ and plain text cards; ffmpeg joins
   them, burns in the subtitles, writes docs/demo.mp4. Verify with ffprobe that it's ≤ 30.0 s
   and 1080p and tell me the exact duration. No AI-generated imagery, no NASA logos.
4. README.md: what it is, live link, video link placeholder, problem, NASA data used and how it
   shaped the project (with DOIs), method, validation results table, how to run locally,
   limitations, AI-use disclosure, team.
5. docs/AI_USE.md: specific disclosure of where and how Claude Code was used.
6. docs/submission_text.md: text for each Space Apps project form field (title, summary, how it
   addresses the challenge, NASA data used, AI use), plus steps to upload demo.mp4 to YouTube as
   Unlisted with subtitles.

Commit and push (skip demo.mp4 if over 50 MB).
```

**Check:** watch the video start to finish with sound off. Every subtitle readable, ≤ 30 s.

---

## Prompt 8: fresh-eyes judge review (M8)

```
Use a subagent that has NOT seen our work so far. Give it only: docs/challenge.md, the live URL,
README.md, results/metrics.json and docs/demo.mp4's script. Ask it to act as a Space Apps judge
and score us 1–10 on Impact, Creativity, Validity, Relevance and Presentation, check every
R1–R18 item on the live site, and list the 10 most important problems (broken things first,
then anything confusing to a fire manager, then anything a scientist would question).

Then fix everything you can in under 90 minutes, highest impact first, re-run tests and the
Playwright flow on the live URL, redeploy, and give me a final checklist: live URL works, video
≤ 30 s with subtitles, every link public with no login, AI use disclosed, NASA data described.
Commit and push.
```

**Then submit** on the Space Apps site by 22:00: project link, video link, repo link,
description from `docs/submission_text.md`. Click **Submit for Judging**.

---

## If something goes wrong

**A check fails:**
```
The check for this milestone failed: <what you saw>. Find the root cause before changing code,
explain it in two sentences, fix it, re-run the check, and show me the result.
```

**Claude Code is going in circles:**
```
Stop. Summarize what you've tried, what failed and why. Propose the simplest approach that meets
CLAUDE.md for this milestone, and wait for my OK.
```

**Running behind schedule:**
```
We're behind. Read CLAUDE.md §8's cut order and tell me what to cut to finish M<N> by <time>
without touching validation, the burning calendar, current-month-vs-median, or the hotspots CSV.
```

**A teammate's laptop needs to run the app:**
```
Write SETUP.md: exact steps for a teammate to clone, add data, install, run the pipeline with
make all, and start the app. Then run through it yourself from a clean clone to confirm it works.
```
