import os, csv
from flask import Flask, render_template, request
from patterns import patterns
import pandas as pd
import yfinance as yf
import talib

app = Flask(__name__)

@app.route('/snapshot')
def snapshot():
  """
  Take a snapshot of the daily closes 
  of all the stocks in the S&P 500.  
  """
  with open('datasets/companies.csv') as f:
    for line in f:
      # loop through each ticker, pass start & end dates
      if "," not in line:
        continue
      ticker = line.split(",")[0]

      # save the dataframe to a CSV file
      data = yf.download(ticker, start="2020-01-01", end="2020-08-01")
      data.to_csv('datasets/daily/{}.csv'.format(ticker))

  return 'Success'

@app.route('/')
def index():
  """
  Landing page, wherein the patterns are
  displayed if a pattern is passed in as 
  an argument in the URL. 
  """

  stocks = {}
  with open('datasets/companies.csv') as f:
    for row in csv.reader(f):
      stocks[row[0]] = {'company': row[1]}

  # check for a pattern in the parameters
  pattern = request.args.get('pattern', False)
  if pattern:
    data_files = os.listdir('datasets/daily')
    for filename in data_files:
      
      company_df = pd.read_csv('datasets/daily/{}'.format(filename))
      ticker = filename.split('.')[0]

      # since the pattern is a string,
      # to access that pattern function of TA-Lib, 
      # access the attribute using getattr()
      pattern_function = getattr(talib, pattern)

      # use that function to generate results
      try:

        result = pattern_function(company_df['Open'], company_df['High'], company_df['Low'], company_df['Close'])
        last = result.tail(1).values[0]
        
        if last>0:
          stocks[ticker][pattern] = 'bullish'
        elif last<0:
          stocks[ticker][pattern] = 'bearish'
        else:
          stocks[ticker][pattern] = None


      except:
        pass

  return render_template('index.html', patterns = patterns, stocks = stocks, current_pattern=pattern)
