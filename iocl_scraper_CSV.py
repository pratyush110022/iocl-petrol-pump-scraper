#!/usr/bin/env python3
r"""
IndianOil (IOCL) Petrol Pump Scraper
Uses your local Chrome profile to bypass 403.

Requirements:
    pip install playwright pandas beautifulsoup4 lxml
    playwright install chromium

Input CSV:
State,URL
Goa,https://locator.iocl.com/location/goa
Andhra Pradesh,https://locator.iocl.com/location/andhra-pradesh

Output Folder:
C:\Users\prdas4\Downloads\IOCL_State_Wise_Output

Output Files:
    Goa_IOCL.csv
    Andhra_Pradesh_IOCL.csv
    All_States_IOCL.csv
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
import os


# ==========================================================
# INPUT / OUTPUT PATHS
# ==========================================================

INPUT_CSV = r"C:\Users\prdas4\Downloads\2025_Projects\2025_H1\H1_2025\2-Junks Check\Petrol Pump\IOCL\input - City.csv"

OUTPUT_FOLDER = r"C:\Users\prdas4\Downloads\2025_Projects\2025_H1\H1_2025\2-Junks Check\Petrol Pump\IOCL\IOCL_State_Wise_Output"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ==========================================================
# CHROME PROFILE SETTINGS
# ==========================================================

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

USER_DATA = r"C:\Users\prdas4\AppData\Local\Google\Chrome\User Data\IOCL"


# ==========================================================
# OUTPUT COLUMNS
# ==========================================================

COLUMNS = [
    "Brand",
    "Dealer_Name",
    "Address",
    "City",
    "State",
    "Pincode",
    "Phone",
    "Latitude",
    "Longitude",
    "Status",
    "Google_Map_URL",
    "Detail_URL"
]


# ==========================================================
# SAFE FILE NAME FUNCTION
# ==========================================================

def make_safe_filename(value):
    """
    Converts state name into safe filename format.
    Example:
        Andhra Pradesh -> Andhra_Pradesh
        Jammu & Kashmir -> Jammu_&_Kashmir
    """

    value = str(value).strip()

    value = (
        value.replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace("*", "_")
        .replace("?", "_")
        .replace('"', "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace("|", "_")
        .replace(" ", "_")
    )

    while "__" in value:
        value = value.replace("__", "_")

    return value.strip("_")


# ==========================================================
# PARSE LISTING PAGE
# ==========================================================

def parse_listing(page):
    soup = BeautifulSoup(page.content(), "lxml")

    rows = []

    for box in soup.select("div.store-info-box"):

        try:
            brand = box.select_one("li.outlet-name a")

            dealer = ""
            info = box.select("div.info-text")

            if len(info) > 1:
                dealer = info[1].get_text(" ", strip=True)

            addr = box.select_one("li.outlet-address .info-text")

            phone = box.select_one("li.outlet-phone a")

            lat = box.select_one("input.outlet-latitude")
            lon = box.select_one("input.outlet-longitude")

            status = box.select_one("li.outlet-timings .info-text")

            detail = box.select_one("a.btn-website")
            gmap = box.select_one("a.btn-direction")

            address = ""
            city = ""
            pin = ""

            if addr:
                lines = list(addr.stripped_strings)

                address = ", ".join(lines)

                if lines:
                    last = lines[-1]

                    if "-" in last:
                        parts = last.split("-")

                        if len(parts) >= 2:
                            city = parts[0].strip()
                            pin = parts[-1].strip()

                    elif len(lines) >= 2:
                        city = lines[-2].strip()

            rows.append({
                "Brand": brand.get_text(strip=True) if brand else "",
                "Dealer_Name": dealer,
                "Address": address,
                "City": city,
                "State": "",
                "Pincode": pin,
                "Phone": phone.get_text(strip=True) if phone else "",
                "Latitude": lat.get("value", "") if lat else "",
                "Longitude": lon.get("value", "") if lon else "",
                "Status": status.get_text(" ", strip=True) if status else "",
                "Google_Map_URL": gmap.get("href", "") if gmap else "",
                "Detail_URL": detail.get("href", "") if detail else ""
            })

        except Exception as e:
            print(f"Parse Error: {e}")

    return rows


# ==========================================================
# SAVE STATE FILE
# ==========================================================

def save_state_file(state, state_rows):
    """
    Saves one CSV file for the given state.
    Filename format:
        State_Name_IOCL.csv
    """

    if not state_rows:
        print(f"No records to save for state: {state}")
        return None

    state_df = pd.DataFrame(state_rows)

    for col in COLUMNS:
        if col not in state_df.columns:
            state_df[col] = ""

    state_df = (
        state_df[COLUMNS]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    safe_state = make_safe_filename(state)

    state_file = os.path.join(
        OUTPUT_FOLDER,
        f"{safe_state}_IOCL.csv"
    )

    state_df.to_csv(
        state_file,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nSaved {len(state_df)} records for {state}")
    print(f"State File: {state_file}")

    return state_df


# ==========================================================
# SAVE MASTER FILE
# ==========================================================

def save_master_file(all_rows):
    """
    Saves consolidated All_States_IOCL.csv file.
    """

    if not all_rows:
        print("\nNo records found. Master file not created.")
        return

    master_df = pd.DataFrame(all_rows)

    for col in COLUMNS:
        if col not in master_df.columns:
            master_df[col] = ""

    master_df = (
        master_df[COLUMNS]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    master_file = os.path.join(
        OUTPUT_FOLDER,
        "All_States_IOCL.csv"
    )

    master_df.to_csv(
        master_file,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 80)
    print(f"Total Records : {len(master_df)}")
    print(f"Master File   : {master_file}")
    print("=" * 80)


# ==========================================================
# MAIN SCRAPER
# ==========================================================

def main():

    df_input = pd.read_csv(INPUT_CSV)

    all_rows = []

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA,
            executable_path=CHROME_PATH,
            headless=False,
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/138.0.0.0 Safari/537.36"
            ),
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--disable-popup-blocking",
                "--disable-notifications"
            ]
        )

        page = context.new_page()

        page.set_extra_http_headers({
            "Accept-Language": "en-IN,en;q=0.9",
            "Upgrade-Insecure-Requests": "1"
        })

        for _, row in df_input.iterrows():

            state = str(row["State"]).strip()
            base = str(row["URL"]).strip()

            print("\n" + "=" * 80)
            print(f"Processing State: {state}")
            print("=" * 80)

            state_rows = []

            page_no = 1

            while True:

                url = f"{base}?page={page_no}"

                print(f"\nProcessing: {url}")

                try:

                    page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=90000
                    )

                    page.wait_for_timeout(5000)

                    print("Title :", page.title())
                    print("URL   :", page.url)

                    count = page.locator(
                        "div.store-info-box"
                    ).count()

                    print("store-info-box :", count)

                    if count == 0:
                        print("No more listings found.")
                        break

                    items = parse_listing(page)

                    if not items:
                        print("No data parsed.")
                        break

                    for item in items:
                        item["State"] = state

                        state_rows.append(item)
                        all_rows.append(item)

                    print(
                        f"Extracted {len(items)} records "
                        f"from page {page_no}"
                    )

                    page_no += 1

                    time.sleep(1)

                except Exception as e:
                    print(f"Page Error: {e}")
                    break

            # ==================================================
            # SAVE CURRENT STATE IMMEDIATELY
            # ==================================================

            save_state_file(state, state_rows)

        context.close()

    # ==========================================================
    # SAVE CONSOLIDATED MASTER FILE
    # ==========================================================

    save_master_file(all_rows)


# ==========================================================
# SCRIPT ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()