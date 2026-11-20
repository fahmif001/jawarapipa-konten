# Jawara Pipa – pabrik konten sosmed (dibuat & dijalankan oleh Claude)

Repo ini berisi semua yang dibutuhkan Claude untuk membuat desain Feed (JPG) dan Reels motion graphic (MP4 + musik + voice-over)
untuk Instagram/Facebook **Jawara Pipa Indonesia**, tanpa Canva. File di `media/` bersifat publik dan dipakai Metricool lewat
`https://raw.githubusercontent.com/fahmif001/jawarapipa-konten/main/media/<file>`.

## Struktur
- `brand/` – font Barlow & Barlow Condensed (OFL), `brand.css` (komponen gaya website), `reel-engine.js` (animasi Reels)
- `assets/web/` – foto asli dari jawarapipa.co.id (produk, hero gudang, pengiriman) + logo mark
- `templates/feed-example.html`, `templates/reel-example.html` – contoh yang sudah disetujui; mulai dari sini
- `content/<YYYY-MM-DD>-<feed|reels>/` – sumber per konten (`design.html` atau `reel.html` + `vo.json`)
- `media/` – hasil final (yang dijadwalkan ke Metricool)
- `tools/` – `setup.sh`, `render_feed.py`, `render_reel.py`, `music.py`, `vo.py`, `mix.py`

## Gaya (ikuti website jawarapipa.co.id)
- Warna: gelap `#16191D`, oranye `#FEA418`, cyan `#00C8F0`, hijau WhatsApp `#1FAF54`, teks sekunder `#cfd8e2`/`#9fb0c0`
- Judul: Barlow Condensed 800 KAPITAL; teks: Barlow 500–700
- Elemen khas: logo mark + "JAWARA PIPA / AHLINYA SISTEM PERPIPAAN", pill "● Stok Ready", eyebrow garis oranye-cyan,
  kartu gelap dengan border atas oranye/cyan, ikon centang lingkaran oranye, garis oranye|cyan, tombol WhatsApp hijau
- Foto: hanya dari `assets/web/` (atau foto asli dari user). Jangan pakai foto stok/AI. Jangan mengarang spesifikasi;
  angka harus ada di website.
- Feed 1080×1350: footer WA 0851 1167 0410 + www.jawarapipa.co.id. Reels 1080×1920: teks di zona aman
  (hindari 220 px teratas & 380 px terbawah untuk teks penting), scene terakhir = CTA WA + website.

## Alur membuat konten
```
bash tools/setup.sh
# FEED
cp templates/feed-example.html content/2026-12-01-feed/design.html   # lalu ubah isi; path ../../ sudah benar dari content/<slug>/
python3 tools/render_feed.py content/2026-12-01-feed/design.html media/2026-12-01-feed.jpg
#   carousel: tiap halaman <section class="page">, lalu --pages  -> media/<slug>-1.jpg, -2.jpg, ...
# REELS
python3 tools/render_reel.py content/<slug>/reel.html /tmp/silent.mp4        # mencetak scene_starts & duration
python3 tools/music.py --dur <duration> --cuts <scene_starts tanpa 0> --hits <momen hentakan> /tmp/music.wav
python3 tools/vo.py content/<slug>/vo.json --dur <duration> /tmp/vo.wav      # 1 kalimat per scene, mulai ±0.15 s setelah scene mulai
python3 tools/mix.py /tmp/silent.mp4 /tmp/music.wav /tmp/vo.wav media/<slug>.mp4
```
Selalu LIHAT hasilnya sebelum commit: buka JPG feed; untuk Reels ambil beberapa frame
(`ffmpeg -ss <t> -i media/<slug>.mp4 -frames:v 1 /tmp/f.jpg`) dan cek teks tidak terpotong/bertumpuk.
Jika `vo.py` menandai "OVERRUNS", pendekkan kalimat atau perpanjang durasi scene di `window.SC`.

## Pelafalan voice-over (disetujui user)
HDPE → "ha-de-pe-e"; "ready"/"stok ready" → "stok tersedia"; "free ongkir" → "gratis ongkir" (diterapkan otomatis di `tools/vo.py`).
Teks di layar tetap "HDPE", "Stok Ready", "Free Ongkir" seperti website.

## Commit
`git add content media && git commit -m "Konten <tanggal>: <topik>" && git push`. Setelah push, link publik:
`https://raw.githubusercontent.com/fahmif001/jawarapipa-konten/main/media/<file>`
