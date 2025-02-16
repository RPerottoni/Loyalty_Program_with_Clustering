import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config( layout= 'wide' )

@st.cache_data
def get_data(path):
    df = pd.read_csv(path)
    return df

###### TITLES AND TEXT ######

st.title('All in One Place: High Value Customer Identification ')

st.write('This page will show the details of the clusters formed by K-Means.')
st.divider()

st.header('A general overview of customers')


###### FUNCTION FOR EDA ######
def eda (df):

    # Customer Statistics
    qty_customers = df['customer_id'].count()
    revenue       = df['gross_revenue'].sum()
    recency       = df['recency_days'].mean()
    frequency     = df['frequency'].mean()


    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(label="Quantity of Customers", value=qty_customers)
    col2.metric(label="Gross Revenue", value=f"$ {revenue:,.2f}")
    col3.metric(label="Avg Recency", value=f" {recency:,.2f}")
    col4.metric(label="Avg Frequency", value=f"{frequency:,.2f}")

    st.divider()
    
           
    ##### cluster tree map #####
    df_treemap = df.groupby('cluster').agg({'customer_id': lambda x: len(x)}).reset_index()
    
    # Treemap
    treemap_fig = px.treemap(
        df_treemap,
        path=['cluster'],
        values='customer_id',
        width=1100,
        height=900,
        color='cluster')
    
    # Layout
    treemap_fig.update_layout(
        title=dict(text='SEGMENT DISTRIBUTION', font=dict(size=40)),
        title_x=0.4,
        plot_bgcolor='white'
    )

    # Text
    treemap_fig.update_traces(
        textinfo='label+value+percent root',
        textfont=dict(size=20),
        textposition='middle center'
    )
        
    st.plotly_chart(treemap_fig)
    

     ##### Bar Charts #####
    c1, c2 = st.columns((1,1))

    # Revenue
    revenue = df[['cluster','gross_revenue']].groupby('cluster').sum().sort_values(by='gross_revenue', ascending=False).reset_index()
    
    rev_chart = px.bar(revenue, 
                       x='cluster',
                       y='gross_revenue',
                       color='gross_revenue',
                       text_auto='.2s',
                       title='Accumulative Revenue by Cluster')
    with c1:
        st.plotly_chart(rev_chart)

    # Qty of Customers
    qtyc = df[['cluster','customer_id']].groupby('cluster').count().sort_values(by='customer_id', ascending=False).reset_index()

    qty_chart = px.bar(qtyc, 
                       x='cluster',
                       y='customer_id',
                       color='customer_id',
                       text_auto='.2s',
                       title='Quantity of Customers by Cluster')
    with c2:
        st.plotly_chart(qty_chart)


    st.divider()

     ##### FILTER #####

    clusters = st.multiselect(
                "Select the Group to Summarize the information:",
                ['Insiders', 'Champions', 'Loyalists', 'Big Spenders', 'Potential Loyalists', 'New Customers', 'Promising',
                'Active Customers', 'High Value Newcomers', 'Rising Stars', 'Occasional Buyers', 'Need Attention',
                'About to Sleep', 'Hibernating', 'At Risk', 'Lost Champions', 'Price Sensitive', 'One-Timers',
                'Bargain Hunters', 'Low Value Customers', 'Churned', 'Ghosts'], default='Insiders'
                )
    
    cl_selected = df['cluster'].isin(clusters)
    df_cl = df.loc[cl_selected]


    # Customer Statistics
    qtc  = df_cl['customer_id'].count()
    rev  = df_cl['gross_revenue'].sum()
    rec  = df_cl['recency_days'].mean()
    freq = df_cl['frequency'].mean()
    inv  = df_cl['qty_invoices'].sum()
    prod = df_cl['qty_prod_purchased'].sum()


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    col1.metric(label="Quantity of Customers", value=qtc)
    col2.metric(label="Gross Revenue", value=f"$ {rev:,.2f}")
    col3.metric(label="Avg Recency", value=f" {rec:,.2f}")
    col4.metric(label="Avg Frequency", value=f"{freq:,.2f}")
    col5.metric(label="Qty of Invoices", value=f"{inv:,.2f}")
    col6.metric(label="Qty of Products", value=f"{prod:,.2f}")

    st.divider()

    c1, c2 = st.columns((1,1))

    #### Gross Revenue per Month ####

    rev_m = df_cl[['gross_revenue','month']].groupby('month').sum().reset_index()

    rev_month = px.line(rev_m, 
                       x='month',
                       y='gross_revenue',
                       title='Gross Revenue per Month')
  
    with c1:
        st.plotly_chart(rev_month)

    #### Gross Revenue per Week Day ####

    rev_d = df_cl[['gross_revenue','week_day']].groupby('week_day').sum().reset_index()

    rev_day = px.line(rev_d, 
                       x='week_day',
                       y='gross_revenue',
                       title='Gross Revenue per Day of Week')
  
    with c2:
        st.plotly_chart(rev_day)


    st.write(df_cl.head())
    return (df)






# ETL

if __name__ == '__main__':

    # Data Extraction
    path = './data/processed/ml_cluster.csv'
    df = get_data(path)

    # Load
    eda(df)
