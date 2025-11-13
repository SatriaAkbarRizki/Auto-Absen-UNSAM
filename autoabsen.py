import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from zoneinfo import ZoneInfo
import os
import send_email

NIM = os.getenv("NIM")
PASSWORD = os.getenv("PASSWORD")


LOGIN_URL = "https://sso.unsam.ac.id/realms/Production/protocol/openid-connect/auth?state=9316d01bff05ae52e5f9216b31f60671&scope=profile%20email%20openid&response_type=code&approval_prompt=auto&redirect_uri=https%3A%2F%2Fmahasiswa.unsam.ac.id%2F&client_id=mahasiswa"
JADWAL_URL = "https://mahasiswa.unsam.ac.id/simkuliah/jadwalkuliah"
SIMKULIAH_URL = "https://mahasiswa.unsam.ac.id/simkuliah"

async def run():
    print("🚀 Mulai script absensi...")

    async with async_playwright() as p:
        
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(LOGIN_URL)
            await page.fill('input#username', NIM)
            await page.fill('input#password', PASSWORD)
            await page.click('input#kc-login')


            await page.wait_for_url("**/mahasiswa.unsam.ac.id/**", timeout=15000)
            print("✅ Login sukses!")
            await page.goto(JADWAL_URL)
            await page.wait_for_selector('#calendar table.fc-list-table tbody tr')

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

            nameMK = ""
            jakarta = ZoneInfo("Asia/Jakarta")
            now = datetime.now(jakarta)
            now_date = now.strftime("%Y-%m-%d")
            now_time = now.strftime("%H:%M")
            hour = now.hour

            print(f"⏰ Sekarang: {now_date}, {now_time}")

            if (hour >= 19 or hour > 6):
                print("Waktu sudah malam, keluar dari script.")
                await browser.close()
                exit(0)
                
            

            found = False
            for row in data:
                if row["date"] == now_date:
                    if row["time"]:
                        start, end = row["time"].split(" - ")
                        nameMK = row['title']
                        print(f"🔎 Cek jadwal {row['title']} [{start} - {end}]")
                        if start <= now_time <= end:
                            print("🟢 Jadwal cocok, absen sekarang!")
                            found = True
                            break


            if found:
                await page.goto(SIMKULIAH_URL)

                try:
                    await page.wait_for_selector("button.btn-absensi-pertemuan", timeout=5000)
                    await page.click("button.btn-absensi-pertemuan")
                    print("✅ Klik ABSEN berhasil, tunggu status...")
                    send_email.succesAbsen(mataKuliah=nameMK, tanggal=now_date, waktu=now_time)
                except:
                    print("⚠️ Tombol absen tidak ditemukan!")
                
                try:
                    await page.wait_for_selector("p.badge-success", timeout=8000)
                    status = await page.inner_text("p.badge-success")

                    print(f"🎉 Absen berhasil, status: {status}")
                except:
                    send_email.errorAbsen(mataKuliah=nameMK, tanggal=now_date, waktu=now_time)
                    print("⚠️ Tidak menemukan status HADIR. Cek manual!")

            else:
                print("⏸ Tidak ada jadwal aktif sekarang.")

            await browser.close()
            print("🏁 Script selesai.")
        except Exception as e:
            send_email.errorAbsen(mataKuliah=nameMK, tanggal=now_date, waktu=now_time)
            print("Error Running: ", e)

asyncio.run(run())
