print('began running...')

#initialized things for SMTP server
#MEDIUM LINK DELETE BEFORE POSS;KFJSDFJSDLFJSDLJFDS
#https://towardsdatascience.com/automate-your-python-scripts-with-task-scheduler-661d0a40b279

#Import the libraries
import smtplib
import ssl
from email.mime.text import MIMEText as MT
from email.mime.multipart import MIMEMultipart as MM

#Store the email addresses for the reciever, and the sender. Also store the senders email password
receiver = 'aarav.dhp@gmail.com'
sender = 'apptest7654@gmail.com'
sender_password = 'garbage@7654'

#Create a MIMEMultipart Object 
msg = MM()
msg["Subject"] = "Python Programming Is Amazing !"
msg["From"] = sender
msg["To"] = receiver



# Import libraries
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import yfinance as yf

import nltk

nltk.download('vader_lexicon')

html_body = ""
def println(s, h=''):
    global html_body
    if h == 'h1':
        html_body += '<h1>' + s + '</h1>'
    elif h == '':
        html_body += '<p>' + s + '</p>'

    print(s)

# Parameters 
n = 5 #the # of article headlines displayed per ticker
'''NYSETickers = pd.read_csv("C:/AaravWorld/StockMarketData/NYSEDataNow.csv")
NASDAQTickers = pd.read_csv("C:/AaravWorld/StockMarketData/NASDAQDataNow.csv")
tickers = list(NYSETickers['Symbol']) + list(NASDAQTickers['Symbol'])[:30]'''

tickers = ['AAPL', 'MU', 'AMZN', 'FB', 'IRBT', 'BABA', 'BIDU', 'JD', 'VRTX', 'REGN', 'FTS', 'TU', 'VALE', 'ASX', 'YETI', 'CROX', 'DG', 'GM', 'SONY']
ticker_entries = {'AAPL': 140, 'MU':-1, 'AMZN':3300, 'FB':300, 'IRBT':-1, 'BABA':210, 'BIDU':-1, 'JD':-1,
                  'VRTX':195, 'REGN': 608, 'FTS':46, 'TU':22, 'VALE': 21, 'ASX':9, 'YETI':102, 'CROX':142,
                  'DG':238, 'GM':54, 'SONY':100}

#normalizes all ticker entries so all have valid value
for ticker in ticker_entries:
    if ticker_entries[ticker] == -1 or ticker_entries[ticker] == None:
        ticker_entries[ticker] = 100000000

#tickers = ['AAPL', 'TSLA', 'AMZN', 'BABA']
#ticker_entries = {'AAPL': 140, 'TSLA':700, 'AMZN':3300, 'BABA':210}

# Get Data
finwiz_url = 'https://finviz.com/quote.ashx?t='
news_tables = {}

for ticker in tickers:
    url = finwiz_url + ticker
    req = Request(url=url,headers={'user-agent': 'my-app/0.0.1'}) 
    resp = urlopen(req)    
    html = BeautifulSoup(resp, features="lxml")
    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table

# Iterate through the news
parsed_news = []
for file_name, news_table in news_tables.items():
    for x in news_table.findAll('tr'):
        text = x.a.get_text() 
        date_scrape = x.td.text.split()

        if len(date_scrape) == 1:
            time = date_scrape[0]
            
        else:
            date = date_scrape[0]
            time = date_scrape[1]

        ticker = file_name.split('_')[0]
        
        parsed_news.append([ticker, date, time, text])
        
# Sentiment Analysis
analyzer = SentimentIntensityAnalyzer()

columns = ['Ticker', 'Date', 'Time', 'Headline']
news = pd.DataFrame(parsed_news, columns=columns)
scores = news['Headline'].apply(analyzer.polarity_scores).tolist()

df_scores = pd.DataFrame(scores)
news = news.join(df_scores, rsuffix='_right')

# View Data 
news['Date'] = pd.to_datetime(news.Date).dt.date

unique_ticker = news['Ticker'].unique().tolist()
news_dict = {name: news.loc[news['Ticker'] == name] for name in unique_ticker}

values = []

#creates filtered watch list

filtered_watch_list = {}
#output results

println('current watch list: ' + ', '.join(tickers))
try:
    for ticker in tickers:

        #view data (con't)
        dataframe = news_dict[ticker]
        dataframe = dataframe.set_index('Ticker')
        dataframe = dataframe.drop(columns = ['Headline'])
        
        sentiment_score = round(dataframe['compound'].mean(), 2)

    
        tk_obj = yf.Ticker(ticker)
        df = news_tables[ticker]
        df_tr = df.findAll('tr')
    
        println('\n'+ '*'*10+ '\n')
        #gives info about stock
        println(ticker + ' --', 'h1')

        gains_realized = str(100*tk_obj.info['regularMarketPrice']/ticker_entries[ticker] - 100)
        println('current price -- ' + str(tk_obj.info['regularMarketPrice']) + ': added to list at ' + str(ticker_entries[ticker]) + ' (' + gains_realized + '%)')
        momentumAnalysis = 'bearish' if tk_obj.info['fiftyDayAverage'] < tk_obj.info['twoHundredDayAverage'] else 'bullish'

        println('momentum -- momentumAnalysis: ' + momentumAnalysis + ', fiftyDayAverage: ' + str(tk_obj.info['fiftyDayAverage']) + ', twoHundredDayAverage: ' + str(tk_obj.info['twoHundredDayAverage'])) 

        #it is more common to have higher sentiment stocks, so I shifted the scale accordingly
        if sentiment_score > 0.15:  
            sentiment = 'extremely good'
        elif sentiment_score > 0.05:
            sentiment = 'good'
        elif sentiment_score > 0:
            sentiment = 'neutral'
        elif sentiment_score > -0.05:
            sentiment = 'bad'
        else:
            sentiment = 'terrible'
        println('sentiment -- sentiment: ' + sentiment + ', sentimentScore: ' + str(sentiment_score))
        println('')
        println('Recent News Headlines for {}: '.format(ticker))
        
        for i, table_row in enumerate(df_tr):
            a_text = table_row.a.text
            td_text = table_row.td.text
            td_text = td_text.strip()
            println(a_text +'(' +td_text +')')
            if i == n-1:
                break

        #code to add stock to filtered watch list if good
        if sentiment_score > 0.05 and momentumAnalysis == 'bullish':
            filtered_watch_list[ticker] = [momentumAnalysis, sentiment_score, gains_realized]
        println('...')
except Exception as e:
    println('Error')
    println(str(e))

println('\n\n******************\nfiltered watch list\n')
println('Momentum Analysis | Sentiment Score | Gains Realized')
for ticker, data in filtered_watch_list.items():
    println('\t- ' + ticker + ': ' + str(data[0]) + ', ' + str(data[1]) + ', ' + str(data[2]) + '%')
    

#helps to send email
HTML = """
<html>
  <body>
   <h1>Daily Watch List Analysis!</h1>""" + html_body + """
  </body>
</html>
"""

print('HTML')
print(HTML)
#Create a html MIMEText object
MTObj = MT(HTML, "html")

msg.attach(MTObj)

#Create the secure socket layer (SSL) context object
SSL_context = ssl.create_default_context() 
#Create the secure Simple Mail Transfer Protocol (SMTP) connection
server = smtplib.SMTP_SSL(host ="smtp.gmail.com",port= 465, context=SSL_context) #Use Googles (Outgoing Mail Server) Simple Mail Transfer Protocol
#Login to the email account
server.login(sender, sender_password)
#Send the email
server.sendmail(sender, receiver, msg.as_string())

print('ended running...')
