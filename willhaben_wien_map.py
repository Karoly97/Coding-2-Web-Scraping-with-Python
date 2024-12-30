import pandas as pd
import plotly.express as px
import json
from ipywidgets import Dropdown, interact

# Load datasets
data = pd.read_csv('cleaned_properties_with_price_per_m2.csv')
with open('vienna.geojson', 'r') as f:
    vienna_geojson = json.load(f)

# Map district names to postal codes
district_to_postcode = {
    "Innere Stadt": "1010", "Leopoldstadt": "1020", "Landstraße": "1030",
    "Wieden": "1040", "Margareten": "1050", "Mariahilf": "1060",
    "Neubau": "1070", "Josefstadt": "1080", "Alsergrund": "1090",
    "Favoriten": "1100", "Simmering": "1110", "Meidling": "1120",
    "Hietzing": "1130", "Penzing": "1140", "Rudolfsheim-Fünfhaus": "1150",
    "Ottakring": "1160", "Hernals": "1170", "Währing": "1180",
    "Döbling": "1190", "Brigittenau": "1200", "Floridsdorf": "1210",
    "Donaustadt": "1220", "Liesing": "1230"
}

# Add properties to GeoJSON
for feature in vienna_geojson['features']:
    district_name = feature['properties']['name']
    feature['properties']['Postcode'] = district_to_postcode.get(district_name)
    feature['properties']['District'] = district_name

# Aggregate property data
stats = data.groupby('Postcode').agg(
    Median_Price_m2=('Price/m2', 'median'),
    Mean_Price_m2=('Price/m2', 'mean'),
    Observations=('Price/m2', 'count')
).reset_index()

# Prepare data for merging
stats['Postcode'] = stats['Postcode'].astype(str)
geojson_data = pd.DataFrame([
    {'Postcode': feature['properties']['Postcode'], 'District': feature['properties']['District']}
    for feature in vienna_geojson['features']
])
geojson_data['Postcode'] = geojson_data['Postcode'].astype(str)

# Merge stats with GeoJSON data
stats = stats.merge(geojson_data, on='Postcode', how='left')

# Round prices and add formatted columns for hover data
stats[['Median_Price_m2', 'Mean_Price_m2']] = stats[['Median_Price_m2', 'Mean_Price_m2']].round(0).astype(int)
stats['Median Price (price/m²)'] = stats['Median_Price_m2'].apply(lambda x: f"{x} €")
stats['Mean Price (price/m²)'] = stats['Mean_Price_m2'].apply(lambda x: f"{x} €")

# Create choropleth map
def create_map(color_column):
    max_val = 16000
    min_val = stats[color_column].min()

    hover_data = {
        'District': True,
        'Observations': True,
        'Median Price (price/m²)': True if color_column == 'Median_Price_m2' else False,
        'Mean Price (price/m²)': True if color_column == 'Mean_Price_m2' else False,
        color_column: False  # Exclude the raw column used for coloring
    }

    fig = px.choropleth(
        stats, geojson=vienna_geojson, locations='Postcode',
        featureidkey='properties.Postcode', color=color_column,
        color_continuous_scale="Blues", range_color=[min_val, max_val],
        title=f"Vienna Property Prices ({'Mean' if color_column == 'Mean_Price_m2' else 'Median'}) per m²",
        hover_data=hover_data
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        coloraxis_colorbar=dict(title=None),
        margin={"r": 0, "t": 50, "l": 0, "b": 90},
        annotations=[dict(
            x=0.5, y=-0.15, showarrow=False, text="This map shows property prices per m² in Vienna. Hover over districts for details.",
            xref="paper", yref="paper", align="center", font=dict(size=12)
        )]
    )
    fig.show()

# Interactive dropdown for map
def interactive_map(view):
    create_map(view)

interact(interactive_map, view=Dropdown(
    options=[('Median Price/m²', 'Median_Price_m2'), ('Mean Price/m²', 'Mean_Price_m2')],
    value='Median_Price_m2', description='Map View:', style={'description_width': 'initial'}
))
