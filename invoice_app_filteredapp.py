import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO

# Streamlit app title
st.title("📄 Clean Invoice PDF Tables and Export to Excel")

# File uploader for multiple PDFs
uploaded_files = st.file_uploader("Upload PDF invoice files", type="pdf", accept_multiple_files=True)

# Define patterns to filter out
japanese_keywords = ['連絡先', '登録番号']
phone_pattern = re.compile(r'\d{2,4}-\d{2,4}-\d{4}')
postal_code_pattern = re.compile(r'〒?\d{3}-\d{4}')
address_keywords = ['都', '道', '府', '県', '市', '区', '町', '丁目', '番地']

def is_address(text):
    return any(kw in text for kw in address_keywords)

def clean_cell(cell):
    if cell is None:
        return ''
    return re.sub(r'\s+', ' ', cell).strip()

def should_remove_row_or_col(values):
    joined = ' '.join(values)
    if any(keyword in joined for keyword in japanese_keywords):
        return True
    if phone_pattern.search(joined) or postal_code_pattern.search(joined):
        return True
    if is_address(joined):
        return True
    return False

# Button to trigger processing
if st.button("Convert to Excel") and uploaded_files:
    all_data = []

    for uploaded_file in uploaded_files:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table)
                    df = df.applymap(clean_cell)

                    # Remove rows with unwanted content
                    df = df[~df.apply(lambda row: should_remove_row_or_col(row.values.astype(str)), axis=1)]

                    # Remove columns with unwanted content
                    df = df.loc[:, ~df.apply(lambda col: should_remove_row_or_col(col.values.astype(str)), axis=0)]

                    if not df.empty:
                        all_data.append(df)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='Cleaned Data')
        output.seek(0)

        st.success("✅ Cleaned data extracted successfully!")
        st.download_button(
            label="📥 Download Excel File",
            data=output,
            file_name="filtered_invoice_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ No valid table data found after filtering.")
elif uploaded_files is None:
    st.info("Please upload one or more PDF files to begin.")

