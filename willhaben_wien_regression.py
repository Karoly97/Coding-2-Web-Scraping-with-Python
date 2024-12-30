import pandas as pd
import plotly.express as px
from sklearn.preprocessing import PolynomialFeatures
import numpy as np

# Load the dataset
file_path = 'cleaned_properties_with_price_per_m2.csv'
data = pd.read_csv(file_path)

# Step 1: Prepare the data
# Drop rows with missing values and limit Size to 400 m²
data = data.dropna(subset=['Size', 'Price/m2'])
data = data[data['Size'] <= 400]

# Step 2: Define clusters based on Price/m²
def classify_price(price):
    if price > 10000:  # Threshold for luxury
        return 'Luxury'
    elif price < 5000:  # Threshold for affordable
        return 'Affordable'
    else:
        return 'Mid-range'

data['Cluster'] = data['Price/m2'].apply(classify_price)

# Step 3: Scatter plot with polynomial regression lines
fig = px.scatter(
    data,
    x='Size',
    y='Price/m2',
    color='Cluster',
    title="Property Prices by Size and Cluster",
    labels={'Size': 'Size (m²)', 'Price/m2': 'Price per m² (€)', 'Cluster': 'Category'},
    hover_data=['Postcode']
)

# Step 4: Add polynomial regression lines for each cluster
# Fit polynomial regression models for each cluster
clusters = data['Cluster'].unique()
regression_lines = []

for cluster in clusters:
    cluster_data = data[data['Cluster'] == cluster]
    X = cluster_data[['Size']].values
    y = cluster_data['Price/m2'].values

    if len(cluster_data) > 1:  # Fit regression if enough data points exist
        poly = PolynomialFeatures(degree=2, include_bias=False)
        X_poly = poly.fit_transform(X)

        model = LinearRegression()
        model.fit(X_poly, y)
        regression_lines.append({
            'Cluster': cluster,
            'Coefficients': model.coef_,
            'Intercept': model.intercept_,
            'Poly': poly
        })

# Add polynomial regression lines to the scatter plot
x_range = np.linspace(0, 250, 300).reshape(-1, 1)
for line in regression_lines:
    y_range = line['Poly'].transform(x_range) @ line['Coefficients'] + line['Intercept']
    fig.add_scatter(
        x=x_range.flatten(),
        y=y_range,
        mode='lines',
        name=f"{line['Cluster']} Trendline",
        line=dict(dash='dash')
    )

# Customize layout for better visibility
fig.update_layout(
    plot_bgcolor='white',
    xaxis=dict(
        gridcolor='lightgray',
        title="Property Size (m²)"
    ),
    yaxis=dict(
        gridcolor='lightgray',
        title="Price per m² (€)"
    ),
    legend=dict(
        title="Cluster",
        bordercolor="black",
        borderwidth=1
    ),
    title=dict(
        x=0.5,  # Center the title
        font=dict(size=20)
    ),
    margin={"r": 0, "t": 50, "l": 50, "b": 50}
)

fig.show()
