import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Dropbox direct download links (with &dl=1)
INFOTABLE_URL = "https://www.dropbox.com/scl/fi/4hlccnqll0qylorf7ve14/INFOTABLE.tsv?rlkey=f63x2bu7r1k378irhnxdehs0x&st=4fir2jwm&dl=1"
COVERPAGE_URL = "https://www.dropbox.com/scl/fi/gxess41wug02mrg246339/COVERPAGE.tsv?rlkey=g0tkbfnw3o1pdc1l44nhti28j&st=521q4bmh&dl=1"

# Streamlit interface
st.set_page_config(layout="wide", initial_sidebar_state="auto", page_title="RIA ETF Finder", page_icon=":search:")
st.title("RIA ETF Finder")
ticker = st.text_input("Enter ETF Ticker (e.g., SPY):").upper()

if st.button("Find RIAs"):
    # Dynamic CUSIP lookup from portfolioslab.com
    try:
        url = f"https://portfolioslab.com/symbol/{ticker}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        cusip_label = soup.find(string=lambda text: text and "CUSIP" in text)
        cusip = cusip_label.find_parent().find_next_sibling("div").text.strip() if cusip_label else None
        if not cusip:
            st.write(f"No CUSIP found for {ticker} on portfolioslab.com.")
            st.stop()
    except Exception as e:
        st.write(f"Error fetching CUSIP: {e}")
        st.stop()

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