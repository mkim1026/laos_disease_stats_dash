import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import gaussian_kde
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from utils import format_kpi_value
import json
import folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex

import plotly.figure_factory as ff
from scipy.stats import gaussian_kde

COLORS = ["#0081a7", "#00afb9", "#f07167", "#e9c46a",
          "#264653", "#f4a261", "#e76f51", "#ef233c", "#fed9b7",
          "#f6bd60", "#84a59d", "#f95738", "#fdfcdc"]


def plot_disease_pie_map(data):
    cutoff_date = datetime.today() - timedelta(days=100)
    data = data[data['reported_date'] >= cutoff_date]

    # data by province and disease
    province_disease = data.groupby(['province', 'disease_code'])['case'].sum().unstack().fillna(0)

    # total cases per province
    province_totals = province_disease.sum(axis=1)

    # unique diseases for color mapping
    diseases = province_disease.columns
    disease_colors = {disease: COLORS[i % len(COLORS)] for i, disease in enumerate(diseases)}

    # base map
    laos_coords = [18.0, 105.0]
    m = folium.Map(
        location=laos_coords,
        zoom_start=15,
        tiles='cartodbpositron',
    )

    # GeoJSON of Laos provinces
    with open("data/laos.geojson", "r") as f:
        laos_geojson = json.load(f)

    folium.GeoJson(
        laos_geojson,
        style_function=lambda x: {
            'fillColor': '#3186cc',
            'color': '#3186cc',
            'weight': 0,
            'fillOpacity': 0.3
        },
        name='Laos Boundary'
    ).add_to(m)

    #map bounds to Laos polygon coordinates
    coordinates = laos_geojson['geometry']['coordinates'][0]
    m.fit_bounds([[min(y for x, y in coordinates), min(x for x, y in coordinates)],
                  [max(y for x, y in coordinates), max(x for x, y in coordinates)]])

    #marker cluster for better handling of markers
    marker_cluster = MarkerCluster().add_to(m)

    # province centers
    province_centers = (
        data.groupby('province')
        .agg({'latitude': 'mean', 'longitude': 'mean'})
        .dropna()
        .to_dict('index')
    )

    max_total = province_totals.max()
    min_size = 80  # minimum pie radius in pixels
    max_size = 120  # maximum pie radius in pixels

    #pie charts for each province
    for province in province_disease.index:
        if province not in province_centers:
            continue

        lat = province_centers[province]['latitude']
        lon = province_centers[province]['longitude']
        total_cases = province_totals[province]

        #pie size based on total cases
        size = min_size + (max_size - min_size) * (total_cases / max_total)

        #pie chart data
        values = province_disease.loc[province].values

        # styled popup content
        popup_content = f"""
        <div style='font-family: Arial, sans-serif; width: 200px;'>
            <h4 style='margin-bottom: 5px; color: #333;'>{province}</h4>
            <p style='margin: 5px 0; font-weight: bold; font-size:12px;'>Total cases: {total_cases}</p>
            <hr style='margin: 8px 0; border-color: #eee;'>
        """

        for disease, value in zip(diseases, values):
            if value > 0:
                popup_content += f"""
                <p style='margin: 3px 0;'>
                    <span style='color: {disease_colors[disease]}; font-size:12px; font-weight: bold;'>■</span>
                    <span style='font-weight: bold; font-size:12px; color: {disease_colors[disease]};'>{disease}</span>: {value}
                </p>
                """

        popup_content += "</div>"

        #figure to hold the pie chart
        fig, ax = plt.subplots(figsize=(size/10, size/10))
        ax.pie(values,
               colors=[disease_colors[d] for d in diseases],
               wedgeprops={'linewidth': 0.5, 'edgecolor': 'white'})
        ax.axis('equal')

        # pie chart to a temporary file
        plt.savefig(f'assets/temp/temp_pie_{province}.png', transparent=True, dpi=100)
        plt.close()

        #marker with pie chart icon
        icon = folium.features.CustomIcon(f'assets/temp/temp_pie_{province}.png', icon_size=(size, size))
        folium.Marker(
            location=[lat, lon],
            icon=icon,
            popup=folium.Popup(popup_content, max_width=250)
        ).add_to(marker_cluster)

    return m


def plot_disease_outbreak_overtime(data, code_filter):
    data = data.sort_values('reported_date')
    data = data.set_index('reported_date')['case'].resample('ME').sum().reset_index()

    fig = go.Figure()

    x_vals = data['reported_date'].tolist()
    y_vals = data['case'].tolist()

    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers+lines+text',
        textposition="top center",
        text=data['case'],
        fill="tozeroy",
        line=dict(color="#00afb9"),
        fillcolor="rgba(0, 175, 185, 0.4)",
        name='Number of Cases',
        hovertext=data['case'],
        hoverinfo='name+text',
    ))

    fig = format_hover_layout(fig)
    fig.update_layout(
        title='Number of Cases Reported overtime',
        xaxis_title='Date',
        yaxis_title='Number of Cases',
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            range=[-1, max(y_vals)+2]  # set y-axis limit here
        ),
        legend=dict(orientation="h", xanchor='center', x=0.5, y=-0.25),
        height=350,

    )
    return fig



def format_hover_layout(fig):
    fig = fig.update_layout(
        height=400,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_color="black",
                        font_size=12, font_family="Rockwell"))
    return fig


COLORS = ["#0081a7", "#00afb9", "#f07167", "#e9c46a",
          "#264653", "#f4a261", "#e76f51", "#ef233c", "#fed9b7",
          "#f6bd60", "#84a59d", "#f95738", "#fdfcdc"]



def create_weather_map(weather_data, LAOS_REGIONS):
    """
    Create a map visualization of weather data
    """
    if not weather_data:
        return None

    # Prepare data for map
    regions = []
    temperatures = []
    humidity_values = []
    lats = []
    lons = []
    hover_texts = []

    for region, data in weather_data.items():
        if data:
            regions.append(region)
            temperatures.append(data['temperature'])
            humidity_values.append(data['humidity'])
            coords = LAOS_REGIONS[region]
            lats.append(coords['latitude'])
            lons.append(coords['longitude'])

            hover_text = f"""
            <b>{region}</b><br>
            Temperature: {data['temperature']:.1f}°C<br>
            Feels like: {data['feels_like']:.1f}°C<br>
            Humidity: {data['humidity']}%<br>
            Description: {data['description']}<br>
            Wind: {data['wind_speed']:.1f} m/s
            """
            hover_texts.append(hover_text)

    # Create map
    fig = go.Figure()

    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers+text',
        marker=dict(
            size=[max(10, temp + 20) for temp in temperatures],  # Size based on temperature
            color=temperatures,
            colorscale='RdYlBu_r',
            showscale=True,
            colorbar=dict(title="Temperature (°C)")
        ),
        text=[f"{temp:.1f}°C" for temp in temperatures],
        textposition="middle center",
        textfont=dict(size=10, color='white'),
        hovertemplate=hover_texts,
        hoverinfo='text',
        name='Weather Stations'
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=19.8563, lon=102.4955),  # Center of Laos
            zoom=6
        ),
        title="Weather Conditions Across Laos",
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    return fig


def create_weather_charts(weather_data):
    """
    Create temperature and humidity comparison charts using go.Figure
    """
    if not weather_data:
        return go.Figure(), go.Figure()

    regions = []
    temperatures = []
    humidity_values = []

    for region, data in weather_data.items():
        if data:
            regions.append(region)
            temperatures.append(data['temperature'])
            humidity_values.append(data['humidity'])

    # Normalize values for coloring
    temp_colors = np.interp(temperatures, (min(temperatures), max(temperatures)), (0, 1))
    humidity_colors = np.interp(humidity_values, (min(humidity_values), max(humidity_values)), (0, 1))

    # Temperature Figure
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Bar(
        x=regions,
        y=temperatures,
        text=[f"{t:.1f}°C" for t in temperatures],
        textposition='outside',
        marker=dict(
            color=temperatures,
            colorscale='RdYlBu_r',
            colorbar=dict(title='Temp (°C)')
        ),
        hovertemplate='Region: %{x}<br>Temperature: %{y}°C<extra></extra>',
        name='Temperature'
    ))
    temp_fig.update_layout(
        title='Temperature by Region (°C)',
        xaxis_title='Region',
        yaxis_title='Temperature (°C)',
        xaxis_tickangle=-45,
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        yaxis=dict(range=[0, max(temperatures) * 1.15])
    )
    temp_fig = format_hover_layout(temp_fig)

    # Humidity Figure
    humidity_fig = go.Figure()
    humidity_fig.add_trace(go.Bar(
        x=regions,
        y=humidity_values,
        text=[f"{h:.0f}%" for h in humidity_values],
        textposition='outside',
        marker=dict(
            color=humidity_values,
            colorscale='Blues',
            colorbar=dict(title='Humidity (%)')
        ),
        hovertemplate='Region: %{x}<br>Humidity: %{y}%<extra></extra>',
        name='Humidity'
    ))
    humidity_fig.update_layout(
        title='Humidity by Region (%)',
        xaxis_title='Region',
        yaxis_title='Humidity (%)',
        xaxis_tickangle=-45,
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        yaxis=dict(range=[0, 110])
    )
    humidity_fig = format_hover_layout(humidity_fig)

    return temp_fig, humidity_fig




def plot_key_disease_distribution(data):
    # total cases per disease code
    summary = data.groupby("disease_code")["case"].sum().reset_index()

    # Plot the pie chart
    fig = go.Figure(data=[go.Pie(
        labels=summary["disease_code"],
        values=summary["case"],
        hole=0.4,
        marker=dict(
            colors=COLORS[:len(summary)],
            line=dict(color="#fff", width=2)
        ),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Cases: %{value}<extra></extra>"
    )])

    fig.update_layout(
        title="Distribution of Key Disease",
        showlegend=True,
        legend=dict(orientation="h", xanchor='center', x=0.5, y=-0.25),
    )
    fig = format_hover_layout(fig)

    return fig


def key_disease_reports_overtime(data):
    data = data.sort_values('reported_date')
    data['reported_date'] = pd.to_datetime(data['reported_date'])

    pivot_df = (
        data.groupby(['reported_date', 'disease_code'])['case']
        .sum()
        .unstack(fill_value=0)
        .resample('ME')  # Monthly end
        .sum()
        .reset_index()
    )

    pivot_df.columns.name = None

    disease_codes = pivot_df.columns[1:]  # exclude date column

    cumulative = pivot_df[disease_codes].cumsum(axis=1)

    fig = go.Figure()

    for i, disease in enumerate(disease_codes):
        base = cumulative[disease_codes[i - 1]] if i > 0 else 0
        stacked_y = base + pivot_df[disease]

        fill_mode = 'tozeroy' if i == 0 else 'tonexty'

        fig.add_trace(go.Scatter(
            x=pivot_df['reported_date'],
            y=stacked_y,
            mode='lines',
            name=disease,
            fill=fill_mode,
            line=dict(width=0),
            hoverinfo='x+name+text',
            text=pivot_df[disease],
            fillcolor=COLORS[i % len(COLORS)]
        ))

    fig = format_hover_layout(fig)
    fig.update_layout(
        title='Stacked Disease Reports Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Cases',
        legend=dict(orientation="h", xanchor='center', x=0.5, y=-0.25),
        yaxis=dict(showticklabels=True),
        height=400
    )

    return fig


def key_disease_dist_overtime(data):
    data['reported_date'] = pd.to_datetime(data['reported_date'])
    data['year'] = data['reported_date'].dt.year

    grouped = (
        data.groupby(['year', 'disease_code'])['case']
        .sum()
        .reset_index()
    )

    pivot_df = grouped.pivot(index='year', columns='disease_code', values='case').fillna(0)

    fig = go.Figure()

    for i, disease in enumerate(pivot_df.columns):
        x_values = pivot_df.index.astype(str).tolist()
        y_values = pivot_df[disease].tolist()

        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            name=disease,
            marker_color=COLORS[i % len(COLORS)],
            orientation='v'
        ))

    fig.update_layout(
        barmode='group',
        title='Yearly Distribution of Disease Cases',
        xaxis_title='Year',
        yaxis_title='Number of Cases',
        xaxis_type='category',
        yaxis=dict(tickformat=',d'),
        legend=dict(orientation="h", xanchor='center', x=0.5, y=-0.25),
    )

    fig = format_hover_layout(fig)
    return fig




def key_disease_kde_distribution(data):
    data['reported_date'] = pd.to_datetime(data['reported_date'])
    disease_codes = data['disease_code'].unique()

    fig = go.Figure()

    for i, disease in enumerate(disease_codes):
        disease_data = data[data['disease_code'] == disease]['case']
        if len(disease_data) > 0:
            # Compute KDE
            kde = gaussian_kde(disease_data)
            x_vals = np.linspace(data['case'].min(), data['case'].max(), 200)
            y_vals = kde(x_vals)

            fig.add_trace(go.Scatter(
                x=x_vals.tolist(),
                y=y_vals.tolist(),
                mode='lines',
                name=disease,
                fill='tozeroy',
                line=dict(color=COLORS[i % len(COLORS)], width=2),
                opacity=0.6
            ))

    fig.update_layout(
        title='Probability Distribution of Key Diseases',
        xaxis_title='Number of Cases per Report',
        yaxis_title='Probability Density',
        legend_title='Disease',
        plot_bgcolor='white',
        hovermode='x unified',
    )

    fig = format_hover_layout(fig)
    return fig


def key_disease_wrt_location(data):
    grouped = (
        data.groupby(['province', 'disease_code'])['case']
        .sum()
        .reset_index()
    )

    pivot_df = grouped.pivot(index='province', columns='disease_code', values='case').fillna(0)

    fig = go.Figure()

    for i, disease in enumerate(pivot_df.columns):
        x_vals = pivot_df.index.tolist()
        y_vals = pivot_df[disease].tolist()

        fig.add_trace(go.Bar(
            x=x_vals,
            y=y_vals,
            name=disease,
            marker_color=COLORS[i % len(COLORS)],
        ))

    fig.update_layout(
        barmode='stack',
        title='Distribution of Disease Cases by Province',
        xaxis_title='Province',
        yaxis_title='Number of Cases',
        xaxis_type='category',
        legend=dict(orientation="h", xanchor='center', x=0.5, y=-0.25),
        height=450,
        plot_bgcolor='white'
    )

    fig = format_hover_layout(fig)
    return fig


def plot_disease_code_map(data):
    # Aggregate by location, disease_code, and coordinates
    grouped = (
        data.groupby(['location', 'disease_code', 'latitude', 'longitude'])['case']
        .sum()
        .reset_index()
    )

    fig = go.Figure()

    for i, disease in enumerate(grouped['disease_code'].unique()):
        df = grouped[grouped['disease_code'] == disease]

        fig.add_trace(go.Scattermapbox(
            lat=df['latitude'].tolist(),
            lon=df['longitude'].tolist(),
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=(df['case'] / df['case'].max() * 40 + 5).tolist(),  # scaled sizes
                color=COLORS[i % len(COLORS)],
                opacity=0.7
            ),
            text=(df['location'] + "<br>Cases: " + df['case'].astype(int).astype(str)).tolist(),
            name=disease,
            hoverinfo="text"
        ))

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            zoom=4.5,
            center=dict(
                lat=data['latitude'].mean(),
                lon=data['longitude'].mean()
            )
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        title="Disease Distribution Map",
        legend=dict(orientation="h", x=0.5, xanchor='center', y=-0.1),
        height=500
    )

    fig = format_hover_layout(fig)
    return fig


def disease_category_by_country(data):
    # Group and pivot the data
    grouped = (
        data.groupby(['Country', 'Category'])
        .size()
        .reset_index(name='Count')
        .pivot(index='Country', columns='Category', values='Count')
        .fillna(0)
    )

    grouped = grouped.sort_index()

    fig = go.Figure()

    for i, category in enumerate(['Wild', 'Domestic']):
        if category in grouped.columns:
            x_vals = grouped.index.tolist()
            y_vals = grouped[category].tolist()

            fig.add_trace(go.Bar(
                x=x_vals,
                y=y_vals,
                name=category,
                marker_color=COLORS[i % len(COLORS)],
            ))

    fig.update_layout(
        barmode='group',
        title='Wild vs Domestic Case Counts by Country',
        xaxis_title='Country',
        yaxis_title='Number of Cases',
        xaxis_type='category',
        height=500,
        plot_bgcolor='white',
        legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.2)
    )

    fig = format_hover_layout(fig)
    return fig



def present_diseases_chart(data):
    filtered_data = data[data['Disease status'] == 'Present']
    disease_counts = filtered_data['Disease'].value_counts().sort_values()

    fig = go.Figure(go.Bar(
        x=disease_counts.values,
        y=disease_counts.index,
        orientation='h',
        marker_color=COLORS[0 % len(COLORS)]
    ))

    fig.update_layout(
        title="Reported Disease Counts in Recent Years",
        xaxis_title="Number of Cases",
        yaxis_title=None,
        margin=dict(l=150, r=20, t=50, b=50),
        height=500
    )

    return fig
