import plotly.express as px
from ipywidgets import interact, Dropdown

# Function to create a bar chart for the top 5 districts
def create_bar_chart(column):
    top_districts = stats.nlargest(5, column)
    top_districts = top_districts[top_districts['District'].notna()]

    # If fewer than 5 rows, fill in additional districts
    if len(top_districts) < 5:
        remaining_districts = stats[~stats['District'].isin(top_districts['District']) & stats['District'].notna()]
        additional_districts = remaining_districts.nlargest(5 - len(top_districts), column)
        top_districts = pd.concat([top_districts, additional_districts])

    # Debug: Print the top 5 districts to verify selection
    print(f"Top 5 districts for {column}:\n", top_districts)

    # Create the bar chart
    fig = px.bar(
        top_districts,
        x='District',
        y=column,
        title=f"Top 5 Districts by {'Mean' if column == 'Mean_Price_m2' else 'Median'} Price per m² (in €)",
        labels={'District': 'District', column: 'Price per m² (€)'}
    )

    # Customize the layout
    fig.update_layout(
        xaxis_title='District',
        yaxis_title='Price per m² (€)',
        yaxis=dict(range=[0, 20000]),  # Adjust scale if necessary
        margin={"r": 0, "t": 50, "l": 50, "b": 50},
        plot_bgcolor='white',  
        paper_bgcolor='white', 
        showlegend=False
    )

    # Add euro/m² labels on the bars at the bottom
    fig.update_traces(
        text=[f"€{int(price):,}" for price in top_districts[column]],
        textposition='inside',  
        textfont=dict(
            size=12,
            color='white', 
            family='Arial',
            weight='bold' 
        )
    )

    fig.show()

# Interactive dropdown for bar chart
def interactive_bar(view):
    create_bar_chart(view)

dropdown_bar = Dropdown(
    options=[
        ('Median Price/m²', 'Median_Price_m2'),
        ('Mean Price/m²', 'Mean_Price_m2')
    ],
    value='Median_Price_m2',
    description='Bar Chart View:',
    style={'description_width': 'initial'}
)

interact(interactive_bar, view=dropdown_bar)
