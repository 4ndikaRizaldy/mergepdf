import streamlit as st
from pypdf import PdfReader, PdfWriter
import io

# ===== KONFIGURASI HALAMAN =====
st.set_page_config(
    page_title="Penggabung Rapor",
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
    "<h4 style='text-align:center;'>Aplikasi Penggabung PDF Rapor</h4>",
    unsafe_allow_html=True
)

st.divider()

# ===== UPLOAD FILE =====
uploaded_files = st.file_uploader(
    "Upload PDF Rapor Siswa",
    type="pdf",
    accept_multiple_files=True
)

# ===== PROSES GABUNG =====
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