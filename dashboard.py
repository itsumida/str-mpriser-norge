import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Norwegian Electricity Prices Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .region-selector {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the electricity price data"""
    # Read all sheets
    xl = pd.ExcelFile('strompriser.xlsx')
    
    all_data = []
    regions = {
        'øst-norge(NO1)': 'Øst-Norge',
        'sør-norge(NO2)': 'Sør-Norge', 
        'midt-norge(NO3)': 'Midt-Norge',
        'nord-norge(NO4)': 'Nord-Norge',
        'vest-norge(NO5)': 'Vest-Norge'
    }
    
    for sheet_name in xl.sheet_names:
        df = pd.read_excel('strompriser.xlsx', sheet_name=sheet_name)
        
        # Clean the data - handle different formats
        if sheet_name in ['midt-norge(NO3)', 'nord-norge(NO4)']:
            # These sheets have a different structure - first row contains month names
            month_names = df.iloc[0, 1:13].tolist()  # Get month names from first row
            df = df.iloc[1:].reset_index(drop=True)  # Remove header row
            df.columns = ['Year'] + month_names + ['Unnamed_13', 'Unnamed_14']
        else:
            # Standard structure
            df.columns = ['Year'] + list(df.columns[1:13]) + ['Unnamed_13', 'Unnamed_14']
        
        # Convert all price columns to numeric, replacing any non-numeric values with NaN
        for col in df.columns[1:13]:  # Skip Year column
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Get only year and month columns
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        # Filter to only have year and month columns
        month_cols = [col for col in df.columns if col in months]
        df_clean = df[['Year'] + month_cols].copy()
        
        # Remove rows with NaN years
        df_clean = df_clean.dropna(subset=['Year'])
        df_clean['Year'] = df_clean['Year'].astype(int)
        
        # Melt to long format
        df_long = pd.melt(df_clean, id_vars=['Year'], 
                         value_vars=month_cols, 
                         var_name='Month', value_name='Price')
        
        # Add region information
        df_long['Region'] = regions[sheet_name]
        df_long['Region_Code'] = sheet_name
        
        # Convert month names to numbers for sorting
        month_map = {month: i+1 for i, month in enumerate(months)}
        df_long['Month_Num'] = df_long['Month'].map(month_map)
        
        # Create date column for better plotting
        df_long['Date'] = pd.to_datetime(df_long['Year'].astype(str) + '-' + df_long['Month_Num'].astype(str) + '-01')
        
        # Remove rows with NaN prices
        df_long = df_long.dropna(subset=['Price'])
        
        all_data.append(df_long)
    
    # Combine all regions
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Calculate annual averages
    annual_avg = combined_df.groupby(['Year', 'Region'])['Price'].mean().reset_index()
    
    return combined_df, annual_avg

def create_overview_metrics(df):
    """Create overview metrics for the dashboard"""
    latest_year = df['Year'].max()
    latest_data = df[df['Year'] == latest_year]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_price = latest_data['Price'].mean()
        st.metric(
            label=f"Average Price ({latest_year})",
            value=f"{avg_price:.2f} øre/kWh",
            delta=None
        )
    
    with col2:
        region_avg = latest_data.groupby('Region')['Price'].mean()
        highest_region = region_avg.idxmax()
        highest_price = region_avg.max()
        st.metric(
            label="Highest Price Region",
            value=highest_region,
            delta=f"{highest_price:.2f} øre/kWh"
        )
    
    with col3:
        lowest_region = region_avg.idxmin()
        lowest_price = region_avg.min()
        st.metric(
            label="Lowest Price Region", 
            value=lowest_region,
            delta=f"{lowest_price:.2f} øre/kWh"
        )
    
    with col4:
        price_range = highest_price - lowest_price
        st.metric(
            label="Price Range",
            value=f"{price_range:.2f} øre/kWh",
            delta=None
        )

def main():
    # Header
    st.markdown('<h1 class="main-header">⚡ Norwegian Electricity Prices Dashboard</h1>', 
                unsafe_allow_html=True)
    st.markdown("**Priser er oppgitt i øre/kWh (inkl. MVA)**")
    
    # Load data
    df, annual_avg = load_data()
    
    # Sidebar filters
    st.sidebar.markdown("## 🎛️ Dashboard Controls")
    
    # Region selection
    st.sidebar.markdown("### Select Regions")
    all_regions = sorted(df['Region'].unique())
    selected_regions = st.sidebar.multiselect(
        "Choose regions to display:",
        options=all_regions,
        default=all_regions,
        key="region_filter"
    )
    
    # Year range selection
    st.sidebar.markdown("### Time Period")
    year_range = st.sidebar.slider(
        "Select year range:",
        min_value=int(df['Year'].min()),
        max_value=int(df['Year'].max()),
        value=(int(df['Year'].min()), int(df['Year'].max())),
        step=1
    )
    
    # Remove view type selection - show all visualizations
    
    # Filter data based on selections
    filtered_df = df[
        (df['Region'].isin(selected_regions)) & 
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1])
    ]
    
    filtered_annual = annual_avg[
        (annual_avg['Region'].isin(selected_regions)) & 
        (annual_avg['Year'] >= year_range[0]) & 
        (annual_avg['Year'] <= year_range[1])
    ]
    
    # Overview metrics
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    create_overview_metrics(filtered_df)
    
    st.markdown("---")
    
    # Show all visualizations
    
    # 1. Yearly Price Change for Whole Norway
    st.markdown("## 📈 Yearly Price Changes in Norway")
    
    # Information board
    with st.expander("ℹ️ What does this graph show?", expanded=False):
        st.markdown("""
        **What this graph tells you:**
        - Shows how much electricity prices went up or down each year compared to the previous year
        - Green bars = prices went down (good news for your wallet!)
        - Red bars = prices went up (more expensive electricity)
        - The percentage shows the size of the change
        
        **Questions this answers:**
        - Which years had the biggest price increases or decreases?
        - Are electricity prices generally going up or down over time?
        - When was the best/worst year for electricity prices?
        - How much did prices change from one year to the next?
        """)
    
    # Calculate yearly averages for whole Norway
    norway_yearly = filtered_df.groupby('Year')['Price'].mean().reset_index()
    norway_yearly['Price_Change'] = norway_yearly['Price'].pct_change() * 100
    
    fig_yearly = px.bar(
        norway_yearly,
        x='Year',
        y='Price_Change',
        title='Year-over-Year Price Change in Norway (%)',
        labels={'Price_Change': 'Price Change (%)', 'Year': 'Year'},
        color='Price_Change',
        color_continuous_scale='RdYlGn_r'
    )
    fig_yearly.update_layout(
        height=500,
        xaxis_title="Year",
        yaxis_title="Price Change (%)"
    )
    st.plotly_chart(fig_yearly, use_container_width=True)
    
    # 2. Regional Price Trends Over Time
    st.markdown("## 📊 Regional Price Trends Over Time")
    
    # Information board
    with st.expander("ℹ️ What does this graph show?", expanded=False):
        st.markdown("""
        **What this graph tells you:**
        - Shows how electricity prices have changed in each region of Norway over the years
        - Each colored line represents a different region
        - You can see which regions are consistently more expensive or cheaper
        - The lines show the overall trend - are prices going up, down, or staying stable?
        
        **Questions this answers:**
        - Which region has the highest/lowest electricity prices?
        - Are some regions consistently more expensive than others?
        - How have prices changed in your region compared to others?
        - Which regions have seen the biggest price increases over time?
        - Are regional price differences getting bigger or smaller?
        """)
    
    # Annual trends
    fig = px.line(
        filtered_annual,
        x='Year',
        y='Price',
        color='Region',
        title='Annual Average Electricity Prices by Region',
        labels={'Price': 'Average Price (øre/kWh)', 'Year': 'Year'},
        markers=True,
        color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"] 
    )
    fig.update_layout(
        height=600,
        xaxis_title="Year",
        yaxis_title="Average Price (øre/kWh)",
        legend_title="Region"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. Seasonal Price Patterns
    st.markdown("## 🌡️ Seasonal Price Patterns")
    
    # Information board
    with st.expander("ℹ️ What does this graph show?", expanded=False):
        st.markdown("""
        **What this graph tells you:**
        - Shows how electricity prices change throughout the year (seasons)
        - Each box shows the range of prices for that season across all years
        - The middle line in each box is the average price for that season
        - You can see which seasons are typically more expensive or cheaper
        
        **Questions this answers:**
        - Is electricity more expensive in winter or summer?
        - Which season has the most stable prices?
        - Which season has the biggest price variations?
        - Are there clear seasonal patterns in electricity prices?
        - How do seasonal patterns differ between regions?
        """)
    
    # Seasonal trends
    seasonal_data = filtered_df.copy()
    seasonal_data['Season'] = seasonal_data['Month_Num'].map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Autumn', 10: 'Autumn', 11: 'Autumn'
    })
    
    seasonal_avg = seasonal_data.groupby(['Region', 'Season', 'Year'])['Price'].mean().reset_index()
    
    fig = px.box(
        seasonal_avg,
        x='Season',
        y='Price',
        color='Region',
        title='Seasonal Price Distribution by Region',
        labels={'Price': 'Price (øre/kWh)', 'Season': 'Season'}
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. Regional Price Differences
    st.markdown("## 🗺️ Regional Price Differences")
    
    # Information board
    with st.expander("ℹ️ What does this graph show?", expanded=False):
        st.markdown("""
        **What this graph tells you:**
        - Shows how different regions compare to each other in terms of electricity prices
        - **Top left**: Price range - how much prices vary in each region (from lowest to highest)
        - **Top right**: Price stability - how much prices jump around in each region
        - **Bottom left**: Last year(within chosen time-range) prices - what each region pays at the last year within set date range
        - **Bottom right**: Average prices - what each region typically pays over time
        
        **Questions this answers:**
        - Which region has the most stable electricity prices?
        - Which region has the biggest price swings?
        - How much more expensive is the most expensive region compared to the cheapest?
        - Are some regions consistently more expensive than others?
        - Which region would be best for someone who wants predictable electricity costs?
        """)
    
    # Create subplots for different metrics
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Price Range by Region', 'Price Stability', 
                      'Last year(of chosen time-range) Prices', 'Average Prices Over Time'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Price range
    price_stats = filtered_df.groupby('Region')['Price'].agg(['min', 'max', 'std', 'mean']).reset_index()
    price_stats['range'] = price_stats['max'] - price_stats['min']
    
    fig.add_trace(
        go.Bar(x=price_stats['Region'], y=price_stats['range'], 
               name='Price Range', marker_color='lightblue'),
        row=1, col=1
    )
    
    # Price stability (standard deviation)
    fig.add_trace(
        go.Bar(x=price_stats['Region'], y=price_stats['std'], 
               name='Price Stability', marker_color='lightcoral'),
        row=1, col=2
    )
    
    # Latest year comparison
    latest_data = filtered_df[filtered_df['Year'] == filtered_df['Year'].max()]
    latest_avg = latest_data.groupby('Region')['Price'].mean().reset_index()
    
    fig.add_trace(
        go.Bar(x=latest_avg['Region'], y=latest_avg['Price'], 
               name='Current Year', marker_color='lightgreen'),
        row=2, col=1
    )
    
    # Overall average
    overall_avg = filtered_df.groupby('Region')['Price'].mean().reset_index()
    
    fig.add_trace(
        go.Bar(x=overall_avg['Region'], y=overall_avg['Price'], 
               name='Average Over Time', marker_color='lightyellow'),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Regional Price Analysis")
    st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>📊 Norwegian Electricity Prices Dashboard | Data: 2014-2024 | Prices in øre/kWh (incl. MVA)</p>
        <p>Built with Streamlit & Plotly | Interactive visualization of regional electricity price trends</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
