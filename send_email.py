import resend
import os
resend.api_key = os.getenv("EMAILAPI")




def succesAbsen(mataKuliah, tanggal, waktu):
  SUCCES_ABSEN =  f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style> body {{ font-family: Arial, sans-serif; line-height: 1.6; }} .container {{ padding: 20px; border: 1px solid #ddd; border-radius: 8px; max-width: 600px; margin: auto; background-color: #f9f9f9; }} .header {{ color: #28a745; }} .details {{ background-color: #ffffff; padding: 15px; border-left: 4px solid #28a745; margin-top: 20px; }} .footer {{ margin-top: 30px; font-size: 0.9em; color: #777; }} </style>
    </head>
    <body>
        <div class="container">
            <h2 class="header">✅ Absensi Berhasil!</h2>
            <p>Halo,</p>
            <p>Ini adalah konfirmasi otomatis bahwa absensi untuk mata kuliah berikut telah berhasil dicatat pada hari ini.</p>
            <div class="details">
                <p><strong>Mata Kuliah:</strong> {mataKuliah}</p>
                <p><strong>Tanggal:</strong> {tanggal}</p>
                <p><strong>Waktu Submit:</strong> {waktu}</p>
                <p><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">BERHASIL</span></p>
            </div>
            <div class="footer">
                <p>Script auto-absen berjalan dengan normal.</p>
                <br>
                <p>Terima kasih,<br>Pengingat Absen Otomatis</p>
            </div>
        </div>
    </body>
    </html>
    """
  sendingEmail(SUCCES_ABSEN)
  



def errorAbsen(mataKuliah, tanggal, waktu):
  ERROR_ABSEN =  f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style> body {{ font-family: Arial, sans-serif; line-height: 1.6; }} .container {{ padding: 20px; border: 1px solid #ddd; border-radius: 8px; max-width: 600px; margin: auto; background-color: #f9f9f9; }} .header {{ color: #dc3545; }} .details {{ background-color: #ffffff; padding: 15px; border-left: 4px solid #dc3545; margin-top: 20px; }} .error-box {{ background-color: #2d2d2d; color: #f1f1f1; padding: 15px; border-radius: 5px; margin-top: 15px; font-family: 'Courier New', Courier, monospace; white-space: pre-wrap; word-wrap: break-word; }} .footer {{ margin-top: 30px; font-size: 0.9em; color: #777; }} </style>
    </head>
    <body>
        <div class="container">
            <h2 class="header">❌ Gagal! Terjadi Kesalahan pada Auto Absen</h2>
            <p>Halo,</p>
            <p>Script auto absen mengalami kegagalan dan tidak dapat menyelesaikan proses untuk mata kuliah <strong>{mataKuliah}</strong>.</p>
            <p>Silakan melalukan absen secara manual.</p>
            <div class="details">
                <p><strong>Mata Kuliah:</strong> {mataKuliah}</p>
                <p><strong>Tanggal:</strong> {tanggal}</p>
                <p><strong>Waktu Submit:</strong> {waktu}</p>
            </div>
            <div class="footer">
                <p>Script dihentikan karena kesalahan.</p>
                <br>
                <p>Terima kasih,<br>Pengingat Absen Otomatis</p>
            </div>
        </div>
    </body>
    </html>
    """
  sendingEmail(ERROR_ABSEN)


def sendingEmail(typeStatus):
  email_json = {
      "from": "xeozn@testerzone.web.id",
      "to": os.getenv("EMAILUSER"),
      "subject": "Absen Auto Status",
      "html": typeStatus
    }

  r = resend.Emails.send(email_json)