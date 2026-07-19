import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Grocery Expenses Mobile Tracker", 
    page_icon="🛒", 
    layout="centered"
)

st.title("🛒 Grocery Expenses Analytics")
st.caption("Live interactive tracking powered by your GitHub Excel data")

@st.cache_data(ttl=300) 
def load_grocery_data():
    
    df = pd.read_excel("./data/Grocessary_items.xlsx", sheet_name="Grocery expenses done", header=1)
    
    string_cols = ['Month', 'Shop', 'Category I', 'Category II', 'Item Name']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    df['Total cost'] = pd.to_numeric(df['Total cost'], errors='coerce').fillna(0.0)
    df['Unit cost'] = pd.to_numeric(df['Unit cost'], errors='coerce').fillna(0.0)
    return df

try:
    df = load_grocery_data()

    # HIGH-VALUE KPIS
    total_spend = df['Total cost'].sum()
    total_items = len(df)

    st.markdown("### 📈 Summary Statistics")
    m1, m2 = st.columns(2)
    with m1:
        st.metric(label="Total Expenses", value=f"€{total_spend:,.2f}")
    with m2:
        st.metric(label="Items Purchased", value=f"{total_items:,}")

    st.markdown("---")

    # CROSS-MARKET PRICE COMPARE (Total)
    st.markdown("### 🔍 Store Price Comparison (Full)")
    st.write("Find where an item is cheapest based on your purchase history:")
    
    unique_items = sorted(df['Item Name'].dropna().unique().tolist())
    
    search_query1 = st.selectbox("Type or choose an item:", unique_items)
    
    if search_query1:
        item_history = df[df['Item Name'] == search_query1]
        
        if not item_history.empty:
            
            table_display = item_history[['Shop', 'Category I', 'Description', 'Amount', 'Total cost']].rename(
                columns={'Shop': 'Market/Store', 'Category I': 'Category', 'Total cost': 'Total'}
            )
            
            # Render the dynamic query table layout
            st.dataframe(table_display, use_container_width=True, hide_index=True)
            
            # mobile helper tip
            st.caption("💡 *'N/A' means you bought the item as a bulk or weight price packet without a per-unit tracking entry.*")
        else:
            st.info("No market matching logs discovered for that item.")

    st.markdown("---")

    # CROSS-MARKET PRICE COMPARE
    st.markdown("### 🔍 Store Price Comparison Search")
    st.write("Find where an item is cheapest based on your purchase history:")
    
    #unique_items = sorted(df['Item Name'].dropna().unique().tolist())
    
    search_query2 = st.selectbox("Type or choose an item:", unique_items)
    
    if search_query2:
        item_history = df[df['Item Name'] == search_query2]
        
        if not item_history.empty:
            # Group by Store to find standard costs recorded
            # Aggregates Min Unit Cost, Max Unit Cost, and Average Total Paid across trips
            price_comparison = item_history.groupby('Shop').agg(
                Lowest_Unit_Cost=('Unit cost', lambda x: x[x > 0].min() if (x > 0).any() else 0.0),
                Highest_Unit_Cost=('Unit cost', max),
                Avg_Total_Paid=('Total cost', 'mean'),
                Total_Times_Bought=('Item Name', 'count')
            ).reset_index()
            
            # Format display strings for mobile layout clean text rendering
            price_comparison['Lowest Unit Cost'] = price_comparison['Lowest_Unit_Cost'].apply(lambda x: f"€{x:.2f}" if x > 0 else "N/A")
            price_comparison['Highest Unit Cost'] = price_comparison['Highest_Unit_Cost'].apply(lambda x: f"€{x:.2f}" if x > 0 else "N/A")
            price_comparison['Avg Total Spent'] = price_comparison['Avg_Total_Paid'].apply(lambda x: f"€{x:.2f}")
            
            # Rename columns nicely for screen viewability
            comparison_display = price_comparison[['Shop', 'Lowest Unit Cost', 'Highest Unit Cost', 'Avg Total Spent', 'Total_Times_Bought']].rename(
                columns={'Shop': 'Market/Store', 'Total_Times_Bought': 'Trips Recorded'}
            )
            
            # Render the dynamic query table layout
            st.dataframe(comparison_display, use_container_width=True, hide_index=True)
            
            # mobile helper tip
            st.caption("💡 *'N/A' means you bought the item as a bulk or weight price packet without a per-unit tracking entry.*")
        else:
            st.info("No market matching logs discovered for that item.")

    st.markdown("---")

    # INTERACTIVE FILTERS
    st.markdown("### 🎛️ Main Dashboard Filter Panel")
    
    month_list = ["All Months"] + sorted(df['Month'].dropna().unique().tolist())
    shop_list = ["All Shops"] + sorted(df['Shop'].dropna().unique().tolist())
    cat_list = ["All Categories"] + sorted(df['Category I'].dropna().unique().tolist())
    
    selected_month = st.selectbox("Filter by Month:", month_list, index=0)
    selected_shop = st.selectbox("Filter by Shop/Store:", shop_list, index=0)
    selected_cat = st.selectbox("Filter by Category:", cat_list, index=0)

    # filters dynamically
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

    # VISUAL ANALYTICS TARGETED FOR MOBILE VIEWPORTS ---
    st.markdown("### 📊 Spending Breakdowns")

    # Tab 1: Category breakdown
    tab1, tab2, tab3 = st.tabs(["📁 By Category", "🏪 By Shop", "📅 By Month"])
    
    with tab1:
        cat_data = filtered_df.groupby('Category I')['Total cost'].sum().reset_index()
        cat_data = cat_data.sort_values(by='Total cost', ascending=True).tail(10)
        
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
        shop_data = shop_data.sort_values(by='Total cost', ascending=False).head(8)
        
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

    # RAW SPREADSHEET VIEWER
    with st.expander("🔍 Open Full Raw Grocery Data Sheets"):
        st.dataframe(
            filtered_df[['Month', 'Date', 'Shop', 'Category I', 'Item Name', 'Total cost']], 
            use_container_width=True
        )

except Exception as e:
    st.error(f"Failed to cleanly interpret Grocessary_items.xlsx. Details: {e}")