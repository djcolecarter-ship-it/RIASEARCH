import streamlit as st
import pandas as pd

# Dropbox direct download links for INFOTABLE and COVERPAGE (from previous)
INFOTABLE_URL = "https://www.dropbox.com/scl/fi/4hlccnqll0qylorf7ve14/INFOTABLE.tsv?rlkey=f63x2bu7r1k378irhnxdehs0x&st=4fir2jwm&dl=1"
COVERPAGE_URL = "https://www.dropbox.com/scl/fi/gxess41wug02mrg246339/COVERPAGE.tsv?rlkey=g0tkbfnw3o1pdc1l44nhti28j&st=521q4bmh&dl=1"

# Set wide mode
st.set_page_config(layout="wide")

# Streamlit interface
st.title("RIA Holdings Finder")
crd_number = st.text_input("Enter RIA CRD Number (e.g., 000324624):").upper()

if st.button("Find Holdings"):
    try:
        infotable = pd.read_csv(INFOTABLE_URL, delimiter="\t", dtype=str)
        coverpage = pd.read_csv(COVERPAGE_URL, delimiter="\t", dtype=str)
        infotable.columns = infotable.columns.str.strip()
        coverpage.columns = coverpage.columns.str.strip()
    except Exception as e:
        st.write(f"Error loading files: {e}")
        st.stop()

    holdings = []
    # Find all accession numbers for the RIA CRD number
    ria_data = coverpage[coverpage["CRDNUMBER"].str.strip() == crd_number]
    if not ria_data.empty:
        for _, firm_row in ria_data.iterrows():
            accession_number = firm_row["ACCESSION_NUMBER"]
            ria_name = firm_row["FILINGMANAGER_NAME"]
            ria_data_chunk = infotable[infotable["ACCESSION_NUMBER"] == accession_number]
            if not ria_data_chunk.empty:
                for index, row in ria_data_chunk.iterrows():
                    product_name = row["NAMEOFISSUER"]
                    cusip = row["CUSIP"]
                    security_info = row["TITLEOFCLASS"]
                    value = row["VALUE"]
                    formatted_value = f"${float(value):,}" if value else "N/A"
                    holdings.append({
                        "RIA Name": ria_name,
                        "Holding Name": product_name,
                        "CUSIP": cusip,
                        "Security Info": security_info,
                        "Dollar Amount": formatted_value
                    })

    results = pd.DataFrame(holdings)
    if not results.empty:
        st.write(f"Holdings for CRD Number {crd_number}:")
        st.dataframe(results[["RIA Name", "Holding Name", "CUSIP", "Security Info", "Dollar Amount"]])
    else:
        st.write(f"No holdings found for CRD Number {crd_number}.")