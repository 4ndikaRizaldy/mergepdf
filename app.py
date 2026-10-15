import streamlit as st
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
import io
import zipfile
from PIL import Image
import os

# ===== KONFIGURASI HALAMAN =====
st.set_page_config(page_title="Aplikasi Pengolah Rapor PDF", page_icon="📄", layout="wide")

DEFAULT_IMAGES_DIR = "default_images"
DEFAULT_FILES_DIR = "default_files"
for folder_name in [DEFAULT_IMAGES_DIR, DEFAULT_FILES_DIR]:
    if not os.path.exists(folder_name): os.makedirs(folder_name)

# ===== HEADER =====
st.markdown("<h2 style='text-align:center;'>SMKS Plus Nurul Hakim</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Aplikasi Pengolah PDF Rapor Terpadu</h4>", unsafe_allow_html=True)
st.divider()

tab1, tab2, tab3 = st.tabs(["➕ Gabung PDF", "✂️ Pisah PDF", "🖼️ Tambah Logo, TTD & Stempel"])

# ==============================================================================
# TAB 1 & 2 (SAMA SEPERTI SEBELUMNYA)
# ==============================================================================
with tab1:
    st.subheader("Gabungkan Beberapa File PDF Menjadi Satu")
    uploaded_files_merge = st.file_uploader("Upload PDF Rapor Siswa", type="pdf", accept_multiple_files=True, key="uploader_merge")
    if uploaded_files_merge:
        st.info(f"✅ {len(uploaded_files_merge)} file siap digabung")
        if st.button("🔄 Gabungkan PDF", type="primary", use_container_width=True):
            with st.spinner("Menggabungkan..."):
                writer = PdfWriter()
                for pdf_file in uploaded_files_merge:
                    reader = PdfReader(pdf_file)
                    for page in reader.pages: writer.add_page(page)
                buffer = io.BytesIO()
                writer.write(buffer)
                buffer.seek(0)
            st.success("✅ PDF berhasil digabung!")
            st.download_button(label="⬇️ Download Rapor Gabungan", data=buffer, file_name="Rapor_Kelas_Lengkap.pdf", mime="application/pdf", use_container_width=True)

with tab2:
    st.subheader("Pisah File PDF Menjadi Beberapa Bagian")
    uploaded_file_split = st.file_uploader("Upload 1 file PDF besar", type="pdf", key="uploader_split")
    if uploaded_file_split:
        reader = PdfReader(uploaded_file_split)
        total_pages = len(reader.pages)
        st.info(f"📄 Total halaman: **{total_pages}**")
        split_mode = st.radio("Mode Pisah", ["Pisah Semua Halaman", "Pisah Berdasarkan Range"], horizontal=True)
        if split_mode == "Pisah Semua Halaman":
            if st.button("✂️ Pisah & Download ZIP", type="primary", use_container_width=True):
                with st.spinner("Memisah..."):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for i in range(total_pages):
                            writer = PdfWriter()
                            writer.add_page(reader.pages[i])
                            pdf_buffer = io.BytesIO()
                            writer.write(pdf_buffer)
                            zip_file.writestr(f"halaman_{i+1:03d}.pdf", pdf_buffer.getvalue())
                    zip_buffer.seek(0)
                st.success("✅ PDF berhasil dipisah!")
                st.download_button(label="⬇️ Download ZIP", data=zip_buffer, file_name="Hasil_Pisah_Halaman.zip", mime="application/zip", use_container_width=True)
        else:
            col_start, col_end = st.columns(2)
            with col_start: start_page = st.number_input("Mulai", min_value=1, max_value=total_pages, value=1, key="range_start")
            with col_end: end_page = st.number_input("Akhir", min_value=1, max_value=total_pages, value=total_pages, key="range_end")
            if st.button("✂️ Pisah Range", type="primary", use_container_width=True):
                if start_page > end_page: st.error("❌ Halaman mulai > akhir!")
                else:
                    with st.spinner("Memisah..."):
                        writer = PdfWriter()
                        for i in range(start_page - 1, end_page): writer.add_page(reader.pages[i])
                        buffer = io.BytesIO()
                        writer.write(buffer)
                        buffer.seek(0)
                    st.success("✅ Range berhasil dipisah!")
                    st.download_button(label=f"⬇️ Download Hal {start_page}-{end_page}", data=buffer, file_name=f"Rapor_{start_page}-{end_page}.pdf", mime="application/pdf", use_container_width=True)

# ==============================================================================
# TAB 3: OVERLAY (DIPERBAIKI)
# ==============================================================================
with tab3:
    st.subheader("Tambahkan Logo, Tanda Tangan & Stempel")
    
    def get_default_image(filename):
        path = os.path.join(DEFAULT_IMAGES_DIR, filename)
        return path if os.path.exists(path) else None
    def get_default_pdf():
        path = os.path.join(DEFAULT_FILES_DIR, "default_rapor.pdf")
        return path if os.path.exists(path) else None

    default_pdf_path = get_default_pdf()
    default_logo = get_default_image("logo_sekolah.png")
    default_ttd = get_default_image("ttd_kepsek.png")
    default_stempel = get_default_image("stempel_sekolah.png")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("###  1. File PDF untuk Preview")
        if default_pdf_path: st.success(f"✅ Pakai default: `default_rapor.pdf`")
        else: st.warning("⚠️ Tidak ada PDF default.")
            
        pdf_sample = st.file_uploader("Upload PDF kustom (opsional)", type="pdf", key="overlay_sample")
        active_pdf_source = pdf_sample if pdf_sample else default_pdf_path
        
        st.markdown("### 🖼️ 2. Upload Gambar")
        logo_file = st.file_uploader("Logo Sekolah", type=["png", "jpg"], key="overlay_logo")
        ttd_kepsek = st.file_uploader("TTD Kepala Sekolah", type=["png"], key="overlay_ttd_kepsek")
        stempel_file = st.file_uploader("Stempel Sekolah", type=["png"], key="overlay_stempel")
        ttd_wali = st.file_uploader("TTD Wali Kelas", type=["png"], key="overlay_ttd_wali")
        ttd_santri = st.file_uploader("TTD Wali Santri", type=["png"], key="overlay_ttd_santri")

    with col_right:
        st.markdown("###  3. Atur Posisi (mm)")
        MM_TO_PT = 2.83 
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            st.markdown("**🎨 Logo**")
            logo_x = st.number_input("X", value=93.0, step=0.1, key="pos_logo_x")
            logo_y = st.number_input("Y", value=4.5, step=0.1, key="pos_logo_y")
            logo_w = st.number_input("Lebar", value=23.5, step=0.1, key="pos_logo_w")
        with col_p2:
            st.markdown("**✍️ TTD**")
            ttd_w = st.number_input("Lebar TTD", value=33.0, step=0.1, key="pos_ttd_w")
            st.markdown("**Kepsek**")
            k_x = st.number_input("X", value=91.5, step=0.1, key="pos_k_x")
            k_y = st.number_input("Y", value=235.0, step=0.1, key="pos_k_y")
            st.markdown("**Wali Kelas**")
            w_x = st.number_input("X", value=145.0, step=0.1, key="pos_w_x")
            w_y = st.number_input("Y", value=235.0, step=0.1, key="pos_w_y")
            st.markdown("**Wali Santri**")
            s_x = st.number_input("X", value=38.0, step=0.1, key="pos_s_x")
            s_y = st.number_input("Y", value=235.0, step=0.1, key="pos_s_y")
        with col_p3:
            st.markdown("**🔴 Stempel**")
            stempel_w = st.number_input("Lebar", value=35.0, step=0.1, key="pos_stempel_w")
            stempel_x = st.number_input("X", value=73.7, step=0.1, key="pos_stempel_x")
            stempel_y = st.number_input("Y", value=233.0, step=0.1, key="pos_stempel_y")
            stempel_opacity = st.slider("Transparansi", 0.1, 1.0, 1.0, 0.1, key="pos_stempel_opacity")

    st.divider()
    
    # FUNGSI PEMROSES GAMBAR (OPTIMIZED FOR PDF VIEWERS)
    def process_image_for_pdf(img_source, opacity=1.0):
        if img_source is None: return None
        try:
            if isinstance(img_source, str) and os.path.exists(img_source): img = Image.open(img_source)
            else: img = Image.open(img_source)
            
            img = img.convert("RGBA")
            bbox = img.getbbox()
            if bbox: img = img.crop(bbox)
            
            if opacity < 1.0:
                alpha = img.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                img.putalpha(alpha)
            
            img_bytes = io.BytesIO()
            # Simpan sebagai PNG standar agar kompatibel dengan semua PDF Viewer
            img.save(img_bytes, format="PNG", optimize=True)
            img_bytes.seek(0)
            
            return {"data": img_bytes.getvalue(), "aspect": img.width / img.height}
        except Exception as e:
            st.error(f"Error gambar: {e}")
            return None

    # Preview Logic
    if active_pdf_source:
        if st.button("️ Tampilkan Preview", type="secondary", use_container_width=True):
            if isinstance(active_pdf_source, str): pdf_doc = fitz.open(active_pdf_source)
            else: pdf_doc = fitz.open(stream=active_pdf_source.getvalue(), filetype="pdf")
            
            # Tampilkan info ukuran halaman untuk diagnosa
            page = pdf_doc[0]
            width_mm = page.rect.width / MM_TO_PT
            height_mm = page.rect.height / MM_TO_PT
            st.info(f"📏 Ukuran Halaman Preview: **{width_mm:.1f} mm x {height_mm:.1f} mm** (Standar A4: 210 x 297 mm)")

            def insert_img(page_obj, img_source, x, y, w, opacity=1.0):
                processed = process_image_for_pdf(img_source, opacity)
                if not processed: return False
                rect = fitz.Rect(x*MM_TO_PT, y*MM_TO_PT, (x+w)*MM_TO_PT, (y + w/processed["aspect"])*MM_TO_PT)
                page_obj.insert_image(rect, stream=processed["data"])
                return True

            logo_src = logo_file if logo_file else default_logo
            ttd_src = ttd_kepsek if ttd_kepsek else default_ttd
            stempel_src = stempel_file if stempel_file else default_stempel
            
            if logo_src: insert_img(page, logo_src, logo_x, logo_y, logo_w, 1.0)
            if ttd_src: insert_img(page, ttd_src, k_x, k_y, ttd_w, 1.0)
            if stempel_src: insert_img(page, stempel_src, stempel_x, stempel_y, stempel_w, stempel_opacity)
            if ttd_wali: insert_img(page, ttd_wali, w_x, w_y, ttd_w, 1.0)
            if ttd_santri: insert_img(page, ttd_santri, s_x, s_y, ttd_w, 1.0)
            
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(pix.tobytes("png"), caption="Preview Hasil", use_container_width=True)
            pdf_doc.close()

    st.divider()
    st.markdown("### 🚀 4. Proses Massal")
    pdf_files_batch = st.file_uploader("Upload SEMUA file PDF rapor siswa", type="pdf", accept_multiple_files=True, key="overlay_batch")
    
    if st.button("🖨️ Proses Massal", type="primary", use_container_width=True):
        has_logo = logo_file or default_logo
        if not pdf_files_batch or not has_logo:
            st.error("❌ Upload PDF dan Logo!")
        else:
            with st.spinner("Memproses..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    logo_src = logo_file if logo_file else default_logo
                    ttd_src = ttd_kepsek if ttd_kepsek else default_ttd
                    stempel_src = stempel_file if stempel_file else default_stempel
                    
                    img_logo = process_image_for_pdf(logo_src, 1.0)
                    img_kepsek = process_image_for_pdf(ttd_src, 1.0)
                    img_stempel = process_image_for_pdf(stempel_src, stempel_opacity)
                    img_wali = process_image_for_pdf(ttd_wali, 1.0)
                    img_santri = process_image_for_pdf(ttd_santri, 1.0)
                    
                    if not img_logo: st.error("❌ Logo error!"); st.stop()
                    
                    size_warnings = []
                    
                    for idx, pdf_file in enumerate(pdf_files_batch):
                        if pdf_file.getbuffer().nbytes > 0:
                            status_text.text(f"Memproses: {pdf_file.name}")
                            pdf_doc = fitz.open(stream=pdf_file.getvalue(), filetype="pdf")
                            
                            for page_num in range(len(pdf_doc)):
                                page = pdf_doc[page_num]
                                
                                # Cek ukuran halaman (Opsional: untuk mendeteksi PDF yang tidak standar)
                                page_w_mm = page.rect.width / MM_TO_PT
                                page_h_mm = page.rect.height / MM_TO_PT
                                # Jika ukuran meleset lebih dari 2mm dari A4 standar, catat sebagai warning
                                if abs(page_w_mm - 210) > 2 or abs(page_h_mm - 297) > 2:
                                    if pdf_file.name not in size_warnings:
                                        size_warnings.append(f"{pdf_file.name} ({page_w_mm:.1f}x{page_h_mm:.1f}mm)")

                                rect = fitz.Rect(logo_x*MM_TO_PT, logo_y*MM_TO_PT, (logo_x+logo_w)*MM_TO_PT, (logo_y + logo_w/img_logo["aspect"])*MM_TO_PT)
                                page.insert_image(rect, stream=img_logo["data"])
                                
                                if img_kepsek:
                                    rect = fitz.Rect(k_x*MM_TO_PT, k_y*MM_TO_PT, (k_x+ttd_w)*MM_TO_PT, (k_y + ttd_w/img_kepsek["aspect"])*MM_TO_PT)
                                    page.insert_image(rect, stream=img_kepsek["data"])
                                if img_stempel:
                                    rect = fitz.Rect(stempel_x*MM_TO_PT, stempel_y*MM_TO_PT, (stempel_x+stempel_w)*MM_TO_PT, (stempel_y + stempel_w/img_stempel["aspect"])*MM_TO_PT)
                                    page.insert_image(rect, stream=img_stempel["data"])
                                if img_wali:
                                    rect = fitz.Rect(w_x*MM_TO_PT, w_y*MM_TO_PT, (w_x+ttd_w)*MM_TO_PT, (w_y + ttd_w/img_wali["aspect"])*MM_TO_PT)
                                    page.insert_image(rect, stream=img_wali["data"])
                                if img_santri:
                                    rect = fitz.Rect(s_x*MM_TO_PT, s_y*MM_TO_PT, (s_x+ttd_w)*MM_TO_PT, (s_y + ttd_w/img_santri["aspect"])*MM_TO_PT)
                                    page.insert_image(rect, stream=img_santri["data"])
                            
                            zip_file.writestr(pdf_file.name, pdf_doc.tobytes())
                            pdf_doc.close()
                        progress_bar.progress((idx + 1) / len(pdf_files_batch))
                
                zip_buffer.seek(0)
            st.success(f"🎉 {len(pdf_files_batch)} file PDF berhasil diproses!")
            
            if size_warnings:
                st.warning(f"⚠️ **Peringatan Ukuran PDF:** Ada {len(size_warnings)} file yang ukuran halamannya tidak standar A4 (210x297mm). Ini bisa menyebabkan posisi bergeser. File: {', '.join(size_warnings[:3])}...")
            
            st.download_button(label="⬇️ Download ZIP", data=zip_buffer, file_name="Rapor_Lengkap.zip", mime="application/zip", use_container_width=True)
            st.caption("💡 *Tips: Tahan tombol ALT saat klik Download jika menggunakan IDM.*")

st.divider()
st.markdown("<p style='text-align:center; color:gray;'>© 2026 SMKS Plus Nurul Hakim</p>", unsafe_allow_html=True)