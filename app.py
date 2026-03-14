import streamlit as st
from pypdf import PdfReader, PdfWriter
import io
import zipfile

# ===== KONFIGURASI HALAMAN =====
st.set_page_config(
    page_title="Pengolah Rapor PDF",
    page_icon="💻",
    layout="centered"
)

# ===== HEADER =====
col1, col2, col3 = st.columns([4,2,4])

with col2:
    st.image("logo.png", width=150)

st.markdown(
    "<h2 style='text-align:center;'>SMKS Plus Nurul Hakim</h2>",
    unsafe_allow_html=True
)

st.markdown(
    "<h4 style='text-align:center;'>Aplikasi Pengolah PDF Rapor</h4>",
    unsafe_allow_html=True
)

st.divider()

# ===== MENU =====
menu = st.radio(
    "Pilih Fitur",
    ["Gabungkan PDF", "Pisah PDF"]
)

# =========================
# GABUNG PDF
# =========================
if menu == "Gabungkan PDF":

    uploaded_files = st.file_uploader(
        "Upload PDF Rapor Siswa",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:

        st.info(f"{len(uploaded_files)} file siap digabung")

        if st.button("Gabungkan PDF"):

            writer = PdfWriter()

            for pdf in uploaded_files:
                reader = PdfReader(pdf)
                for page in reader.pages:
                    writer.add_page(page)

            buffer = io.BytesIO()
            writer.write(buffer)
            buffer.seek(0)

            st.success("PDF berhasil digabung!")

            st.download_button(
                "⬇️ Download Rapor Gabungan",
                data=buffer,
                file_name="rapor_kelas.pdf",
                mime="application/pdf"
            )

# =========================
# PISAH PDF
# =========================
if menu == "Pisah PDF":

    uploaded_file = st.file_uploader(
        "Upload 1 file PDF",
        type="pdf"
    )

    if uploaded_file:

        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)

        st.info(f"Total halaman: {total_pages}")

        split_mode = st.radio(
            "Mode Pisah",
            ["Pisah Semua Halaman", "Pisah Berdasarkan Range"]
        )

        # ===== PISAH SEMUA HALAMAN =====
        if split_mode == "Pisah Semua Halaman":

            if st.button("Pisah & Download ZIP"):

                zip_buffer = io.BytesIO()

                with zipfile.ZipFile(zip_buffer, "w") as zip_file:

                    for i in range(total_pages):

                        writer = PdfWriter()
                        writer.add_page(reader.pages[i])

                        pdf_buffer = io.BytesIO()
                        writer.write(pdf_buffer)

                        zip_file.writestr(
                            f"halaman_{i+1}.pdf",
                            pdf_buffer.getvalue()
                        )

                zip_buffer.seek(0)

                st.success("PDF berhasil dipisah!")

                st.download_button(
                    "⬇️ Download Semua Halaman (ZIP)",
                    data=zip_buffer,
                    file_name="hasil_pisah_pdf.zip",
                    mime="application/zip"
                )

        # ===== PISAH RANGE =====
        if split_mode == "Pisah Berdasarkan Range":

            start = st.number_input(
                "Halaman mulai",
                min_value=1,
                max_value=total_pages,
                value=1
            )

            end = st.number_input(
                "Halaman akhir",
                min_value=1,
                max_value=total_pages,
                value=1
            )

            if st.button("Pisah Range"):

                writer = PdfWriter()

                for i in range(start-1, end):
                    writer.add_page(reader.pages[i])

                buffer = io.BytesIO()
                writer.write(buffer)
                buffer.seek(0)

                st.download_button(
                    "⬇️ Download PDF Range",
                    data=buffer,
                    file_name=f"halaman_{start}-{end}.pdf",
                    mime="application/pdf"
                )