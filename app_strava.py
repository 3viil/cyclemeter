import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Load data
df = pd.read_csv('activities.csv')
df['Activity Date'] = pd.to_datetime(df['Activity Date'])

# Meters to miles: 1 meter = 0.000621371 miles
df['Distance (miles)'] = df['Distance (meters)'] * 0.000621371
# Meters to feet: 1 meter = 3.28084 feet
df['Ascent (feet)'] = df['Elevation Gain (meters)'] * 3.28084
# Seconds to hours
df['Elapsed Time (hours)'] = df['Elapsed Time (seconds)'] / 3600

# Create activity type filter
activity_types = df['Activity Type'].unique()
selected_activities = st.sidebar.multiselect(
    'Select Activity Types:',
    options=activity_types,
    default=['Ride', 'E-Bike Ride']
)

if selected_activities:
    df_filtered = df[df['Activity Type'].isin(selected_activities)].copy()
else:
    df_filtered = df.copy()

# Extract year, month, and week from Activity Date
df_filtered['Year'] = df_filtered['Activity Date'].dt.year
df_filtered['Month'] = df_filtered['Activity Date'].dt.to_period('M')
df_filtered['Week'] = df_filtered['Activity Date'].dt.to_period('W')

# Aggregate by Year
df_year = df_filtered.groupby('Year').agg({
    'Ascent (feet)': 'sum',
    'Calories': 'sum',
    'Distance (miles)': 'sum'
}).reset_index()

# Calculate climb/distance ratio, handling division by zero
df_year['Climb/distance ratio'] = df_year.apply(
    lambda row: row['Ascent (feet)'] / row['Distance (miles)'] if row['Distance (miles)'] > 0 else 0,
    axis=1
)

# Convert years to datetime for consistent plotting
df_year['Year'] = pd.to_datetime(df_year['Year'].astype(str) + '-01-01')

# Aggregate by Month
df_month = df_filtered.groupby('Month').agg({
    'Ascent (feet)': 'sum',
    'Calories': 'sum',
    'Distance (miles)': 'sum'
}).reset_index()

# Calculate climb/distance ratio, handling division by zero
df_month['Climb/distance ratio'] = df_month.apply(
    lambda row: row['Ascent (feet)'] / row['Distance (miles)'] if row['Distance (miles)'] > 0 else 0,
    axis=1
)

# Convert Month period to datetime
df_month['Month'] = df_month['Month'].dt.to_timestamp()

# Aggregate by Week
df_week = df_filtered.groupby('Week').agg({
    'Ascent (feet)': 'sum',
    'Calories': 'sum',
    'Distance (miles)': 'sum'
}).reset_index()

# Calculate climb/distance ratio, handling division by zero
df_week['Climb/distance ratio'] = df_week.apply(
    lambda row: row['Ascent (feet)'] / row['Distance (miles)'] if row['Distance (miles)'] > 0 else 0,
    axis=1
)

# Convert Week period to datetime
df_week['Week'] = df_week['Week'].dt.to_timestamp()

# Round numeric columns for better display
for df_temp in [df_year, df_month, df_week]:
    df_temp['Ascent (feet)'] = df_temp['Ascent (feet)'].round(0).astype(int)
    df_temp['Calories'] = df_temp['Calories'].round(0).astype(int)
    df_temp['Distance (miles)'] = df_temp['Distance (miles)'].round(1)
    df_temp['Climb/distance ratio'] = df_temp['Climb/distance ratio'].round(1)

# Prepare data for weekly ride type analysis
df_ride_types = df[df['Activity Type'].isin(['Ride', 'E-Bike Ride'])].copy()

# Add Week column to df_ride_types
df_ride_types['Week'] = df_ride_types['Activity Date'].dt.to_period('W')

# Filter out rides longer than 8 hours for time analysis
df_ride_types_time = df_ride_types[df_ride_types['Elapsed Time (hours)'] <= 8].copy()

# Aggregate by week and activity type for distance
weekly_distance = df_ride_types.groupby(['Week', 'Activity Type'])['Distance (miles)'].sum().reset_index()
weekly_distance_pivot = weekly_distance.pivot(index='Week', columns='Activity Type', values='Distance (miles)').fillna(0)

# Aggregate by week and activity type for time (filtered)
weekly_time = df_ride_types_time.groupby(['Week', 'Activity Type'])['Elapsed Time (hours)'].sum().reset_index()
weekly_time_pivot = weekly_time.pivot(index='Week', columns='Activity Type', values='Elapsed Time (hours)').fillna(0)

# Ensure both ride types exist in the dataframes
for df_pivot in [weekly_distance_pivot, weekly_time_pivot]:
    if 'Ride' not in df_pivot.columns:
        df_pivot['Ride'] = 0
    if 'E-Bike Ride' not in df_pivot.columns:
        df_pivot['E-Bike Ride'] = 0

# Reset index and convert Week period to datetime
weekly_distance_pivot = weekly_distance_pivot.reset_index()
weekly_distance_pivot['Week'] = weekly_distance_pivot['Week'].dt.to_timestamp()
weekly_distance_pivot = weekly_distance_pivot.sort_values('Week')

weekly_time_pivot = weekly_time_pivot.reset_index()
weekly_time_pivot['Week'] = weekly_time_pivot['Week'].dt.to_timestamp()
weekly_time_pivot = weekly_time_pivot.sort_values('Week')

# Calculate totals and percentages
weekly_distance_pivot['Total Distance'] = weekly_distance_pivot['Ride'] + weekly_distance_pivot['E-Bike Ride']
weekly_distance_pivot['Ride %'] = (weekly_distance_pivot['Ride'] / weekly_distance_pivot['Total Distance'] * 100).fillna(0)
weekly_distance_pivot['E-Bike Ride %'] = (weekly_distance_pivot['E-Bike Ride'] / weekly_distance_pivot['Total Distance'] * 100).fillna(0)

weekly_time_pivot['Total Time'] = weekly_time_pivot['Ride'] + weekly_time_pivot['E-Bike Ride']
weekly_time_pivot['Ride %'] = (weekly_time_pivot['Ride'] / weekly_time_pivot['Total Time'] * 100).fillna(0)
weekly_time_pivot['E-Bike Ride %'] = (weekly_time_pivot['E-Bike Ride'] / weekly_time_pivot['Total Time'] * 100).fillna(0)

# Create combined dataframe for display
combined_weekly_df = pd.merge(
    weekly_distance_pivot[['Week', 'Ride', 'E-Bike Ride', 'Total Distance', 'Ride %', 'E-Bike Ride %']],
    weekly_time_pivot[['Week', 'Ride', 'E-Bike Ride', 'Total Time', 'Ride %', 'E-Bike Ride %']],
    on='Week',
    suffixes=(' (miles)', ' (hours)')
)

# Function to create stacked bar chart
def create_stacked_bar_chart(df, value_col, value_name, value_unit):
    """Create a stacked bar chart for the given metric"""
    fig = go.Figure()

    # Add trace for regular rides
    fig.add_trace(go.Bar(
        x=df['Week'],
        y=df['Ride'],
        name='Ride',
        marker_color='#1f77b4',
        hovertemplate=f'Week: %{{x|%Y-%m-%d}}<br>Regular Ride: %{{y:.1f}} {value_unit}<br><extra></extra>'
    ))

    # Add trace for e-bike rides
    fig.add_trace(go.Bar(
        x=df['Week'],
        y=df['E-Bike Ride'],
        name='E-Bike Ride',
        marker_color='#ff7f0e',
        hovertemplate=f'Week: %{{x|%Y-%m-%d}}<br>E-Bike Ride: %{{y:.1f}} {value_unit}<br><extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        barmode='stack',
        title=f'Weekly {value_name} by Ride Type',
        xaxis_title='Week',
        yaxis_title=f'{value_name} ({value_unit})',
        hovermode='x unified',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

# Display summary statistics in sidebar
st.sidebar.markdown("### Summary Statistics")
if not df_filtered.empty:
    total_rides = len(df_filtered)
    total_distance = df_filtered['Distance (miles)'].sum()
    total_ascent = df_filtered['Ascent (feet)'].sum()
    total_calories = df_filtered['Calories'].sum()

    st.sidebar.metric("Total Rides", f"{total_rides:,}")
    st.sidebar.metric("Total Distance", f"{total_distance:,.1f} mi")
    st.sidebar.metric("Total Ascent", f"{total_ascent:,.0f} ft")
    st.sidebar.metric("Total Calories", f"{total_calories:,.0f}")

# Streamlit app layout

# Get dates for title, trim to year only
if not df_year.empty:
    year_start = df_year['Year'].iloc[0]
    year_start = str(year_start)[0:4]
    year_end = df_year['Year'].iloc[-1]
    year_end = str(year_end)[0:4]
    st.header(f":blue[Cyclemeter MTB Data, {year_start}-{year_end}]")
else:
    st.header(":blue[Cyclemeter MTB Data]")

# Show selected activity types
if selected_activities:
    st.caption(f"Showing data for: {', '.join(selected_activities)}")
else:
    st.caption("No activity types selected")

# Data by Year
st.subheader("Data by Year")
tab1, tab2, tab3 = st.tabs(["Ascent & Calories", "Ascent/distance ratio", "Dataframe"])
tab1.line_chart(df_year, x="Year", y=['Ascent (feet)', 'Calories'], height=400)
tab2.line_chart(df_year, x="Year", y="Climb/distance ratio", height=400)
tab3.dataframe(df_year, height=400, use_container_width=True)

# Data by Month
st.subheader("Data by Month")
tab1, tab2, tab3 = st.tabs(["Ascent & Calories", "Ascent/distance ratio", "Dataframe"])
tab1.line_chart(df_month, x="Month", y=['Ascent (feet)', 'Calories'], height=400)
tab2.line_chart(df_month, x="Month", y="Climb/distance ratio", height=400)
tab3.dataframe(df_month, height=400, use_container_width=True)

# Data by Week
st.subheader("Data by Week")
tab1, tab2, tab3 = st.tabs(["Ascent & Calories", "Ascent/distance ratio", "Dataframe"])
tab1.line_chart(df_week, x="Week", y=['Ascent (feet)', 'Calories'], height=400)
tab2.line_chart(df_week, x="Week", y="Climb/distance ratio", height=400)
tab3.dataframe(df_week, height=400, use_container_width=True)


st.subheader("Analog versus E-bike rides")
tab1, tab2, tab3 = st.tabs(["Weekly Total Distance", "Weekly Total Time", "Dataframe"])

# Tab 1: Weekly Distance
if not weekly_distance_pivot.empty:
    distance_fig = create_stacked_bar_chart(weekly_distance_pivot, 'Distance', 'Distance', 'miles')
    tab1.plotly_chart(distance_fig, use_container_width=True)

# Tab 2: Weekly Time
if not weekly_time_pivot.empty:
    time_fig = create_stacked_bar_chart(weekly_time_pivot, 'Time', 'Time', 'hours')
    tab2.plotly_chart(time_fig, use_container_width=True)

# Tab 3: Dataframe
if not combined_weekly_df.empty:
    # Format the combined dataframe for display
    display_df = combined_weekly_df.copy()
    display_df['Week'] = display_df['Week'].dt.strftime('%Y-%m-%d')

    # Round numeric columns
    numeric_columns = [
        'Ride (miles)', 'E-Bike Ride (miles)', 'Total Distance',
        'Ride (hours)', 'E-Bike Ride (hours)', 'Total Time'
    ]
    for col in numeric_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(1)

    # Round percentage columns
    percentage_columns = [
        'Ride % (miles)', 'E-Bike Ride % (miles)',
        'Ride % (hours)', 'E-Bike Ride % (hours)'
    ]
    for col in percentage_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(1)

    # Rename columns for better readability
    display_df = display_df.rename(columns={
        'Ride (miles)': 'Ride Distance (mi)',
        'E-Bike Ride (miles)': 'E-Bike Distance (mi)',
        'Total Distance': 'Total Distance (mi)',
        'Ride % (miles)': 'Ride %',
        'E-Bike Ride % (miles)': 'E-Bike %',
        'Ride (hours)': 'Ride Time (hr)',
        'E-Bike Ride (hours)': 'E-Bike Time (hr)',
        'Total Time': 'Total Time (hr)',
        'Ride % (hours)': 'Ride Time %',
        'E-Bike Ride % (hours)': 'E-Bike Time %'
    })

    # Display the dataframe
    tab3.dataframe(display_df, use_container_width=True, hide_index=True)
