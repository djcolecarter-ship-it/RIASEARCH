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
            ria_name