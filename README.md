# Norwegian Electricity Prices Dashboard ⚡

Site live at https://strompriser-norge-monster.streamlit.app/

An interactive dashboard for analyzing electricity price trends across Norway's five regions from 2014-2024.

## Features

- **Regional Filtering**: Select specific regions (Øst-Norge, Sør-Norge, Midt-Norge, Nord-Norge, Vest-Norge)
- **Time Range Selection**: Choose any year range within 2014-2024
- **Multiple View Types**:
  - Monthly Trends: Detailed monthly price movements
  - Annual Averages: Year-over-year comparisons
  - Seasonal Analysis: Winter, Spring, Summer, Autumn patterns
  - Regional Comparison: Statistical analysis across regions

## Data Source

- **File**: `strompriser.xlsx`
- **Period**: 2014-2024
- **Regions**: 5 Norwegian electricity price areas (NO1-NO5)
- **Unit**: øre/kWh (including MVA)
- **Frequency**: Monthly data

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
streamlit run dashboard.py
```

## Usage

1. **Select Regions**: Use the sidebar to choose which regions to analyze
2. **Set Time Period**: Adjust the year range slider
3. **Choose View Type**: Select from four different visualization modes
4. **Explore**: Interact with charts, hover for details, and analyze trends

## Dashboard Views

### Monthly Trends
- Line charts showing price movements over time
- Monthly heatmap for seasonal patterns
- Interactive hover details

### Annual Averages
- Year-over-year price comparisons
- Regional bar chart for latest year
- Trend analysis

### Seasonal Analysis
- Box plots showing seasonal price distributions
- Seasonal trends over time
- Weather-related price patterns

### Regional Comparison
- Price range and volatility analysis
- Statistical summaries
- Comparative metrics

## Key Insights

The dashboard helps identify:
- Regional price differences
- Seasonal patterns
- Long-term trends
- Price volatility
- Market dynamics across Norway

## Technical Details

- Built with Streamlit for the web interface
- Plotly for interactive visualizations
- Pandas for data processing
- Responsive design with custom CSS styling
