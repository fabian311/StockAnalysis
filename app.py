import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from PIL import Image

@st.cache(suppress_st_warning=True)
def plot_line(df,x_val,y_val,ticks,color):
    fig = px.line(data_frame=df,x=x_val,y=y_val,markers=True,color_discrete_sequence=color)
    fig.update_layout(xaxis=dict(tickmode='array',
                                 tickvals=ticks))
    return fig

@st.cache(suppress_st_warning=True)
def plot_bar(df,x_val,y_val,ticks,color):
    fig = px.bar(data_frame=df,x=x_val,y=y_val,color_discrete_sequence=color,barmode='group')
    fig.update_layout(xaxis=dict(tickmode='array',
                                 tickvals=ticks))
    return fig

@st.cache(suppress_st_warning=True)
def get_data(ticker):
    company = yf.Ticker(ticker)
    adj_close = yf.download(ticker, start, end)['Adj Close']
    infodf = pd.DataFrame.from_dict(data=company.info, 
                                orient='index', 
                                columns=['Value']).T
    financials = pd.DataFrame(company.financials.dropna(), 
                              columns=company.financials.columns.date)
    bsheet = pd.DataFrame(company.balancesheet.dropna(), 
                              columns=company.balancesheet.columns.date)
    earnings = pd.DataFrame(company.earnings.reset_index().dropna())
    holders = pd.DataFrame(company.institutional_holders.dropna())
    rec = pd.DataFrame(company.recommendations.iloc[-11:-1].set_index(company.recommendations.iloc[-11:-1].index.date))
    
    return adj_close, infodf, financials, bsheet, earnings, holders, rec

# Option to generalise stock ticker input
# ticker = st.text_input(label="Insert the Company's Ticker Symbol")

# Some predefined stocks to choose from
ticker_list = ['AAPL','MSFT','GOOGL','AMZN',
               'FB','TSLA','NVDA','JPM','V','JNJ',
               'WMT','BAC','MC','PG','DIS','PYPL',
               'NFLX','XOM','ORCL','PFE','NKE']

st.header('Stock Analysis Dashboard')

ticker = st.selectbox('Select Company Ticker Symbol', 
                        options=ticker_list)

start = st.date_input('Select Start Date',
                      value=pd.to_datetime('2018-01-01'))
end = st.date_input('Select End Date',
                    value=pd.to_datetime('today'))

adj_close, infodf, financials, bsheet, earnings, holders, rec = get_data(ticker)

# Sidebar
pic = Image.open('C:/Users/fabia/OneDrive/Pictures/stock.jfif')
st.sidebar.image(pic)
st.sidebar.header(ticker)
st.sidebar.subheader('Choose options to visualise')


st.write('---')


st.header('Stock Price Overview')

#adj_close = yf.download(ticker, start, end)['Adj Close']

#infodf = pd.DataFrame.from_dict(data=company.info, 
                                #orient='index', 
                                #columns=['Value']).T

# Insert a Moving Average and Rolling Std. Visualisation Option
ma_checkbox = st.checkbox('Moving Average')
rolling_std_checkbox = st.checkbox('Rolling Std.')

if ma_checkbox:
    days_ma = st.slider('Select Moving Average Rolling Window (Days)',
                     min_value=0,
                     max_value=90,
                     step=2)
    if rolling_std_checkbox:
        days_std = st.slider('Select Rolling Std. Window (Days)',
                         min_value=0,
                         max_value=90,
                         step=2)
        ma = adj_close.rolling(days_ma).mean()
        rollstd = adj_close.rolling(days_std).std()
        data = pd.DataFrame(data=pd.concat([adj_close, ma.rename('Moving Average'), 
                                            rollstd.rename('Rolling Std.')], 
                                           axis=1))
        st.line_chart(data[['Adj Close','Moving Average','Rolling Std.']])
    else:
        ma = adj_close.rolling(days_ma).mean()
        data = pd.DataFrame(data=pd.concat([adj_close, ma.rename('Moving Average')], 
                                           axis=1))
        st.line_chart(data[['Adj Close','Moving Average']])

elif rolling_std_checkbox:
    days_std = st.slider('Select Rolling Std. Window (Days)',
                         min_value=0,
                         max_value=90,
                         step=2)
    if ma_checkbox:
        days_ma = st.slider('Select Moving Average Rolling Window (Days)',
                         min_value=0,
                         max_value=90,
                         step=2)
        ma = adj_close.rolling(days_ma).mean()
        rollstd = adj_close.rolling(days_std).std()
        data = pd.DataFrame(data=pd.concat([adj_close, ma.rename('Moving Average'), 
                                            rollstd.rename('Rolling Std.')], 
                                           axis=1))
        st.line_chart(data[['Adj Close','Moving Average','Rolling Std.']])
    else:  
        rollstd = adj_close.rolling(days_std).std()
        data = pd.DataFrame(data=pd.concat([adj_close, rollstd.rename('Rolling Std.')], 
                                           axis=1))
        st.line_chart(data[['Adj Close','Rolling Std.']])

else:
    st.line_chart(adj_close)
    

# Display Stock Overview Table
st.subheader('Stock Info')

infodf = infodf[['currentPrice','marketCap','volume','beta','returnOnAssets',
                 'returnOnEquity','trailingPE']]

infodf = infodf.rename(columns={'currentPrice':'Current Price',
                                'marketCap':'Market Cap',
                                'volume':'Volume',
                                'beta':'Beta',
                                'returnOnAssets':'RoA',
                                'returnOnEquity':'RoE',
                                'trailingPE':'Trailing PE'})
st.table(infodf.T)


# Sidebar Options
returns = st.sidebar.checkbox('Stock Returns')
if returns:
    dwm_returns = st.sidebar.radio(label='Select Daily, Weekly or Monthly Returns',
                                  options=['Daily Returns',
                                           'Weekly Returns',
                                           'Monthly Returns'])
    if dwm_returns == 'Daily Returns':
        st.subheader('Daily Returns')
        daily_returns = adj_close.pct_change()
        st.line_chart(daily_returns)
        st.write('Mean', round(np.mean(daily_returns),3))
        st.write('Std.', round(np.std(daily_returns),3))
    
    elif dwm_returns == 'Weekly Returns':
        st.subheader('Weekly Returns')
        weekly_returns = adj_close.resample('W').ffill().pct_change()
        st.line_chart(weekly_returns) 
        st.write('Mean', round(np.mean(weekly_returns),3))
        st.write('Std.', round(np.std(weekly_returns),3))
    
    elif dwm_returns == 'Monthly Returns':
        st.subheader('Monthly Returns')
        monthly_returns = adj_close.resample('M').ffill().pct_change()
        st.line_chart(monthly_returns)
        st.write('Mean', round(np.mean(monthly_returns),3))
        st.write('Std.', round(np.std(monthly_returns),3))



#------------- FINANCIALS ------------
financials_checkbox = st.sidebar.checkbox('Financials')
if financials_checkbox:
    st.header('Financials')
    #financials = pd.DataFrame(company.financials.dropna(), 
                              #columns=company.financials.columns.date)
    st.table(financials)	   
	   
    viz = st.sidebar.radio('Data Visualisation Options', 
                           ['Yes','No'],
                           key='financialsradio',
                          index=1)
    
    if viz == 'Yes':
        line_or_bar = st.sidebar.selectbox('Choose Chart Option', 
                                            options=['Line Chart','Bar Chart'],
                                            key='financialsselect')
        
        ind = st.sidebar.selectbox('Select Financial Data To Plot', 
								   options=financials.index)
		
        vizdf = pd.DataFrame(financials.loc[financials.index == ind])
        vizdf = vizdf.T.reset_index().rename(columns={'index':'Date'})
		
        if line_or_bar == 'Line Chart':
            fig = plot_line(df=vizdf, x_val='Date', y_val=ind, 
                            ticks=vizdf['Date'], color=['orange'])
            st.plotly_chart(fig)
        
        elif line_or_bar == 'Bar Chart':
            fig = plot_bar(df=vizdf, x_val='Date', y_val=ind, 
                           ticks=vizdf['Date'], color=['orange'])
            st.plotly_chart(fig)
        
        st.table(vizdf.style.hide_index())
        
        
# --------- BALANCE SHEET -------------        
bsheet_checkbox = st.sidebar.checkbox('Balance Sheet')
if bsheet_checkbox:
    st.header('Balance Sheet')
    #bsheet = pd.DataFrame(company.balancesheet.dropna(), 
                              #columns=company.balancesheet.columns.date)
    st.table(bsheet)
    viz = st.sidebar.radio('Data Visualisation Options',
                           ['Yes','No'],
                           key='bsheetradio',
                           index=1)
    
    if viz == 'Yes':
        line_or_bar = st.sidebar.selectbox('Choose Chart Option', 
                                   options=['Line Chart','Bar Chart'],
                                   key='bsheetselect')
        
        ind = st.sidebar.selectbox('Select Balance Sheet Data To Plot', options=bsheet.index)
        
        vizdf = pd.DataFrame(bsheet.loc[bsheet.index == ind])
        vizdf = vizdf.T.reset_index().rename(columns={'index':'Date'})
        
        if line_or_bar == 'Line Chart':
            fig = plot_line(df=vizdf, x_val='Date', y_val=ind, 
                            ticks=vizdf['Date'], color=['orange'])
            st.plotly_chart(fig)
        
        elif line_or_bar == 'Bar Chart':
            fig = plot_bar(df=vizdf, x_val='Date', y_val=ind, 
                           ticks=vizdf['Date'], color=['orange'])
            st.plotly_chart(fig)
        
        st.table(vizdf.style.hide_index())
        
        
# ---------- EARNINGS -----------        
earnings_checkbox = st.sidebar.checkbox('Earnings')
if earnings_checkbox:
    st.header('Earnings')
    #earnings = pd.DataFrame(company.earnings.reset_index().dropna())
    st.table(earnings)
    viz = st.sidebar.radio('Data Visualisation Options', 
                           ['Yes','No'],
                           key='earningsradio',
                           index=1)
    
    if viz == 'Yes':
        line_or_bar = st.sidebar.selectbox('Choose Chart Option', 
                                   options=['Line Chart','Bar Chart'],
                                   key='earningsselect')
        
        rev_or_earn = st.sidebar.multiselect('Select Earnings Data To Plot', 
                           options=["Revenue", "Earnings"])
        
        if rev_or_earn == ["Revenue"]: 
            if line_or_bar == 'Line Chart':
                fig = plot_line(df=earnings, x_val='Year', y_val='Revenue', 
                               ticks=earnings['Year'], color=['orange'])
                st.plotly_chart(fig)
            
            elif line_or_bar == 'Bar Chart':
                fig = plot_bar(df=earnings, x_val='Year', y_val='Revenue', 
                               ticks=earnings['Year'], color=['orange'])                
                st.plotly_chart(fig)       
        
        elif rev_or_earn == ['Earnings']:            
            if line_or_bar == 'Line Chart':
                fig = plot_line(df=earnings, x_val='Year', y_val='Earnings', 
                               ticks=earnings['Year'], color=['orange'])             
                st.plotly_chart(fig)
            
            elif line_or_bar == 'Bar Chart':
                fig = plot_bar(df=earnings, x_val='Year', y_val='Earnings', 
                               ticks=earnings['Year'], color=['orange'])           
                st.plotly_chart(fig)
            
        elif (rev_or_earn == ['Revenue','Earnings']) or (rev_or_earn == ['Earnings','Revenue']):
            if line_or_bar == 'Line Chart':
                fig = plot_line(df=earnings, x_val='Year', y_val=['Earnings','Revenue'], 
                               ticks=earnings['Year'], color=['orange','red'])
                st.plotly_chart(fig)
            
            elif line_or_bar == 'Bar Chart':
                fig = plot_bar(df=earnings, x_val='Year', y_val=['Earnings','Revenue'], 
                               ticks=earnings['Year'], color=['orange','red'])
                st.plotly_chart(fig)


# ------------ INSTITUTIONAL HOLDERS -------------
holders_checkbox = st.sidebar.checkbox('Institutional Holders')
if holders_checkbox:
    st.header('Institutional Holders')
    #holders = pd.DataFrame(company.institutional_holders.dropna())
    st.table(holders)
    

# ------------ RECOMMENDATIONS -------------
rec_checkbox = st.sidebar.checkbox('Analysts Recommendations (10 most recent available)')
if rec_checkbox:
    st.header('Analysts Recommendations')
    #rec = pd.DataFrame(company.recommendations.iloc[-11:-1].set_index(company.recommendations.iloc[-11:-1].index.date))
    st.table(rec)

