# 🎨 AI Procedural Material Generator for Blender

**Oleh: Hafizh Zaldy Alviansyah ([Devgame Tutorial](https://www.youtube.com/@DevgameTutorial))**

Addon Blender mutakhir yang memungkinkan Anda membuat dan memodifikasi *procedural shader materials* menggunakan kekuatan AI (**Google Gemini**) hanya melalui perintah bahasa natural.

---

## 🌟 Fitur Unggulan

* **Text-to-Material**: Deskripsikan material (misal: "besi berkarat") dan biarkan AI menyusun node-nya.
* **Iterative Modification**: Tambahkan detail ke material yang sudah ada tanpa menghapusnya (kontekstual).
* **Context-Aware**: AI mengingat riwayat prompt Anda untuk hasil yang lebih konsisten.
* **Auto-Assignment**: Material langsung diterapkan ke objek yang sedang dipilih secara otomatis.
* **Pilihan Model Luas**: Mendukung seri Gemini 2.5 hingga Gemini 3 (Flash & Pro).

---

## 📋 Persyaratan Sistem

| Komponen | Persyaratan |
| --- | --- |
| **Blender** | Versi 3.6 atau yang lebih baru |
| **Internet** | Koneksi aktif untuk API calls |
| **API Key** | Google Gemini API Key (Gratis di [Google AI Studio](https://ai.google.dev/)) |
| **Libraries** | `pydantic`, `google-genai`, `requests` (Otomatis via installer) |

---

## 🚀 Panduan Instalasi

### 1. Install Dependencies

Sebelum menginstal di Blender, library Python yang dibutuhkan harus terpasang:

1. Download/Clone folder addon ini.
2. Jalankan (Double-click) file `install_dependencies.bat`.
3. Script akan otomatis mendeteksi Blender dan menginstal library yang diperlukan.
4. Tunggu hingga pesan **"Installation complete!"** muncul.

### 2. Membuat Package Addon

1. Jalankan file `create_installable_addon_zip.bat`.
2. File bernama `blender_ai_material_gen.zip` akan tercipta di folder utama.

### 3. Aktivasi di Blender

1. Buka Blender, pergi ke **Edit** → **Preferences** → **Add-ons**.
2. Klik **Install...** dan pilih file `.zip` yang tadi dibuat.
3. Centang box **"Material: AI Procedural Material Generator"**.

---

## ⚙️ Konfigurasi API (Penting)

1. Dapatkan API Key dari [Google AI Studio](https://ai.google.dev/).
2. Di Blender, buka **Shader Editor** dan tekan `N` untuk membuka sidebar.
3. Pilih tab **"AI Material"** → Expand bagian **"Settings"**.
4. Masukkan API Key Anda, lalu klik **"Initialize API"**.
5. Status akan berubah menjadi **"✓ API Ready"**.

---

## 📖 Cara Penggunaan

### Memperkenalkan Material Baru

1. Pilih objek di Viewport.
2. Ketik deskripsi di panel AI Material. Contoh: `brushed aluminum metal with subtle scratches`.
3. Klik **Generate**.

### Memodifikasi Material

1. Pastikan objek memiliki material aktif hasil generate AI.
2. Ketik instruksi tambahan. Contoh: `add more rust on the edges` atau `make it darker`.
3. Klik **Modify**.

---

## 💡 Tips & Best Practices

### Menulis Prompt yang Efektif

> **✅ Lakukan:** Gunakan kata sifat tekstur dan material yang spesifik (misal: *Polished, Grainy, Oxidized, Matte*).
> **❌ Hindari:** Kata-kata yang terlalu umum seperti "bagus", "keren", atau referensi pop-kultur yang tidak deskriptif secara visual.

### Workflow Iteratif

Jangan mencoba membuat material kompleks dalam satu prompt. Mulailah dari dasar:

1. `Metal` (Generate)
2. `Add blue paint` (Modify)
3. `Add scratches and dust` (Modify)

---

## 🔧 Detail Teknis & Model

### Node yang Didukung

AI mampu menyusun berbagai node kompleks termasuk:

* **Shaders**: Principled BSDF, Glass, Emission.
* **Textures**: Noise, Voronoi, Wave, Musgrave.
* **Utilities**: Color Ramp, Bump, Mapping, Math Nodes, Mix RGB.

### Pilihan Model AI

| Tier | Model | Karakteristik |
| --- | --- | --- |
| **Free** | `gemini-2.5-flash` | Cepat, efisien, limit 20x/hari. |
| **Pro** | `gemini-3-flash / pro` | Sangat akurat, pemahaman material lebih dalam. |

---

## 🛠 Troubleshooting

* **API Not Initialized**: Pastikan Key benar dan klik tombol Initialize.
* **Material Aneh**: AI terkadang melakukan kesalahan logika node. Coba gunakan prompt "simplify the nodes" atau generate ulang.
* **Console Error**: Cek log detail melalui menu `Window` → `Toggle System Console`.

---

## ☕ Dukung Pengembangan

Jika addon ini membantu alur kerja Anda, pertimbangkan untuk mendukung pengembangan berkelanjutan:

* **Donasi via Dana:** [Klik di sini](https://link.dana.id/minta?full_url=https://qr.dana.id/v1/281012012020010557803638)
* **YouTube:** [Devgame Tutorial](https://www.youtube.com/@DevgameTutorial)

---

*License: Provided as-is for creative purposes. © 2025 Hafizh Zaldy Alviansyah.*

**Mau saya buatkan file `README.md` yang siap pakai atau ada bagian instruksi yang ingin Anda perjelas lagi?**
