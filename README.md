# 🍽️ Maslow Restaurant Group - Forecast Dashboard

## 📊 Advanced Multi-Restaurant Analytics Platform

A comprehensive forecasting dashboard for the Maslow Restaurant Group, featuring simultaneous analysis across three unique restaurant concepts:

- **🍽️ Maslow Mégisserie**: Artisanal Vegetarian • Shared Plates
- **🍝 Fellows Restaurant**: Artisanal Pasta • 100% Maison  
- **🏛️ Maslow Temple**: Premium Artisanal • Temple Experience

**📍 Location**: 84 rue du Fg St Denis, 75010 Paris

## 🚀 Features

### 📈 Forecasting Capabilities
- **Prophet Time Series Forecasting** with restaurant-specific parameters
- **Revenue & Quantity Predictions** with confidence intervals (80-99%)
- **Seasonal Pattern Detection** adapted for restaurant industry
- **Multi-period forecasting** (7-90 days)

### 🎨 Multi-View Analysis
- **📊 Combined Dashboard**: Overview of revenue and quantity
- **💰 Revenue Focus**: Deep dive into pricing strategies
- **🍽️ Quantity Focus**: Operational planning and capacity management
- **📈 Comparison View**: Side-by-side revenue vs quantity analysis
- **🏢 Multi-Restaurant Comparison**: Simultaneous analysis of all 3 brands

### 🎯 Business Intelligence
- **Customer Behavior Analysis** with restaurant-specific metrics
- **Staffing Recommendations** based on forecasted demand
- **Revenue Optimization Insights** for each concept
- **Cross-Restaurant Performance Comparison**
- **Strategic Business Recommendations**

### 📤 Export & Reporting
- **Branded Excel Reports** with restaurant theming
- **Executive Summary Sheets** with key metrics
- **Forecast Data Export** with confidence bounds
- **Operational Recommendations** for management

## 🛠️ Technical Stack

- **Frontend**: Streamlit with custom CSS theming
- **Forecasting**: Facebook Prophet
- **Visualization**: Plotly with interactive charts
- **Data Processing**: Pandas
- **Export**: XlsxWriter for branded Excel reports

## 📁 File Structure

```
maslow-forecast-dashboard/
├── app.py                          # Main dashboard application
├── requirements.txt                # Python dependencies
├── .streamlit/config.toml         # Streamlit configuration
├── README.md                      # Project documentation
└── cleaned_sales_data_maslow.xlsx # Sample data file (optional)
```

## 🚀 Quick Start

### Option 1: Upload Your Data
1. Launch the application
2. Use the sidebar "Upload File" option
3. Upload your Excel/CSV file with columns: `Date`, `Revenue`, `Quantity_Sold`

### Option 2: Use Sample Data
1. Place your `cleaned_sales_data_maslow.xlsx` file in the project directory
2. Select "Use Local File" in the sidebar

## 📊 Data Requirements

Your data file should contain these columns:
- **Date**: Date column (YYYY-MM-DD format)
- **Revenue**: Daily revenue figures in EUR
- **Quantity_Sold**: Number of items/plates sold per day

## 🎨 Restaurant Themes

Each restaurant has a unique visual theme:

### 🍽️ Maslow Mégisserie (Orange Theme)
- **Concept**: 2-3 shared plates per person
- **Focus**: Artisanal vegetarian dishes
- **Service**: Plates arrive at kitchen rhythm

### 🍝 Fellows Restaurant (Black & White Theme)  
- **Concept**: Artisanal pasta with wine pairings
- **Focus**: 100% house-made pasta
- **Service**: Pasta + appetizers/desserts

### 🏛️ Maslow Temple (Red Theme)
- **Concept**: Premium 4+ course tasting experience
- **Focus**: Luxury dining experience
- **Service**: Each dish as an experience

## 🔧 Configuration

The dashboard automatically adapts to different restaurant concepts with:
- **Dynamic color theming** based on selected restaurant
- **Restaurant-specific forecasting parameters**
- **Customized operational recommendations**
- **Brand-specific customer metrics**

## 📈 Forecasting Models

- **Weekly Seasonality**: Captures day-of-week patterns
- **Daily Seasonality**: For restaurants with distinct meal periods
- **Yearly Seasonality**: For establishments with >365 days of data
- **Custom Seasonalities**: Lunch/dinner patterns for applicable concepts

## 🎯 Business Applications

- **Daily Operations Planning**: Staffing and inventory optimization
- **Revenue Management**: Pricing strategy optimization
- **Multi-Brand Strategy**: Cross-restaurant performance analysis
- **Customer Experience**: Service level recommendations
- **Financial Planning**: Revenue forecasting and budgeting

## 📞 Support

For technical support or business inquiries regarding the Maslow Restaurant Group dashboard, please contact the development team.

---

**🍽️ Maslow Restaurant Group** | *Data-Driven Decisions • Advanced Analytics • Revenue Optimization*