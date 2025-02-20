"""
Streamlit Dashboard for Customer Segmentation Analysis

This dashboard provides insights into customer clusters identified by a K-Means model.
It includes high-level metrics, visualizations, and filtered views of customer segments.

Key Features:
- Overall customer statistics
- Cluster distribution treemap
- Revenue and customer quantity analysis
- Interactive cluster filtering
- Time-based and geographical analysis
"""

import pandas as pd
import streamlit as st
import plotly.express as px
from numerize.numerize import numerize

# Constants
CLUSTER_NAMES = [
    'Insiders', 'Champions', 'Loyalists', 'Big Spenders', 'Potential Loyalists',
    'New Customers', 'Promising', 'Active Customers', 'High Value Newcomers',
    'Rising Stars', 'Occasional Buyers', 'Need Attention', 'About to Sleep',
    'Hibernating', 'At Risk', 'Lost Champions', 'Price Sensitive', 'One-Timers',
    'Bargain Hunters', 'Low Value Customers', 'Churned', 'Ghosts'
]
WEEKDAY_MAP = {
    0: 'Monday', 1: 'Sunday', 2: 'Tuesday', 3: 'Wednesday',
    4: 'Thursday', 5: 'Friday', 6: 'Saturday'
}
THEME_PLOTLY = None
TREEMAP_COLORS = {
    'highlight': "#FF8C42",
    'base': "#D3D3D3"
}

# Configure page settings
st.set_page_config(
    page_title="Insiders Dashboard - ML",
    page_icon="🌍",
    layout="wide"
)

@st.cache_data
def get_data(path: str, path_o: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and cache processed data files."""
    df = pd.read_csv(path)
    df_oml = pd.read_csv(path_o)
    return df, df_oml

def display_main_metrics(df: pd.DataFrame) -> None:
    """Display key customer metrics in a 6-column layout."""
    metrics = {
        'Customers': df['customer_id'].count(),
        'Revenue': df['gross_revenue'].sum(),
        'Avg Recency': df['recency_days'].mean(),
        'Avg Frequency': df['frequency'].mean(),
        'Invoices': df['qty_invoices'].sum(),
        'Products': df['qty_prod_purchased'].sum()
    }

    cols = st.columns(6)
    for col, (label, value) in zip(cols, metrics.items()):
        # Handle NaN/None values
        formatted_value = numerize(float(value)) if pd.notnull(value) else 'N/A'
        col.metric(label=label, value=formatted_value)

def create_treemap(df: pd.DataFrame) -> px.treemap:
    """Create cluster distribution treemap with highlighted Insiders cluster."""
    df_treemap = df.groupby('cluster')['customer_id'].count().reset_index()
    
    color_map = {
        cluster: TREEMAP_COLORS['highlight'] if cluster == "Insiders" else TREEMAP_COLORS['base']
        for cluster in df_treemap['cluster']
    }

    fig = px.treemap(
        df_treemap,
        path=['cluster'],
        values='customer_id',
        color='cluster',
        color_discrete_map=color_map,
        width=1100,
        height=900
    )

    fig.update_layout(
        title=dict(text='Segment Distribution', font=dict(size=30)),
        title_x=0.5,
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    fig.update_traces(
        textinfo='label+value+percent root',
        textfont=dict(size=20),
        marker=dict(line=dict(width=2, color='white')))
    
    return fig

def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str) -> px.bar:
    """Helper function to create standardized bar charts."""
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=y,
        text_auto='.2s',
        title=title
    )
    
    fig.update_layout(
        xaxis_title=x.capitalize(),
        yaxis_title=y.capitalize(),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        showlegend=False
    )
    
    return fig

def filtered_section(df: pd.DataFrame, df_oml: pd.DataFrame) -> None:
    """Display filtered cluster information and related visualizations."""
    st.header("Filtered Information")
    
    selected_clusters = st.multiselect(
        "Select clusters to analyze:",
        CLUSTER_NAMES,
        default='Insiders'
    )
    
    if not selected_clusters:
        st.warning("Please select at least one cluster")
        return

    df_filtered = df[df['cluster'].isin(selected_clusters)]
    display_main_metrics(df_filtered)

    df_oml_filtered = df_oml[df_oml['cluster'].isin(selected_clusters)] # to be used for products and country

    # Create visualization columns
    col1, col2, col3, col4 = st.columns(4)
    
    # Revenue by Month
    rev_month = df_filtered.groupby('month')['gross_revenue'].sum().reset_index()
    fig = px.line(rev_month, x='month', y='gross_revenue', title='Gross Revenue per Month')
    col1.plotly_chart(fig, use_container_width=True)

    # Revenue by Weekday
    df_filtered['week_day'] = df_filtered['week_day'].map(WEEKDAY_MAP)
    rev_day = df_filtered.groupby('week_day')['gross_revenue'].sum().sort_values(ascending=False).reset_index()
    fig = create_bar_chart(rev_day, 'week_day', 'gross_revenue', 'Gross Revenue by Week Day')
    col2.plotly_chart(fig, use_container_width=True)

    # Top Products
    df_oml["stock_code"] = df_oml["stock_code"].astype(str) # Just for labels appear correclty
    top_products = df_oml_filtered.groupby("stock_code")["quantity"].sum().nlargest(10).reset_index()
    fig = create_bar_chart(top_products, 'stock_code', 'quantity', 'Top 10 Best Seller Items')
    fig.update_layout(xaxis=dict(type="category")) # set the x axis as category
    col3.plotly_chart(fig, use_container_width=True)

    # Country
    country = df_oml_filtered.groupby("country")["customer_id"].nunique().sort_values(ascending=False).reset_index()
    fig = px.bar(country, x="country", y="customer_id", color="customer_id", text_auto=".2s", title="Qty of Customers by Country")
    fig.update_layout(xaxis_title="Country", yaxis_title="Quantity of Customers", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    col4.plotly_chart(fig, use_container_width=True)

def main() -> None:
    """Main function to orchestrate the dashboard layout."""
    st.title('All in One Place: High Value Customer Identification')
    st.write('This page shows summarized cluster information from K-Means analysis.')
    st.divider()

    # Load data
    df, df_oml = get_data('./data/processed/ml_cluster.csv', './data/processed/df_oml.csv')

    # Main metrics section
    st.header('General Customer Overview')
    display_main_metrics(df)
    st.markdown("<br>"*3, unsafe_allow_html=True)  # Add vertical spacing

    # Treemap visualization
    st.plotly_chart(create_treemap(df), use_container_width=True)

    # Comparative analysis section
    st.header('Cluster Comparison')
    col1, col2 = st.columns(2)
    
    revenue_data = df.groupby('cluster')['gross_revenue'].sum().sort_values(ascending=False).reset_index()
    col1.plotly_chart(
        create_bar_chart(revenue_data, 'cluster', 'gross_revenue', 'Revenue by Cluster'),
        use_container_width=True
    )
    
    customer_data = df.groupby('cluster')['customer_id'].count().sort_values(ascending=False).reset_index()
    col2.plotly_chart(
        create_bar_chart(customer_data, 'cluster', 'customer_id', 'Customers by Cluster'),
        use_container_width=True
    )

    # Filtered analysis section
    filtered_section(df, df_oml)

if __name__ == '__main__':
    main()
    # Hide default Streamlit elements
    st.markdown("""<style> #MainMenu, footer, header {visibility: hidden;} </style>""", unsafe_allow_html=True)