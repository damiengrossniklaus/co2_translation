import streamlit as st
import pandas as pd
import asyncio


# --- Data Preparation ---

digitec_df = pd.read_csv('data/digitec_sample_data.csv')
galaxus_df = pd.read_csv('data/galaxus_sample_data.csv')


# Cleaning



# ---- App ----

st.markdown("# 💨 🌍 Contextualizing CO₂-Emissions")
st.dataframe(digitec_df)

# Dropdown selection
digitec_df['price_str'] = digitec_df['price'].apply(lambda x: f"CHF {str(x)}0")
product_zip = list(zip(digitec_df['name'], digitec_df['category'], digitec_df['price_str']))
choices = [" - ".join(product) for product in product_zip]

product_choice = st.selectbox("Choose product", choices)

st.markdown("---")

# Product metrics
if product_choice:
    selected_product = digitec_df[(digitec_df['name'] == product_choice.split(" - ")[0]) &\
                                  (digitec_df['price'] == float(product_choice.replace("CHF ", "").split(" - ")[2]))].iloc[0, :]
    st.markdown(f"### {selected_product['name']}")
    st.markdown(f"Category: {selected_product['category']}")

    col1, col2 = st.columns(2)

    col1.metric("💰 Price:", f"CHF {selected_product['price']}0")
    col1.metric("💨 ♻️ Compensation Price:", f"CHF {selected_product['compensation_price']}")

    col2.metric("⚖️ Weight:", selected_product['weight'])
    col2.metric("💨 Emission:", f"{selected_product['emission']} Kg/CO₂")


st.markdown("---")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

async def time_passed():

    with col1:
        co2 = 50
        st.markdown("#### Compensation amount:")
        st.markdown(f"{co2} Kg/CO₂")
        st.markdown("Time passed by: ")
        placeholder = st.empty()
        t = 0
        for i in range(1, 101):
            with placeholder.container():
                months = abs(t)
                days = round((months - int(months)) * 30)
                st.markdown(f"#### {int(months)} months {days} days")
                t += 3/100
                await asyncio.sleep(0.35)
                placeholder.empty()
        st.markdown(f"#### {round(t)} months")


async def trees():
    col2.markdown("#### 🌳 Trees")
    col2.markdown("Months: 2")
    tree_bar = col2.progress(0)
    for percent_complete in range(1, 101):
        await asyncio.sleep(0.2)
        tree_bar.progress(percent_complete, text=f"{percent_complete} %")


async def solar():
    col3.markdown("#### ☀️ Solar")
    col3.markdown("Months: 2.5")
    solar_bar = col3.progress(0)
    for percent_complete in range(1, 101):
        await asyncio.sleep(0.25)
        solar_bar.progress(percent_complete, text=f"{percent_complete} %")


async def hydro():
    col4.markdown("#### 🌊 Hydro")
    col4.markdown("Months: 3")
    progress_text = "Time with hydro"
    hydro_bar = col4.progress(0)
    for percent_complete in range(1, 101):
        await asyncio.sleep(0.4)
        hydro_bar.progress(percent_complete, text=f"{percent_complete} %")


async def main():
    await asyncio.gather(time_passed(), trees(), solar(), hydro())


button = st.button("See time needed per compensation method")

if button:
    asyncio.run(main())

