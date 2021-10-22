import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from PIL import Image

def plot_line(df,x_val,y_val,ticks,color):
    fig = px.line(data_frame=df,x=x_val,y=y_val,markers=True,color_discrete_sequence=color)
    fig.update_layout(xaxis=dict(tickmode='array',
                                 tickvals=ticks))
    return fig

def plot_bar(df,x_val,y_val,ticks,color):
    fig = px.bar(data_frame=df,x=x_val,y=y_val,color_discrete_sequence=color,barmode='group')
    fig.update_layout(xaxis=dict(tickmode='array',
                                 tickvals=ticks))
    return fig

@st.cache(suppress_st_warning=True)
def get_data(ticker):
    company = yf.Ticker(ticker)
    hist_data = yf.download(ticker, start, end)[['Adj Close', 'Volume']]
    adj_close = hist_data['Adj Close']
    volume = hist_data['Volume']
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
    
    return adj_close, volume, infodf, financials, bsheet, earnings, holders, rec

@st.cache(suppress_st_warning=True)
def get_adj_close(ticker):
    adj_close = yf.download(ticker, start, end)['Adj Close']    
    return adj_close
    

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

adj_close, volume, infodf, financials, bsheet, earnings, holders, rec = get_data(ticker)

# Sidebar
st.sidebar.header(ticker)
st.sidebar.subheader('Choose options to visualise')

st.write('---')

st.header('Stock Price Overview')


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
    
    
vol = st.checkbox('Show Volume')
if vol:
    st.bar_chart(data=volume)
    

# Display Stock Overview Table
st.subheader('Stock Info')

infodf = infodf[['currentPrice','marketCap','beta','returnOnAssets',
                 'returnOnEquity','trailingPE']]

infodf = infodf.rename(columns={'currentPrice':'Current Price',
                                'marketCap':'Market Cap',
                                'beta':'Beta',
                                'returnOnAssets':'RoA',
                                'returnOnEquity':'RoE',
                                'trailingPE':'Trailing PE'})
st.table(infodf.T)

# ------- RETURNS --------
returns = st.sidebar.checkbox('Stock Returns')
if returns:
    dwm_returns = st.sidebar.radio(label='Select Daily, Weekly or Monthly Returns',
                                  options=['Daily Returns',
                                           'Weekly Returns',
                                           'Monthly Returns'])
    
    #compare = st.checkbox('Compare Stock Returns')
    
    if dwm_returns == 'Daily Returns':
        st.subheader('Daily Returns')
        daily_returns = adj_close.pct_change().dropna().rename(str(ticker)+' Daily Returns')  
        fig = px.line(daily_returns)
        fig.update_layout(width=950,height=500) 
        st.plotly_chart(fig)
        df = pd.DataFrame(data= [[round(np.mean(daily_returns),3),
                                 round(np.std(daily_returns),3)]], 
                          columns=['Mean', 'Std.'])
        st.table(df)
        #st.write('Mean', round(np.mean(daily_returns),3))
        #st.write('Std.', round(np.std(daily_returns),3))
    
    elif dwm_returns == 'Weekly Returns':
        st.subheader('Weekly Returns')
        weekly_returns = adj_close.resample('W').ffill().pct_change().dropna().rename(str(ticker)+' Weekly Returns')
        fig = px.line(weekly_returns)
        fig.update_layout(width=950,height=500) 
        st.plotly_chart(fig) 
        df = pd.DataFrame(data= [[round(np.mean(weekly_returns),3),
                                 round(np.std(weekly_returns),3)]], 
                          columns=['Mean', 'Std.'])
        st.table(df)
    
    elif dwm_returns == 'Monthly Returns':
        st.subheader('Monthly Returns')
        monthly_returns = adj_close.resample('M').ffill().pct_change().dropna().rename(str(ticker)+' Monthly Returns')
        fig = px.line(monthly_returns)
        fig.update_layout(width=950,height=500) 
        st.plotly_chart(fig)
        df = pd.DataFrame(data= [[round(np.mean(monthly_returns),3),
                                 round(np.std(monthly_returns),3)]], 
                          columns=['Mean', 'Std.'])
        st.table(df)

# ------ Compare Returns ------
    compare = st.checkbox('Compare Stock Returns')
    if compare:
        compStock = st.multiselect('Select Other Stocks', 
                                   options=[x for x in ticker_list if x != ticker])
        
        
        if dwm_returns == 'Daily Returns':
            for comp in compStock:
                adjCloseToCompare = get_adj_close(comp)
                d = adjCloseToCompare.pct_change().dropna().rename(str(comp)+' Daily Returns')
                fig.add_scatter(cliponaxis=True, 
                                x=d.index, y=d.values, 
                                mode='lines', 
                                name = str(comp)+' Daily Returns')
            fig.update_layout(width=950,height=500)   
            st.plotly_chart(fig)
            
            
        if dwm_returns == 'Weekly Returns':
            for comp in compStock:
                adjCloseToCompare = get_adj_close(comp)
                w = adjCloseToCompare.resample('W').ffill().pct_change().dropna().rename(str(ticker)+' Weekly Returns')
                fig.add_scatter(cliponaxis=True, 
                                x=w.index, y=w.values, 
                                mode='lines', 
                                name = str(comp)+' Weekly Returns')
            fig.update_layout(width=950,height=500) 
            st.plotly_chart(fig)
            

        if dwm_returns == 'Monthly Returns':
            for comp in compStock:
                adjCloseToCompare = get_adj_close(comp)
                m = adjCloseToCompare.resample('M').ffill().pct_change().dropna().rename(str(ticker)+' Monthly Returns')
                fig.add_scatter(cliponaxis=True, 
                                x=m.index, y=m.values, 
                                mode='lines', 
                                name = str(comp)+' Monthly Returns')
            fig.update_layout(width=950,height=500)   
            st.plotly_chart(fig)
        


#------------- FINANCIALS ------------
financials_checkbox = st.sidebar.checkbox('Financials')
if financials_checkbox:
    st.header('Financials')
    
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
    st.table(holders)
    

# ------------ RECOMMENDATIONS -------------
rec_checkbox = st.sidebar.checkbox('Analysts Recommendations (10 most recent available)')
if rec_checkbox:
    st.header('Analysts Recommendations')
    st.table(rec)

