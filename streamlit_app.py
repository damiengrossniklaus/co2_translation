import psycopg2
import asyncio
import streamlit as st
import pandas as pd
from typing import Dict, Set, List
from PIL import Image
from streamlit_plotly_events import plotly_events
from utils.design_functions import style_columns, assign_weather_background
from utils.helper_functions import read_markdown
from utils.calc_co2_offset_functions import calc_solar_energy_offset, calc_trees_offset, calc_hydro_offset
from utils.plot_functions import create_color_list, build_product_data_fig, build_product_comparison_fig, \
    create_color_legend
# --- Layout ----
style_columns()


# --- Data Query ---
@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


@st.cache_data(ttl=60)
def get_data_from_db(query):
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


async def compensation_bar(t_compensation: float, time_waiting: float, title: str,
                           column, help_string: str):
    months = round(t_compensation // 30)
    days = round(t_compensation % 30)
    t = 0

    column.markdown(title, help=help_string)  # type: ignore
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


async def async_main(sun_hours: float, num_trees: int, water_flow: float):
    tree_compensation = calc_trees_offset(num_trees)
    hydro_compensation = calc_hydro_offset(water_flow)
    solar_compensation = calc_solar_energy_offset(sun_hours)

    tree_info = read_markdown('assets/tree_calc_info.md')
    hydro_info = read_markdown('assets/hydro_calc_info.md')
    solar_info = read_markdown('assets/solar_calc_info.md')

    if emission:
        t_tree = emission / tree_compensation
        t_hydro = emission / hydro_compensation
        t_solar = emission / solar_compensation
        max_t = max(t_tree, t_hydro, t_solar)

        if max_t <= 720:
            time_waiting = 0.2
        else:
            time_waiting = max_t / (max_t ** 1.7)

        await asyncio.gather(time_passed(max_t, time_waiting),
                             compensation_bar(t_tree, time_waiting, "#### 🌳 One Trees", col6, tree_info),
                             compensation_bar(t_solar, time_waiting, "#### ☀️ One Solar Panel (1.767 m x 1.041 m)",
                                              col7, solar_info),
                             compensation_bar(t_hydro, time_waiting,
                                              "#### 🌊 Water wheel Aare (2m x 1m)",
                                              col8, hydro_info))

        stop_flag = st.session_state.get("stop_flag", False)

        if stop_flag:
            st.stop()

    else:
        st.warning("Please select a product!")


##### INITIALIZE AND GET DATA #####
init_session_state()

conn = init_connection()

# Get data
product_data_df = get_data_from_db("""SELECT * FROM product_data WHERE emission != 0;""")
weather_data_df = get_data_from_db("""SELECT * FROM current_weather;""")
sun_hours = get_data_from_db("""SELECT * FROM sun_hours""")
hydro_data_df = get_data_from_db("""SELECT * FROM current_hydro_data ;""")

# Cleaning - Remove symbols in name that might disrupt filtering dropdown section
product_data_df['name'] = product_data_df['name'].apply(lambda x: x.replace("-", "").replace("/", "").replace("\\", ""))

# Create copy of data frame to also filter for category of product
product_filter_df = product_data_df.copy()


##### SIDEBAR #####

auto_background = st.sidebar.checkbox("Automatically change background based on current weather",
                                      value=True)
if auto_background:
    current_weather = weather_data_df['condition'].iloc[0]
    assign_weather_background(weather_condition=current_weather)

else:
    checkbox = st.sidebar.checkbox("Apply weather background",
                                   value=True)

    if checkbox:
        # Temporary to display
        weather = st.sidebar.selectbox("Choose weather to display",
                                       ['sun', 'covered', 'rain', 'snow'])
        assign_weather_background(weather_condition=weather)



##### APP #####

##### Lead section #####

st.markdown("# 💨 🌍 Contextualizing CO₂-Emissions")

# Read lead text
lead_text = read_markdown('assets/lead_text.md')

st.markdown(lead_text)

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



##### Filter categories #####

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

subcategory_filter = st.checkbox("Check to filter for specific subcategories")

if subcategory_filter:
    sorted_categories = sorted(product_data_df['detailed_category'].unique())
    sorted_categories.insert(0, "All subcategories")

    selected_subcategories: List[str] = st.multiselect("Select the subcategories you are interested in",
                                                    sorted_categories,
                                                    default="All subcategories")

    if "All subcategories" not in selected_subcategories:
        product_data_df = product_data_df[product_data_df['detailed_category'].isin(selected_subcategories)]

product_data_df = query_data(product_data_df)

if subcategory_filter:
    category_color_list, category_color_legend_list = create_color_list(product_data_df, 'detailed_category')
    filter_level = 'Subcategory'
else:
    category_color_list, category_color_legend_list = create_color_list(product_data_df, 'category')
    filter_level = 'Category'

product_fig = build_product_data_fig(product_data_df, category_color_list, level=filter_level)

legend_html = create_color_legend(category_color_legend_list, level=filter_level)

# Render the legend in Streamlit
st.markdown(legend_html, unsafe_allow_html=True)

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
choices = sorted([" - ".join(product) for product in product_zip])

product_choice = st.selectbox("Choose product", choices)

st.markdown("---")



##### Product metrics #####

if product_choice:
    selected_product = product_data_df[(product_data_df['name'] == product_choice.split(" - ")[0]) & \
                                       (product_data_df['price'] == float(
                                           product_choice.replace("CHF ", "").split(" - ")[2]))].iloc[0, :]
    st.markdown(f"### 📝 {selected_product['name']} ({selected_product['detailed_category']})")
    st.markdown("Please find below more detailed information about the product you selected.")
    st.markdown(f"Category: {selected_product['category']}")

    col3, col4 = st.columns(2)
    col3.metric("💰 Price:", f"CHF {selected_product['price']}0")
    col4.metric("💨 ♻️ Compensation Price:", f"CHF {selected_product['compensation_price']}")

    col5, col6 = st.columns(2)
    col5.metric("⚖️ Weight:", f"{selected_product['weight_gram'] / 1000} Kg")

    # Get delta emission of category or subcategory to product
    if filter_level == 'Subcategory':
        aggregation = 'detailed_category'
        filter_cat = 'subcat.'
    else:
        aggregation = 'category'
        filter_cat = 'category'

    cat = str(selected_product.loc[aggregation])
    cat_df = product_filter_df[product_filter_df[aggregation] == cat]
    avg_emission = cat_df['emission'].mean()
    delta_emission_pct = round(((selected_product['emission'] / avg_emission - 1) * 100), 1)
    high_or_low_text = "higher" if delta_emission_pct > 0 else "lower"
    delta_text = f"""{delta_emission_pct}% {high_or_low_text} to avg. in {filter_cat}"""

    col6.metric("💨 Emission:", f"{selected_product['emission']} Kg/CO₂",
                delta=delta_text,
                delta_color='inverse')

    emission: float = float(selected_product['emission'])

    emission_comparison_fig = build_product_comparison_fig(selected_product, cat_df)

    st.plotly_chart(emission_comparison_fig)

st.markdown("---")



##### Weather section #####

st.markdown("### 🌤️ 💧 Weather and Aare information")
st.markdown("Here is the current weather for Bern as well as the current Aare information.")

st.markdown("#### 🌦️ Current Weather in Bern")

col7, col8 = st.columns(2)

col7.metric("🌡️ Temperature:",
            f"{weather_data_df['TTT_C'].iloc[0]} °C")

sun_hours_today = round(sun_hours['sum'].iloc[0] / 60, 2)
col8.metric("☀️⌛ Sun hours",
            f"{sun_hours_today} hours")

st.markdown("#### 🌊 Aare water temperature and flow")

col9, col10 = st.columns(2)

col9.metric("🌡️ Temperature:",
            f"{hydro_data_df['aare_temp'].iloc[0]} °C")

current_water_flow = hydro_data_df['aare_flow'].iloc[0]
col10.metric("🌊 Water flow",
             f"{current_water_flow} m3/s")

st.markdown("---")



##### Time for compensation method #####

st.markdown("### ♻️⌛ How long does it take to compensate/offset for the emission?")

time_comp_lead_text = read_markdown('assets/offset_comparison_lead.md')
st.markdown(time_comp_lead_text)

button = st.button("See time needed per compensation method")

if button:
    stop_button = st.button("Stop time comparison", key="stop_button")
    if stop_button:
        st.stop()
    col5, col6 = st.columns(2)
    col7, col8 = st.columns(2)

    asyncio.run(async_main(sun_hours=sun_hours_today,
                           num_trees=1,
                           water_flow=current_water_flow))


st.markdown("---")



##### Compensation/offset method choice #####


st.markdown("### 🌳☀️🌊 How would you like to compensate for your product?")

chosen_method = st.selectbox("Choose the compensation method:",
                             ['Choose here', 'Trees', 'Solar', 'Hydro'])

if chosen_method == 'Trees':
    text = """
    ### 🌳 Plant Trees in Bern - CHF XY.-    
    Joining forces with company XYZ, planting trees in Bern becomes a 
    powerful solution to combat emissions and tackle climate change. 
    Together, we can reduce the city's carbon footprint, 
    create a greener environment, and build a sustainable future for Bern and beyond.
    """
    st.success(text)
    image = Image.open('images/trees.jpg')
    st.image(image, caption='Plant trees with company XYZ in Bern')

elif chosen_method == 'Solar':
    text = """
    ### ☀️ Fund a Solar Panel in Bern - CHF XY.- 
    Funding a solar panel in the Canton of Bern offers a sustainable 
    solution to harness clean energy and reduce reliance on fossil fuels. 
    By supporting solar initiatives, we can empower the community to embrace 
    renewable energy, lower carbon emissions, and pave the way for a greener future in the region.
    """
    st.success(text)
    image = Image.open('images/solar.jpg')
    st.image(image, caption='Fund solar panels in the canton of Bern')

elif chosen_method == 'Hydro':
    text = """
        ### 🌊 Fund Hydro Power in Bern (Mühleberg) - CHF XY.- 
        Bern is harnessing the power of water through hydro compensation, 
        a sustainable solution to offset carbon emissions. 
        By supporting hydro power projects, we can tap into the region's natural resources, 
        generate clean electricity, and contribute to a greener future. 
        Join us in supporting hydro compensation initiatives to create a more sustainable 
        and resilient energy landscape in Bern.
        """
    st.success(text)
    image = Image.open('images/hydro.jpeg')
    st.image(image, caption='Support the generation of hydro power in Mühleberg')

else:
    st.info("Please choose a compensation method")

if chosen_method in ['Trees', 'Solar', 'Hydro']:
    compensate_button = st.button(f"Yes, I want to compensate with the {chosen_method} option")

    if compensate_button:
        st.balloons()
        st.success("♻️ Thank you for choosing a compensation method to offset "
                   "the emissions of your product. By doing so, you are helping to make the "
                   "world a better place. We appreciate your efforts to reduce your carbon footprint!")


if __name__ == "__main__":
    pass
