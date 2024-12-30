import os
import pandas as pd

# Define the file path dynamically based on the current working directory
current_directory = os.getcwd()
file_path = os.path.join(current_directory, 'scraped_properties.csv')

# Detect delimiter and load the dataset
with open(file_path, 'r') as file:
    first_line = file.readline()
    delimiter = ',' if ',' in first_line else (';' if ';' in first_line else '\t')

# Load the dataset
data = pd.read_csv(file_path, delimiter=delimiter, on_bad_lines='skip')

# Clean the data
data = data.dropna(subset=['Size', 'Price', 'Postcode'])
data['Size'] = data['Size'].str.replace(r'\D+', '', regex=True).astype(int)

# Modify the Price column to remove numbers after the comma
data['Price'] = data['Price'].str.replace(r',(\d+)$', '', regex=True)

# Remove all non-digit characters for numerical processing
data['Price'] = data['Price'].str.replace(r'\D+', '', regex=True).astype(int)

# Remove outliers based on the 2nd and 98th percentiles
size_lower_bound = data['Size'].quantile(0.02)
size_upper_bound = data['Size'].quantile(0.98)
price_lower_bound = data['Price'].quantile(0.02)
price_upper_bound = data['Price'].quantile(0.98)

data = data[
    (data['Size'] >= size_lower_bound) & 
    (data['Size'] <= size_upper_bound) & 
    (data['Price'] >= price_lower_bound) & 
    (data['Price'] <= price_upper_bound)
]

# Calculate Price/m2
data['Price/m2'] = data['Price'] / data['Size']

# Save the cleaned data dynamically to the same directory
cleaned_file_path = os.path.join(current_directory, 'cleaned_properties_with_price_per_m2.csv')
data.to_csv(cleaned_file_path, index=False)

# Display a preview of the cleaned data
print("Cleaned Data Preview:")
print(data.head())
