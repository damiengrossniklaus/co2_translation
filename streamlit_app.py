import psycopg2
import asyncio
import colorsys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Set, List
from streamlit_plotly_events import plotly_events
from design_functions.design_functions import style_columns, assign_weather_background

# --- Layout ----
style_columns()


# --- Data Query ---
@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


@st.cache_data(ttl=60)
def get_product_data(query):
    return pd.read_sql_query(query, conn)


# --- Functions ---

def init_session_state():
    """
     Initializes Streamlit Session State
    """
    if "counter" not in st.session_state:
        st.session_state.counter = 0

    if "product_query" not in st.session_state:
        st.session_state["product_query"] = set()


def query_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply filters in Streamlit Session State
    to filter the input DataFrame.
    """
    df["emission_weight"] = df['emission'].astype(str) + "-" + df['weight_gram'].astype(int).astype(str)

    df["selected"] = True

    if st.session_state["product_query"]:
        df.loc[~df['emission_weight'].isin(st.session_state["product_query"]), "selected"] = False

    return df


def update_state(current_query: Dict[str, Set]):
    """
    Stores input dict of filters into Streamlit Session State.

    If one of the input filters is different from previous value in Session State,
    rerun Streamlit to activate the filtering and plot updating with the new info in State.
    """
    rerun = False
    if current_query['product_query'] - st.session_state['product_query']:
        st.session_state['product_query'] = current_query['product_query']
        rerun = True

    if rerun:
        st.experimental_rerun()


def create_color_list(df: pd.DataFrame) -> List[str]:
    """
    Creates RGBA values for every unique category in pd.DataFrame.
    Every category has two RGBA values where alpha corresponds to
    selected=True --> alpha=0.8 and selected=False --> alpha=0.2
    """
    num_categories = df['category'].nunique()
    color_map = []

    for i in range(num_categories):
        hue = i / num_categories
        rgb = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(hue, 0.7, 0.9))
        color_map.append(rgb)

    unique_categories = df['category'].unique()
    category_color_map = {}

    for i, category in enumerate(unique_categories):
        category_color_map[category] = color_map[i % len(color_map)]

    color_list = []

    for category, selected in df[['category', 'selected']].values:
        if selected:
            opacity = 0.8
        else:
            opacity = 0.2
        color = category_color_map[category]
        rgba = f"rgba({color[0]}, {color[1]}, {color[2]}, {opacity})"
        color_list.append(rgba)

    return color_list


def build_product_data_fig(df: pd.DataFrame, color_list: List[str]) -> go.Figure:
    """
    Creates go.Scatter figure of product data.
    """

    fig = go.Figure()

    fig.add_trace(go.Scatter(mode='markers',
                             x=df['emission'],
                             y=df['weight_gram'],
                             marker=dict(
                                 color=color_list,
                                 size=df['price'] / 35,
                                 sizemode='diameter',
                                 sizemin=7
                             ),
                             hovertemplate='<b>%{customdata[0]}</b>'
                                           '<br>Category: %{customdata[2]}'
                                           '<br>Price: CHF %{customdata[1]:,.2f}'
                                           '<br>Weight: %{y:,} gram'
                                           '<br>Emission: %{x}'
                                           '<extra></extra>',
                             customdata=list(zip(df['name'], df['price'], df['category']))
                             ))

    fig.update_layout(
        title="Emission vs Weight of products (color indicate different category)",
        xaxis_title="Emission",
        yaxis_title="Weight (gram)",
        template='plotly_dark'
    )

    return fig


# --- Time bars / Async functions ---
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


async def async_main():
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


# --- Sidebar ---
# Temporary to display
weather = st.sidebar.selectbox("Choose weather to display",
                               ['sun', 'covered', 'rain', 'snow'])
assign_weather_background(weather_condition=weather)  # type: ignore


# ---- App ----

init_session_state()

conn = init_connection()
# Get data
product_data_df = get_product_data("""SELECT * FROM product_data WHERE emission != 0;""")
st.dataframe(product_data_df)

st.markdown("# 💨 🌍 Contextualizing CO₂-Emissions")

# Total product metrics
col1, col2 = st.columns(2)

col1.metric("📁 Products in database:",
            f"{len(product_data_df)} products")

col2.metric("🎨 Categories in database:",
            f"{product_data_df['category'].nunique()} categories")

col3, col4 = st.columns(2)

col3.metric("🌱 Lowest emission of product:",
            f"{min(product_data_df['emission'])} Kg/CO₂")

col4.metric("💨 Highest emission of product:",
            f"{max(product_data_df['emission'])} Kg/CO₂")

st.markdown("---")

# Filter categories

st.markdown("### 🔬 Filter Product")
st.markdown("Filter for the product you would like to inspect more closely. "
            "For this you can narrow down the category and afterwards "
            "select a product by clicking on the point in the chart or "
            "selecting it in the dropdown below the chart.")
category_filter = st.checkbox("Check to filter for specific categories")

if category_filter:

    sorted_categories = sorted(product_data_df['category'].unique())
    sorted_categories.insert(0, "All categories")

    selected_categories: List[str] = st.multiselect("Select the categories you are interested in",
                                         sorted_categories,
                                         default="All categories")

    if "All categories" not in selected_categories:
        product_data_df = product_data_df[product_data_df['category'].isin(selected_categories)]


product_data_df = query_data(product_data_df)

category_color_list = create_color_list(product_data_df)
product_fig = build_product_data_fig(product_data_df, category_color_list)

selected_points = plotly_events(product_fig,
                                select_event=True,
                                key=f"product_{st.session_state.counter}")

# Update session state
current_query = {"product_query": {f"{el['x']}-{el['y']}" for el in selected_points}}
update_state(current_query)

# Dropdown selection
product_data_df = product_data_df[product_data_df['selected'] == True]
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
    st.markdown(f"### 📝 {selected_product['name']}")
    st.markdown(f"Category: {selected_product['category']}")

    col3, col4 = st.columns(2)
    col3.metric("💰 Price:", f"CHF {selected_product['price']}0")
    col4.metric("💨 ♻️ Compensation Price:", f"CHF {selected_product['compensation_price']}")

    col5, col6 = st.columns(2)
    col5.metric("⚖️ Weight:", f"{selected_product['weight_gram'] / 1000} Kg")
    # Make sure emission is displayed in kg
    col6.metric("💨 Emission:", f"{selected_product['emission']} Kg/CO₂")

    emission: float = float(selected_product['emission'])

st.markdown("---")

button = st.button("See time needed per compensation method")

if button:
    col5, col6 = st.columns(2)
    col7, col8 = st.columns(2)
    asyncio.run(async_main())

if __name__ == "__main__":
    pass
