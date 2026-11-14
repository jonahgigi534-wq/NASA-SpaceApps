# Challenge: Harmonization of MODIS and VIIRS Hot Spots (NASA Space Apps 2026)

Official page: https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/
Subject: Earth Science / Software. Difficulty: Advanced / Intermediate. Challenge author: CONAE
(Argentina's national space agency).

> **TEAM TODO before Prompt 0:** open the official page above and paste the full text
> (summary, objectives, potential considerations, resources) into the "Official text" section
> at the bottom. We could not fetch it automatically. Everything else in this file was assembled
> from secondary sources and our own notes, so the official text wins if anything differs.

## What the challenge asks for (summary, from public descriptions of the official text)

- Context: satellites have tracked active-fire hotspots for 20+ years, including wildfires and
  agricultural burns big enough to be seen from orbit. But the record is split across sensors
  (MODIS 1 km, VIIRS 375 m) whose data can't be compared directly, so fire managers lack a
  consistent picture of when and where burning has happened.
- **Build a web application** that **harmonizes these records into a burning activity calendar**
  based on active-fire hotspots.
- Users: **early-warning and emergency responders, scientists, and land managers**.
- Within a **user-selected area of interest**, they must be able to examine:
  1. **historical fire patterns**
  2. **unusual conditions** (anomalies)
  3. **critical periods** (when burning is typically most intense or most likely)

## Our team's notes on the brief (from the challenge list we reviewed)

MODIS has 20+ years of fire hotspot data but is aging out; VIIRS has better resolution but
different sensitivity and schedule, so the records can't be compared directly. Two parts:
harmonize the two FIRMS datasets so the source sensor stops mattering, then build a web app
with a "burning activity calendar" where a user draws an area, picks dates, and gets anomalies
against multi-year averages plus a CSV download.

## Why it matters now (verify before quoting in the demo)

- NASA plans to end Terra MODIS data collection in January 2027 and Aqua MODIS around
  September 2027 (reported by Copernicus CAMS, Feb 2026).
- The FIRMS archive form lists VIIRS S-NPP data ending 2 November 2026.
- So the 20+ year MODIS record is about to stop, and VIIRS is the only way forward. Without
  harmonization, every long-term fire trend has an artificial jump in 2012.

## Requirement checklist (used by Claude Code to track coverage)

| # | Requirement | Where we cover it |
|---|---|---|
| R1 | Harmonize MODIS + VIIRS into one consistent record | CLAUDE.md §4 |
| R2 | Prove the harmonization works | CLAUDE.md §4.5 |
| R3 | Web app | CLAUDE.md §6 |
| R4 | User-selected area of interest (draw on map) | CLAUDE.md §6 |
| R5 | Burning activity calendar | CLAUDE.md §5–6 |
| R6 | Historical fire patterns | long-term chart, calendar by year (§6) |
| R7 | Unusual conditions (anomalies vs multi-year normal) | CLAUDE.md §5 |
| R8 | Critical periods | CLAUDE.md §5.1 |
| R9 | Useful to responders, scientists, land managers | presets, plain-language summary panel, CSV (§6) |
| R10 | CSV download | CLAUDE.md §6 |
| R11 | Missing data is not zero fire | CLAUDE.md §3, §5 |

## Official text

(paste here)
