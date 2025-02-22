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
APPROACH = ['RFM Matrix', 'K-Means']

WEEKDAY_MAP = {
    0: 'Monday', 1: 'Sunday', 2: 'Tuesday', 3: 'Wednesday',
    4: 'Thursday', 5: 'Friday', 6: 'Saturday'
}

THEME_PLOTLY = None

TREEMAP_COLORS = {
    'highlight': "#FF8C42",
    'base': "#D3D3D3"
}

TREEMAP_LEGEND = {
    'Insiders': 'VIP customers, extremely loyal and high-value',
    'Champions': 'Buy very frequently and recently',
    'Loyalists': 'Loyal customers who make regular purchases',
    'Big Spenders': 'Spend a lot of money, but may not buy as frequently',
    'Potential Loyalists': 'Recent and frequent buyers, but not spending much yet',
    'New Customers': 'New, promising buyers',
    'Promising': 'Made a few purchases, but recent ones',
    'Active Customers': 'Buy with reasonable frequency',
    'High Value Newcomers': 'New customers who spent a lot right from the start',
    'Rising Stars': 'Recently increased frequency or average spend',
    'Occasional Buyers': 'Buy sporadically, but still active',
    'Need Attention': 'Regular customers who have started to reduce their purchases',
    'About to Sleep': 'Old customers who are disappearing',
    'Hibernating': 'Haven’t bought in a long time, but were once good customers',
    'At Risk': 'High-value customers from the past, but inactive now',
    'Lost Champions': 'Used to be VIPs, but stopped buying',
    'Price Sensitive': 'Buy, but only when there are discounts',
    'One-Timers': 'Bought only once and never returned',
    'Bargain Hunters': 'Only look for discounts, no loyalty',
    'Low Value Customers': 'Buy very little and rarely',
    'Churned': 'Completely lost customers',
    'Ghosts': 'Inactive for so long that they are difficult to re-engage'
}

RFM_LEGEND = {
    'Insiders': 'Top-tier customers who buy frequently, recently, and spend the most',
    'Champions': 'Recent and frequent buyers with high spending',
    'Potential Loyalists': 'Recent customers with increasing frequency and spending',
    'New Customers': 'Very recent buyers with low frequency but varying spending',
    'Promising': 'Moderately recent customers with low to moderate spending',
    'Need Attention': 'Regular customers whose spending is decreasing',
    'About to Sleep': 'Older customers with declining frequency and low spending',
    'At Risk': 'Previously high-value customers who are now buying less frequently',
    'Can’t Lose': 'Declining but still valuable customers with moderate spending',
    'Hibernating': 'Inactive customers with low frequency and varying spending',
    'Lost': 'Completely inactive customers with no recent purchases'
}

# Configure page settings
st.set_page_config(
    page_title="Insiders Dashboard - ML",
    page_icon="🌍",
    layout="wide"
)

@st.cache_data
def get_data(path_ml: str, path_oml: str, path_rfm: str, path_orfm: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load and cache processed data files."""
    df_ml = pd.read_csv(path_ml)
    df_oml = pd.read_csv(path_oml)
    df_rfm = pd.read_csv(path_rfm)
    df_orfm = pd.read_csv(path_orfm)
    return df_ml, df_oml, df_rfm, df_orfm

def filter_approach(df_ml: pd.DataFrame, df_oml: pd.DataFrame, df_rfm: pd.DataFrame, df_orfm: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Handle dataset selection and return chosen dataframe with appropriate legend."""
    with st.sidebar:
        st.image("reports/figures/logo.png")
        st.title("An online retail store!")

        # Setting the approach filter        
        sl_approach = st.selectbox(
            "Select the solution approach:",
            APPROACH,
            index=1
        )

    # Initializing variables UnboundLocalError
    df = pd.DataFrame()
    df_o = pd.DataFrame()
    legend_df = pd.DataFrame()

    if sl_approach == 'RFM Matrix':
        df = df_rfm.copy()
        df_o = df_orfm.copy()
        legend_df = pd.DataFrame(list(RFM_LEGEND.items()), columns=['Cluster ID', 'Description'])
    elif sl_approach == 'K-Means':
        df = df_ml.copy()
        df_o = df_oml.copy()
        legend_df = pd.DataFrame(list(TREEMAP_LEGEND.items()), columns=['Cluster ID', 'Description'])

    return df, df_o, legend_df
  
def display_main_metrics(df: pd.DataFrame) -> None:
    """Display key customer metrics in a 6-column layout."""
    metrics = {
        '🧑‍🤝‍🧑 Customers': df['customer_id'].count(),
        '💰 Revenue': df['gross_revenue'].sum(),
        '📈 Avg Recency': df['recency_days'].mean(),
        '📈 Avg Frequency': df['frequency'].mean(),
        '📝 Invoices': df['qty_invoices'].sum(),
        '🛍️ Products': df['qty_prod_purchased'].sum()
    }

    cols = st.columns(6)
    for col, (label, value) in zip(cols, metrics.items()):
        # Handle NaN/None values
        formatted_value = numerize(float(value)) if pd.notnull(value) else 'N/A'
        col.metric(label=label, value=formatted_value)

def create_treemap(df: pd.DataFrame) -> px.treemap:
    """Create cluster distribution treemap with highlighted Insiders cluster."""
    df_treemap = df.groupby('cluster')['customer_id'].count().reset_index()
    fig = px.treemap(
        df_treemap,
        path=['cluster'],
        values='customer_id',
        color='cluster',
        color_discrete_sequence=px.colors.qualitative.Alphabet,
        width=1100,
        height=900
    )
    fig.update_layout(
        title=dict(text='Segment Distribution', font=dict(size=30)),
        title_x=0.35,
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

def create_bubble_chart(df: pd.DataFrame, x: str, y: str, title: str) -> px.scatter:
    """ Helper function to create standardized bubble charts. """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=y, 
        color=y,
        hover_name=x,
        size_max=50,
        title=title,
        text=y
    )
    fig.update_layout(
        xaxis_title=x.capitalize(),
        yaxis_title=y.capitalize(),
        xaxis=dict(
            showgrid=False,
            tickangle=-45  # Rotaciona rótulos do eixo X para evitar sobreposição
        ),
        yaxis=dict(showgrid=False),
        coloraxis_showscale=False  # Remove a barra de cores (opcional)
    )
    
    return fig

def filtered_section(df: pd.DataFrame, df_o: pd.DataFrame) -> None:
    """Display filtered cluster information and related visualizations."""

    # List of Available Clusters
    available_clusters = df['cluster'].unique().tolist()

    # 2. Filter on sidebar
    with st.sidebar:
        selected_clusters = st.multiselect(
            "Select clusters to analyze:",
            available_clusters,
            default='Insiders' if 'Insiders' in available_clusters else available_clusters[0]
        )

    # 3. Validation
    if not selected_clusters:
        st.warning("Please select at least one cluster")
        st.stop()
          
    # Printing the selected clusters
    st.subheader('Active Clusters:')
    for idx, cluster in enumerate(selected_clusters, 1):
        st.markdown(f"🏷️ **{idx}.** {cluster}")
    
    st.markdown("<br>""<br>""<br>", unsafe_allow_html=True)
    
    # 4. Processamento dos dados filtrados
    df_filtered = df[df['cluster'].isin(selected_clusters)]
    df_of = df_o[df_o['cluster'].isin(selected_clusters)]

    # Plot Metrics
    display_main_metrics(df_filtered)
    
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
    df_o["stock_code"] = df_o["stock_code"].astype(str) # Just for labels appear correclty
    top_products = df_of.groupby("stock_code")["quantity"].sum().nlargest(10).reset_index()
    fig = create_bar_chart(top_products, 'stock_code', 'quantity', 'Top 10 Best Seller Items')
    fig.update_layout(xaxis=dict(type="category")) # set the x axis as category
    col3.plotly_chart(fig, use_container_width=True)
    
    # Country
    country = df_of.groupby("country")["customer_id"].nunique().nlargest(5).sort_values(ascending=False).reset_index()
    fig = px.bar(country, x="country", y="customer_id", color="customer_id", text_auto=".2s", title="Qty of Customers by Country")
    fig.update_layout(xaxis_title="Country", yaxis_title="Quantity of Customers", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    col4.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df_filtered, use_container_width=True)

def main() -> None:
    """Main function to orchestrate the dashboard layout."""
    st.title('🥇 Insiders: High Value Customer Identification')
    st.subheader('Dashboard for Customer Segmentation Analysis')
    st.write("""
        This dashboard provides insights into customer clusters identified either through an RFM Matrix or K-Means.  
        The user can select which one to analyze using the filters.  
        It includes high-level metrics, visualizations, and filtered views of customer segments.
    """)
    st.write("### Key Features:")
    st.write("""
        - Overall customer statistics
        - Cluster distribution treemap
        - Revenue and customer quantity analysis
        - Interactive cluster filtering
        - Time-based and geographical analysis
    """)

    st.divider()

    # Load data
    df_ml, df_oml, df_rfm, df_orfm = get_data('./data/processed/df_ml.csv',
                                              './data/processed/df_oml.csv',
                                              './data/processed/df_rfm.csv',
                                              './data/processed/df_orfm.csv')

    # Selecting the dataset to be analised
    df, df_o, df_legend = filter_approach(df_ml, df_oml, df_rfm, df_orfm)

    # Main metrics section
    st.header('General Customer Overview')
    display_main_metrics(df)
    st.markdown("<br>"*3, unsafe_allow_html=True)  # Add vertical spacing

    # Treemap visualization
    col1, col2 = st.columns(2)
    col1.plotly_chart(create_treemap(df), use_container_width=True)
    with col2:
        st.markdown("<br>""<br>""<br>", unsafe_allow_html=True)
        st.table(df_legend)

    # Comparative analysis section
    col1, col2 = st.columns(2)
    
    # Gross Revenue by Cluster
    revenue_data = df.groupby('cluster')['gross_revenue'].sum().sort_values(ascending=False).reset_index()
    col1.plotly_chart(
        create_bar_chart(revenue_data, 'cluster', 'gross_revenue', 'Revenue by Cluster'),
        use_container_width=True
    )
    
    # Quantity of Custers per Cluster
    customer_data = df.groupby('cluster')['customer_id'].count().sort_values(ascending=False).reset_index()
    col2.plotly_chart(
        create_bubble_chart(customer_data, 'cluster', 'customer_id', 'Quantity of Customers by Cluster'),
        use_container_width=True
    )

     # Comparative analysis section
    col1, col2 = st.columns(2)

    # Top 10 Best Seller Items
    df_o["stock_code"] = df_o["stock_code"].astype(str) # Just for labels appear correclty
    top_products = df_o.groupby("stock_code")["quantity"].sum().nlargest(10).reset_index()
    fig = create_bar_chart(top_products, 'stock_code', 'quantity', 'Top 10 Best-Selling Products')
    fig.update_layout(xaxis=dict(type="category")) # set the x axis as category
    col1.plotly_chart(fig, use_container_width=True)


    # Bottom 10 Lowest-Selling Products 
    df_o["stock_code"] = df_o["stock_code"].astype(str) # Just for labels appear correclty
    bottom_products = df_o.groupby("stock_code")["quantity"].sum().nsmallest(10).reset_index()
    fig = create_bar_chart(bottom_products, 'stock_code', 'quantity', 'Bottom 10 Lowest-Selling Products')
    fig.update_layout(xaxis=dict(type="category")) # set the x axis as category
    col2.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>""<br>""<br>", unsafe_allow_html=True)
    
    st.divider()

    # Filtered analysis section
    st.header('Cluster Analysis')
    st.write('Select the clusters by the filter on the side bar.')
    
    filtered_section(df, df_o)

if __name__ == '__main__':
    main()
    # Hide default Streamlit elements
    st.markdown("""<style> #MainMenu, footer, header {visibility: hidden;} </style>""", unsafe_allow_html=True)