import psycopg2
import streamlit as st
import pandas as pd
import asyncio

# --- Styling ---

# St.columns style
custom_style_async_cols = """
div[data-testid="column"] {
    background-color: rgba(20, 23, 29, 0.7);
    border: 1px solid rgba(255, 255, 255);
    padding: 5% 5% 5% 10%;
    border-radius: 5px;
    color: white;
    overflow-wrap: break-word;
}
"""
st.markdown(f'<style>{custom_style_async_cols}</style>', unsafe_allow_html=True)


def assign_weather_background(weather_condition: str):
    """
    Changes background based on weather
    """

    if weather_condition == 'rain':
        url = "https://images.unsplash.com/photo-1620385019253-b051a26048ce?ixlib=rb-4.0.3&ixid" \
              "=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80"
    elif weather_condition == 'sun':
        url = "https://images.unsplash.com/photo-1419833173245-f59e1b93f9ee?ixlib=rb-4.0.3&ixid" \
              "=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80"
    elif weather_condition == 'cloudy':
        url = "https://images.unsplash.com/photo-1534088568595-a066f410bcda?ixlib=rb-4.0.3&ixid" \
              "=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=902&q=80"
    elif weather_condition == 'snow':
        url = "https://images.unsplash.com/photo-1511131341194-24e2eeeebb09?ixlib=rb-4.0.3&ixid" \
              "=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80"

    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
    background-image: url({url});
    background-size: cover;
    background-position: top left;
    background-repeat: no-repeat;
    background-attachment: local;
    }}
    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}
    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}
    [data-testid="stToolbar"] {{
    right: 2rem;
    }}
    </style>
    """

    return st.markdown(page_bg_img, unsafe_allow_html=True)


# --- Data Query ---
@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


conn = init_connection()


@st.cache_data(ttl=60)
def get_product_data(query):
    return pd.read_sql_query(query, conn)


# Get data
product_data_df = get_product_data("SELECT * FROM product_data;")

st.dataframe(product_data_df)

# --- Sidebar ---
# Temporary to display
weather = st.sidebar.selectbox("Choose weather to display",
                               ['sun', 'rain', 'cloudy', 'snow'])
assign_weather_background(weather_condition=weather)  # type: ignore

# ---- App ----
st.markdown("# 💨 🌍 Contextualizing CO₂-Emissions")

# Dropdown selection
product_data_df['price_str'] = product_data_df['price'].apply(lambda x: f"CHF {str(x)}0")
product_zip = list(zip(product_data_df['name'], product_data_df['category'], product_data_df['price_str']))
choices = [" - ".join(product) for product in product_zip]

product_choice = st.selectbox("Choose product", choices)

st.markdown("---")

# Product metrics
if product_choice:
    selected_product = product_data_df[(product_data_df['name'] == product_choice.split(" - ")[0]) & \
                                       (product_data_df['price'] == float(
                                           product_choice.replace("CHF ", "").split(" - ")[2]))].iloc[0, :]
    st.markdown(f"### {selected_product['name']}")
    st.markdown(f"Category: {selected_product['category']}")

    col1, col2 = st.columns(2)
    col1.metric("💰 Price:", f"CHF {selected_product['price']}0")
    col2.metric("💨 ♻️ Compensation Price:", f"CHF {selected_product['compensation_price']}")

    col3, col4 = st.columns(2)
    col3.metric("⚖️ Weight:", f"{selected_product['weight_gram'] / 1000} Kg")
    # Make sure emission is displayed in kg
    col4.metric("💨 Emission:", f"{selected_product['emission']} Kg/CO₂")

    emission: float = float(selected_product['emission'])

st.markdown("---")


# --- Time bars ---
async def time_passed(max_t: float, time_waiting: float):
    with col5:
        t = 0
        co2 = emission
        st.markdown("##### Compensation amount:")
        st.markdown(f"{co2} Kg/CO₂")
        st.markdown("##### Time passed by: ")
        placeholder = st.empty()
        final_time = st.empty()

        while t < max_t:
            with placeholder.container():
                days = t
                months = days // 30
                remaining_days = days % 30

                st.markdown(f"##### **{int(months)} months {remaining_days} days**")
                t += 1  # update time by 1 day
                await asyncio.sleep(time_waiting)
                placeholder.empty()

        with final_time.container():
            months = max_t // 30  # type: ignore
            days = round(max_t % 30)  # type: ignore
            st.markdown(f"##### **{int(months)} months {days} days**")


async def compensation_bar(t_compensation: float, time_waiting: float, title: str, column):
    months = round(t_compensation // 30)
    days = round(t_compensation % 30)
    t = 0

    column.markdown(title)  # type: ignore
    column.markdown(f"{months} months {days} days")  # type: ignore
    progress_bar = column.progress(0)  # type: ignore

    while t < t_compensation:
        t += 1
        percent_complete = round(t / t_compensation * 100)

        if percent_complete > 100:
            percent_complete = 100
            t = t_compensation  # type: ignore

        await asyncio.sleep(time_waiting)
        progress_bar.progress(percent_complete, text=f"{percent_complete} %")


async def main():
    # max compensation amount in days
    # Trees assumption: 22kg per year --> day = 0.0602 kg --> 10 trees 0.602
    TREE_COMPENSATION = 0.602
    HYDRO_COMPENSATION = 0.7
    SOLAR_COMPENSATION = 1.5

    if emission:
        t_tree = emission / TREE_COMPENSATION
        t_hydro = emission / HYDRO_COMPENSATION
        t_solar = emission / SOLAR_COMPENSATION
        max_t = max(t_tree, t_hydro, t_solar)

        if max_t <= 720:
            time_waiting = 0.2
        else:
            time_waiting = max_t / (max_t ** 1.6)

        await asyncio.gather(time_passed(max_t, time_waiting),
                             compensation_bar(t_tree, time_waiting, "#### 🌳 10 Trees", col6),
                             compensation_bar(t_solar, time_waiting, "#### ☀️ One Solar Panel (1.767 x 1.041)", col7),
                             compensation_bar(t_hydro, time_waiting, "#### 🌊 Hydro", col8))

    else:
        st.warning("Please select a product!")


button = st.button("See time needed per compensation method")

if button:
    col5, col6 = st.columns(2)
    col7, col8 = st.columns(2)
    asyncio.run(main())
