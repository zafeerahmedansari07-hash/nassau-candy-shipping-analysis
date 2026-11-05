import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Nassau Candy - Shipping Route Efficiency",
    page_icon="🍬",
    layout="wide"
)

st.title("🍬 Nassau Candy Distributor")
st.subheader("Factory-to-Customer Shipping Route Efficiency Analysis")

# 2. Load and Clean Dataset
@st.cache_data
def load_data():
    # Use 'Nassau Candy Distributor.csv' (or update filename if yours is named differently)
    df = pd.read_csv('Downloads/Nassau_Candy_Project/Nassau Candy Distributor.csv')
    
    # Date formatting & Lead time calculation
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d-%m-%Y', errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d-%m-%Y', errors='coerce')
    df['Shipping Lead Time (days)'] = (df['Ship Date'] - df['Order Date']).dt.days
    
    # Remove negative or invalid lead times
    df = df[df['Shipping Lead Time (days)'] >= 0]
    
    # Factory Mapping Logic
    factory_mapping = {
        'Wonka Bar - Nutty Crunch Surprise': "Lot's O' Nuts",
        'Wonka Bar - Fudge Mallows': "Lot's O' Nuts",
        'Wonka Bar -Scrumdiddlyumptious': "Lot's O' Nuts",
        'Wonka Bar - Milk Chocolate': "Wicked Choccy's",
        'Wonka Bar - Triple Dazzle Caramel': "Wicked Choccy's",
        'Laffy Taffy': "Sugar Shack",
        'SweeTARTS': "Sugar Shack",
        'Nerds': "Sugar Shack",
        'Fun Dip': "Sugar Shack",
        'Fizzy Lifting Drinks': "Sugar Shack",
        'Everlasting Gobstopper': "Secret Factory",
        'Hair Toffee': "The Other Factory",
        'Lickable Wallpaper': "Secret Factory",
        'Wonka Gum': "Secret Factory",
        'Kazookles': "The Other Factory"
    }
    
    factory_coords = {
        "Lot's O' Nuts": {'Lat': 32.881893, 'Lon': -111.768036},
        "Wicked Choccy's": {'Lat': 32.076176, 'Lon': -81.088371},
        "Sugar Shack": {'Lat': 48.119140, 'Lon': -96.181150},
        "Secret Factory": {'Lat': 41.446333, 'Lon': -90.565487},
        "The Other Factory": {'Lat': 35.117500, 'Lon': -89.971107}
    }
    
    df['Factory'] = df['Product Name'].map(factory_mapping).fillna("Unknown Factory")
    df['Factory Latitude'] = df['Factory'].map(lambda x: factory_coords.get(x, {}).get('Lat'))
    df['Factory Longitude'] = df['Factory'].map(lambda x: factory_coords.get(x, {}).get('Lon'))
    
    # Create Route Field
    df['Route'] = df['Factory'] + ' → ' + df['State/Province']
    
    return df

try:
    df = load_data()
    
    # 3. Sidebar Filters
    st.sidebar.header("🔍 Dashboard Filters")
    
    # Region Filter
    regions = ['All'] + sorted(df['Region'].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("Select Region", regions)
    
    # Ship Mode Filter
    ship_modes = ['All'] + sorted(df['Ship Mode'].dropna().unique().tolist())
    selected_ship_mode = st.sidebar.selectbox("Select Ship Mode", ship_modes)
    
    # Apply Filters
    filtered_df = df.copy()
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    if selected_ship_mode != 'All':
        filtered_df = filtered_df[filtered_df['Ship Mode'] == selected_ship_mode]
        
    # 4. KPI Summary Cards
    st.markdown("### 📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Shipments", f"{len(filtered_df):,}")
    col2.metric("Avg Lead Time", f"{filtered_df['Shipping Lead Time (days)'].mean():.1f} Days")
    col3.metric("Total Sales", f"${filtered_df['Sales'].sum():,.2f}")
    col4.metric("Gross Profit", f"${filtered_df['Gross Profit'].sum():,.2f}")
    
    st.markdown("---")
    
    # 5. Visualizations & Analytics
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🚀 Top 10 Most Efficient Routes (Lowest Lead Time)")
        route_efficiency = filtered_df.groupby('Route')['Shipping Lead Time (days)'].agg(['mean', 'count']).reset_index()
        route_efficiency = route_efficiency[route_efficiency['count'] >= 5] # filter for stable routes
        top_efficient = route_efficiency.sort_values(by='mean', ascending=True).head(10)
        
        fig_top = px.bar(
            top_efficient, 
            x='mean', 
            y='Route', 
            orientation='h',
            labels={'mean': 'Average Lead Time (Days)', 'Route': 'Factory → State'},
            title="Fastest Delivery Routes"
        )
        fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)
        
    with col_b:
        st.subheader("⚠️ Top 10 Bottleneck Routes (Highest Lead Time)")
        bottom_inefficient = route_efficiency.sort_values(by='mean', ascending=False).head(10)
        
        fig_bottom = px.bar(
            bottom_inefficient, 
            x='mean', 
            y='Route', 
            orientation='h',
            labels={'mean': 'Average Lead Time (Days)', 'Route': 'Factory → State'},
            title="Slowest Delivery Routes"
        )
        fig_bottom.update_layout(yaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig_bottom, use_container_width=True)

    # 6. Ship Mode Comparison
    st.subheader("📦 Lead Time Comparison by Shipping Mode")
    fig_ship = px.box(
        filtered_df, 
        x='Ship Mode', 
        y='Shipping Lead Time (days)', 
        color='Ship Mode',
        title="Distribution of Shipping Lead Times Across Ship Modes"
    )
    st.plotly_chart(fig_ship, use_container_width=True)

    # 7. Raw Data Preview Table
    with st.expander("📄 View Processed Shipment Data"):
        st.dataframe(filtered_df[['Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'Factory', 'State/Province', 'Shipping Lead Time (days)', 'Sales']])

except Exception as e:
    st.error(f"Error loading dataset: {e}. Please ensure 'Nassau Candy Distributor.csv' is in the same folder as app.py.")