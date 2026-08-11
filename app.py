from datetime import datetime
from zoneinfo import ZoneInfo  # Modul bawaan Python untuk zona waktu
from geopy.distance import geodesic
import streamlit as st
from streamlit_geolocation import streamlit_geolocation

# Konfigurasi Kantor Jatinunggal
KANTOR_LAT = -6.948340492177861
KANTOR_LON = 108.12643322430392
RADIUS_MAX = 13000  # 10 km untuk uji coba

st.title("📍 Aplikasi Absensi PKL Geofencing (Mode Uji Coba)")
st.markdown("Kecamatan Jatinunggal")

# --- MENGAMBIL WAKTU INDONESIA (WIB / Asia/Jakarta) ---
tz_wib = ZoneInfo("Asia/Jakarta")
now = datetime.now(tz_wib)
current_time = now.time()

# Tampilkan informasi waktu server lokal untuk memastikan
st.write(
    f"🕒 Waktu Server saat ini (WIB): **{now.strftime('%H:%M:%S')}**"
)

# Jam Pagi: 05.00 - 09.00 | Jam Pulang: 14.00 - 18.00
is_sesi_pagi = (
    datetime.strptime("05:00:00", "%H:%M:%S").time()
    <= current_time
    <= datetime.strptime("09:00:00", "%H:%M:%S").time()
)
is_sesi_pulang = (
    datetime.strptime("14:00:00", "%H:%M:%S").time()
    <= current_time
    <= datetime.strptime("18:00:00", "%H:%M:%S").time()
)

if not (is_sesi_pagi or is_sesi_pulang):
    st.error(
        "❌ Diluar jam absensi! Sesi Pagi (05:00-09:00) & Sesi Pulang"
        " (14:00-18:00)."
    )
    st.stop()

sesi_aktif = "Pagi" if is_sesi_pagi else "Pulang"
st.info(f"ℹ️ Sesi Aktif saat ini: **Absen {sesi_aktif}**")

# Input Identitas Siswa
nama_siswa = st.text_input("Nama Lengkap Siswa")

if nama_siswa:
  st.write("---")
  st.subheader("1. Deteksi Lokasi Anda (Geofencing 10.000 Meter)")
  st.write(
      "Klik tombol di bawah untuk mendeteksi posisi GPS perangkat Anda secara"
      " akurat."
  )

  loc = streamlit_geolocation()

  if loc.get("latitude") and loc.get("longitude"):
    lat_siswa = loc["latitude"]
    lon_siswa = loc["longitude"]

    jarak = geodesic((lat_siswa, lon_siswa), (KANTOR_LAT, KANTOR_LON)).meters

    st.write(f"Jarak Anda dari titik kantor: **{round(jarak, 2)} meter**")

    if jarak <= RADIUS_MAX:
      st.success(
          "✅ Anda berada dalam radius uji coba (<= 10.000 meter / 10 km)."
      )

      st.subheader("2. Ambil Foto Kegiatan (Selfie)")
      foto_selfie = st.camera_input("Ambil Foto Selfie Kegiatan PKL")

      if foto_selfie:
        keterangan = st.text_area("Keterangan Kegiatan / Pekerjaan Hari Ini")

        if st.button("Kirim Absensi"):
          data_absen = {
              "Waktu": now.strftime("%Y-%m-%d %H:%M:%S"),
              "Nama": nama_siswa,
              "Sesi": sesi_aktif,
              "Jarak": round(jarak, 2),
              "Status": "Pending (Menunggu Verifikasi Guru)",
              "Keterangan": keterangan,
          }

          st.success(
              "🎉 Absensi berhasil dikirim! Menunggu verifikasi dari Guru"
              " Pembimbing."
          )
    else:
      st.error(
          f"❌ Anda berada di luar radius uji coba ({round(jarak, 2)} meter)."
      )
  else:
    st.warning(
        "⚠️ Silakan izinkan akses lokasi (GPS) pada browser Anda lalu klik"
        " tombol GPS."
    )