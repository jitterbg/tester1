import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

# Streamlit app title
st.title("📄 PDF Table Extractor to Excel")

# File uploader for multiple PDFs
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

# Button to trigger processing
if st.button("Convert to Excel") and uploaded_files:
    all_data = []

    # Process each uploaded PDF
    for uploaded_file in uploaded_files:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table)
                    all_data.append(df)

    # Combine all dataframes and export to Excel
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='Extracted Data')
        output.seek(0)

        # Provide download link
        st.success("✅ Data extracted successfully!")
        st.download_button(
            label="📥 Download Excel File",
            data=output,
            file_name="combined_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No tables found in the uploaded PDF files.")
elif uploaded_files is None:
    st.info("Please upload one or more PDF files to begin.")
