import streamlit as st
import pandas as pd
import plotly.express as px

# Optimize layout viewport strictly for mobile touchscreens
st.set_page_config(
    page_title="Grocery Expenses Mobile Tracker", 
    page_icon="🛒", 
    layout="centered"
)

st.title("🛒 Grocery Expenses Analytics")
st.caption("Live interactive tracking powered by your GitHub Excel data")

@st.cache_data(ttl=300) # Caches for 5 minutes to keep it highly snappy on mobile web browsers
def load_grocery_data():
    # Load the specific worksheet, skipping the initial blank line row layout
    df = pd.read_excel("./data/Grocessary_items.xlsx", sheet_name="Grocery expenses done", header=1)
    
    # Strip spaces from string columns
    string_cols = ['Month', 'Shop', 'Category I', 'Category II', 'Item Name']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Clean numeric fields safely
    df['Total cost'] = pd.to_numeric(df['Total cost'], errors='coerce').fillna(0.0)
    df['Unit cost'] = pd.to_numeric(df['Unit cost'], errors='coerce').fillna(0.0)
    return df

try:
    df = load_grocery_data()

    # --- TOP LEVEL HIGH-VALUE KPIS ---
    total_spend = df['Total cost'].sum()
    total_items = len(df)
    unique_shops = df['Shop'].nunique()

    st.markdown("### 📈 Summary Statistics")
    m1, m2 = st.columns(2)
    with m1:
        st.metric(label="Total Expenses", value=f"€{total_spend:,.2f}")
    with m2:
        st.metric(label="Items Purchased", value=f"{total_items:,}")

    st.markdown("---")

    # --- PHONE COMPATIBLE INTERACTIVE FILTERS ---
    st.markdown("### 🔍 Mobile Filter Panel")
    
    # Fetch lists for dropdown selection filters
    month_list = ["All Months"] + sorted(df['Month'].dropna().unique().tolist())
    shop_list = ["All Shops"] + sorted(df['Shop'].dropna().unique().tolist())
    cat_list = ["All Categories"] + sorted(df['Category I'].dropna().unique().tolist())
    
    selected_month = st.selectbox("Filter by Month:", month_list, index=0)
    selected_shop = st.selectbox("Filter by Shop/Store:", shop_list, index=0)
    selected_cat = st.selectbox("Filter by Category:", cat_list, index=0)

    # Apply filters dynamically
    filtered_df = df.copy()
    if selected_month != "All Months":
        filtered_df = filtered_df[filtered_df['Month'] == selected_month]
    if selected_shop != "All Shops":
        filtered_df = filtered_df[filtered_df['Shop'] == selected_shop]
    if selected_cat != "All Categories":
        filtered_df = filtered_df[filtered_df['Category I'] == selected_cat]

    # Dynamically adjusted metrics
    if selected_month != "All Months" or selected_shop != "All Shops" or selected_cat != "All Categories":
        st.subheader("Filtered View Metrics")
        fm1, fm2 = st.columns(2)
        with fm1:
            st.metric(label="Filtered Spend", value=f"€{filtered_df['Total cost'].sum():,.2f}")
        with fm2:
            st.metric(label="Filtered Items", value=f"{len(filtered_df)}")

    st.markdown("---")

    # --- VISUAL ANALYTICS TARGETED FOR MOBILE VIEWPORTS ---
    st.markdown("### 📊 Spending Breakdowns")

    # Tab 1: Category breakdown
    tab1, tab2, tab3 = st.tabs(["📁 By Category", "🏪 By Shop", "📅 By Month"])
    
    with tab1:
        cat_data = filtered_df.groupby('Category I')['Total cost'].sum().reset_index()
        cat_data = cat_data.sort_values(by='Total cost', ascending=True).tail(10) # Top 10 categories
        
        fig_cat = px.bar(
            cat_data, 
            x='Total cost', 
            y='Category I', 
            orientation='h',
            title="Expenses by Category (Top 10)",
            labels={'Total cost': 'Total Cost (€)', 'Category I': 'Category'},
            color='Total cost',
            color_continuous_scale='Viridis'
        )
        fig_cat.update_layout(margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        st.plotly_chart(fig_cat, use_container_width=True)

    with tab2:
        shop_data = filtered_df.groupby('Shop')['Total cost'].sum().reset_index()
        shop_data = shop_data.sort_values(by='Total cost', ascending=False).head(8) # Top 8 shops
        
        fig_shop = px.pie(
            shop_data, 
            values='Total cost', 
            names='Shop', 
            title="Expense Distribution by Shop",
            hole=0.4
        )
        fig_shop.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_shop, use_container_width=True)

    with tab3:
        month_data = filtered_df.groupby('Month')['Total cost'].sum().reset_index()
        # Sort values logically by volume/order if necessary
        fig_month = px.bar(
            month_data, 
            x='Month', 
            y='Total cost', 
            title="Monthly Expense Performance",
            labels={'Total cost': 'Total Cost (€)'},
            color_discrete_sequence=['#4361EE']
        )
        fig_month.update_layout(margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_month, use_container_width=True)

    st.markdown("---")

    # --- RAW SPREADSHEET VIEWER ---
    with st.expander("🔍 Open Full Raw Grocery Data Sheets"):
        st.dataframe(
            filtered_df[['Month', 'Date', 'Shop', 'Category I', 'Item Name', 'Total cost']], 
            use_container_width=True
        )

except Exception as e:
    st.error(f"Failed to cleanly interpret Grocessary_items.xlsx. Error layout specifics: {e}")