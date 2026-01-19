from playwright.sync_api import sync_playwright, expect
import os
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        page.goto("http://localhost:8000", timeout=10000)

        # Fill form using IDs
        page.fill("#make", "Toyota")
        page.fill("#model", "Camry")
        page.fill("#year_min", "2020")
        page.fill("#year_max", "2023")

        # Click search
        page.click("#searchBtn")

        # Wait for results area
        # It takes a bit of time (simulated or real)
        page.wait_for_selector("#resultsArea:not(.hidden)", state="visible", timeout=15000)

        # Check if table has rows
        rows = page.locator("#resultsTableBody tr")
        # Mock data has 3 items
        count = rows.count()
        print(f"Found {count} rows")

        # Take screenshot of the results
        page.screenshot(path="verification/verification.png", full_page=True)

    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path="verification/error.png")
        raise e
    finally:
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
