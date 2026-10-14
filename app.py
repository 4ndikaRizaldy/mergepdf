import streamlit as st
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
import io
import zipfile
from PIL import Image
import os

# ===== KONFIGURASI HALAMAN =====
st.set_page_config(
    page_title="Aplikasi Pengolah Rapor PDF",
    page_icon="📄",
    layout="wide"
)

# Folder untuk default files (tetap dibuat untuk menyimpan template default)
DEFAULT_IMAGES_DIR = "default_images"
DEFAULT_FILES_DIR = "default_files"

for folder_name in [DEFAULT_IMAGES_DIR, DEFAULT_FILES_DIR]:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# ===== HEADER =====
st.markdown("<h2 style='text-align:center;'>SMKS Plus Nurul Hakim</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Aplikasi Pengolah PDF Rapor Terpadu</h4>", unsafe_allow_html=True)
st.divider()

# ===== TAB MENU =====
tab1, tab2, tab3 = st.tabs(["➕ Gabung PDF", "️ Pisah PDF", "🖼️ Tambah Logo, TTD & Stempel"])

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
                for pdf_file in uploaded_files_merge:
                    reader = PdfReader(pdf_file)
                    for page in reader.pages:
                        writer.add_page(page)

                buffer = io.BytesIO()
                writer.write(buffer)
                buffer.seek(0) # PENTING: Kembalikan kursor ke awal agar bisa didownload
                
            st.success("✅ PDF berhasil digabung!")
            
            # KEMBALI KE DOWNLOAD BUTTON AGAR BISA DIAKSES DI WEB
            st.download_button(
                label="⬇️ Download Rapor Gabungan",
                data=buffer,
                file_name="Rapor_Kelas_Lengkap.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.caption("💡 *Tips: Jika download gagal/error IDM, **tahan tombol ALT** di keyboard saat mengklik Download.*")

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

        if split_mode == "Pisah Semua Halaman":
            if st.button("✂️ Pisah & Download ZIP", type="primary", use_container_width=True):
                with st.spinner("Sedang memisah halaman..."):
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
                st.download_button(
                    label="⬇️ Download Semua Halaman (ZIP)",
                    data=zip_buffer,
                    file_name="Hasil_Pisah_Halaman.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                st.caption("💡 *Tips: Tahan tombol ALT saat klik Download jika menggunakan IDM.*")

        else:
            col_start, col_end = st.columns(2)
            with col_start: 
                start_page = st.number_input("Halaman mulai", min_value=1, max_value=total_pages, value=1, key="range_start")
            with col_end: 
                end_page = st.number_input("Halaman akhir", min_value=1, max_value=total_pages, value=total_pages, key="range_end")

            if st.button("✂️ Pisah Range", type="primary", use_container_width=True):
                if start_page > end_page:
                    st.error("❌ Halaman mulai tidak boleh lebih besar dari halaman akhir!")
                else:
                    with st.spinner("Sedang memisah halaman..."):
                        writer = PdfWriter()
                        for i in range(start_page - 1, end_page):
                            writer.add_page(reader.pages[i])
                        buffer = io.BytesIO()
                        writer.write(buffer)
                        buffer.seek(0)
                            
                    st.success("✅ Range halaman berhasil dipisah!")
                    st.download_button(
                        label=f"⬇️ Download Halaman {start_page} - {end_page}",
                        data=buffer,
                        file_name=f"Rapor_Halaman_{start_page}_sampai_{end_page}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

# ==============================================================================
# TAB 3: TAMBAH LOGO, TTD & STEMPEL (OVERLAY)
# ==============================================================================
with tab3:
    st.subheader("Tambahkan Logo, Tanda Tangan & Stempel ke PDF Rapor")
    
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
        st.markdown("### 📄 1. File PDF untuk Preview")
        
        if default_pdf_path:
            st.success(f"✅ Menggunakan PDF default: `default_rapor.pdf`")
            st.caption("Upload file di bawah ini jika ingin melihat preview PDF milik Anda sendiri.")
        else:
            st.warning("⚠️ Tidak ada PDF default. Silakan upload 1 PDF untuk preview.")
            
        pdf_sample = st.file_uploader("Upload PDF kustom (kosongkan jika pakai default)", type="pdf", key="overlay_sample")
        active_pdf_source = pdf_sample if pdf_sample else default_pdf_path
        
        st.markdown("### 🖼️ 2. Upload Gambar (Opsional)")
        st.caption("Kosongkan jika ingin menggunakan gambar default dari folder 'default_images'")
        
        logo_file = st.file_uploader("Logo Sekolah", type=["png", "jpg"], key="overlay_logo")
        ttd_kepsek = st.file_uploader("TTD Kepala Sekolah", type=["png"], key="overlay_ttd_kepsek")
        stempel_file = st.file_uploader("Stempel Sekolah", type=["png"], key="overlay_stempel")
        ttd_wali = st.file_uploader("TTD Wali Kelas", type=["png"], key="overlay_ttd_wali")
        ttd_santri = st.file_uploader("TTD Wali Santri", type=["png"], key="overlay_ttd_santri")
        
        st.markdown("### 📁 Status File Default")
        col_chk1, col_chk2, col_chk3, col_chk4 = st.columns(4)
        with col_chk1:
            if default_pdf_path: st.success("✅ PDF")
            else: st.error("❌ PDF")
        with col_chk2:
            if default_logo: st.success("✅ Logo")
            else: st.error(" Logo")
        with col_chk3:
            if default_ttd: st.success("✅ TTD")
            else: st.error("❌ TTD")
        with col_chk4:
            if default_stempel: st.success("✅ Stempel")
            else: st.error("❌ Stempel")

    with col_right:
        st.markdown("###  3. Atur Posisi (dalam mm)")
        MM_TO_PT = 2.83 
        
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            st.markdown("**🎨 Logo Sekolah**")
            logo_x = st.number_input("X", value=93.0, step=0.1, key="pos_logo_x")
            logo_y = st.number_input("Y", value=4.5, step=0.1, key="pos_logo_y")
            logo_w = st.number_input("Lebar", value=23.5, step=0.1, key="pos_logo_w")
            
        with col_p2:
            st.markdown("**✍️ Tanda Tangan**")
            ttd_w = st.number_input("Lebar TTD", value=33.0, step=0.1, key="pos_ttd_w")
            
            st.markdown("**Kepala Sekolah**")
            k_x = st.number_input("X", value=91.5, step=0.1, key="pos_k_x")
            k_y = st.number_input("Y", value=235.0, step=0.1, key="pos_k_y")
            
            st.markdown("**Wali Kelas**")
            w_x = st.number_input("X", value=145.0, step=0.1, key="pos_w_x")
            w_y = st.number_input("Y", value=235.0, step=0.1, key="pos_w_y")
            
            st.markdown("**Wali Santri**")
            s_x = st.number_input("X", value=38.0, step=0.1, key="pos_s_x")
            s_y = st.number_input("Y", value=235.0, step=0.1, key="pos_s_y")
            
        with col_p3:
            st.markdown("** Stempel Sekolah**")
            stempel_w = st.number_input("Lebar", value=35.0, step=0.1, key="pos_stempel_w")
            stempel_x = st.number_input("X", value=73.7, step=0.1, key="pos_stempel_x")
            stempel_y = st.number_input("Y", value=233.0, step=0.1, key="pos_stempel_y")
            stempel_opacity = st.slider("Transparansi", 0.0, 1.0, 1.0, 0.1, key="pos_stempel_opacity")

    st.divider()
    
    # Preview Logic
    if active_pdf_source:
        if st.button("👁️ Tampilkan Preview Posisi", type="secondary", use_container_width=True):
            if isinstance(active_pdf_source, str):
                pdf_doc = fitz.open(active_pdf_source)
            else:
                pdf_doc = fitz.open(stream=active_pdf_source.getvalue(), filetype="pdf")
                
            page = pdf_doc[0]
            
            def insert_img(page_obj, img_source, x, y, w, opacity=1.0):
                if img_source is None: return False
                try:
                    if isinstance(img_source, str) and os.path.exists(img_source):
                        img = Image.open(img_source)
                    else:
                        img = Image.open(img_source)
                    
                    img_bytes = io.BytesIO()
                    if opacity < 1.0:
                        img = img.convert("RGBA")
                        img.putalpha(int(opacity * 255))
                    
                    img.save(img_bytes, format="PNG")
                    img_bytes.seek(0)
                    aspect = img.width / img.height
                    rect = fitz.Rect(x*MM_TO_PT, y*MM_TO_PT, (x+w)*MM_TO_PT, (y + w/aspect)*MM_TO_PT)
                    page_obj.insert_image(rect, stream=img_bytes.getvalue())
                    return True
                except Exception as e:
                    return False

            logo_src = logo_file if logo_file else default_logo
            ttd_src = ttd_kepsek if ttd_kepsek else default_ttd
            stempel_src = stempel_file if stempel_file else default_stempel
            
            if logo_src: insert_img(page, logo_src, logo_x, logo_y, logo_w)
            if ttd_src: insert_img(page, ttd_src, k_x, k_y, ttd_w)
            if stempel_src: insert_img(page, stempel_src, stempel_x, stempel_y, stempel_w, stempel_opacity)
            if ttd_wali: insert_img(page, ttd_wali, w_x, w_y, ttd_w)
            if ttd_santri: insert_img(page, ttd_santri, s_x, s_y, ttd_w)
            
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            st.image(pix.tobytes("png"), caption="Preview Hasil", use_container_width=True)
            pdf_doc.close()
    else:
        st.info("ℹ️ Silakan upload PDF atau tambahkan `default_rapor.pdf` di folder `default_files`.")

    st.divider()
    st.markdown("###  4. Proses Massal")
    st.caption("Upload semua PDF rapor, lalu tempelkan logo, TTD & stempel sesuai posisi di atas.")
    
    pdf_files_batch = st.file_uploader("Upload SEMUA file PDF rapor siswa", type="pdf", accept_multiple_files=True, key="overlay_batch")
    
    if st.button("🖨️ Proses & Tambahkan Logo/TTD/Stempel ke Semua PDF", type="primary", use_container_width=True):
        has_logo = logo_file or default_logo
        if not pdf_files_batch or not has_logo:
            st.error("❌ Upload minimal 1 file PDF dan pastikan logo tersedia!")
        else:
            with st.spinner("Sedang memproses PDF..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    def prep_img(img_source):
                        if img_source is None: return None
                        try:
                            if isinstance(img_source, str) and os.path.exists(img_source):
                                img = Image.open(img_source)
                            else:
                                img = Image.open(img_source)
                            b = io.BytesIO()
                            img.save(b, format="PNG")
                            return {"data": b.getvalue(), "aspect": img.width / img.height, "img": img}
                        except:
                            return None

                    logo_src = logo_file if logo_file else default_logo
                    ttd_src = ttd_kepsek if ttd_kepsek else default_ttd
                    stempel_src = stempel_file if stempel_file else default_stempel
                    
                    img_logo = prep_img(logo_src)
                    img_kepsek = prep_img(ttd_src)
                    img_stempel = prep_img(stempel_src)
                    img_wali = prep_img(ttd_wali)
                    img_santri = prep_img(ttd_santri)
                    
                    if not img_logo:
                        st.error("❌ Logo tidak bisa diproses!")
                        st.stop()
                    
                    for idx, pdf_file in enumerate(pdf_files_batch):
                        if pdf_file.getbuffer().nbytes > 0:
                            status_text.text(f"Memproses: {pdf_file.name}")
                            pdf_doc = fitz.open(stream=pdf_file.getvalue(), filetype="pdf")
                            
                            for page_num in range(len(pdf_doc)):
                                page = pdf_doc[page_num]
                                
                                rect = fitz.Rect(logo_x*MM_TO_PT, logo_y*MM_TO_PT, (logo_x+logo_w)*MM_TO_PT, (logo_y + logo_w/img_logo["aspect"])*MM_TO_PT)
                                page.insert_image(rect, stream=img_logo["data"])
                                
                                if img_kepsek:
                                    rect = fitz.Rect(k_x*MM_TO_PT, k_y*MM_TO_PT, (k_x+ttd_w)*MM_TO_PT, (k_y + ttd_w/img_kepsek["aspect"])*MM_TO_PT)
                                    page.insert_image(rect, stream=img_kepsek["data"])
                                
                                if img_stempel:
                                    stempel_img = img_stempel["img"].convert("RGBA")
                                    stempel_img.putalpha(int(stempel_opacity * 255))
                                    stempel_bytes = io.BytesIO()
                                    stempel_img.save(stempel_bytes, format="PNG")
                                    stempel_bytes.seek(0)
                                    
                                    rect = fitz.Rect(stempel_x*MM_TO_PT, stempel_y*MM_TO_PT, (stempel_x+stempel_w)*MM_TO_PT, (stempel_y + stempel_w/img_stempel["aspect"])*MM_TO_PT)
                                    page.insert_image(rect, stream=stempel_bytes.getvalue())
                                
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
            
            # KEMBALI KE DOWNLOAD BUTTON AGAR BISA DIAKSES DI WEB
            st.download_button(
                label="⬇️ Download Semua PDF (ZIP)",
                data=zip_buffer,
                file_name="Rapor_Lengkap_Logo_TTD_Stempel.zip",
                mime="application/zip",
                use_container_width=True
            )
            st.caption("💡 *Tips: Tahan tombol ALT saat klik Download jika menggunakan IDM.*")

# ===== FOOTER =====
st.divider()
st.markdown("<p style='text-align:center; color:gray;'>© 2026 SMKS Plus Nurul Hakim - Aplikasi Pengolah Rapor PDF</p>", unsafe_allow_html=True)