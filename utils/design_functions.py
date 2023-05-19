import streamlit as st


def style_columns():
    """
    Apply white border with black background to
    st.columns()
    """
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
    return st.markdown(f'<style>{custom_style_async_cols}</style>', unsafe_allow_html=True)


def assign_weather_background(weather_condition: str):
    """
    Changes background based on weather
    """

    if weather_condition == 'rain':
        url = "https://images.unsplash.com/photo-1620385019253-b051a26048ce?ixlib=rb-4.0.3&ixid" \
              "=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80"
    elif weather_condition == 'sun':
        url = "https://images.unsplash.com/photo-1559628376-f3fe5f782a2e?ixlib=rb-4.0.3&ixid" \
              "=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=862&q=80"
    elif weather_condition == 'covered':
        url = "https://images.unsplash.com/photo-1500740516770-92bd004b996e?ixlib=rb-4.0.3&ixid" \
              "=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1472&q=80"
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