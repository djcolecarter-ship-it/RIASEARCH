import streamlit as st
import pandas as pd

# Dropbox direct download link for CUSIPS (with &dl=1)
CUSIPS_URL = "https://www.dropbox.com/scl/fi/fw0xkwlszl9fzk4z5tktj/CUSIPS.txt?rlkey=zn4fy9snn79swj3pnz6qk211s&st=pfgrlojo&dl=1"

# Dropbox direct download links for INFOTABLE and COVERPAGE (from previous)
INFOTABLE_URL = "https://www.dropbox.com/scl/fi/4hlccnqll0qylorf7ve14/INFOTABLE.tsv?rlkey=f63x2bu7r1k378irhnxdehs0x&st=4fir2jwm&dl=1"
COVERPAGE_URL = "https://www.dropbox.com/scl/fi/gxess41wug02mrg246339/COVERPAGE.tsv?rlkey=g0tkbfnw3o1pdc1l44nhti28j&st=521q4bmh&dl=1"

# Set wide mode
st.set_page_config(layout="wide")

# Streamlit interface
st.title("RIA ETF Finder")
ticker = st.text_input("Enter ETF Ticker (e.g., SPY):").upper()

@st.cache_data
def load_files():
    etf_list = pd.read_csv(CUSIPS_URL, delimiter="\t", dtype=str)
    coverpage = pd.read_csv(COVERPAGE_URL, delimiter="\t", dtype=str)
    etf_list.columns = etf_list.columns.str.strip()
    coverpage.columns = coverpage.columns.str.strip()
    return etf_list, coverpage

if st.button("Find RIAs"):
    etf_list, coverpage = load_files()
    cusip_row = etf_list[etf_list["Symbol"].str.strip().str.upper() == ticker]
    cusip = cusip_row["CUSP"].iloc[0].strip() if not cusip_row.empty else None
    if not cusip:
        st.write(f"No CUSIP found for {ticker} in CUSIPS.")
        st.stop()

    firms = []
    chunks = pd.read_csv(INFOTABLE_URL, delimiter="\t", dtype=str, chunksize=100000)  # Load in chunks of 100,000 rows
    for chunk in chunks:
        chunk.columns = chunk.columns.str.strip()
        cusip_data = chunk[chunk["CUSIP"].str.strip() == cusip]
        if not cusip_data.empty:
            for index, row in cusip_data.iterrows():
                accession_number = row["ACCESSION_NUMBER"]
                value = row["VALUE"]
                firm_data = coverpage[coverpage["ACCESSION_NUMBER"] == accession_number]
                if not firm_data.empty:
                    firm_name = firm_data["FILINGMANAGER_NAME"].iloc[0]
                    street = f"{firm_data['FILINGMANAGER_STREET1'].iloc[0]} {firm_data['FILINGMANAGER_STREET2'].iloc[0] or ''}"
                    city = firm_data['FILINGMANAGER_CITY'].iloc[0]
                    state = firm_data['FILINGMANAGER_STATEORCOUNTRY'].iloc[0]
                    zipcode = firm_data['FILINGMANAGER_ZIPCODE'].iloc[0]
                    address = f"{street}, {city}, {state} {zipcode}"
                    crd_number = firm_data["CRDNUMBER"].iloc[0]
                    sec_number = firm_data["SECFILENUMBER"].iloc[0]

                    if pd.notna(crd_number) or (pd.notna(sec_number) and sec_number.startswith("801-")):
                        formatted_value = f"${float(value):,}"
                        firms.append({
                            "RIA Name": firm_name,
                            "Dollar Amount": formatted_value,
                            "Street": street,
                            "City": city,
                            "State": state,
                            "Zipcode": zipcode,
                            "CRD Number": crd_number,
                            "SEC Number": sec_number
                        })

    results = pd.DataFrame(firms).drop_duplicates(subset=["RIA Name", "CRD Number"])
    if not results.empty:
        st.write(f"RIAs holding {ticker} (CUSIP: {cusip}):")
        st.dataframe(results[["RIA Name", "Dollar Amount", "Street", "City", "State", "Zipcode", "CRD Number", "SEC Number"]])
    else:
        st.write(f"No RIAs found holding {ticker} (CUSIP: {cusip}).")