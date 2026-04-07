import streamlit as st
import pandas as pd
import numpy as np
import httpx

st.set_page_config(page_title="Archive-It Search", layout="wide")

st.title('U-M Music-Performance Group Web Archive')

# Input fields
collection_id = "31146"
url_to_search = ""
limit = st.number_input("Limit Results", value=10)

if st.button("Search Archive"):
    # Build API URL
    # CDX API documentation: https://support.archive-it.org/hc/en-us/articles/360001231286
    base_url = f"http://wayback.archive-it.org/{collection_id}/timemap/cdx?url=archive-it.org"

    with st.spinner('Fetching archives...'):
        try:
            response = httpx.get(base_url)
            response.raise_for_status()
            
            # Parse CDX data (JSON lines format)
            data = [line.split() for line in response.text.strip().split('\n') if line]
            df = pd.DataFrame(data, columns=['timestamp', 'original_url'])
            
            # Format display
            df['date'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M%S')
            df['link'] = df['timestamp'].apply(lambda x: f"http://wayback.archive-it.org/{collection_id}/{x}/{url_to_search}")
            
            st.success("Found captures!")
            
            # Display results
            for _, row in df.iterrows():
                st.markdown(f"- {row['date']}: [{row['link']}]({row['link']})")

        except Exception as e:
            st.error(f"Error fetching data: {e}")

