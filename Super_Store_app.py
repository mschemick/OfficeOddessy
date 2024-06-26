import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import datetime
import os
import requests
import warnings
warnings.filterwarnings('ignore')

print(st.__path__)
############################
## Web App Setup
############################

## Setting up the page
st.set_page_config(page_title="Store Report Dashboard",
                   page_icon=":bar_chart:",
                   layout="wide")


## Title of dashboard
st.title(" :bar_chart: Office Odyssey KPI Dashboard")


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
st.sidebar.title('KPI')

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

DOW_Percent = filtered_data['Days_of_week'].value_counts()

fig_city_pie= px.pie(
    names=DOW_Percent.index,
    values=DOW_Percent.values,
    title=f'Percentage of Orders placed by Day for {Selected_city}',
    labels={'value': 'Count'},
    width=500, height=500
)

fig_city_pie.update_layout(
    title=dict(font=dict(size=24)))


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

## Insert Charts based on condition of filtered data

with col8:
    if Select_option == 'Sales':
        if Selected_region != all_option:
            if Selected_state != all_option:
                if Selected_city != all_option:
                    st.plotly_chart(fig_city_pie)
                else:    
                    st.plotly_chart(fig_city)
            else:
                st.plotly_chart(fig_state)    
        elif Selected_state != all_option:
                if Selected_city != all_option:
                    st.plotly_chart(fig_city_pie)
                else:
                     st.plotly_chart(fig_city)
        else:
            st.plotly_chart(fig_region)
    if Select_option == 'Profit':
        if Selected_region != all_option:
            if Selected_state != all_option:
                if Selected_city != all_option:
                    st.plotly_chart(fig_city_pie)
                else:    
                    st.plotly_chart(fig_city2)
            else:
                st.plotly_chart(fig_state2)    
        elif Selected_state != all_option:
                if Selected_city != all_option:
                    st.plotly_chart(fig_city_pie)
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
                    st.markdown(f'### Days of the Week for {Selected_city} Ranked by Sales')
                    table_1 = (filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
                    table_1_format = table_1.style.format({'Sales': "${:,.2f}"})
                    st.table(table_1_format)
                else:
                    st.markdown(f"### Top 10 Cities in {Selected_state} by Sales")
                    table_2 =(filtered_data[filtered_data['State'] == Selected_state][['City', 'Sales']].groupby('City').sum().nlargest(10, 'Sales'))                
                    table_2_format = table_2.style.format({'Sales': "${:,.2f}"})
                    st.table(table_2_format)
            else:
                st.markdown(f"### Top 10 States in {Selected_region} by Sales")
                table_3 = (filtered_data[['Sales', 'State']].groupby('State').sum().nlargest(10, 'Sales'))     
                table_3_format = table_3.style.format({'Sales': "${:,.2f}"})
                st.table(table_3_format)
        elif Selected_state != all_option:
            if Selected_city != all_option:
                st.markdown(f'### Days of the Week for {Selected_city} Ranked by Sales')
                table_4 = (filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
                table_4_format = table_4.style.format({'Sales': "${:,.2f}"})
                st.table(table_4_format)
            else:
                st.markdown(f"### Top 10 Cities in {Selected_state} Ranked by Sales")
                table_5 = (filtered_data[filtered_data['State'] == Selected_state][['City', 'Sales']].groupby('City').sum().nlargest(10, 'Sales'))                
                table_5_format = table_5.style.format({'Sales': "${:,.2f}"})
                st.table(table_5_format)
        elif Selected_city != all_option:
            st.markdown(f'### Days of the Week for {Selected_city} Ranked by sales')
            table_6 = (filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
            table_6_format = table_6.style.format({'Sales': "${:,.2f}"})
            st.table(table_6_format)
        else:
            st.markdown("### Regions ranked by Sales")
            table_7 = (filtered_data[['Region', 'Sales']].groupby('Region').sum().nlargest(10, 'Sales'))
            table_7_format = table_7.style.format({'Sales': "${:,.2f}"})
            st.table(table_7_format)
    if Select_option == 'Profit':    
        if Selected_region != all_option:
            if Selected_state != all_option:    
                if Selected_city != all_option:
                    st.markdown(f'### Days of the Week for {Selected_city} Ranked by Profit')
                    table_8 = (filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))                 
                    table_8_format = table_8.style.format({'Profit': "${:,.2f}"})
                    st.table(table_8_format)
                else:
                    st.markdown(f"### Top 10 Cities in {Selected_state} Ranked by Profit")
                    table_9 = (filtered_data[filtered_data['State'] == Selected_state][['City', 'Profit']].groupby('City').sum().nlargest(10, 'Profit'))                
                    table_9_format = table_9.style.format({'Profit': "${:,.2f}"})
                    st.table(table_9_format)
            else:
                st.markdown(f"### Top 10 States in {Selected_region} Ranked by Profit")
                table_10 = (filtered_data[['Profit', 'State']].groupby('State').sum().nlargest(10, 'Profit'))     
                table_10_format = table_10.style.format({'Profit': "${:,.2f}"})
                st.table(table_10_format)
        elif Selected_state != all_option:
            if Selected_city != all_option:
                st.markdown(f'### Days of the Week for {Selected_city} Ranked by Profit')
                table_11 = (filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
                table_11_format = table_11.style.format({'Profit': "${:,.2f}"})
                st.table(table_11_format)
            else:
                st.markdown(f"### Top 10 Cities in {Selected_state} Ranked by Proft")
                table_12 = (filtered_data[filtered_data['State'] == Selected_state][['City', 'Profit']].groupby('City').sum().nlargest(10, 'Profit'))                
                table_12_format = table_12.style.format({'Profit': "${:,.2f}"})
        elif Selected_city != all_option:
            st.markdown(f'### Days of the Week for {Selected_city} Ranked by Profit')
            table_13 = (filtered_data[filtered_data['State'] == Selected_state][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
            table_13_format = table_13.style.format({'Profit': "${:,.2f}"})
            st.table(table_13_format)
        else:
            st.markdown("### Regions Ranked by Profit")
            table_14 = (filtered_data[['Region', 'Profit']].groupby('Region').sum().nlargest(10, 'Profit'))
            table_14_format = table_14.style.format({'Profit': "${:,.2f}"})
            st.table(table_14_format)

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
ship_mode_counts = filtered_data['Days_of_week'].value_counts()

fig_product3 = px.pie(
    names=ship_mode_counts.index,
    values=ship_mode_counts.values,
    title=f'Percentage of Orders placed by Day for {Selected_Product}',
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
                    st.markdown(f'### Days of the Week for {Selected_Product} Ranked by Sales')
                    table_data1 = (filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
                    table_data1_format = table_data1.style.format({'Sales': "${:,.2f}"})
                    st.table(table_data1_format)
                else:
                    st.markdown(f"### Top-Performing Products in {Selected_Sub_Category} Segment Ranked by Sales")
                    table_data2 = (filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Product_Name', 'Sales']].groupby('Product_Name').sum().nlargest(10, 'Sales'))                
                    table_data2_format = table_data2.style.format({'Sales': "${:,.2f}"})
                    st.table(table_data2_format)
            else:
                st.markdown(f"### Top-performing sub-categories in {Selected_Category} Segment Ranked by Sales")
                table_data3 = (filtered_data[['Sales', 'Sub-Category']].groupby('Sub-Category').sum().nlargest(10, 'Sales'))
                table_data3_format = table_data3.style.format({'Sales': "${:,.2f}"})
                st.table(table_data3_format)
        elif Selected_Sub_Category != all_option:
            if Selected_Product != all_option:
                st.markdown(f'### Days of the Week for {Selected_Product} Ranked by Sales')
                table_data4 = (filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
                table_data4_format = table_data4.style.format({'Sales': "${:,.2f}"})
                st.table(table_data4_format)
            else:
                st.markdown(f"### Top-Performing Products in {Selected_Sub_Category} Segment Ranked by Sales")
                table_data5 = (filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Product_Name', 'Sales']].groupby('Product_Name').sum().nlargest(10, 'Sales'))                
                table_data5_format = table_data5.style.format({'Sales': "${:,.2f}"})
                st.table(table_data5_format)
        elif Selected_Product != all_option:
            st.markdown(f'### Days of the Week for {Selected_Product} Ranked by Sales')
            table_data6 =(filtered_data[filtered_data['Product_Name'] == Selected_Product][['Days_of_week', 'Sales']].groupby('Days_of_week').sum().nlargest(10, 'Sales'))
            table_data6_format = table_data6.style.format({'Sales': "${:,.2f}"})
            st.table(table_data6_format)
        else:
            st.markdown("### Category ranked by Sales")
            table_data7 = (filtered_data[['Category', 'Sales']].groupby('Category').sum().nlargest(10, 'Sales'))
            table_data7_format = table_data7.style.format({'Sales': "${:,.2f}"})
            st.table(table_data7_format)
    if Select_option == 'Profit':    
        if Selected_Category != all_option:
            if Selected_Sub_Category != all_option:    
                if Selected_Product != all_option:
                    st.markdown(f'### Days of the Week for {Selected_Product} Ranked by Profit')
                    table_data8 =(filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
                    table_data8_format = table_data8.style.format({'Profit': "${:,.2f}"})
                    st.table(table_data8_format)
                else:
                    st.markdown(f"### Top-Performing Products in {Selected_Sub_Category} Segment Ranked by Profit")
                    table_data9 = (filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Product_Name', 'Profit']].groupby('Product_Name').sum().nlargest(10, 'Profit'))                
                    table_data9_format = table_data9.style.format({'Profit': "${:,.2f}"})
                    st.table(table_data9_format)
            else:
                st.markdown(f"### Top-performing sub-categories in {Selected_Category} Segment Ranked by Profit")
                table_data10 =(filtered_data[['Profit', 'Sub-Category']].groupby('Sub-Category').sum().nlargest(10, 'Profit'))     
                table_data10_format = table_data10.style.format({'Profit': "${:,.2f}"})
                st.table(table_data10_format)
        elif Selected_Sub_Category != all_option:
            if Selected_Product != all_option:
                st.markdown(f'### Days of the Week for {Selected_Product} Ranked by Profit')
                table_data11 = (filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
                table_data11_format = table_data11.style.format({'Profit': "${:,.2f}"})
                st.table(table_data11_format)
            else:
                st.markdown(f"### Top-Performing Products in {Selected_Sub_Category} Segment Ranked by Profit")
                table_data12 = (filtered_data[filtered_data['Sub-Category'] == Selected_Sub_Category][['Product_Name', 'Profit']].groupby('Product_Name').sum().nlargest(10, 'Profit'))                
                table_data12_format = table_data12.style.format({'Profit': "${:,.2f}"})
                st.table(table_data12_format)
        elif Selected_Product != all_option:
            st.markdown(f'### Days of the Week for {Selected_Product} Ranked by Profit')
            table_data13 = (filtered_data[filtered_data['Product_Name'] == Selected_Product][['Days_of_week', 'Profit']].groupby('Days_of_week').sum().nlargest(10, 'Profit'))
            table_data13_format = table_data13.style.format({'Profit': "${:,.2f}"})
            st.table(table_data13_format)
        else:
            st.markdown("### Categories ranked by Profit")
            table_data14 = (filtered_data[['Category', 'Profit']].groupby('Category').sum().nlargest(10, 'Profit'))
            table_data14_format = table_data14.style.format({'Profit': "${:,.2f}"})
            st.table(table_data14_format)

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


