import streamlit as st
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
import io
import zipfile
from PIL import Image
import os
from datetime import datetime

# ===== KONFIGURASI HALAMAN =====
st.set_page_config(
    page_title="Aplikasi Pengolah Rapor PDF",
    page_icon="📄",
    layout="wide"
)

# Buat folder output jika belum ada
OUTPUT_DIR = "Output_Rapor"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ===== HEADER =====
st.markdown("<h2 style='text-align:center;'>SMKS Plus Nurul Hakim</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Aplikasi Pengolah PDF Rapor Terpadu</h4>", unsafe_allow_html=True)
st.divider()

# ===== TAB MENU =====
tab1, tab2, tab3 = st.tabs(["➕ Gabung PDF", "✂️ Pisah PDF", "🖼️ Tambah Logo & TTD"])

# ==============================================================================
# TAB 1: GABUNG PDF (MERGE)
# ==============================================================================
with tab1:
    st.subheader("Gabungkan Beberapa File PDF Menjadi Satu")
    uploaded_files_merge = st.file_uploader("Upload PDF Rapor Siswa", type="pdf", accept_multiple_files=True, key="uploader_merge")

    if uploaded_files_merge:
        st.info(f"✅ {len(uploaded_files_merge)} file siap digabung")

        if st.button("🔄 Gabungkan PDF", type="primary", use_container_width=True):
            with st.spinner("Sedang menggabungkan file..."):
                writer = PdfWriter()
                for pdf in uploaded_files_merge:
                    reader = PdfReader(pdf)
                    for page in reader.pages:
                        writer.add_page(page)

                buffer = io.BytesIO()
                writer.write(buffer)
                
                # SIMPAN KE FOLDER (Menggantikan st.download_button)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(OUTPUT_DIR, f"Rapor_Gabungan_{timestamp}.pdf")
                
                with open(file_path, "wb") as f:
                    f.write(buffer.getvalue())
                
            st.success(f"✅ PDF berhasil digabung dan disimpan di: `{file_path}`")

# ==============================================================================
# TAB 2: PISAH PDF (SPLIT)
# ==============================================================================
with tab2:
    st.subheader("Pisah File PDF Menjadi Beberapa Bagian")
    uploaded_file_split = st.file_uploader("Upload 1 file PDF besar", type="pdf", key="uploader_split")

    if uploaded_file_split:
        reader = PdfReader(uploaded_file_split)
        total_pages = len(reader.pages)
        st.info(f"📄 Total halaman pada file ini: **{total_pages}**")

        split_mode = st.radio("Mode Pisah", ["Pisah Semua Halaman", "Pisah Berdasarkan Range"], horizontal=True)

        # --- Mode 1: Pisah Semua ---
        if split_mode == "Pisah Semua Halaman":
            if st.button("️ Pisah & Simpan ZIP", type="primary", use_container_width=True):
                with st.spinner("Sedang memisah halaman..."):
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for i in range(total_pages):
                            writer = PdfWriter()
                            writer.add_page(reader.pages[i])
                            pdf_buffer = io.BytesIO()
                            writer.write(pdf_buffer)
                            zip_file.writestr(f"halaman_{i+1:03d}.pdf", pdf_buffer.getvalue())
                    
                    # SIMPAN KE FOLDER
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_path = os.path.join(OUTPUT_DIR, f"Hasil_Pisah_Halaman_{timestamp}.zip")
                    
                    with open(file_path, "wb") as f:
                        f.write(zip_buffer.getvalue())
                        
                st.success(f"✅ PDF berhasil dipisah dan disimpan di: `{file_path}`")

        # --- Mode 2: Pisah Range ---
        else:
            col_start, col_end = st.columns(2)
            with col_start: start = st.number_input("Halaman mulai", min_value=1, max_value=total_pages, value=1, key="range_start")
            with col_end: end = st.number_input("Halaman akhir", min_value=1, max_value=total_pages, value=total_pages, key="range_end")

            if st.button("✂️ Pisah Range", type="primary", use_container_width=True):
                if start > end:
                    st.error("❌ Halaman mulai tidak boleh lebih besar dari halaman akhir!")
                else:
                    with st.spinner("Sedang memisah halaman..."):
                        writer = PdfWriter()
                        for i in range(start - 1, end):
                            writer.add_page(reader.pages[i])
                        buffer = io.BytesIO()
                        writer.write(buffer)
                        
                        # SIMPAN KE FOLDER
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_path = os.path.join(OUTPUT_DIR, f"Rapor_Halaman_{start}_sampai_{end}_{timestamp}.pdf")
                        
                        with open(file_path, "wb") as f:
                            f.write(buffer.getvalue())
                            
                    st.success(f"✅ Range halaman berhasil dipisah dan disimpan di: `{file_path}`")

# ==============================================================================
# TAB 3: TAMBAH LOGO & TTD (OVERLAY)
# ==============================================================================
with tab3:
    st.subheader("Tambahkan Logo & Tanda Tangan ke PDF Rapor")
    st.caption("Atur posisi dalam milimeter (mm).")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("### 📄 1. Upload File")
        pdf_sample = st.file_uploader("Upload 1 PDF contoh (untuk preview)", type="pdf", key="overlay_sample")
        
        st.markdown("### 🖼️ 2. Upload Gambar")
        logo_file = st.file_uploader("Logo Sekolah (PNG/JPG)", type=["png", "jpg"], key="overlay_logo")
        ttd_kepsek = st.file_uploader("TTD Kepala Sekolah (PNG)", type=["png"], key="overlay_ttd_kepsek")
        ttd_wali = st.file_uploader("TTD Wali Kelas (PNG)", type=["png"], key="overlay_ttd_wali")
        ttd_santri = st.file_uploader("TTD Wali Santri (PNG)", type=["png"], key="overlay_ttd_santri")

    with col_right:
        st.markdown("### 📐 3. Atur Posisi (dalam mm)")
        MM_TO_PT = 2.83 
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("**Logo**")
            logo_x = st.number_input("X (mm)", value=15.0, step=0.5, key="pos_logo_x")
            logo_y = st.number_input("Y (mm)", value=10.0, step=0.5, key="pos_logo_y")
            logo_w = st.number_input("Lebar (mm)", value=25.0, step=0.5, key="pos_logo_w")
            
        with col_p2:
            st.markdown("**Tanda Tangan (Lebar)**")
            ttd_w = st.number_input("Lebar TTD (mm)", value=35.0, step=0.5, key="pos_ttd_w")
            
            st.markdown("**Kepala Sekolah (X, Y)**")
            k_x = st.number_input("X", value=105.0, step=0.5, key="pos_k_x")
            k_y = st.number_input("Y", value=235.0, step=0.5, key="pos_k_y")
            
            st.markdown("**Wali Kelas (X, Y)**")
            w_x = st.number_input("X", value=155.0, step=0.5, key="pos_w_x")
            w_y = st.number_input("Y", value=235.0, step=0.5, key="pos_w_y")
            
            st.markdown("**Wali Santri (X, Y)**")
            s_x = st.number_input("X", value=55.0, step=0.5, key="pos_s_x")
            s_y = st.number_input("Y", value=235.0, step=0.5, key="pos_s_y")

    st.divider()
    
    if pdf_sample and pdf_sample.getbuffer().nbytes > 0 and logo_file:
        if st.button("👁️ Tampilkan Preview Posisi", type="secondary"):
            pdf_doc = fitz.open(stream=pdf_sample.getvalue(), filetype="pdf")
            page = pdf_doc[0]
            
            def insert_img(page, img_file, x, y, w):
                img = Image.open(img_file)
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")
                img_bytes.seek(0)
                aspect = img.width / img.height
                rect = fitz.Rect(x*MM_TO_PT, y*MM_TO_PT, (x+w)*MM_TO_PT, (y + w/aspect)*MM_TO_PT)
                page.insert_image(rect, stream=img_bytes.getvalue())

            insert_img(page, logo_file, logo_x, logo_y, logo_w)
            if ttd_kepsek: insert_img(page, ttd_kepsek, k_x, k_y, ttd_w)
            if ttd_wali: insert_img(page, ttd_wali, w_x, w_y, ttd_w)
            if ttd_santri: insert_img(page, ttd_santri, s_x, s_y, ttd_w)
            
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(pix.tobytes("png"), caption="Preview Hasil", use_container_width=True)
            pdf_doc.close()

    st.divider()
    st.markdown("###  4. Proses Massal")
    pdf_files_batch = st.file_uploader("Upload SEMUA file PDF rapor siswa", type="pdf", accept_multiple_files=True, key="overlay_batch")
    
    if st.button("🖨️ Proses & Tambahkan Logo/TTD ke Semua PDF", type="primary", use_container_width=True):
        if not pdf_files_batch or not logo_file:
            st.error("❌ Upload minimal 1 file PDF dan Logo Sekolah!")
        else:
            with st.spinner("Sedang memproses PDF..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    def prep_img(img_file):
                        if not img_file: return None
                        img = Image.open(img_file)
                        b = io.BytesIO()
                        img.save(b, format="PNG")
                        return {"data": b.getvalue(), "aspect": img.width / img.height}

                    img_logo = prep_img(logo_file)
                    img_kepsek = prep_img(ttd_kepsek)
                    img_wali = prep_img(ttd_wali)
                    img_santri = prep_img(ttd_santri)
                    
                    for idx, pdf_file in enumerate(pdf_files_batch):
                        if pdf_file.getbuffer().nbytes > 0:
                            status_text.text(f"Memproses: {pdf_file.name}")
                            pdf_doc = fitz.open(stream=pdf_file.getvalue(), filetype="pdf")
                            
                            for page in pdf_doc:
                                rect = fitz.Rect(logo_x*MM_TO_PT, logo_y*MM_TO_PT, (logo_x+logo_w)*MM_TO_PT, (logo_y + logo_w/img_logo["aspect"])*MM_TO_PT)
                                page.insert_image(rect, stream=img_logo["data"])
                                
                                ttd_list = [(img_kepsek, k_x, k_y), (img_wali, w_x, w_y), (img_santri, s_x, s_y)]
                                for img_data, tx, ty in ttd_list:
                                    if img_data:
                                        rect = fitz.Rect(tx*MM_TO_PT, ty*MM_TO_PT, (tx+ttd_w)*MM_TO_PT, (ty + ttd_w/img_data["aspect"])*MM_TO_PT)
                                        page.insert_image(rect, stream=img_data["data"])
                            
                            zip_file.writestr(pdf_file.name, pdf_doc.tobytes())
                            pdf_doc.close()
                        
                        progress_bar.progress((idx + 1) / len(pdf_files_batch))
                
                # SIMPAN KE FOLDER
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(OUTPUT_DIR, f"Rapor_Lengkap_Logo_TTD_{timestamp}.zip")
                
                with open(file_path, "wb") as f:
                    f.write(zip_buffer.getvalue())
                    
                st.success(f"🎉 {len(pdf_files_batch)} file PDF berhasil diproses dan disimpan di: `{file_path}`")

# ===== FOOTER =====
st.divider()
st.markdown("<p style='text-align:center; color:gray;'>© 2026 SMKS Plus Nurul Hakim - Aplikasi Pengolah Rapor PDF</p>", unsafe_allow_html=True)