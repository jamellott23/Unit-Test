#Section 1: Imports

import streamlit as st
import pandas as pd
import plotly.express as px

csv_file_path = 'vehicles_us.csv'

cars = pd.read_csv(csv_file_path)


#Section 2: Data Cleaning


#Dropping all duplicates excluding date posted and days listened
cars = cars.drop_duplicates(subset=[col for col in cars.columns if col not in ['date_posted', 'days_listed']])

#Adding a manufacturer column by taking the first word from the model column.
cars['manufacturer'] = cars['model'].apply(lambda x: x.split()[0])

#Filling in the blanks for model_year and odometer
cars['model_year'] = cars['model_year'].fillna(0).astype(int)
cars['odometer'] = cars['odometer'].fillna(0).astype(int)

#Changing the model year and odometer columns from float to int dtype.
cars['model_year'] = cars['model_year'].astype(int)
cars['odometer'] = cars['odometer'].astype(int)

#Filling the 4wd column with 0's for cars that don't have 4wd.
cars['is_4wd'] = cars['is_4wd'].fillna(0).astype(int)

#Deleting the handful of cars made before 1950 or with odometers over 600000 or prices over $79000 as the data there is suspicious.
cars = cars[cars['model_year'] >= 1950]
cars = cars[cars['odometer'] <= 600000]
cars = cars[cars['price'] <= 79000]

#Converting date_posted to datetime and then creating a year_posted column
cars['date_posted'] = pd.to_datetime(cars['date_posted'])
cars['year_posted'] = cars['date_posted'].dt.year

#Creating a car age column
cars['age'] = cars['year_posted'] - cars['model_year']

#Listing all blank paint colors as unknown
cars['paint_color'] = cars['paint_color'].fillna("unknown")

#Changing all types to lowercase
cars['type'] = cars['type'].str.lower()



#Section 3: Data Exploration and Visualization


#Histogram of Car Prices with Color Coded Transmission Type

color_mapping = {'automatic': 'blue', 'manual': 'orange'}

transmission_prices = px.histogram(
    cars,
    x='price',
    color='transmission',
    color_discrete_map=color_mapping,
    labels={'price': 'Price', 'transmission': 'Transmission'},
    title='Overlapping Histogram of Car Prices by Transmission Type',
    nbins=20)


#Model and Year Prices

#Grouping the cars by model and year, then finding the average price for each car and how many there are of each
average_prices = cars.groupby(['model', 'model_year'])['price'].agg(['mean', 'count']).reset_index()

#Renaming the columns
average_prices.rename(columns={'mean': 'average_price', 'count': 'car_count'}, inplace=True)

#Changing the average price column to int dtype
average_prices['average_price'] = average_prices['average_price'].astype(int)

#Deleting any cars that don't have at least 5 ads listed
average_prices = average_prices[average_prices['car_count'] >= 5]

#Expensive Cars DF
expensive_cars_average = average_prices.sort_values(by='average_price', ascending=False).head(100)


#A scatter plot of the most expensive 21st century cars listed for sale.

#Sorting for only 21st century cars
modern_expensive_cars_average = expensive_cars_average[expensive_cars_average['model_year'] > 1999]

#Allowing models to be color coded by making model category dtype
modern_expensive_cars_average.loc[:, 'model'] = modern_expensive_cars_average['model'].astype('category')

expensive_modern = px.scatter(
    modern_expensive_cars_average,
    x='model_year',
    y='average_price',
    color='model',
    labels={'model_year': 'Model Year', 'average_price': 'Average Price'},
    title='Scatter Plot: Most Expensive Modern Cars',
    hover_name='model',
    color_discrete_sequence=px.colors.qualitative.Set1,)


#Car Colors DF

#Grouping the cars by color and finding out how many there are of each and what the average price is.
car_colors = cars.groupby('paint_color').agg({'price': ['count', 'mean']}).reset_index()

#Renaming the columns
car_colors.columns = ['paint_color', 'car_count', 'average_price']


#Bar chart of average price by paint color.

color_mapping = {
    'blue': 'blue',
    'green': 'green',
    'black': 'black',
    'brown': 'saddlebrown',
    'grey': 'grey',
    'orange': 'orange',
    'purple': 'purple',
    'red': 'red',
    'silver': 'silver',
    'white': 'whitesmoke',
    'yellow': 'yellow',
    'unknown': 'lightskyblue',
    'custom': 'gold'}

#Changing the order to be more readable
paint_color_order = ['red', 'blue', 'green', 'yellow', 'orange', 'brown', 'purple', 'black', 'white', 'silver', 'grey', 'custom', 'unknown']


paint_colors = px.bar(car_colors, x='paint_color', y='average_price',
             color='paint_color', color_discrete_map=color_mapping,
             title='Average Price by Paint Color',
             labels={'paint_color': 'Paint Color', 'average_price': 'Average Price'},
             category_orders={'paint_color': paint_color_order})


#4WD DF

#Getting the average price by car with and without 4wd.
is_4wd_counts = cars.groupby(['model', 'is_4wd']).agg({'price': ['count', 'mean']}).reset_index()

is_4wd_counts.columns = ['model', 'is_4wd', 'car_count', 'average_price']

with_4wd = is_4wd_counts[is_4wd_counts['is_4wd'] == 1].reset_index(drop=True)
without_4wd = is_4wd_counts[is_4wd_counts['is_4wd'] == 0].reset_index(drop=True)

#Merging the df's on the 'model' column
cars_4wd_final = pd.merge(with_4wd, without_4wd, on='model', suffixes=('_4wd', '_no_4wd'))

#Deleting any models that don't have at least 3 cars with 4wd and 10 cars total
cars_4wd_final = cars_4wd_final[(cars_4wd_final['car_count_4wd'] + cars_4wd_final['car_count_no_4wd']) >= 10]
cars_4wd_final = cars_4wd_final[cars_4wd_final['car_count_4wd'] >= 3]

#Calculating the difference in price between cars with 4wd and without
cars_4wd_final['price_difference'] = cars_4wd_final['average_price_4wd'] - cars_4wd_final['average_price_no_4wd']


#Shows the difference in price between each car model that had 4wd as an option. Average price differential is $2,775 dollars.

_4wd_difference = px.bar(cars_4wd_final, x='model', y='price_difference',
             color_discrete_map={'is_4wd_4wd': 'blue', 'is_4wd_no_4wd': 'orange'},
             title='Price Difference by Model (4WD vs. No 4WD)',
             labels={'price_difference': 'Price Difference', 'model': 'Car Model'},)



#A scatterplot showing the price of cars versus their age, color coded by condition

#Changing the legend order to go from salvage to new
condition_order = ['salvage', 'fair', 'good', 'excellent', 'like new', 'new']

scatter_condition = px.scatter(cars, x='age', y='price', color='condition',
                 color_discrete_map={'excellent': 'blue', 'good': 'green', 'fair': 'orange', 'like new': 'purple', 'new': 'red', 'salvage': 'black'},
                 title='Scatter Plot of Car Prices by Age and Condition',
                 labels={'age': 'Age', 'price': 'Price', 'condition': 'Condition', 'model': 'Model'},
                 category_orders={'condition': condition_order},
                 hover_data={'model': True})


# Creating a line chart looking at how each manufacturer maintains its value over time

#Grouping the cars by manufacturer and year and getting the average price and count for each
average_manuf_prices = cars.groupby(['manufacturer', 'model_year'])['price'].agg(['mean', 'count']).reset_index()

# Convert manufacturer names to the desired format
average_manuf_prices['manufacturer'] = average_manuf_prices['manufacturer'].apply(
    lambda x: 'GMC' if x == 'GMC' else x.title())

# Getting rid of cars before 1990 and over $40000 because the data isn't very interesting and gets into classics
average_manuf_prices_90 = average_manuf_prices[(average_manuf_prices['model_year'] >= 1990) & (average_manuf_prices['mean'] <= 40000)]

color_scale = px.colors.qualitative.Set1

man_mean_90 = px.scatter(average_manuf_prices_90, x='model_year', y='mean', color='manufacturer',
                 title='Average Price by Manufacturer and Model Year',
                 labels={'model_year': 'Model Year', 'mean': 'Average Price', 'manufacturer': 'Manufacturer'},
                 color_discrete_sequence=color_scale,
                 hover_data={'manufacturer': True, 'count': True, 'mean': True},
                 custom_data=['mean'],
                 trendline='lowess')


#One more but set to 2010 to get a better look at newer car's pricing.

average_manuf_prices_10 = average_manuf_prices[average_manuf_prices['model_year'] >= 2010]

color_scale = px.colors.qualitative.Set1

man_mean_10 = px.scatter(average_manuf_prices_10, x='model_year', y='mean', color='manufacturer',
                 title='Average Price by Manufacturer and Model Year',
                 labels={'model_year': 'Model Year', 'mean': 'Average Price', 'manufacturer': 'Manufacturer'},
                 color_discrete_sequence=color_scale,
                 hover_data={'manufacturer': True, 'count': True, 'mean': True},
                 custom_data=['mean'],
                 trendline='lowess')





#Section 4: Streamlit Web Dashboard

st.markdown(
    "<h1 style='text-align: center; color: #3498db; font-family: Arial, sans-serif;'>Jessiah's TripleTen Software Development Tools Unit Test</h1>",
    unsafe_allow_html=True,)


#Adding an image just to try it

st.image("me.jpeg", caption="Me", use_column_width=True)
st.markdown(
    "<h1 style='text-align: center; color: #3498db; font-family: Arial, sans-serif;'>Car Sales Dataframe (Sample)</h1>",
    unsafe_allow_html=True,)

st.write(cars.sample(200), height=300)

st.plotly_chart(transmission_prices)

st.plotly_chart(expensive_modern)

st.plotly_chart(paint_colors)

st.plotly_chart(_4wd_difference)


#Providing Tabs to see the manufacturer averages from '90 on and '10 on

tab1, tab2 = st.tabs(["Manufacturer Avg Prices After 1990", "Manufacturer Avg Prices After 2010"])
with tab1:
    st.plotly_chart(man_mean_90, theme="streamlit", use_container_width=True)
with tab2:
    st.plotly_chart(man_mean_10, theme="streamlit", use_container_width=True)


#A scatterplot showing the price of cars versus their age, color coded by condition, with checkbox

#Changing the legend order to go from salvage to new
condition_order = ['salvage', 'fair', 'good', 'excellent', 'like new', 'new']

# Checkbox to show/hide conditions
show_conditions = st.checkbox("Select Conditions", value=True)

# Scatter plot
scatter_condition = px.scatter(cars, x='age', y='price', color='condition',
                               color_discrete_map={'excellent': 'blue', 'good': 'green', 'fair': 'orange', 'like new': 'purple', 'new': 'red', 'salvage': 'black'},
                               title='Scatter Plot of Car Prices by Age and Condition',
                               labels={'age': 'Age', 'price': 'Price', 'condition': 'Condition', 'model': 'Model'},
                               category_orders={'condition': condition_order},
                               hover_data={'model': True})

# Apply condition based on checkbox
if not show_conditions:
    scatter_condition.update_traces(visible='legendonly')

# Display the scatter plot
st.plotly_chart(scatter_condition)

