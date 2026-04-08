import streamlit as st
import pandas as pd
import httpx

st.set_page_config(page_title="Archive-It Search", layout="wide")
st.title("U-M Music-Performance Group Web Archive")

collection_id = "31146"
url_to_search = st.text_input("URL to search", value="maizepages.umich.edu")
limit = st.number_input("Limit Results", min_value=1, value=10)

if st.button("Search Archive"):
    base_url = f"https://wayback.archive-it.org/{collection_id}/timemap/cdx"

    params = {
        "url": url_to_search,
        "matchType": "host",          # or "exact" / "prefix" depending on what you want
        "output": "json",
        "fl": "timestamp,original",
        "limit": int(limit),
    }

    with st.spinner("Fetching archives..."):
        try:
            response = httpx.get(base_url, params=params, timeout=20.0)
            response.raise_for_status()

            data = response.json()

            if not data or len(data) <= 1:
                st.warning("No captures found for that URL.")
            else:
                st.write(data)
                headers = data[0]
                rows = data[1:]
                df = pd.DataFrame(rows, columns=headers)

                df["date"] = pd.to_datetime(df["timestamp"], format="%Y%m%d%H%M%S")
                df["link"] = df.apply(
                    lambda row: f"https://wayback.archive-it.org/{collection_id}/{row['timestamp']}/{row['original']}",
                    axis=1
                )

                st.success(f"Found {len(df)} captures")
                st.dataframe(df[["date", "original", "link"]])

                for _, row in df.iterrows():
                    st.markdown(f"- {row['date']}: [{row['link']}]({row['link']})")

        except Exception as e:
            st.error(f"Error fetching data: {e}")
