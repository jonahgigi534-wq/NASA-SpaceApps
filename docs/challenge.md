# Challenge: Harmonization of MODIS and VIIRS Hot Spots (NASA Space Apps 2026)

Official page: https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/
Subject: Earth Science / Software. Difficulty: Advanced / Intermediate. Challenge author: CONAE
(Argentina's national space agency).

> The full official text is at the bottom of this file (copied from the challenge page on
> Nov 13). **The official text wins** if anything above it differs. Still check the page's
> **Resources tab** on Saturday morning: more resources may be added before the hackathon.

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

## Requirement checklist (from the official text; Claude Code tracks coverage here)

| # | Requirement (official wording in quotes) | Where we cover it |
|---|---|---|
| R1 | Harmonize MODIS + VIIRS so "the sensor of origin no longer matters" | CLAUDE.md §4 |
| R2 | Prove the harmonization works (our addition; it's what makes R1 credible) | CLAUDE.md §4.5 |
| R3 | A web application that takes the harmonized data as input | CLAUDE.md §6 |
| R4 | Select a region: draw on a map **or enter latitude/longitude** | CLAUDE.md §6 |
| R5 | Pick "a specific date range" | CLAUDE.md §6 |
| R6 | Burning activity calendar: **number of hotspots from the early 2000s to the present** (month × year) | CLAUDE.md §5, §6 |
| R7 | "Which periods of the year see more fires" | critical periods, CLAUDE.md §5.2 |
| R8 | "Which years had more burning activity" | yearly totals + ranking, CLAUDE.md §5 |
| R9 | "How a current fire compares with previous ones"; **current month vs the historical median** | CLAUDE.md §5.3, live data §3.1 |
| R10 | Anomalies against multi-year averages | CLAUDE.md §5.1 |
| R11 | Number of fires detected (hotspot counts as a key figure) | CLAUDE.md §6 key-figures strip |
| R12 | Color ramps that show similarities and differences across months; **accessible** color ramps | CLAUDE.md §6 |
| R13 | "Download analytics and visualizations" (charts as PNG, summary tables) | CLAUDE.md §6 exports |
| R14 | **CSV of the hotspots detected during a search** (the points themselves) | CLAUDE.md §6 exports |
| R15 | Audience: early warning, emergency responders, scientists, land managers, **firefighters** | plain-language summary, CLAUDE.md §6 |
| R16 | Missing data is not zero fire (our addition) | CLAUDE.md §3, §5 |
| R17 | Use NASA Earthdata FIRMS hotspots (MODIS + VIIRS) | CLAUDE.md §3 |
| R18 | Check the Resources tab for anything added before the hackathon | Prompt 0 |

## Official text (copied from the challenge page, Nov 13, 2026)

Understanding how burning activity is distributed across our planet over time, including wildfires and agricultural burns intense enough to be detected by satellite sensors, enables us to anticipate critical periods, guide monitoring efforts, and improve fire response. Satellites have tracked active fire hotspots for more than two decades, but the record is split across sensors whose data cannot be compared directly, leaving fire managers without a consistent picture of when and where burning has occurred. Your challenge is to build a web application that harmonizes these records into a burning activity calendar based on active fire hotspots, enabling early warning and emergency responders, scientists, and land managers to examine historical fire patterns, unusual conditions, and critical periods within a selected area of interest.


Background
Fire regimes

Some ecosystems need periodic fires to maintain their function and their structure. However, changes in fire intensity, extent, and frequency can have negative impacts on climate, society, and biodiversity, along with the ecosystem services they provide. Fires can also cause loss of life and properties, degradation of health, and acute risk to fire managers.

Because humans have modified global patterns of vegetation, ignition, and climate over millennia, fires on both local and global scales are increasingly human-related.

Burning activity involves wildfires in natural vegetation and forested areas, as well as anthropogenic fires associated with agriculture, land-clearing, waste disposal, and industrial activities. It is one of the many dynamic phenomena that can be detected with remote sensing.

Satellite fire detection and monitoring

Climate models project that fire weather will become more common and more intense. Earth Observation (EO) satellites provide technological solutions for early detection, rapid response, and postfire assessment, measuring thermal radiation and smoke across regional to global scales.

Detecting hotspots on Earth's surface

EO satellites provide information on fire location, intensity, and temporal evolution. Satellite sensors operating in the thermal infrared (TIR) range can detect hotspots on the Earth's surface generated by urban and wildfires, volcanic eruptions, and industrial processes such as gas flares in oil and gas operations.

For active fires, detection and monitoring rely mainly on mid-infrared (MIR) and TIR measurements, where active combustion produces its stronger signal. Sensors such as MODIS and VIIRS provide real-time thermal anomaly detection, enabling early hotspot identification and the assessment of burned areas.

Burn activity calendars

Using satellite-detected hotspots, fire activity calendars can be developed by integrating historical information with recent data, allowing for the rapid visual identification of seasonal patterns, anomalies, and trends in each region.

MODIS sensors on board Terra and Aqua satellites provide more than two decades of observations, but they are approaching the end of their operational life and are being replaced by VIIRS sensors. Their records cannot be directly compared without harmonization, since MODIS and VIIRS have different spatial resolutions, sensitivities, and observation schedules.

Therein lies the root of the challenge. As fire frequency and intensity increase, emergency managers benefit from an updated and consistent hotspot calendar that enables them to rapidly visualize, for example, which month and years had the highest fire activity, and compare the burning activity of the current month against the historical median for a selected area.

You may consider harmonizing NASA Earthdata FIRMS hotspots, combining the extensive historical series of MODIS with the continuity and greater detail of VIIRS.

Emergency managers could then use the web application to monitor sensitive regions, recognize changes relative to historical patterns, and strengthen fire forecasting and response.

Objectives
Your challenge is to develop a harmonized burning activity calendar based on active fire hotspots in a web application, combining the extensive historical series of MODIS with the continuity and greater detail of VIIRS to provide a consistent time series of hotspot activity.

This challenge could be approached in two parts. The first is MODIS and VIIRS hotspot harmonization, so that by the end of that phase the sensor of origin no longer matters and the patterns, trends, and anomalies become the focus.

The second involves developing a web application that takes harmonized hotspot data as input. Through this visual tool, a user could select a region and a specific date range, then download analytics and visualizations of fire activity.

A calendar of burning activity showing the number of hotspots detected from the early 2000s to the present, built on the harmonized hotspots dataset and integrated into the web application, would give emergency managers a view of the fire history of an area: which periods of the year see more fires, which years had more burning activity, and how a current fire compares with previous ones.

In addition to numerical information, you could consider how color ramps might represent similarities and differences in the number of detected hotspots across months, providing an accessible and intuitive way to visualize fire activity. A downloadable CSV File of hot spots detected during a search would be another useful output.

Potential Considerations
You may (but are not required to) consider the following:

Your target audience can include early warning and emergency responders, scientists, land managers, and firefighters.
Consider making your web application interactive – for example, a map where users can draw the area of interest, or an option to enter latitude and longitude.
Consider using accessible color ramps.
Your tool could depict a burning calendar
Your tool could focus on a few key indices and figures and present them through data visualizations, such as:
Historical comparisons, including anomalies against multi-year averages
Number of fires detected and reported
For data and resources related to this challenge, refer to the Resources tab at the top of the page. More resources may be added before the hackathon begins.
