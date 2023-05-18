import colorsys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List

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
                                           '<br>Sub-category: %{customdata[3]}'
                                           '<br>Price: CHF %{customdata[1]:,.2f}'
                                           '<br>Weight: %{y:,} gram'
                                           '<br>Emission: %{x}'
                                           '<extra></extra>',
                             customdata=list(zip(df['name'], df['price'], df['category'], df['detailed_category']))
                             ))

    fig.update_layout(
        title="Emission vs Weight of products (color indicate different category)",
        xaxis_title="Emission",
        yaxis_title="Weight (gram)",
        template='plotly_dark'
    )

    return fig


def build_product_comparison_fig(selected_product_series: pd.Series, category_df: pd.DataFrame):
    """
    Create px.bar figure of selected product compared to other products in category.
    """

    category = category_df['category'].iloc[0]
    title = f'💨🎨 Emission Comparison of your product in {category}'

    # Create category dataframe
    selected_product_df = pd.DataFrame(selected_product_series).transpose()
    selected_product_df['selected'] = "Your Product"
    category_df['selected'] = "Other Product"

    selected_category_df = pd.concat([selected_product_df, category_df])

    # Drop selected product duplicate out of category_df
    selected_category_df.drop_duplicates(subset=['name', 'price', 'category',
                                                 'emission', 'compensation_price',
                                                 'weight_gram'], inplace=True)

    # Sort values and create unique product name for separate plotting
    selected_category_df.sort_values(by='emission', ascending=True, inplace=True)
    selected_category_df['product_name'] = selected_category_df.apply(lambda row: f"{row['name']}-{row['selected']}"
                                                                                  f"-{row['price']}-{row['emission']}"
                                                                                  f"-{row['compensation_price']}-"
                                                                                  f"{row['weight_gram']}", axis=1)


    sorted_product_names = selected_category_df['product_name'].unique().tolist()

    emission_comparison_fig = px.bar(selected_category_df,
                                     x='product_name',
                                     y='emission',
                                     color='selected',
                                     color_discrete_sequence=['darkseagreen', 'coral'],
                                     custom_data=['price', 'category', 'detailed_category'],
                                     title=title,
                                     category_orders={'product_name': sorted_product_names}
                                     )

    emission_comparison_fig.update_traces(hovertemplate='<br>Category: %{customdata[1]}'
                                                        '<br>Sub-category: %{customdata[2]}'
                                                        '<br>Price: CHF %{customdata[0]:,.2f}'
                                                        '<br>Emission: %{y} Kg/CO₂'
                                                        '<extra></extra>')

    emission_comparison_fig.update_layout(
        xaxis_title='',
        xaxis=dict(
            tickmode='array',
            tickvals=selected_category_df['product_name'].to_list(),
            ticktext=selected_category_df['name'].to_list()
        ),
        yaxis_title='Emission in Kg/CO₂',
        hovermode='x unified',
        title_x=0.1)

    return emission_comparison_fig