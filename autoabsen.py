# check_and_absen.py
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import os

NIM = os.getenv("NIM")
PASSWORD = os.getenv("PASSWORD")

LOGIN_URL = "https://sso.unsam.ac.id/realms/Production/protocol/openid-connect/auth?state=...&client_id=mahasiswa"
JADWAL_URL = "https://mahasiswa.unsam.ac.id/simkuliah/jadwalkuliah"
SIMKULIAH_URL = "https://mahasiswa.unsam.ac.id/simkuliah"

async def run_once():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # true for cloud
        page = await browser.new_page()

        # Login
        await page.goto(LOGIN_URL)
        await page.fill('input#username', NIM)
        await page.fill('input#password', PASSWORD)
        await page.click('input#kc-login')
        await page.wait_for_url("**/mahasiswa.unsam.ac.id/**", timeout=30000)

        # Grab schedule
        await page.goto(JADWAL_URL)
        await page.wait_for_selector('#calendar table.fc-list-table tbody tr', timeout=15000)
        data = await page.evaluate("""() => {
          const rows = Array.from(document.querySelectorAll('#calendar table.fc-list-table tbody tr'));
          const out = [];
          let currentDate = null;
          rows.forEach(tr => {
            if (tr.classList.contains('fc-list-day')) {
              currentDate = tr.getAttribute('data-date') || tr.querySelector('.fc-list-day-text')?.textContent.trim();
            } else if (tr.classList.contains('fc-list-event')) {
              const time = tr.querySelector('.fc-list-event-time')?.textContent.trim() || '';
              const title = tr.querySelector('.fc-list-event-title a')?.textContent.trim()
                          || tr.querySelector('.fc-list-event-title')?.textContent.trim() || '';
              out.push({date: currentDate, time, title});
            }
          });
          return out;
        }""")

        now_date = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M")
        print(f"Now: {now_date} {now_time}")

        found = False
        for row in data:
            if row.get("date") == now_date and row.get("time"):
                start, end = row["time"].split(" - ")
                if start <= now_time <= end:
                    print(f"Match: {row.get('title')} {row.get('time')}")
                    found = True
                    break

        if found:
            await page.goto(SIMKULIAH_URL)
            # click if button present
            btn = await page.query_selector("button.btn-absensi-pertemuan") or await page.query_selector("button.btn-detail-pertemuan-modal")
            if btn:
                await btn.click()
                print("Clicked absen button.")
                # check for HADIR
                try:
                    await page.wait_for_selector("p.badge-success", timeout=7000)
                    status = await page.inner_text("p.badge-success")
                    print("Absen success:", status)
                except Exception:
                    print("Absen clicked but HADIR not detected.")
            else:
                print("Absen button not found.")
        else:
            print("No matching schedule now.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_once())
