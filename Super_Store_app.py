import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import datetime
import os
import requests
import warnings
warnings.filterwarnings('ignore')

############################
## Web App Setup
############################

## Setting up the page
st.set_page_config(page_title="Store Report Dashboard",
                   page_icon=":bar_chart:",
                   layout="wide")


## Title of dashboard
st.title(" :bar_chart: Office Odyssey KPI Dashboard")

css_url = 'https://raw.githubusercontent.com/mschemick/OfficeOddessy/main/superstore.css'
css_response = requests.get(css_url)

# Check if the request was successful (status code 200)
if css_response.status_code == 200:
    css_code = f'<style>{css_response.text}</style>'
    st.markdown(css_code, unsafe_allow_html=True)
else:
    st.warning(f"Failed to load CSS from {css_url}")

## Page Layout
col1, col2, col3, col4, = st.columns ((4))
col5, col6 = st.columns ((2))
col7, _ = st.columns((32,1))
col12, _ = st.columns((42,1))
col8, col10 = st.columns((2))
col11, col13 = st.columns((2))


## Loading in the Dataset

df = pd.read_csv("Super_Store.csv", encoding=('ISO-8859-1'), low_memory=False)

###################################
## Creating SideBar
###################################
## Company logo

st.sidebar.image("https://github.com/mschemick/OfficeOddessy/blob/main/Office_oasis4.jpg?raw=true", width=120)


## Sidebar Title
st.sidebar.title('Choose KPI')

Select_option = st.sidebar.radio('select option', ('Sales', 'Profit'), key="radio_buttons", format_func=lambda x: x)

## SideBar 2nd Title

st.sidebar.title('Parameters')

## Filter Options

all_option = 'All'

## Region filter
Selected_region = st.sidebar.selectbox('Select Region', [all_option] + list(df['Region'].unique()), index=0)

## State filter
if Selected_region != all_option:
     Selected_state = [all_option] + list(df[df['Region'] == Selected_region]['State'].unique())
else:
     Selected_state = [all_option] + list(df['State'].unique())

Selected_state = st.sidebar.selectbox('Select State', Selected_state, index=0, key='state_selector')

## City filter
if Selected_state != all_option:
     Selected_city = [all_option] + list(df[df['State'] == Selected_state]['City'].unique())
else:
     Selected_city = [all_option] + list(df['City'].unique())

Selected_city = st.sidebar.selectbox('Select City', Selected_city, index=0, key='City_selector')

## Category filter
Selected_Category = st.sidebar.selectbox('Select Category', [all_option] + list(df['Category'].unique()), index=0)

## Sub_Category filter
if Selected_Category != all_option:
     Selected_Sub_Category = [all_option] + list(df[df['Category'] == Selected_Category]['Sub-Category'].unique())
else:
     Selected_Sub_Category = [all_option] + list(df['Sub-Category'].unique())

Selected_Sub_Category = st.sidebar.selectbox('Select Sub Category', Selected_Sub_Category, index=0, key='Sub_Category_Selector')

## Product filter
if Selected_Sub_Category != all_option:
    Selected_Product = [all_option] + list(df[df['Sub-Category'] == Selected_Sub_Category]['Product_Name'].unique())
    
    if Selected_state != all_option:
        if Selected_city != all_option:
            Selected_Product = [all_option] + list(df[(df['Sub-Category'] == Selected_Sub_Category) & 
                                       (df['State'] == Selected_state) &
                                       (df['City'] == Selected_city)]['Product_Name'].unique())
        else:
            Selected_Product = [all_option] + list(df[(df['Sub-Category'] == Selected_Sub_Category) & 
                                       (df['State'] == Selected_state)]['Product_Name'].unique())
else:
    
    if Selected_state != all_option:
        if Selected_city != all_option:
            Selected_Product = [all_option] + list(df[(df['State'] == Selected_state) &
                                       (df['City'] == Selected_city)]['Product_Name'].unique())
        else:
            Selected_Product = [all_option] + list(df[df['State'] == Selected_state]['Product_Name'].unique())
    else:
        Selected_Product = [all_option] + list(df['Product_Name'].unique())

Selected_Product = st.sidebar.selectbox('Select Product', Selected_Product, index=0, key='Product_selector')

##############################
## Time and Days of Week graphs
###############################


## Convert to date time
df["order_Date"] = pd.to_datetime(df["Order_Date"])

## Getting Min and Max Dates

startdate = pd.to_datetime(df["Order_Date"]).min()
enddate = pd.to_datetime(df["Order_Date"]).max()

with col5:
    date1 = pd.to_datetime(st.date_input("Start Date", startdate))
with col6:
    date2 = pd.to_datetime(st.date_input("End Date", enddate))

## Convert Order_Date to Date
df['Order_Date'] = pd.to_datetime(df['Order_Date'])

## Set the ranges and filtered data
filtered_data = df[
    (df['City'] == Selected_city if Selected_city != all_option else True) &
    (df['State'] == Selected_state if Selected_state != all_option else True) &
    (df['Region'] == Selected_region if Selected_region != all_option else True) &
    (df['Category'] == Selected_Category if Selected_Category != all_option else True) &
    (df['Sub-Category'] == Selected_Sub_Category if Selected_Sub_Category != all_option else True) &
    (df['Product_Name'] == Selected_Product if Selected_Product != all_option else True) &
    (df["Order_Date"] >= pd.Timestamp(date1)) &
    (df["Order_Date"] <= pd.Timestamp(date2))
].copy()

with col7:
    if not filtered_data.empty:
        if Select_option == 'Sales':
              st.title('Sales Over Time')
              chart_data = filtered_data.set_index('Order_Date')['Sales']
        else:
             st.title('Profit Over Time')
             chart_data = filtered_data.set_index('Order_Date')['Profit']


        # Display the line chart
        st.line_chart(chart_data)
    else:
        st.write('No data available for this selection')

## Days of week chart - Sales
        
total_sales_dow = filtered_data.groupby('Days_of_week')['Sales'].sum().reset_index()
df_sales_by_dow = pd.DataFrame(total_sales_dow)
df_sales_by_dow.columns = ['Days_of_week', 'Total_Sales']

x_values = df_sales_by_dow['Days_of_week']
bar_data = df_sales_by_dow['Total_Sales']
fig_dow = px.bar(filtered_data, y=bar_data, x=x_values, labels={'x': 'Days of Week', 'y': Select_option}, width=1100, height=500)

fig_dow.update_layout(xaxis_categoryorder='array', xaxis_categoryarray=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday','Friday','Saturday'])

## Days of week chart - Profit

total_profit_dow = filtered_data.groupby('Days_of_week')['Profit'].sum().reset_index()
df_profit_by_dow = pd.DataFrame(total_profit_dow)
df_profit_by_dow.columns = ['Days_of_week', 'Total_Profit']

x_values = df_profit_by_dow['Days_of_week']
bar_data = df_profit_by_dow['Total_Profit']
fig_dow2 = px.bar(filtered_data, y=bar_data, x=x_values, labels={'x': 'Days of Week', 'y': Select_option}, width=1100, height=500)

fig_dow2.update_layout(xaxis_categoryorder='array', xaxis_categoryarray=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday','Friday','Saturday'])

## Inputing days of week chart
with col12:
    if not filtered_data.empty:
        if Select_option == 'Sales':
              st.title('Sales Per Days of Week')
              st.plotly_chart(fig_dow)
        else:
             st.title('Profit Per Days of Week')
             st.plotly_chart(fig_dow2)

###################################
## Location Chart and table
###################################


## Create new dataframes for total sales
total_sales_by_state = filtered_data.groupby('State')['Sales'].sum().reset_index()
df_sales_by_state = pd.DataFrame(total_sales_by_state)
df_sales_by_state.columns = ['State', 'Total_Sales']

total_sales_by_region = filtered_data.groupby('Region')['Sales'].sum().reset_index()
df_sales_by_region = pd.DataFrame(total_sales_by_region)
df_sales_by_region.columns = ['region', 'Total_Sales']

total_sales_by_city = filtered_data.groupby('City')['Sales'].sum().reset_index()
df_sales_by_city = pd.DataFrame(total_sales_by_city)
df_sales_by_city.columns = ['city', 'Total_Sales']


## Sales Parameter
x_values = df_sales_by_state['State']
bar_data = df_sales_by_state['Total_Sales']
fig_state = px.bar(filtered_data, y=x_values, x=bar_data, labels={'y': 'State', 'x': Select_option}, title=f'{Select_option} by State', width=500, height=500)

fig_state.update_layout(
    title=dict(font=dict(size=24)))

x_city = df_sales_by_city['city']
bar_data = df_sales_by_city['Total_Sales']
fig_city = px.bar(filtered_data, y=x_city, x=bar_data, labels={'y': 'city', 'x': Select_option}, title=f'{Select_option} by City', width=500, height=500)

fig_city.update_layout(
    title=dict(font=dict(size=24)))

x_region = df_sales_by_region['region']
bar_data = df_sales_by_region['Total_Sales']
fig_region = px.bar(filtered_data, y=x_region, x=bar_data, labels={'y': 'region', 'x': Select_option}, title=f'{Select_option} by Region', width=500, height=500)

fig_region.update_layout(
    title=dict(font=dict(size=24)))

selected_city2 = filtered_data[filtered_data['City'] == Selected_city]

if not selected_city2.empty:
    selected_Per_city = selected_city2['Sales'].values[0] / filtered_data['Sales'].sum() * 100
    other_per = 100 - selected_Per_city
    fig_pie_sales = px.pie(values=[selected_Per_city, other_per], names=[Selected_city, 'Other Cities'],
                           title=f'Sales Distribution for {Selected_city} vs Other Cities in State')
else:
    # Handle the case when selected_city2 is empty
    fig_pie_sales = px.pie(values=[0, 100], names=['No Sales Data', 'Other Cities'],
                           title=f'No Sales Data for {Selected_city}')

## Creating dataframes for profit

total_profit_by_state = filtered_data.groupby('State')['Profit'].sum().reset_index()
df_profit_by_state = pd.DataFrame(total_profit_by_state)
df_profit_by_state.columns = ['State', 'Total_Profit']

total_profit_by_region = filtered_data.groupby('Region')['Profit'].sum().reset_index()
df_profit_by_region = pd.DataFrame(total_profit_by_region)
df_profit_by_region.columns = ['region', 'Total_Profit']

total_profit_by_city = filtered_data.groupby('City')['Profit'].sum().reset_index()
df_profit_by_city = pd.DataFrame(total_profit_by_city)
df_profit_by_city.columns = ['city', 'Total_Profit']


## Profit Parameter
x_values = df_profit_by_state['State']
bar_data = df_profit_by_state['Total_Profit']
fig_state2 = px.bar(filtered_data, y=x_values, x=bar_data, labels={'y': 'State', 'x': Select_option}, title=f'{Select_option} by State in {Selected_region} Region', width=500, height=500)

fig_state2.update_layout(
    title=dict(font=dict(size=24)))

x_city = df_profit_by_city['city']
bar_data = df_profit_by_city['Total_Profit']
fig_city2 = px.bar(filtered_data, y=x_city, x=bar_data, labels={'y': 'city', 'x': Select_option}, title=f'{Select_option} by City in {Selected_state}', width=500, height=500)

fig_city2.update_layout(
    title=dict(font=dict(size=24)))

x_region = df_profit_by_region['region']
bar_data = df_profit_by_region['Total_Profit']
fig_region2 = px.bar(filtered_data, y=x_region, x=bar_data, labels={'y': 'region', 'x': Select_option}, title=f'{Select_option} by Region', width=500, height=500)

fig_region2.update_layout(
    title=dict(font=dict(size=24)))

if not selected_city2.empty:
    selected_Per_city = selected_city2['Profit'].values[0] / filtered_data['Profit'].sum() * 100
    other_per = 100 - selected_Per_city
    fig_pie_profit = px.pie(values=[selected_Per_city, other_per], names=[Selected_city, 'Other Cities'],
                           title=f'Profit Distribution for {Selected_city} vs Other Cities in State')
else:
    # Handle the case when selected_city2 is empty
    fig_pie_profit = px.pie(values=[0, 100], names=['No Profit Data', 'Other Cities'],
                           title=f'No Profit Data for {Selected_city}')

## Insert Charts based on condition of filtered data

with col8:
    if Select_option == 'Sales':
        if Selected_region != all_option:
            if Selected_state != all_option:
                if Selected_city != all_option:
                    st.plotly_chart(fig_pie_sales)
                else:    
                    st.plotly_chart(fig_city)
            else:
                st.plotly_chart(fig_state)    
        elif Selected_state != all_option:
                if Selected_city != all_option:
                    st.plotly_chart(fig_pie_sales)
                else:
                     st.plotly_chart(fig_city)
        else:
            st.plotly_chart(fig_region)
    if Select_option == 'Profit':
        if Selected_region != all_option:
            if Selected_state != all_option:
                if Selected_city != all_option:
                    st.plotly_chart(fig_pie_profit)
                else:    
                    st.plotly_chart(fig_city2)
            else:
                st.plotly_chart(fig_state2)    
        elif Selected_state != all_option:
                if Selected_city != all_option:
                    st.plotly_chart(fig_pie_profit)
                else:
                     st.plotly_chart(fig_city2)
        else:
            st.plotly_chart(fig_region2)

    
## Creating the tables for location data

with col10:
    if Select_option == 'Sales':
        if Selected_region != all_option:
            if Selected_state != all_option:    
                if Selected_city != all_option:
                    st.markdown(f'### Day of Week for {Selected_city} Ranked by Sales')
                    st.table(filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
                else:
                    st.markdown(f"### Top 10 Cities in {Selected_state} by Sales")
                    st.table(filtered_data[filtered_data['State'] == Selected_state][['City', 'Sales']].groupby('City').sum().nlargest(10, 'Sales'))                
            else:
                st.markdown(f"### Top 10 States in {Selected_region} by Sales")
                st.table(filtered_data[['Sales', 'State']].groupby('State').sum().nlargest(10, 'Sales'))     
        elif Selected_state != all_option:
            if Selected_city != all_option:
                st.markdown(f'### Day of Week for {Selected_city} Ranked by Sales')
                st.table(filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
            else:
                st.markdown(f"### Top 10 Cities in {Selected_state} Ranked by Sales")
                st.table(filtered_data[filtered_data['State'] == Selected_state][['City', 'Sales']].groupby('City').sum().nlargest(10, 'Sales'))                
        elif Selected_city != all_option:
            st.markdown(f'### Day of Week for {Selected_city} Ranked by sales')
            st.table(filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
        else:
            st.markdown("### Regions ranked by Sales")
            st.table(filtered_data[['Region', 'Sales']].groupby('Region').sum().nlargest(10, 'Sales'))
    if Select_option == 'Profit':    
        if Selected_region != all_option:
            if Selected_state != all_option:    
                if Selected_city != all_option:
                    st.markdown(f'### Day of Week for {Selected_city} Ranked by Profit')
                    st.table(filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))                 
                else:
                    st.markdown(f"### Top 10 Cities in {Selected_state} Ranked by Profit")
                    st.table(filtered_data[filtered_data['State'] == Selected_state][['City', 'Profit']].groupby('City').sum().nlargest(10, 'Profit'))                
            else:
                st.markdown(f"### Top 10 States in {Selected_region} Ranked by Profit")
                st.table(filtered_data[['Profit', 'State']].groupby('State').sum().nlargest(10, 'Profit'))     
        elif Selected_state != all_option:
            if Selected_city != all_option:
                st.markdown(f'### Day of Week for {Selected_city} Ranked by Profit')
                st.table(filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
            else:
                st.markdown(f"### Top 10 Cities in {Selected_state} Ranked by Proft")
                st.table(filtered_data[filtered_data['State'] == Selected_state][['City', 'Profit']].groupby('City').sum().nlargest(10, 'Profit'))                
        elif Selected_city != all_option:
            st.markdown(f'### Day of Week for {Selected_city} Ranked by Profit')
            st.table(filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
        else:
            st.markdown("### Regions Ranked by Profit")
            st.table(filtered_data[['Region', 'Profit']].groupby('Region').sum().nlargest(10, 'Profit'))

######################################
## Product graph and Table
#######################################

x_values = filtered_data['Category'].unique()
bar_data = filtered_data.groupby('Category')[Select_option].sum()
fig_cat = px.bar(y=x_values, x=bar_data, labels={'y': 'Category', 'x': Select_option}, title=f'{Select_option} by Category', width=500, height=500)

fig_cat.update_layout(
    title=dict(font=dict(size=24)))


x_values = filtered_data['Sub-Category'].unique()
bar_data = filtered_data.groupby('Sub-Category')[Select_option].sum()
fig_sub_cat = px.bar(y=x_values, x=bar_data, labels={'y': 'Sub-Category', 'x': Select_option}, title=f'{Select_option} for sub categories in {Selected_Category}', width=500, height=500)

fig_sub_cat.update_layout(
    title=dict(font=dict(size=24)))

x_values = filtered_data['Product_Name'].unique()
bar_data = filtered_data.groupby('Product_Name')[Select_option].sum()
fig_product = px.bar(y=x_values, x=bar_data, labels={'y': 'Product_Name', 'x': Select_option}, title=f'{Select_option} for Products in {Selected_Sub_Category}', width=500, height=500)

fig_product.update_layout(
    title=dict(font=dict(size=24)))

x_values = filtered_data['Ship_Mode'].unique()
ship_mode_counts = filtered_data['Ship_Mode'].value_counts()

fig_product3 = px.pie(
    names=ship_mode_counts.index,
    values=ship_mode_counts.values,
    title=f'{Select_option} by Ship Mode for {Selected_Product}',
    labels={'value': 'Count'},
    width=500, height=500
)

fig_product3.update_layout(
    title=dict(font=dict(size=24)))

    ## Placing Bar Chart on filtered categories
with col11:
    if Selected_Category != all_option:
        if Selected_Sub_Category != all_option:
            if Selected_Product != all_option:
                st.plotly_chart(fig_product3)
            else:
                st.plotly_chart(fig_product)
        else:
            st.plotly_chart(fig_sub_cat)
              
    elif Selected_Sub_Category != all_option:
        if Selected_Product != all_option:
            st.plotly_chart(fig_product3)
        else:
            st.plotly_chart(fig_product)
    elif Selected_Product != all_option:
        st.plotly_chart(fig_product3)
    else:
        st.plotly_chart(fig_cat)

## Creating Product Tables
with col13:
    if Select_option == 'Sales':
        if Selected_Category != all_option:
            if Selected_Sub_Category != all_option:    
                if Selected_Product != all_option:
                    st.markdown(f'### Day of Week for {Selected_Product} Ranked by Sales')
                    st.table(filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
                else:
                    st.markdown(f"### Top-Performing Products in {Selected_Sub_Category} Segment Ranked by Sales")
                    st.table(filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Product_Name', 'Sales']].groupby('Product_Name').sum().nlargest(10, 'Sales'))                
            else:
                st.markdown(f"### Top-performing sub-categories in {Selected_Category} Segment Ranked by Sales")
                st.table(filtered_data[['Sales', 'Sub-Category']].groupby('Sub-Category').sum().nlargest(10, 'Sales'))     
        elif Selected_Sub_Category != all_option:
            if Selected_Product != all_option:
                st.markdown(f'### Day of Week for {Selected_Product} Ranked by Sales')
                st.table(filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
            else:
                st.markdown(f"### Top-Performing Products in {Selected_Sub_Category} Segment Ranked by Sales")
                st.table(filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Product_Name', 'Sales']].groupby('Product_Name').sum().nlargest(10, 'Sales'))                
        elif Selected_Product != all_option:
            st.markdown(f'### Day of Week for {Selected_Product} Ranked by Sales')
            st.table(filtered_data[filtered_data['Product_Name'] == Selected_Product][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
        else:
            st.markdown("### Category ranked by Sales")
            st.table(filtered_data[['Category', 'Sales']].groupby('Category').sum().nlargest(10, 'Sales'))
    if Select_option == 'Profit':    
        if Selected_Category != all_option:
            if Selected_Sub_Category != all_option:    
                if Selected_Product != all_option:
                    st.markdown(f'### Day of Week for {Selected_Product} Ranked by Profit')
                    st.table(filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
                else:
                    st.markdown(f"### Top-Performing Products in {Selected_Sub_Category} Segment Ranked by Profit")
                    st.table(filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Product_Name', 'Profit']].groupby('Product_Name').sum().nlargest(10, 'Profit'))                
            else:
                st.markdown(f"### Top-performing sub-categories in {Selected_Category} Segment Ranked by Profit")
                st.table(filtered_data[['Profit', 'Sub-Category']].groupby('Sub-Category').sum().nlargest(10, 'Profit'))     
        elif Selected_Sub_Category != all_option:
            if Selected_Product != all_option:
                st.markdown(f'### Day of Week for {Selected_Product} Ranked by Profit')
                st.table(filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
            else:
                st.markdown(f"### Top-Performing Products in {Selected_Sub_Category} Segment Ranked by Profit")
                st.table(filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Product_Name', 'Profit']].groupby('Product_Name').sum().nlargest(10, 'Profit'))                
        elif Selected_Product != all_option:
            st.markdown(f'### Day of Week for {Selected_Product} Ranked by Profit')
            st.table(filtered_data[filtered_data['Product_Name'] == Selected_Product][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
        else:
            st.markdown("### Categories ranked by Profit")
            st.table(filtered_data[['Category', 'Profit']].groupby('Category').sum().nlargest(10, 'Profit'))

###########################
## Metric Information
########################### 
    
if not filtered_data.empty:
        if Select_option == 'Sales':
            total_sales = round(filtered_data['Sales'].sum())
            formatted_total_sales = '${:,}'.format(int(total_sales))
            col1.metric("Total Sales", formatted_total_sales)
        else:
            total_profit = round(filtered_data['Profit'].sum())
            formatted_total_profit = '${:,}'.format(int(total_profit))
            col1.metric("Total Profit", formatted_total_profit)

if not filtered_data.empty:
        if Select_option == 'Sales':
            average_sales = round(filtered_data['Sales'].mean())
            formatted_average_sales = '${:,}'.format(int(average_sales))
            col2.metric("Average Sales", formatted_average_sales)
        else:
            average_profit = round(filtered_data['Profit'].mean())
            formatted_average_profit = '${:,}'.format(int(average_profit))
            col2.metric("Average Profit", formatted_average_profit)

total_revenue = df['Sales'].sum()
total_Profit_df = df['Profit'].sum()

if not filtered_data.empty:
        if Select_option == 'Sales':
            sales_percentage = round(filtered_data['Sales'].sum() / total_revenue * 100, 2)
            formatted_Sales_Percentage = '{:,.2f}%'.format(int(sales_percentage))
            col3.metric("Sales Percentage", formatted_Sales_Percentage)
        else:
            Profit_percentage = round(filtered_data['Profit'].sum() / total_Profit_df * 100, 2)
            formatted_Profit_percentage = '{:,.2f}%'.format(int(Profit_percentage))
            col3.metric("Profit Percentage", formatted_Profit_percentage)

if not filtered_data.empty:
    if Select_option == 'Sales':
        Sales_per_unit = round(filtered_data['Sales'].sum() / filtered_data['Quantity'].sum(), 2)
        formatted_Spu = '${:,}'.format(int(Sales_per_unit))
        col4.metric("Sales Per Unit", formatted_Spu)
    else:
        Profit_margin = round((filtered_data['Profit'].sum() / filtered_data['Sales'].sum()) * 100, 2)
        formatted_Profit_margin = '{:,}%'.format(int(Profit_margin))
        col4.metric("Profit Margin", formatted_Profit_margin)
