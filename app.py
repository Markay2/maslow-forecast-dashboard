import pandas as pd
import streamlit as st
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
from io import BytesIO
import base64

# 🎨 Maslow Restaurant Group Brand Colors
RESTAURANT_THEMES = {
    'maslow': {
        'name': 'Maslow Mégisserie',
        'concept': 'Artisanal Vegetarian • Shared Plates',
        'address': '84 rue du Fg St Denis, 75010 Paris',
        'colors': {
            'primary': '#FF8C00',      # Dark orange (Maslow signature)
            'secondary': '#FF6347',    # Tomato orange (complementary)
            'accent': '#FFB347',       # Light orange (accent)
            'background': '#FFF8DC',   # Cornsilk (warm light background)
            'text': '#8B4513',         # Dark brown text for readability
            'success': '#FF8C00',
            'warning': '#FFA500',
            'danger': '#FF4500',
            'neutral': '#D2691E'
        }
    },
    'fellows': {
        'name': 'Fellows Restaurant',
        'concept': 'Artisanal Pasta • 100% Maison',
        'address': '84 rue du Fg St Denis, 75010 Paris',
        'colors': {
            'primary': '#2F2F2F',      # Dark charcoal (sophisticated)
            'secondary': '#FFFFFF',    # Pure white (clean/minimal)
            'accent': '#808080',       # Medium gray (balance)
            'background': '#F8F8FF',   # Ghost white (subtle background)
            'text': '#2F2F2F',         # Dark charcoal text
            'success': '#696969',
            'warning': '#A9A9A9',
            'danger': '#4F4F4F',
            'neutral': '#C0C0C0'
        }
    },
    'temple': {
        'name': 'Maslow Temple',
        'concept': 'Premium Artisanal • Temple Experience',
        'address': '84 rue du Fg St Denis, 75010 Paris',
        'colors': {
            'primary': '#8B0000',      # Dark red (premium/temple)
            'secondary': '#DC143C',    # Crimson (vibrant red)
            'accent': '#FFB6C1',       # Light pink (soft accent)
            'background': '#FFF0F5',   # Lavender blush (elegant light)
            'text': '#8B0000',         # Dark red text
            'success': '#B22222',
            'warning': '#CD5C5C',
            'danger': '#A0252B',
            'neutral': '#BC8F8F'
        }
    }
}

# 🖥 Page Setup with Dynamic Branding
st.set_page_config(
    page_title="Maslow Group - Forecast Dashboard", 
    layout="wide",
    page_icon="🍽️",
    initial_sidebar_state="expanded"
)

# Add title and introduction
st.title("🍽️ Maslow Restaurant Group - Forecast Dashboard")

# Restaurant Selection
st.sidebar.header("🍽️ MASLOW GROUP Restaurants")
selected_restaurant = st.sidebar.selectbox(
    "Choose Restaurant Brand:",
    list(RESTAURANT_THEMES.keys()),
    format_func=lambda x: RESTAURANT_THEMES[x]['name'],
    help="Select which Maslow Group restaurant to analyze"
)

# Get selected theme
CURRENT_THEME = RESTAURANT_THEMES[selected_restaurant]
MASLOW_COLORS = CURRENT_THEME['colors']

# Custom CSS with Dynamic Theming
st.markdown(f"""
<style>
    .main-header {{
        background: linear-gradient(90deg, {MASLOW_COLORS['primary']} 0%, {MASLOW_COLORS['secondary']} 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }}
    
    .metric-card {{
        background: {MASLOW_COLORS['background']};
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid {MASLOW_COLORS['accent']};
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }}
    
    .restaurant-info {{
        background: linear-gradient(135deg, {MASLOW_COLORS['primary']}, {MASLOW_COLORS['accent']});
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    
    .toggle-container {{
        background: {MASLOW_COLORS['background']};
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid {MASLOW_COLORS['primary']};
    }}
    
    .insight-card {{
        background: {MASLOW_COLORS['background']};
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid {MASLOW_COLORS['neutral']};
        margin: 1rem 0;
    }}
    
    .comparison-card {{
        background: linear-gradient(135deg, #FF8C00, #2F2F2F, #8B0000);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }}
</style>
""", unsafe_allow_html=True)

# 🍽️ Dynamic Restaurant Header
st.markdown(f"""
<div class="main-header">
    <h1>🍽️ {CURRENT_THEME['name'].upper()}</h1>
    <h2>📊 Forecast Dashboard – Revenue & Quantity Analytics</h2>
    <p>{CURRENT_THEME['concept']} • {CURRENT_THEME['address']}</p>
    <p>Data-Driven Decisions • Real-Time Forecasting</p>
</div>
""", unsafe_allow_html=True)

# 📁 Data Loading Function for Cloud Deployment
@st.cache_data
def load_sample_data():
    """Generate sample data for demonstration purposes"""
    dates = pd.date_range(start='2023-01-01', end='2024-01-31', freq='D')
    
    # Generate realistic restaurant data with seasonality
    import numpy as np
    np.random.seed(42)
    
    base_revenue = 1000
    base_quantity = 150
    
    # Add weekly seasonality (weekends higher)
    weekly_pattern = np.sin(np.arange(len(dates)) * 2 * np.pi / 7) * 200
    
    # Add some randomness
    revenue = base_revenue + weekly_pattern + np.random.normal(0, 100, len(dates))
    quantity = base_quantity + (weekly_pattern * 0.2) + np.random.normal(0, 20, len(dates))
    
    # Ensure positive values
    revenue = np.maximum(revenue, 200)
    quantity = np.maximum(quantity, 30)
    
    sample_df = pd.DataFrame({
        'Date': dates,
        'Revenue': revenue,
        'Quantity_Sold': quantity
    })
    
    return sample_df

# Enhanced Toggle Switch Section
st.sidebar.markdown(f"""
<div class="restaurant-info">
    <h3>🍽️ {CURRENT_THEME['name']}</h3>
    <p>{CURRENT_THEME['concept']}</p>
    <p>📍 {CURRENT_THEME['address']}</p>
</div>
""", unsafe_allow_html=True)

# File Upload Option
st.sidebar.header("📂 Data Source")
upload_option = st.sidebar.radio(
    "Choose data source:",
    ["Upload File", "Use Sample Data"],
    help="Upload your sales data or use sample data for demonstration"
)

# Dashboard View Mode
st.sidebar.header("🧪 Dashboard View Mode")

view_toggle = st.sidebar.radio(
    "Select Analysis Focus:",
    ["📊 Combined Dashboard", "💰 Revenue Focus", "🍽️ Quantity Focus", "📈 Comparison View", "🏢 Multi-Restaurant Comparison"],
    index=0,
    help="Toggle between different analytical perspectives"
)

# Advanced View Options
st.sidebar.subheader("🔧 Advanced Options")
show_confidence_bands = st.sidebar.checkbox("Show Confidence Intervals", value=True)
show_trend_components = st.sidebar.checkbox("Show Trend Components", value=False)
enable_interactive_mode = st.sidebar.checkbox("Interactive Charts", value=True)

# Enhanced color scheme based on view
if "Revenue" in view_toggle:
    primary_color = MASLOW_COLORS['secondary']
    view_icon = "💰"
elif "Quantity" in view_toggle:
    primary_color = MASLOW_COLORS['accent']
    view_icon = "🍽️"
elif "Comparison" in view_toggle:
    primary_color = MASLOW_COLORS['primary']
    view_icon = "📈"
elif "Multi-Restaurant" in view_toggle:
    primary_color = "#FF8C00"
    view_icon = "🏢"
else:
    primary_color = MASLOW_COLORS['primary']
    view_icon = "📊"

# Visual Toggle Indicator
st.markdown(f"""
<div class="toggle-container">
    <h3 style="color: {primary_color}; text-align: center;">
        {view_icon} Current View: {view_toggle}
    </h3>
    <p style="text-align: center; color: {MASLOW_COLORS['text']};">
        Analyzing data for <strong>{CURRENT_THEME['name'] if view_toggle != "🏢 Multi-Restaurant Comparison" else "All Restaurants"}</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# Data Loading
df = None

if upload_option == "Upload File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload your Excel file", 
        type=['xlsx', 'xls', 'csv'],
        help="Upload your cleaned sales data file"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            df["Date"] = pd.to_datetime(df["Date"])
            st.sidebar.success("✅ File uploaded successfully!")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.stop()
    else:
        st.info("👆 Please upload your data file to get started!")
        st.stop()
else:
    df = load_sample_data()
    st.sidebar.success("✅ Using sample data for demonstration")

# Data validation
required_columns = ['Date', 'Revenue', 'Quantity_Sold']
if df is not None:
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"❌ Missing columns: {missing_columns}")
        st.info("""
        **Please ensure your file contains these columns:**
        - Date: Date column (YYYY-MM-DD format)
        - Revenue: Daily revenue figures
        - Quantity_Sold: Number of items sold per day
        """)
        st.stop()

# Enhanced Export Function
def create_enhanced_excel_export(revenue_forecast, quantity_forecast, forecast_days, restaurant_info):
    """Create comprehensive Excel file with forecast data and restaurant branding"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Define formats with restaurant colors
        header_format = workbook.add_format({
            'bold': True,
            'font_color': 'white',
            'bg_color': MASLOW_COLORS['primary'].replace('#', ''),
            'border': 1
        })
        
        # Revenue forecast
        revenue_export = revenue_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days)
        revenue_export.columns = ['Date', 'Revenue_Forecast', 'Revenue_Lower', 'Revenue_Upper']
        revenue_export.to_excel(writer, sheet_name='Revenue_Forecast', index=False)
        
        # Quantity forecast
        quantity_export = quantity_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_days)
        quantity_export.columns = ['Date', 'Quantity_Forecast', 'Quantity_Lower', 'Quantity_Upper']
        quantity_export.to_excel(writer, sheet_name='Quantity_Forecast', index=False)
        
        # Summary
        summary_data = {
            'Restaurant': [restaurant_info['name']] * 4,
            'Metric': ['Total_Revenue_Forecast', 'Total_Quantity_Forecast', 'Avg_Daily_Revenue', 'Avg_Daily_Quantity'],
            'Value': [
                f"€{revenue_export['Revenue_Forecast'].sum():,.2f}",
                f"{quantity_export['Quantity_Forecast'].sum():,.0f}",
                f"€{revenue_export['Revenue_Forecast'].mean():,.2f}",
                f"{quantity_export['Quantity_Forecast'].mean():,.0f}"
            ],
            'Forecast_Period': [f"{forecast_days} days"] * 4,
            'Generated_Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 4
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
    
    return output.getvalue()

# Display data overview
with st.expander(f"📋 {CURRENT_THEME['name']} - Data Overview", expanded=False):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🍽️ Total Orders", f"{len(df):,}")
    with col2:
        st.metric("📅 Date Range", f"{(df['Date'].max() - df['Date'].min()).days} days")
    with col3:
        st.metric("💰 Total Revenue", f"€{df['Revenue'].sum():,.2f}")
    with col4:
        if df['Quantity_Sold'].sum() > 0:
            avg_order = df['Revenue'].sum() / df['Quantity_Sold'].sum()
            st.metric("🧾 Avg Order Value", f"€{avg_order:.2f}")
        else:
            st.metric("🧾 Avg Order Value", "N/A")
    
    st.dataframe(df.head(), use_container_width=True)

# Forecast Settings
st.sidebar.header("🔧 Forecast Settings")
forecast_days = st.sidebar.slider("Forecast Period (days)", min_value=7, max_value=90, value=30, help="Number of days to forecast")
confidence_interval = st.sidebar.slider("Confidence Level", min_value=0.8, max_value=0.99, value=0.95, help="Statistical confidence for predictions")

# Forecasting Function
def create_enhanced_forecast_model(data, target_col, model_name, restaurant_key=None):
    """Create and train enhanced Prophet model with restaurant-specific parameters"""
    try:
        model_df = data.groupby("Date")[target_col].sum().reset_index()
        model_df.columns = ["ds", "y"]
        model_df = model_df.dropna()
        
        if len(model_df) < 2:
            st.error(f"❌ Not enough data points for {model_name} forecasting.")
            return None, None
        
        # Restaurant-specific model parameters
        seasonality_params = {
            'maslow': {'weekly_seasonality': True, 'daily_seasonality': True},
            'fellows': {'weekly_seasonality': True, 'daily_seasonality': False},
            'temple': {'weekly_seasonality': True, 'daily_seasonality': True}
        }
        
        restaurant_key = restaurant_key or selected_restaurant
        params = seasonality_params.get(restaurant_key, {'weekly_seasonality': True, 'daily_seasonality': True})
        
        model = Prophet(
            interval_width=confidence_interval,
            daily_seasonality=params['daily_seasonality'],
            weekly_seasonality=params['weekly_seasonality'],
            yearly_seasonality=True if len(model_df) > 365 else False,
            changepoint_prior_scale=0.05
        )
        
        model.fit(model_df)
        
        future = model.make_future_dataframe(periods=forecast_days)
        forecast = model.predict(future)
        
        return model, forecast
    except Exception as e:
        st.error(f"❌ Error in {model_name} forecasting: {str(e)}")
        return None, None

# Multi-Restaurant Comparison Function
def create_multi_restaurant_comparison():
    """Create comparison analysis for all three restaurants"""
    
    st.markdown("""
    <div class="comparison-card">
        <h2>🏢 MASLOW GROUP - Multi-Restaurant Comparison</h2>
        <p>Comparative Analysis Across All Restaurant Brands</p>
        <p>📍 All Located at: 84 rue du Fg St Denis, 75010 Paris</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample comparison data
    comparison_data = {
        'Restaurant': ['Maslow Mégisserie', 'Fellows Restaurant', 'Maslow Temple'],
        'Concept': ['Shared Plates', 'Artisanal Pasta', 'Premium Experience'],
        'Avg_Revenue': [1200, 950, 1800],
        'Avg_Quantity': [180, 140, 120],
        'AOV': [6.67, 6.79, 15.00],
        'Primary_Color': ['#FF8C00', '#2F2F2F', '#8B0000']
    }
    
    comp_df = pd.DataFrame(comparison_data)
    
    # Revenue Comparison Chart
    fig_revenue_comp = go.Figure()
    
    for i, row in comp_df.iterrows():
        fig_revenue_comp.add_trace(go.Bar(
            name=row['Restaurant'],
            x=[row['Restaurant']], 
            y=[row['Avg_Revenue']],
            marker_color=row['Primary_Color'],
            text=f"€{row['Avg_Revenue']}",
            textposition='auto'
        ))
    
    fig_revenue_comp.update_layout(
        title="💰 Average Daily Revenue Comparison",
        yaxis_title="Revenue (€)",
        xaxis_title="Restaurant",
        showlegend=False,
        height=400
    )
    
    # Quantity Comparison Chart
    fig_quantity_comp = go.Figure()
    
    for i, row in comp_df.iterrows():
        fig_quantity_comp.add_trace(go.Bar(
            name=row['Restaurant'],
            x=[row['Restaurant']], 
            y=[row['Avg_Quantity']],
            marker_color=row['Primary_Color'],
            text=f"{row['Avg_Quantity']}",
            textposition='auto'
        ))
    
    fig_quantity_comp.update_layout(
        title="🍽️ Average Daily Quantity Comparison",
        yaxis_title="Quantity Sold",
        xaxis_title="Restaurant",
        showlegend=False,
        height=400
    )
    
    # Display charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig_revenue_comp, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_quantity_comp, use_container_width=True)
    
    # Performance Summary
    st.subheader("📊 Performance Summary")
    st.dataframe(comp_df[['Restaurant', 'Concept', 'Avg_Revenue', 'Avg_Quantity', 'AOV']], use_container_width=True)
    
    # Strategic Insights
    st.subheader("🎯 Strategic Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🍽️ Maslow Mégisserie**
        - **Strength**: Balanced volume & revenue
        - **Focus**: Shared plates experience
        - **Opportunity**: Optimize plate combinations
        """)
    
    with col2:
        st.markdown("""
        **🍝 Fellows Restaurant** 
        - **Strength**: Consistent pasta quality
        - **Focus**: Artisanal preparation
        - **Opportunity**: Increase wine pairings
        """)
    
    with col3:
        st.markdown("""
        **🏛️ Maslow Temple**
        - **Strength**: Highest AOV - premium positioning
        - **Focus**: Luxury dining experience
        - **Opportunity**: Maintain exclusivity
        """)

# Create forecasts
with st.spinner("🔮 Generating forecasts..."):
    revenue_model, forecast_rev = create_enhanced_forecast_model(df, "Revenue", "Revenue")
    quantity_model, forecast_qty = create_enhanced_forecast_model(df, "Quantity_Sold", "Quantity")

# Export functionality
if forecast_rev is not None and forecast_qty is not None:
    st.sidebar.header("📤 Export Forecasts")
    
    excel_data = create_enhanced_excel_export(
        forecast_rev, 
        forecast_qty, 
        forecast_days, 
        CURRENT_THEME
    )
    
    filename = f"{selected_restaurant}_forecast_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    st.sidebar.download_button(
        label="📥 Download Excel Report",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help=f"Download detailed forecast data for {CURRENT_THEME['name']}"
    )

# Enhanced Plotting Function
def create_restaurant_themed_chart(model, forecast, title, color_scheme):
    """Create forecast chart with restaurant-specific theming"""
    fig = plot_plotly(model, forecast)
    
    # Apply restaurant theme
    fig.update_traces(
        line=dict(color=color_scheme, width=3),
        name="Forecast"
    )
    
    # Enhanced styling
    fig.update_layout(
        title=dict(
            text=f"{title} - {CURRENT_THEME['name']}",
            font=dict(size=18, color=MASLOW_COLORS['text']),
            x=0.5
        ),
        paper_bgcolor='white',
        plot_bgcolor=MASLOW_COLORS['background'],
        font=dict(color=MASLOW_COLORS['text'], size=12),
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

# Dashboard Views
if view_toggle == "📊 Combined Dashboard":
    # Revenue Forecasting
    st.header(f"💰 Revenue Forecast - {CURRENT_THEME['name']}")
    
    if forecast_rev is not None:
        st.subheader(f"📅 {forecast_days}-Day Revenue Forecast")
        fig_rev = create_restaurant_themed_chart(
            revenue_model, 
            forecast_rev, 
            "Revenue Forecast", 
            MASLOW_COLORS['secondary']
        )
        st.plotly_chart(fig_rev, use_container_width=True)
        
        # Revenue metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            revenue_df = df.groupby("Date")["Revenue"].sum().reset_index()
            avg_historical = revenue_df['Revenue'].mean()
            st.metric("📊 Avg Historical Revenue", f"€{avg_historical:,.2f}")
        
        with col2:
            if len(forecast_rev) > 0:
                predicted_tomorrow = forecast_rev[forecast_rev['ds'] == forecast_rev['ds'].max()]['yhat'].values[0]
                st.metric("🔮 Tomorrow's Forecast", f"€{predicted_tomorrow:,.2f}")
        
        with col3:
            future_avg = forecast_rev.tail(forecast_days)['yhat'].mean()
            change_pct = ((future_avg - avg_historical) / avg_historical) * 100
            st.metric("📈 Avg Future Revenue", f"€{future_avg:,.2f}", f"{change_pct:+.1f}%")
        
        with col4:
            total_forecast = forecast_rev.tail(forecast_days)['yhat'].sum()
            st.metric(f"💰 Total {forecast_days}-Day Revenue", f"€{total_forecast:,.2f}")

    # Quantity Forecasting
    st.header(f"🍽️ Quantity Forecast - {CURRENT_THEME['name']}")
    
    if forecast_qty is not None:
        st.subheader(f"📅 {forecast_days}-Day Quantity Forecast")
        fig_qty = create_restaurant_themed_chart(
            quantity_model, 
            forecast_qty, 
            "Quantity Forecast", 
            MASLOW_COLORS['accent']
        )
        st.plotly_chart(fig_qty, use_container_width=True)
        
        # Quantity metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            quantity_df = df.groupby("Date")["Quantity_Sold"].sum().reset_index()
            avg_historical_qty = quantity_df['Quantity_Sold'].mean()
            st.metric("📊 Avg Historical Quantity", f"{avg_historical_qty:.0f}")
        
        with col2:
            if len(forecast_qty) > 0:
                predicted_qty_tomorrow = forecast_qty[forecast_qty['ds'] == forecast_qty['ds'].max()]['yhat'].values[0]
                st.metric("🔮 Tomorrow's Quantity", f"{predicted_qty_tomorrow:.0f}")
        
        with col3:
            future_avg_qty = forecast_qty.tail(forecast_days)['yhat'].mean()
            qty_change_pct = ((future_avg_qty - avg_historical_qty) / avg_historical_qty) * 100
            st.metric("📈 Avg Future Quantity", f"{future_avg_qty:.0f}", f"{qty_change_pct:+.1f}%")
        
        with col4:
            total_qty_forecast = forecast_qty.tail(forecast_days)['yhat'].sum()
            st.metric(f"🍽️ Total {forecast_days}-Day Quantity", f"{total_qty_forecast:.0f}")

elif view_toggle == "💰 Revenue Focus":
    st.header(f"💰 Deep Revenue Analysis - {CURRENT_THEME['name']}")
    
    if forecast_rev is not None:
        fig_rev = create_restaurant_themed_chart(revenue_model, forecast_rev, "Revenue Deep Dive", MASLOW_COLORS['secondary'])
        st.plotly_chart(fig_rev, use_container_width=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <h4 style="color: {MASLOW_COLORS['secondary']};">💰 Revenue Insights</h4>
            <p>This focused view helps optimize pricing strategy and revenue management for {CURRENT_THEME['name']}.</p>
        </div>
        """, unsafe_allow_html=True)

elif view_toggle == "🍽️ Quantity Focus":
    st.header(f"🍽️ Deep Quantity Analysis - {CURRENT_THEME['name']}")
    
    if forecast_qty is not None:
        fig_qty = create_restaurant_themed_chart(quantity_model, forecast_qty, "Quantity Deep Dive", MASLOW_COLORS['accent'])
        st.plotly_chart(fig_qty, use_container_width=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <h4 style="color: {MASLOW_COLORS['accent']};">🍽️ Quantity Insights</h4>
            <p>This focused view helps optimize operations and staffing for {CURRENT_THEME['name']}.</p>
        </div>
        """, unsafe_allow_html=True)

elif view_toggle == "📈 Comparison View":
    st.header(f"📈 Revenue vs Quantity Comparison - {CURRENT_THEME['name']}")
    
    if forecast_rev is not None and forecast_qty is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_rev = create_restaurant_themed_chart(revenue_model, forecast_rev, "Revenue", MASLOW_COLORS['secondary'])
            st.plotly_chart(fig_rev, use_container_width=True)
        
        with col2:
            fig_qty = create_restaurant_themed_chart(quantity_model, forecast_qty, "Quantity", MASLOW_COLORS['accent'])
            st.plotly_chart(fig_qty, use_container_width=True)
        
        # Correlation analysis
        st.subheader("📊 Revenue-Quantity Correlation")
        correlation = df['Revenue'].corr(df['Quantity_Sold'])
        st.metric("📈 Correlation Coefficient", f"{correlation:.3f}")
        
        if correlation > 0.7:
            st.success("🟢 Strong positive correlation - Quantity drives revenue effectively")
        elif correlation > 0.4:
            st.warning("🟡 Moderate correlation - Room for pricing optimization") 
        else:
            st.error("🔴 Weak correlation - Review pricing strategy")

elif view_toggle == "🏢 Multi-Restaurant Comparison":
    create_multi_restaurant_comparison()

# Operational Insights (only for single restaurant views)
if view_toggle != "🏢 Multi-Restaurant Comparison":
    st.header(f"👨‍🍳 {CURRENT_THEME['name']} - Operational Insights")

    def get_restaurant_specific_recommendations(revenue, quantity, restaurant_type):
        """Restaurant-specific operational recommendations"""
        if restaurant_type == 'maslow':
            if revenue < 800 or quantity < 120:
                return "🟢 Light Service (2-3 staff)", "Focus on plate quality and sharing experience"
            elif revenue < 1800 or quantity < 280:
                return "🟡 Standard Service (4-6 staff)", "Maintain 2-3 plates per person rhythm"
            else:
                return "🔴 Full Service (7+ staff)", "High volume - ensure sharing plate timing"
        
        elif restaurant_type == 'fellows':
            if revenue < 600 or quantity < 100:
                return "🟢 Minimal Service (2-3 staff)", "Focus on pasta preparation quality"
            elif revenue < 1400 or quantity < 250:
                return "🟡 Standard Service (4-5 staff)", "Artisanal pasta requires skilled preparation"
            else:
                return "🔴 Full Service (6+ staff)", "High pasta volume - ensure fresh preparation"
        
        elif restaurant_type == 'temple':
            if revenue < 1200 or quantity < 80:
                return "🟢 Premium Light (3-4 staff)", "Maintain premium service standards"
            elif revenue < 2500 or quantity < 160:
                return "🟡 Premium Standard (5-7 staff)", "Temple experience requires attention to detail"
            else:
                return "🔴 Premium Full (8+ staff)", "High-end service - ensure luxury experience"
        
        else:
            if revenue < 800 or quantity < 150:
                return "🟢 Minimal Service (2-3 staff)", "Light day operations"
            elif revenue < 1800 or quantity < 350:
                return "🟡 Standard Service (4-6 staff)", "Regular operations"
            else:
                return "🔴 Full Service (7+ staff)", "High volume operations"

    try:
        if forecast_rev is not None and forecast_qty is not None:
            latest_rev = forecast_rev[forecast_rev["ds"] == forecast_rev["ds"].max()]["yhat"].values[0]
            latest_qty = forecast_qty[forecast_qty["ds"] == forecast_qty["ds"].max()]["yhat"].values[0]
            
            staff_rec, staff_note = get_restaurant_specific_recommendations(latest_rev, latest_qty, selected_restaurant)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🍽️ Tomorrow's Staffing", staff_rec)
                st.markdown(f"""
                <div class="insight-card">
                    <p style="color: {MASLOW_COLORS['text']};">{staff_note}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                week_rev = forecast_rev.tail(7)['yhat'].mean()
                week_qty = forecast_qty.tail(7)['yhat'].mean()
                week_staff, week_note = get_restaurant_specific_recommendations(week_rev, week_qty, selected_restaurant)
                st.metric("📅 Weekly Average Staffing", week_staff)
                st.markdown(f"""
                <div class="insight-card">
                    <p style="color: {MASLOW_COLORS['text']};">{week_note}</p>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.warning("Could not generate operational insights")

# Customer Insights
if view_toggle != "🏢 Multi-Restaurant Comparison":
    st.header(f"👥 Customer Insights - {CURRENT_THEME['name']}")

    def get_restaurant_customer_metrics(restaurant_type, quantity_forecast, revenue_forecast, forecast_days):
        """Calculate restaurant-specific customer metrics"""
        metrics = {}
        
        total_quantity = quantity_forecast["yhat"].tail(forecast_days).sum()
        total_revenue = revenue_forecast["yhat"].tail(forecast_days).sum()
        
        if restaurant_type == 'maslow':
            estimated_customers = int(total_quantity / 2.5)
            metrics['customer_concept'] = "2-3 shared plates per person"
            metrics['optimal_plates'] = 2.5
            
        elif restaurant_type == 'fellows':
            estimated_customers = int(total_quantity / 1.3)
            metrics['customer_concept'] = "Pasta + sides/dessert"
            metrics['optimal_plates'] = 1.3
            
        elif restaurant_type == 'temple':
            estimated_customers = int(total_quantity / 4.0)
            metrics['customer_concept'] = "Premium tasting experience"
            metrics['optimal_plates'] = 4.0
        
        else:
            estimated_customers = int(total_quantity / 2.0)
            metrics['customer_concept'] = "Standard dining"
            metrics['optimal_plates'] = 2.0
        
        metrics['estimated_customers'] = estimated_customers
        metrics['avg_daily_customers'] = estimated_customers / forecast_days
        metrics['avg_order_value'] = total_revenue / estimated_customers if estimated_customers > 0 else 0
        
        return metrics

    try:
        if forecast_rev is not None and forecast_qty is not None:
            customer_metrics = get_restaurant_customer_metrics(
                selected_restaurant, 
                forecast_qty, 
                forecast_rev, 
                forecast_days
            )
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "🧑‍🤝‍🧑 Estimated Customers", 
                    f"{customer_metrics['estimated_customers']:,}",
                    f"({customer_metrics['avg_daily_customers']:.0f}/day)"
                )
            
            with col2:
                historical_aov = df['Revenue'].sum() / df['Quantity_Sold'].sum() if df['Quantity_Sold'].sum() > 0 else 0
                aov_change = ((customer_metrics['avg_order_value'] - historical_aov) / historical_aov) * 100 if historical_aov > 0 else 0
                st.metric(
                    "🧾 Forecast Avg Order Value", 
                    f"€{customer_metrics['avg_order_value']:.2f}", 
                    f"{aov_change:+.1f}%"
                )
            
            with col3:
                actual_plates_per_customer = forecast_qty["yhat"].tail(forecast_days).sum() / customer_metrics['estimated_customers']
                optimal_check = "✅ Optimal" if abs(actual_plates_per_customer - customer_metrics['optimal_plates']) < 0.5 else "⚠️ Review"
                st.metric(
                    "🍽️ Plates per Customer", 
                    f"{actual_plates_per_customer:.1f}", 
                    optimal_check
                )
            
            with col4:
                st.metric("💡 Dining Concept", customer_metrics['customer_concept'])
            
            # Restaurant-specific recommendations
            st.markdown(f"""
            <div class="insight-card">
                <h4 style="color: {MASLOW_COLORS['primary']};">🎯 {CURRENT_THEME['name']} Recommendations</h4>
            """, unsafe_allow_html=True)
            
            if selected_restaurant == 'maslow':
                st.markdown("""
                    <p><strong>Shared Plates Strategy:</strong> Maintain 2-3 plates per person for optimal sharing experience</p>
                    <p><strong>Service Style:</strong> Plates arrive at kitchen rhythm - educate staff on timing</p>
                    <p><strong>Pricing:</strong> Focus on premium ingredients to justify shared plate pricing</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif selected_restaurant == 'fellows':
                st.markdown("""
                    <p><strong>Pasta Focus:</strong> Artisanal preparation requires skilled kitchen staff</p>
                    <p><strong>Portion Strategy:</strong> Balance pasta portion with appetizers/desserts</p>
                    <p><strong>Wine Pairing:</strong> Promote wine pairings to increase AOV</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif selected_restaurant == 'temple':
                st.markdown("""
                    <p><strong>Premium Experience:</strong> 4+ course tasting approach</p>
                    <p><strong>Service Excellence:</strong> Each dish should be an experience</p>
                    <p><strong>Pricing Strategy:</strong> Premium positioning requires flawless execution</p>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.warning("Could not calculate customer insights")

# Performance Monitoring
st.header("📊 Dashboard Performance")
col1, col2, col3 = st.columns(3)

with col1:
    if df is not None:
        data_quality = "🟢 Good" if len(df) > 100 else "🟡 Limited"
        st.metric("📋 Data Quality", data_quality, f"{len(df)} records")

with col2:
    forecast_status = "🟢 Active" if forecast_rev is not None else "🔴 Failed"
    st.metric("🔮 Forecast Status", forecast_status)

with col3:
    if view_toggle == "🏢 Multi-Restaurant Comparison":
        theme_status = "🏢 All Restaurants"
    else:
        theme_status = f"🎨 {CURRENT_THEME['name']}"
    st.metric("🏷️ Current Theme", theme_status)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="
    text-align: center; 
    padding: 2.5rem; 
    background: linear-gradient(135deg, {MASLOW_COLORS['background']}, white); 
    border-radius: 15px; 
    margin-top: 2rem;
    border: 2px solid {MASLOW_COLORS['primary']};
">
    <h2 style="color: {MASLOW_COLORS['primary']}; margin-bottom: 1rem;">
        🍽️ MASLOW RESTAURANT GROUP
    </h2>
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin-bottom: 1.5rem;">
        <div style="margin: 0.5rem;">
            <h4 style="color: {RESTAURANT_THEMES['maslow']['colors']['primary']};">Maslow Mégisserie</h4>
            <p style="color: {MASLOW_COLORS['text']}; font-size: 0.9em;">Artisanal Vegetarian • Shared Plates</p>
        </div>
        <div style="margin: 0.5rem;">
            <h4 style="color: {RESTAURANT_THEMES['fellows']['colors']['primary']};">Fellows Restaurant</h4>
            <p style="color: {MASLOW_COLORS['text']}; font-size: 0.9em;">Artisanal Pasta • 100% Maison</p>
        </div>
        <div style="margin: 0.5rem;">
            <h4 style="color: {RESTAURANT_THEMES['temple']['colors']['primary']};">Maslow Temple</h4>
            <p style="color: {MASLOW_COLORS['text']}; font-size: 0.9em;">Premium Experience • Temple</p>
        </div>
    </div>
    <p style="color: {MASLOW_COLORS['text']}; font-weight: bold;">
        📍 84 rue du Fg St Denis, 75010 Paris | 📊 Multi-Restaurant Forecast Dashboard
    </p>
    <p style="color: {MASLOW_COLORS['text']}; font-size: 0.9em;">
        Advanced Analytics Platform | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </p>
    <p style="color: {MASLOW_COLORS['text']}; font-size: 0.9em;">
        🌱 Data-Driven Decisions • 🧪 Advanced Analytics • 📈 Revenue Optimization
    </p>
    <div style="margin-top: 1rem;">
        <strong style="color: {MASLOW_COLORS['primary']};">
            {'Currently viewing: All Restaurants | Multi-Restaurant Analysis' if view_toggle == "🏢 Multi-Restaurant Comparison" else f'Currently viewing: {CURRENT_THEME["name"]} | View Mode: {view_toggle}'}
        </strong>
    </div>
</div>
""", unsafe_allow_html=True)