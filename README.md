# LVO 2026 List Browser

A searchable, sortable browser for all 656 army lists submitted to the **LVO 2026 Warhammer 40k Championships** (Las Vegas Open), pulled from Best Coast Pairings.

**Live page:** open `index.html`, or visit the GitHub Pages link once Pages is turned on for this repo.

## Features
- Sort by player, faction, detachment, force disposition, unit count or points
- Filter by faction (including individual Space Marine chapters), detachment and force disposition
- Search any player, unit or piece of wargear across every list
- Faction breakdown with counts and share of the field
- Most-played units for whatever you've filtered to
- Click any list to see its units, enhancements, the full list text and a link back to Best Coast Pairings

## What's in the repo
| Path | What it is |
|---|---|
| `index.html` | The whole app in one file. List data is embedded gzip-compressed and unpacked in the browser. |
| `data/LVO_2026_BCP_List_Links.csv` | The 656 Best Coast Pairings list links |
| `data/lvo_2026_lists_raw.json` | Raw list text captured from each BCP list page |
| `data/lvo_2026_lists_parsed.json` | Parsed data: player, faction, chapter, detachments, disposition, units, enhancements |
| `scripts/grab_lists_from_bcp.js` | Browser console script that loads every list and downloads the raw JSON |
| `scripts/parse_lists.py` | Python parser that turns the raw text into the parsed JSON |

## Notes
- Lists were submitted in several export formats (GW app, New Recruit, WTC-style and hand-typed). The parser handles all of them; faction was inferred from units for a few lists that didn't state one.
- Points totals are summed from the units as players submitted them, so a few lists show slightly over or under 2000.
- Two lists don't name a detachment.

Army list data belongs to the players and Best Coast Pairings. Warhammer 40,000 is a trademark of Games Workshop. This is an unofficial fan project.
