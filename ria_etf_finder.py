import streamlit as st
import pandas as pd

# Direct download URLs from Google Drive (make files public and use this format)
CUSIPS_URL = "https://drive.google.com/uc?export=download&id=1irqCNmaLo6u5OplgpaMt_30W_CsZP-dq"
INFOTABLE_URL = "https://drive.google.com/uc?export=download&id=1MAa_5cMDjlzkUzVzK4EpirWRF9xuu781"
COVERPAGE_URL = "https://drive.google.com/uc?export=download&id=1X4kwQTFDCrwovOoMb851k-wIIwtbjFEe"

# Streamlit interface
st.title("RIA ETF Finder")
ticker = st.text_input("Enter ETF Ticker (e.g., SPY):").upper()

if st.button("Find RIAs"):
    # Load CUSIPS from URL for CUSIP lookup
    try:
        etf_list = pd.read_csv(CUSIPS_URL, delimiter="\t", dtype=str)
        etf_list.columns = etf_list.columns.str.strip()
        cusip_row = etf_list[etf_list["Symbol"].str.strip().str.upper() == ticker]
        cusip = cusip_row["CUSP"].iloc[0].strip() if not cusip_row.empty else None
        if not cusip:
            st.write(f"No CUSIP found for {ticker} in CUSIPS.")
            st.stop()
    except Exception as e:
        st.write(f"Error loading CUSIPS: {e}")
        st.stop()

    # Load INFOTABLE and COVERPAGE from URLs
    try:
        infotable = pd.read_csv(INFOTABLE_URL, delimiter="\t", dtype=str)
        coverpage = pd.read_csv(COVERPAGE_URL, delimiter="\t", dtype=str)
        infotable.columns = infotable.columns.str.strip()
        coverpage.columns = coverpage.columns.str.strip()
    except Exception as e:
        st.write(f"Error loading files: {e}")
        st.stop()

    firms = []
    cusip_data = infotable[infotable["CUSIP"].str.strip() == cusip]
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