# IOCL Fuel Outlet Scraper

A Playwright-based Python scraper for collecting Indian Oil outlet listing data and exporting state-wise and consolidated CSV files.

## How it works

1. Reads a CSV containing State and URL columns.
2. Opens each base URL with a persistent Chrome profile and visits sequential listing pages.
3. Parses listing cards for outlet name, dealer, address, phone, coordinates, status, and available links.
4. Adds the state label from the input row, standardizes the output columns, and removes duplicate rows.
5. Writes a CSV for each state and a consolidated All_States_IOCL.csv file.

## Output fields

The output schema includes:

- Brand and Dealer_Name
- Address, City, State, and Pincode
- Phone
- Latitude and Longitude
- Status
- Google_Map_URL and Detail_URL

CSV files use UTF-8 BOM encoding to improve compatibility with spreadsheet applications.

## Repository contents

- iocl_scraper_CSV.py — scraper entry point
- Input CSV examples — state and listing URL configuration
- A sample outlet CSV — example output data

## Requirements

- Python 3.10 or a compatible version
- Playwright
- pandas
- beautifulsoup4
- lxml
- Google Chrome installed at the configured path

Install Python packages:

    python -m venv .venv
    .venv/Scripts/Activate.ps1
    pip install playwright pandas beautifulsoup4 lxml

The script uses a persistent Chrome context and a custom Chrome executable path; it does not use Playwright's default browser executable for navigation.

## Configuration and run

Before running, review these constants in iocl_scraper_CSV.py:

- INPUT_CSV — must point to an input CSV with State and URL columns
- OUTPUT_FOLDER — directory for all generated CSVs
- CHROME_PATH — installed Chrome executable path
- USER_DATA — Chrome profile directory used by the persistent context

The paths currently refer to the original Windows workstation and must be adjusted for your environment.

Run:

    python iocl_scraper_CSV.py

The output folder receives <State>_IOCL.csv files for states with data and the consolidated All_States_IOCL.csv file.

## Notes

- The browser is visible (headless=False).
- Listing selectors and site behavior may change over time.
- Respect the source website's terms and applicable access policies.
