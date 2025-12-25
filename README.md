# AI Procedural Material Generator untuk Blender

Addon Blender yang memungkinkan kamu membuat dan memodifikasi procedural shader materials menggunakan AI (Google Gemini) melalui natural language prompts.

## 🌟 Fitur

- **Generate Material dari Text**: Deskripsikan material yang kamu inginkan dalam bahasa natural
- **Iterative Modification**: Tambahin detail ke material existing dengan prompt tambahan
- **Context-Aware**: AI bakal inget prompt sebelumnya buat hasil yang lebih oke
- **Auto-Assignment**: Material langsung di-assign ke object yang dipilih

## 📋 Requirements

- **Blender**: Versi 3.6 atau lebih baru
- **Internet Connection**: Perlu koneksi internet buat API calls ke Google Gemini
- **Google Gemini API Key**: Dapetin gratis dari [Google AI Studio](https://ai.google.dev/)

## 🚀 Instalasi

### Step 1: Install Dependencies

1. Download atau clone folder addon ini
2. **Double-click** file `install_dependencies.bat`
3. Script bakal otomatis:
   - Nyari instalasi Blender kamu
   - Install `pydantic` library (buat schema validation)
   - Install `google-genai` library (NEW Gemini SDK)
   - Install `requests` library
4. Tunggu sampe muncul "Installation complete!"

> **Note**: Script bakal auto-detect Blender di lokasi default (Disk C: komputer). Kalau nggak ketemu, kamu bakal diminta masukin path manual.

### Step 2: Buat Package Addon ZIP

Addon harus dipackage dalam bentuk ZIP buat diinstall ke Blender:

**Opsi A: Otomatis (Recommended)**
1. **Double-click** file `create_installable_addon_zip.bat`
2. Script bakal otomatis bikin file `blender_ai_material_gen.zip`
3. Tunggu sampe muncul "PACKAGE CREATED SUCCESSFULLY!"

**Opsi B: Manual**
1. Bikin folder baru namanya `blender_ai_material_gen`
2. Copy semua file `.py` dari addon ke dalam folder tersebut:
   - `__init__.py`
   - `operators.py`
   - `panels.py`
   - `ai_connector.py`
   - `material_generator.py`
   - `utils.py`
   - `prompt_templates.py`
   - `material_schema.py`
   - `node_reference.py`
   - `material_references.py`
3. Compress folder `blender_ai_material_gen` jadi file ZIP

> **Important**: Addon harus ada di dalam folder dulu sebelum di-zip. Jangan langsung zip file-file `.py` tanpa folder pembungkus.

### Step 3: Install Addon di Blender

1. Buka Blender
2. Buka `Edit` → `Preferences` → `Add-ons`
3. Klik `Install...`
4. Pilih file **`blender_ai_material_gen.zip`** yang udah dibuat
5. **Enable** addon dengan centang checkbox "Material: AI Procedural Material Generator"

### Step 4: Setup API Key

1. Dapetin API key gratis dari [Google AI Studio](https://ai.google.dev/)
   - Login pake Google account kamu
   - Klik "Get API Key"
   - Copy API key yang digenerate
2. Di Blender, buka **Shader Editor**
3. Tekan `N` buat show sidebar
4. Klik tab **"AI Material"**
5. Expand **"Settings"**
6. Paste API key kamu
7. Klik **"Initialize API"**
8. Tunggu sampe muncul "✓ API Ready"

## 📖 Cara Penggunaan

### Generate Material Baru

1. Pilih object di viewport
2. Di Shader Editor sidebar, tab "AI Material"
3. Ketik deskripsi material di text field, contoh:
   - `shiny red plastic`
   - `brushed aluminum metal`
   - `old rusty iron with scratches`
4. Klik tombol **"Generate"**
5. Tunggu beberapa detik
6. Material bakal otomatis dibuat dan di-assign ke object

### Modify Material Existing

1. Pastiin object punya material aktif
2. Ketik modifikasi yang kamu pengen, contoh:
   - `add rust`
   - `make it more reflective`
   - `add scratches and dirt`
3. Klik tombol **"Modify"**
4. Material bakal diupdate dengan perubahan



## 💡 Tips & Best Practices

### Prompt Yang Baik

**Good Prompts** ✓
- `polished gold metal`
- `worn concrete with cracks`
- `glossy red car paint`
- `dark oak wood with visible grain`
- `scratched silver metal`

**Less Effective** ✗
- `nice material` (terlalu vague)
- `material like in that movie` (AI tidak bisa lihat referensi)
- `just make it cool` (tidak specific)

### Iterative Workflow

1. Start simple: `metal`
2. Add detail: `add brushed texture`
3. Refine: `make it more shiny`
4. Final touch: `add slight rust on edges`

### Troubleshooting

**"API not initialized"**
- Pastiin API key udah di-set
- Klik "Initialize API" di Settings
- Check console buat error messages

**"Failed to generate material"**
- Check koneksi internet
- Cek API key kamu masih valid
- Coba lagi dengan prompt yang lebih sederhana
- Check Blender console (`Window` → `Toggle System Console`) buat error details

**Material keliatan aneh**
- AI nggak sempurna, hasil bisa bervariasi
- Coba modify pake prompt tambahan
- Atau edit manual di Shader Editor
- Coba generate ulang dengan prompt yang lebih detail

**Dependencies error saat enable addon**
- Jalanin ulang `install_dependencies.bat`
- Pastiin install ke Blender version yang bener
- Restart Blender abis install dependencies

## 🎨 Contoh Prompts

### Metals
- `polished chrome`
- `brushed stainless steel`
- `oxidized copper`
- `rusty iron barrel`
- `gold ring with scratches`

### Plastics
- `matte black plastic`
- `glossy white plastic`
- `transparent acrylic`
- `rubberized soft touch plastic`

### Natural Materials
- `dark walnut wood`
- `polished marble with veins`
- `rough granite stone`
- `weathered concrete`
- `aged leather`

### Special Effects
- `carbon fiber weave`
- `anodized aluminum blue`
- `holographic metallic`
- `pearlescent car paint`

## 🔧 Technical Details

### Node Types Supported

AI bisa bikin node-node berikut:
- `Principled BSDF` - Main shader
- `Noise Texture` - Procedural noise
- `Voronoi Texture` - Cell patterns
- `Wave Texture` - Wave patterns
- `Musgrave Texture` - Terrain-like
- `Color Ramp` - Color gradients
- `Mix RGB` - Color mixing
- `Bump` - Surface detail
- `Mapping` - Texture transformation
- `Math` - Mathematical operations
- Dan masih banyak lagi...

### Model AI Yang Tersedia

Kamu bisa pilih dari berbagai model AI berikut:

#### Free Tier (API Key Gratis)
- **gemini-2.5-flash** - Model cepat dan efisien, cocok buat penggunaan sehari-hari

#### Pro Tier (API Key Berbayar)
- **gemini-2.5-pro** - Model premium dengan hasil lebih akurat
- **gemini-3-flash** - Model generasi terbaru versi flash
- **gemini-3-preview** - Model preview generasi terbaru dengan fitur terdepan

> **Note**: Free tier bisa pakai API Key gratis dari [Google AI Studio](https://ai.google.dev/). Pro tier harus beli API Key berbayar dari Google.

### API Usage & Limits

#### Free Tier
- **Quota**: 20x pemakaian per hari
- **Model Default**: gemini-2.5-flash
- **Rate Limit**: 15 requests/minute
- **API Key**: Gratis dari Google AI Studio

#### Pro Tier
- **Quota**: Lebih banyak pemakaian (lihat ketentuan di [Google AI Studio](https://ai.google.dev/))
- **Model**: Akses ke semua model (gemini-2.5-pro, gemini-3-flash, gemini-3-preview)
- **Rate Limit**: Lebih tinggi tergantung paket
- **API Key**: Berbayar dari Google Cloud

## 📝 Changelog

### Version 1.0.0
- Initial release
- Basic material generation
- Iterative modification
- Context-aware prompts
- Auto-installer untuk dependencies
- Auto-packager untuk membuat ZIP installable

## 🤝 Contributing

Feedback dan contributions welcome!

## 📄 License

This addon is provided as-is for educational and creative purposes.

## ⚠️ Disclaimer

- Material AI mungkin nggak sempurna dan perlu adjustment manual
- Butuh koneksi internet aktif
- Google Gemini API terms apply
- Kualitas material tergantung seberapa jelas prompt kamu

## 🆘 Support

Kalau ngalamin masalah:
1. Check console buat error messages (Window → Toggle System Console)
2. Cek API key dan koneksi internet kamu
3. Coba generate material simple dulu buat test (contoh: `red plastic`)
4. Restart Blender terus coba lagi

---

## 👨‍💻 Tentang Pembuat

Addon ini dibuat oleh **Hafizh Zaldy Alviansyah**, creator dari channel YouTube **[Devgame Tutorial](https://www.youtube.com/@DevgameTutorial)**.

### 🙏 Terima Kasih

Makasih banget udah pake addon AI Procedural Material Generator ini! Semoga addon ini bisa bantu mempercepat workflow kamu dalam bikin material di Blender.

### 🚀 Pengembangan Berkelanjutan

Script ini bakal **terus dikembangin** dengan fitur-fitur baru dan perbaikan buat kasih pengalaman yang lebih baik. Stay tuned buat update selanjutnya!

### ☕ Dukung Pengembangan

Kalau addon ini bermanfaat buat kamu dan mau dukung pengembangan lebih lanjut, atau bahkan cuma sekedar mau ngucapin terima kasih, kamu bisa kasih donasi lewat Dana:

**[👉 Klik di sini buat donasi via Dana](https://link.dana.id/minta?full_url=https://qr.dana.id/v1/281012012020010557803638)**

Atau scan QR Code berikut:

![QR Code Dana](https://ik.imagekit.io/kazuyura/QR%20code%20Dana.jpeg)

Setiap dukungan dari kamu sangat berarti dan bantu aku buat terus bikin tools yang bermanfaat! 💙

---

**Enjoy creating materials with AI!** 🎨✨
