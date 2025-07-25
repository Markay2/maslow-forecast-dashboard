import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import math
import io

# Page configuration
st.set_page_config(
    page_title="Restaurant Forecasting Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Restaurant configurations with enhanced data
restaurants = {
    'maslow': {
        'name': 'Maslow Mégisserie',
        'concept': 'Artisanal Vegetarian • Shared Plates',
        'color': '#FF8C00',
        'light_color': '#FFE4B5',
        'base_metrics': {
            'revenue': 1200,
            'customers': 72,
            'staff_needed': 8,
            'products': {
                'Vegetarian Bowl': 25,
                'Shared Tapas': 30,
                'Artisan Salads': 15,
                'Fresh Juices': 20,
                'Dessert Plates': 12
            }
        }
    },
    'fellows': {
        'name': 'Fellows Restaurant',
        'concept': 'Artisanal Pasta • 100% Maison',
        'color': '#2F2F2F',
        'light_color': '#E8E8E8',
        'base_metrics': {
            'revenue': 950,
            'customers': 108,
            'staff_needed': 6,
            'products': {
                'Fresh Pasta': 40,
                'Risotto': 20,
                'Wine Selection': 35,
                'Antipasti': 18,
                'Tiramisu': 15
            }
        }
    },
    'temple': {
        'name': 'Maslow Temple',
        'concept': 'Premium Experience • Temple',
        'color': '#8B0000',
        'light_color': '#FFB6C1',
        'base_metrics': {
            'revenue': 1800,
            'customers': 30,
            'staff_needed': 12,
            'products': {
                'Tasting Menu': 15,
                'Premium Wine': 25,
                'Appetizer Course': 30,
                'Main Course': 30,
                'Dessert Course': 30
            }
        }
    }
}

# Initialize session state
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'selected_restaurant' not in st.session_state:
    st.session_state.selected_restaurant = 'maslow'
if 'forecast_days' not in st.session_state:
    st.session_state.forecast_days = 7
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'detailed_forecast'
if 'use_uploaded_data' not in st.session_state:
    st.session_state.use_uploaded_data = False

# Generate forecast data based on source - moved up to get colors early
if st.session_state.use_uploaded_data and st.session_state.uploaded_data is not None:
    restaurant_name = "Your Restaurant"
    restaurant_color = "#4CAF50"
else:
    if not st.session_state.use_uploaded_data:
        current_restaurant = restaurants[st.session_state.selected_restaurant]
        restaurant_name = current_restaurant['name']
        restaurant_color = current_restaurant['color']
    else:
        restaurant_color = "#4CAF50"

# Custom CSS for styling - now with dynamic colors
st.markdown(f"""
<style>
    .main-header {{
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid;
        margin-bottom: 2rem;
    }}
    
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid {restaurant_color};
        margin-bottom: 1rem;
    }}
    
    .forecast-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid {restaurant_color}40;
    }}
    
    .insight-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid {restaurant_color};
    }}
    
    .comparison-card {{
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }}
    
    .upload-section {{
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }}
    
    .stSelectbox > div > div {{
        background-color: white;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
    }}
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {{
        color: {restaurant_color};
    }}
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p {{
        color: {restaurant_color};
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

def calculate_staff_requirement(customers, restaurant_key):
    """Calculate staff needed based on customer volume"""
    base_staff = restaurants[restaurant_key]['base_metrics']['staff_needed']
    base_customers = restaurants[restaurant_key]['base_metrics']['customers']
    
    # Staff scaling formula: base staff + additional staff based on customer increase
    if restaurant_key == 'temple':
        staff_ratio = 0.4  # Premium service needs more staff per customer
    elif restaurant_key == 'maslow':
        staff_ratio = 0.11  # Shared plates need moderate staffing
    else:
        staff_ratio = 0.06  # Fellows - efficient pasta service
    
    calculated_staff = base_staff + (customers - base_customers) * staff_ratio
    return max(3, math.ceil(calculated_staff))  # Minimum 3 staff

def generate_forecast_from_data(uploaded_data, days_ahead):
    """Generate forecast from uploaded data"""
    try:
        # Ensure we have the required columns
        required_columns = ['date', 'revenue', 'customers']
        missing_columns = [col for col in required_columns if col not in uploaded_data.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            st.info("Required columns: date, revenue, customers")
            st.info("Optional columns: staff, product quantities")
            return None
        
        # Convert date column
        uploaded_data['date'] = pd.to_datetime(uploaded_data['date'])
        uploaded_data = uploaded_data.sort_values('date')
        
        # Calculate basic statistics for forecasting
        avg_revenue = uploaded_data['revenue'].mean()
        avg_customers = uploaded_data['customers'].mean()
        revenue_std = uploaded_data['revenue'].std()
        customers_std = uploaded_data['customers'].std()
        
        # Generate forecast
        forecast_data = []
        last_date = uploaded_data['date'].max()
        
        for i in range(days_ahead):
            forecast_date = last_date + timedelta(days=i+1)
            
            # Add some realistic variation and trend
            trend_factor = 1.0 + (0.1 * math.sin(2 * math.pi * i / 365))  # Seasonal trend
            random_factor = 0.9 + np.random.random() * 0.2  # ±10% variation
            
            forecasted_revenue = int(avg_revenue * trend_factor * random_factor)
            forecasted_customers = int(avg_customers * trend_factor * random_factor)
            
            # If staff column exists in uploaded data, use it for calculation
            if 'staff' in uploaded_data.columns:
                avg_staff = uploaded_data['staff'].mean()
                forecasted_staff = max(3, int(avg_staff * trend_factor * random_factor))
            else:
                # Calculate based on customers (default logic)
                forecasted_staff = max(3, math.ceil(forecasted_customers * 0.1))
            
            forecast_row = {
                'date': forecast_date.strftime('%b %d'),
                'full_date': forecast_date.strftime('%Y-%m-%d'),
                'revenue': forecasted_revenue,
                'customers': forecasted_customers,
                'staff_needed': forecasted_staff,
                'day_of_week': forecast_date.strftime('%A')
            }
            
            # Add product forecasts if product columns exist
            product_columns = [col for col in uploaded_data.columns if col not in ['date', 'revenue', 'customers', 'staff']]
            for product in product_columns:
                if uploaded_data[product].dtype in ['int64', 'float64']:
                    avg_product = uploaded_data[product].mean()
                    forecast_row[product] = int(avg_product * trend_factor * random_factor)
            
            forecast_data.append(forecast_row)
        
        return pd.DataFrame(forecast_data)
        
    except Exception as e:
        st.error(f"Error processing uploaded data: {str(e)}")
        return None

def generate_enhanced_forecast_data(restaurant_key, days):
    """Generate comprehensive forecast data for default restaurants"""
    restaurant = restaurants[restaurant_key]
    base = restaurant['base_metrics']
    
    data = []
    
    for i in range(days):
        date = datetime.now() + timedelta(days=i+1)
        
        # Add realistic variation
        weekend_boost = 1.3 if date.weekday() >= 4 else 1.0  # Friday, Saturday, Sunday
        seasonal_factor = 1.0 + 0.2 * math.sin(2 * math.pi * date.timetuple().tm_yday / 365)
        random_variation = 0.85 + np.random.random() * 0.3
        
        # Calculate base metrics
        multiplier = weekend_boost * seasonal_factor * random_variation
        
        customers = int(base['customers'] * multiplier)
        revenue = int(base['revenue'] * multiplier)
        staff_needed = calculate_staff_requirement(customers, restaurant_key)
        
        # Calculate product quantities
        products = {}
        for product, base_qty in base['products'].items():
            products[product] = int(base_qty * multiplier)
        
        data.append({
            'date': date.strftime('%b %d'),
            'full_date': date.strftime('%Y-%m-%d'),
            'revenue': revenue,
            'customers': customers,
            'staff_needed': staff_needed,
            'day_of_week': date.strftime('%A'),
            **products
        })
    
    return pd.DataFrame(data)

def create_metric_card(title, value, subtitle=""):
    """Create a metric card using Streamlit native components"""
    return title, value, subtitle

def create_forecast_charts(forecast_data, restaurant_color):
    """Create comprehensive forecast charts"""
    
    # Main metrics chart
    fig_main = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Revenue Forecast', 'Customer Forecast', 'Staff Requirements', 'Revenue vs Customers'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Revenue
    fig_main.add_trace(
        go.Scatter(x=forecast_data['date'], y=forecast_data['revenue'],
                  mode='lines+markers', name='Revenue', 
                  line=dict(color=restaurant_color, width=3)),
        row=1, col=1
    )
    
    # Customers
    fig_main.add_trace(
        go.Scatter(x=forecast_data['date'], y=forecast_data['customers'],
                  mode='lines+markers', name='Customers',
                  line=dict(color='#1f77b4', width=3)),
        row=1, col=2
    )
    
    # Staff
    fig_main.add_trace(
        go.Scatter(x=forecast_data['date'], y=forecast_data['staff_needed'],
                  mode='lines+markers', name='Staff Needed',
                  line=dict(color='#ff7f0e', width=3)),
        row=2, col=1
    )
    
    # Revenue vs Customers scatter
    fig_main.add_trace(
        go.Scatter(x=forecast_data['customers'], y=forecast_data['revenue'],
                  mode='markers', name='Revenue vs Customers',
                  marker=dict(color=restaurant_color, size=8)),
        row=2, col=2
    )
    
    fig_main.update_layout(height=600, showlegend=False, title_text="Key Metrics Forecast")
    fig_main.update_xaxes(title_text="Date", row=1, col=1)
    fig_main.update_xaxes(title_text="Date", row=1, col=2)
    fig_main.update_xaxes(title_text="Date", row=2, col=1)
    fig_main.update_xaxes(title_text="Customers", row=2, col=2)
    fig_main.update_yaxes(title_text="Revenue (€)", row=1, col=1)
    fig_main.update_yaxes(title_text="Customers", row=1, col=2)
    fig_main.update_yaxes(title_text="Staff Count", row=2, col=1)
    fig_main.update_yaxes(title_text="Revenue (€)", row=2, col=2)
    
    return fig_main

def create_product_forecast_chart(forecast_data, products_list, restaurant_color):
    """Create product quantity forecast chart"""
    fig = go.Figure()
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    for i, product in enumerate(products_list):
        if product in forecast_data.columns:
            fig.add_trace(go.Scatter(
                x=forecast_data['date'],
                y=forecast_data[product],
                mode='lines+markers',
                name=product,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="Product Quantity Forecast",
        xaxis_title="Date",
        yaxis_title="Quantity",
        height=400,
        hovermode='x unified'
    )
    
    return fig

# Sidebar for controls
with st.sidebar:
    st.title("🎛️ Forecasting Controls")
    
    # Data source selection
    st.markdown("### 📊 Data Source")
    data_source = st.radio(
        "Choose data source:",
        ["Default Restaurant Data", "Upload Your Data"],
        key="data_source"
    )
    
    st.session_state.use_uploaded_data = (data_source == "Upload Your Data")
    
    if st.session_state.use_uploaded_data:
        st.markdown("""
        <div class="upload-section">
            <h4 style="margin: 0;">📤 Upload Historical Data</h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">Upload CSV/Excel with your restaurant data</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Required columns: date, revenue, customers. Optional: staff, product quantities"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    st.session_state.uploaded_data = pd.read_csv(uploaded_file)
                else:
                    st.session_state.uploaded_data = pd.read_excel(uploaded_file)
                
                st.success(f"✅ Data uploaded successfully! {len(st.session_state.uploaded_data)} rows")
                
                # Show data preview
                with st.expander("📋 Preview uploaded data"):
                    st.dataframe(st.session_state.uploaded_data.head())
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
                st.session_state.uploaded_data = None
        
        # Sample data template
        st.markdown("---")
        st.markdown("**📋 Sample Data Format:**")
        sample_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'revenue': [1200, 1100, 1300],
            'customers': [72, 65, 78],
            'staff': [8, 7, 9],
            'Pizza': [25, 23, 28],
            'Pasta': [30, 28, 32]
        })
        st.dataframe(sample_data)
        
        # Download sample template
        csv_template = sample_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Template",
            data=csv_template,
            file_name="restaurant_data_template.csv",
            mime="text/csv"
        )
    
    else:
        # Default restaurant selection
        st.session_state.selected_restaurant = st.selectbox(
            "🏢 Select Restaurant",
            options=list(restaurants.keys()),
            format_func=lambda x: restaurants[x]['name'],
            index=list(restaurants.keys()).index(st.session_state.selected_restaurant)
        )
    
    # Forecast period selection
    st.markdown("---")
    st.markdown("### 📅 Forecast Period")
    
    # Custom day selection
    st.session_state.forecast_days = st.selectbox(
        "Select forecast period:",
        options=[1, 2, 3, 4, 5, 6, 7, 14, 21, 30, 60, 90],
        format_func=lambda x: f"{x} day{'s' if x > 1 else ''}",
        index=6  # Default to 7 days
    )
    
    # View selection
    st.markdown("---")
    st.session_state.current_view = st.selectbox(
        "📊 Dashboard View",
        options=['detailed_forecast', 'overview', 'comparison'],
        format_func=lambda x: {
            'detailed_forecast': "🔮 Detailed Forecasting",
            'overview': "📈 Overview Dashboard", 
            'comparison': "🏢 Restaurant Comparison"
        }[x],
        index=['detailed_forecast', 'overview', 'comparison'].index(st.session_state.current_view)
    )

# Generate forecast data based on source
if st.session_state.use_uploaded_data and st.session_state.uploaded_data is not None:
    forecast_data = generate_forecast_from_data(st.session_state.uploaded_data, st.session_state.forecast_days)
    restaurant_name = "Your Restaurant"
    restaurant_color = "#4CAF50"
    products_list = [col for col in st.session_state.uploaded_data.columns if col not in ['date', 'revenue', 'customers', 'staff']]
else:
    if not st.session_state.use_uploaded_data:
        current_restaurant = restaurants[st.session_state.selected_restaurant]
        forecast_data = generate_enhanced_forecast_data(st.session_state.selected_restaurant, st.session_state.forecast_days)
        restaurant_name = current_restaurant['name']
        restaurant_color = current_restaurant['color']
        products_list = list(current_restaurant['base_metrics']['products'].keys())
    else:
        st.warning("Please upload data to continue with forecasting.")
        st.stop()

# Header
if not st.session_state.use_uploaded_data:
    current_restaurant = restaurants[st.session_state.selected_restaurant]
    header_color = current_restaurant['color']
    header_concept = current_restaurant['concept']
else:
    header_color = "#4CAF50"
    header_concept = "Data-driven Forecasting"

st.markdown(f"""
<div class="main-header" style="border-left-color: {header_color};">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="color: {header_color}; margin: 0; font-size: 2.5rem;">
                {restaurant_name}
            </h1>
            <p style="color: #666; margin: 0.5rem 0;">{header_concept}</p>
            <p style="color: #999; font-size: 0.9rem; margin: 0;">📍 84 rue du Fg St Denis, 75010 Paris</p>
        </div>
        <div style="text-align: right;">
            <p style="color: #999; font-size: 0.9rem; margin: 0;">Forecast Period</p>
            <p style="color: {header_color}; font-size: 1.2rem; font-weight: bold; margin: 0;">
                {st.session_state.forecast_days} day{'s' if st.session_state.forecast_days > 1 else ''}
            </p>
            <p style="color: #666; font-size: 0.8rem; margin: 0;">
                {'From uploaded data' if st.session_state.use_uploaded_data else 'Predictive model'}
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if forecast_data is not None and not forecast_data.empty:
    if st.session_state.current_view == 'detailed_forecast':
        # Enhanced forecast view with restaurant-specific colors
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {restaurant_color}CC 0%, {restaurant_color}80 100%); color: white; padding: 1.5rem; border-radius: 10px; margin: 1rem 0;">
            <h2 style="margin: 0; font-size: 1.8rem; color: white;">🔮 Advanced Forecasting Dashboard</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; color: white;">Comprehensive predictions for revenue, customers, staff, and products</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced metrics
        total_revenue = forecast_data['revenue'].sum()
        total_customers = forecast_data['customers'].sum()
        avg_daily_revenue = forecast_data['revenue'].mean()
        avg_staff_needed = forecast_data['staff_needed'].mean()
        peak_customers = forecast_data['customers'].max()
        peak_staff = forecast_data['staff_needed'].max()
        
        # Key Metrics Row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="💰 Total Revenue",
                value=f"€{total_revenue:,}",
                delta=f"Avg: €{avg_daily_revenue:.0f}/day"
            )
        
        with col2:
            st.metric(
                label="👥 Total Customers",
                value=f"{total_customers:,}",
                delta=f"Peak: {peak_customers}"
            )
        
        with col3:
            st.metric(
                label="👨‍🍳 Avg Staff Needed",
                value=f"{avg_staff_needed:.1f}",
                delta=f"Peak: {peak_staff} staff"
            )
        
        with col4:
            aov = total_revenue / total_customers if total_customers > 0 else 0
            st.metric(
                label="🎯 Avg Order Value",
                value=f"€{aov:.0f}"
            )
        
        with col5:
            capacity_utilization = (total_customers / (peak_customers * len(forecast_data))) * 100 if peak_customers > 0 else 0
            st.metric(
                label="📊 Capacity Usage",
                value=f"{capacity_utilization:.1f}%"
            )
        
        # Tabbed forecast displays
        tab1, tab2, tab3 = st.tabs(["📈 Main Metrics", "🍽️ Product Forecast", "📋 Detailed Data"])
        
        with tab1:
            # Main forecast charts
            fig_main = create_forecast_charts(forecast_data, restaurant_color)
            st.plotly_chart(fig_main, use_container_width=True)
            
            # Staff optimization insights
            st.markdown(f"""
            <div class="insight-card">
                <h3 style="color: {restaurant_color};">👨‍🍳 Staff Optimization Insights</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Minimum Staff Required:** {forecast_data['staff_needed'].min()}")
                st.markdown(f"**Maximum Staff Required:** {forecast_data['staff_needed'].max()}")
                st.markdown(f"**Average Staff Required:** {forecast_data['staff_needed'].mean():.1f}")
            
            with col2:
                peak_day = forecast_data.loc[forecast_data['staff_needed'].idxmax(), 'date']
                low_day = forecast_data.loc[forecast_data['staff_needed'].idxmin(), 'date']
                st.markdown(f"**Peak Staffing Day:** {peak_day}")
                st.markdown(f"**Lowest Staffing Day:** {low_day}")
                
                # Calculate staff costs (assuming €15/hour, 8-hour shifts)
                staff_cost = forecast_data['staff_needed'].sum() * 15 * 8
                st.markdown(f"**Estimated Staff Costs:** €{staff_cost:,}")
        
        with tab2:
            # Product forecast
            if products_list:
                fig_products = create_product_forecast_chart(forecast_data, products_list, restaurant_color)
                st.plotly_chart(fig_products, use_container_width=True)
                
                # Product insights
                st.markdown(f"""
                <div class="insight-card">
                    <h3 style="color: {restaurant_color};">🍽️ Product Demand Forecast</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if len(products_list) > 0:
                    product_cols = st.columns(min(len(products_list), 5))  # Max 5 columns
                    
                    for i, product in enumerate(products_list[:5]):  # Show first 5 products
                        if product in forecast_data.columns:
                            with product_cols[i]:
                                total_qty = forecast_data[product].sum()
                                avg_daily = forecast_data[product].mean()
                                st.metric(
                                    label=product,
                                    value=f"{total_qty:,} units",
                                    delta=f"Avg: {avg_daily:.1f}/day"
                                )
                    
                    # Show remaining products in a second row if needed
                    if len(products_list) > 5:
                        remaining_products = products_list[5:10]  # Show next 5
                        product_cols2 = st.columns(len(remaining_products))
                        
                        for i, product in enumerate(remaining_products):
                            if product in forecast_data.columns:
                                with product_cols2[i]:
                                    total_qty = forecast_data[product].sum()
                                    avg_daily = forecast_data[product].mean()
                                    st.metric(
                                        label=product,
                                        value=f"{total_qty:,} units",
                                        delta=f"Avg: {avg_daily:.1f}/day"
                                    )
            else:
                st.info("No product data available for forecasting. Upload data with product columns to see product forecasts.")
        
        with tab3:
            # Detailed data table
            st.markdown(f"""
            <div class="insight-card">
                <h3 style="color: {restaurant_color};">📋 Detailed Forecast Data</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Format the dataframe for display
            display_df = forecast_data.copy()
            display_df['Revenue'] = display_df['revenue'].apply(lambda x: f"€{x:,}")
            display_df['Customers'] = display_df['customers']
            display_df['Staff Needed'] = display_df['staff_needed']
            
            # Select columns to display
            display_columns = ['date', 'Revenue', 'Customers', 'Staff Needed']
            for product in products_list:
                if product in forecast_data.columns:
                    display_columns.append(product)
            
            st.dataframe(display_df[display_columns], use_container_width=True)
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                csv = forecast_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download Forecast Data (CSV)",
                    data=csv,
                    file_name=f"forecast_{restaurant_name.lower().replace(' ', '_')}_{st.session_state.forecast_days}days.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Create Excel file
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    forecast_data.to_excel(writer, sheet_name='Forecast', index=False)
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📊 Download Forecast Data (Excel)",
                    data=excel_data,
                    file_name=f"forecast_{restaurant_name.lower().replace(' ', '_')}_{st.session_state.forecast_days}days.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    elif st.session_state.current_view == 'overview':
        # Original overview functionality
        total_revenue = forecast_data['revenue'].sum()
        total_customers = forecast_data['customers'].sum()
        avg_daily_revenue = forecast_data['revenue'].mean()
        avg_order_value = total_revenue / total_customers if total_customers > 0 else 0
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Total Revenue",
                value=f"€{total_revenue:,}"
            )
        
        with col2:
            st.metric(
                label="📈 Avg Daily Revenue",
                value=f"€{avg_daily_revenue:.0f}"
            )
        
        with col3:
            st.metric(
                label="👥 Total Customers",
                value=f"{total_customers:,}"
            )
        
        with col4:
            st.metric(
                label="🎯 Avg Order Value",
                value=f"€{avg_order_value:.0f}"
            )
        
        # Revenue Forecast Chart
        st.markdown(f"""
        <div class="insight-card">
            <h3 style="color: {restaurant_color}; margin-bottom: 1rem;">
                Revenue Forecast - {st.session_state.forecast_days} day{'s' if st.session_state.forecast_days > 1 else ''}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast_data['date'],
            y=forecast_data['revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color=restaurant_color, width=3),
            marker=dict(color=restaurant_color, size=8)
        ))
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Revenue (€)",
            template="plotly_white",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    else:  # Comparison view - only works with default data
        if st.session_state.use_uploaded_data:
            st.warning("Comparison view is only available with default restaurant data. Please switch to 'Default Restaurant Data' to use this feature.")
        else:
            st.markdown("""
            <div class="insight-card">
                <h3 style="color: #333; margin-bottom: 1rem;">
                    🏢 Multi-Restaurant Performance Comparison
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Generate comparison data for all restaurants
            comparison_data = []
            for rest_key, rest_data in restaurants.items():
                temp_forecast = generate_enhanced_forecast_data(rest_key, st.session_state.forecast_days)
                total_rev = temp_forecast['revenue'].sum()
                total_cust = temp_forecast['customers'].sum()
                avg_staff = temp_forecast['staff_needed'].mean()
                
                comparison_data.append({
                    'Restaurant': rest_data['name'],
                    'Revenue': total_rev,
                    'Customers': total_cust,
                    'AOV': total_rev / total_cust if total_cust > 0 else 0,
                    'Avg Staff': avg_staff,
                    'Color': rest_data['color']
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"Revenue Comparison ({st.session_state.forecast_days} days)")
                fig_revenue = px.bar(
                    comparison_df, 
                    x='Restaurant', 
                    y='Revenue',
                    color='Restaurant',
                    color_discrete_map={row['Restaurant']: row['Color'] for _, row in comparison_df.iterrows()}
                )
                fig_revenue.update_layout(showlegend=False, height=350)
                st.plotly_chart(fig_revenue, use_container_width=True)
            
            with col2:
                st.subheader("Average Staff Requirements")
                fig_staff = px.bar(
                    comparison_df, 
                    x='Restaurant', 
                    y='Avg Staff',
                    color='Restaurant',
                    color_discrete_map={row['Restaurant']: row['Color'] for _, row in comparison_df.iterrows()}
                )
                fig_staff.update_layout(showlegend=False, height=350)
                st.plotly_chart(fig_staff, use_container_width=True)
            
            # Strategic Summary
            st.subheader("Strategic Summary")
            col1, col2, col3 = st.columns(3)
            
            restaurants_list = list(restaurants.items())
            for i, (col, (rest_key, rest_data)) in enumerate(zip([col1, col2, col3], restaurants_list)):
                with col:
                    st.markdown(f"""
                    <div class="comparison-card" style="background-color: {rest_data['light_color']};">
                        <h5 style="color: {rest_data['color']}; font-weight: bold;">{rest_data['name']}</h5>
                        <p style="color: {rest_data['color']}; font-size: 0.9rem;">{rest_data['concept']}</p>
                        <p style="color: {rest_data['color']}; font-size: 0.8rem;">Avg Staff: {comparison_df.iloc[i]['Avg Staff']:.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)

else:
    st.error("Unable to generate forecast data. Please check your input.")

# Business Impact Section with restaurant-specific colors
if st.session_state.use_uploaded_data:
    impact_color = "#4CAF50"
    impact_gradient = "linear-gradient(135deg, #4CAF50 0%, #45a049 100%)"
    company_name = "Your Restaurant"
else:
    impact_color = restaurant_color
    impact_gradient = f"linear-gradient(135deg, {restaurant_color} 0%, {restaurant_color}CC 100%)"
    company_name = restaurant_name

st.markdown(f"""
<div style="background: {impact_gradient}; color: white; padding: 2rem; border-radius: 10px; text-align: center; margin-top: 2rem;">
    <h2 style="font-size: 2rem; margin-bottom: 1rem; color: white;">🎯 Advanced Forecasting Impact</h2>
    <p style="font-size: 1.2rem; margin-bottom: 2rem; color: white; opacity: 0.95;">
        {company_name} - Comprehensive forecasting for revenue, customers, staff optimization, and product planning
    </p>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; text-align: center;">
        <div style="background: rgba(255,255,255,0.15); padding: 1.5rem; border-radius: 10px; backdrop-filter: blur(10px);">
            <div style="font-size: 3rem; font-weight: bold; color: white;">25-35%</div>
            <div style="font-size: 1rem; color: white;">Cost Reduction</div>
            <div style="font-size: 0.8rem; opacity: 0.8; color: white;">Through optimized staffing</div>
        </div>
        <div style="background: rgba(255,255,255,0.15); padding: 1.5rem; border-radius: 10px; backdrop-filter: blur(10px);">
            <div style="font-size: 3rem; font-weight: bold; color: white;">15-25%</div>
            <div style="font-size: 1rem; color: white;">Revenue Increase</div>
            <div style="font-size: 0.8rem; opacity: 0.8; color: white;">Better demand prediction</div>
        </div>
        <div style="background: rgba(255,255,255,0.15); padding: 1.5rem; border-radius: 10px; backdrop-filter: blur(10px);">
            <div style="font-size: 3rem; font-weight: bold; color: white;">40%</div>
            <div style="font-size: 1rem; color: white;">Better Planning</div>
            <div style="font-size: 0.8rem; opacity: 0.8; color: white;">Inventory & staff scheduling</div>
        </div>
        <div style="background: rgba(255,255,255,0.15); padding: 1.5rem; border-radius: 10px; backdrop-filter: blur(10px);">
            <div style="font-size: 3rem; font-weight: bold; color: white;">20%</div>
            <div style="font-size: 1rem; color: white;">Waste Reduction</div>
            <div style="font-size: 0.8rem; opacity: 0.8; color: white;">Accurate product forecasts</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)