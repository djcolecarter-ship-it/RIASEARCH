import streamlit as st
import pandas as pd

# Streamlit page config (set to wide layout and dark theme)
st.set_page_config(layout="wide", initial_sidebar_state="auto", page_title="RIA ETF Finder", page_icon=":search:", theme="dark")

# Streamlit interface
st.title("RIA ETF Finder")
ticker = st.text_input("Enter ETF Ticker (e.g., SPY):").upper()

if st.button("Find RIAs"):
    cusip = ticker_to_cusip.get(ticker)
    if not cusip:
        st.write(f"No CUSIP found for {ticker}.")
        st.stop()

    try:
        infotable = pd.read_csv("https://drive.google.com/uc?export=download&id=1MAa_5cMDjlzkUzVzK4EpirWRF9xuu781", delimiter="\t", dtype=str)
        coverpage = pd.read_csv("https://drive.google.com/uc?export=download&id=1X4kwQTFDCrwovOoMb851k-wIIwtbjFEe", delimiter="\t", dtype=str)
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