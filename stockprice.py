# -*- coding: utf-8 -*-
''' 
即時股價
'''
import requests
import datetime
import json
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import pandas_datareader as pdr
from bs4 import BeautifulSoup
import Imgur
import yfinance as yf
from matplotlib.font_manager import FontProperties # 設定字體
font_path = matplotlib.font_manager.FontProperties(fname='msjh.ttf')

emoji_upinfo = u'\U0001F447'
emoji_midinfo = u'\U0001F538'
emoji_downinfo = u'\U0001F60A'

def get_stock_name(stockNumber):
    try:
        url = f'https://tw.stock.yahoo.com/quote/{stockNumber}.TW'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        stock_name = soup.find('h1', class_='C($c-link-text) Fw(b) Fz(24px) Mend(8px)').text
        return stock_name
    except Exception as e:
        print(f"Error in get_stock_name: {e}")
        return "no"

# 使用者查詢股票
def getprice(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    if stock_name == "no": return "股票代碼錯誤!"
    content = ""
    stock = yf.Ticker(stockNumber + '.TW')
    hist = stock.history(period="5d")  # 獲取近5天的歷史數據
    if hist.empty:return "無法獲取股票數據，請確認代碼或稍後再試!"
    date = hist.index[-1].strftime('%Y-%m-%d')
    price = '%.2f' % hist["Close"][-1]  # 近日收盤價
    last_price = '%.2f' % hist["Close"][-2]  # 前一日收盤價
    spread_price = '%.2f' % (float(price) - float(last_price))  # 價差
    spread_ratio = '%.2f' % (float(spread_price) / float(last_price) * 100) + '%'  # 漲跌幅（百分比）
    spread_price = spread_price.replace("-", "▽ ") if float(last_price) > float(price) else "△ " + spread_price
    spread_ratio = spread_ratio.replace("-", "▽ ") if float(last_price) > float(price) else "△ " + spread_ratio
    open_price = '%.2f' % hist["Open"][-1]  # 開盤價
    high_price = '%.2f' % hist["High"][-1]  # 最高價
    low_price = '%.2f' % hist["Low"][-1]  # 最低價
    price_five = hist["Close"][-5:]  # 近五日收盤價
    stockAverage = '%.2f' % price_five.mean()  # 近五日平均價格
    stockSTD = '%.2f' % price_five.std()  # 近五日標準差
    content += f"回報編號{stock_name}的股價{emoji_upinfo}\n--------------\n日期: {date}\n{emoji_midinfo}最新收盤價: {price}\n{emoji_midinfo}開盤價: {open_price}\n{emoji_midinfo}最高價: {high_price}\n{emoji_midinfo}最低價: {low_price}\n{emoji_midinfo}價差: {spread_price} 漲跌幅: {spread_ratio}\n{emoji_midinfo}近五日平均價格: {stockAverage}\n{emoji_midinfo}近五日標準差: {stockSTD}\n"
    if msg.startswith("#"): content += f"--------------\n需要更詳細的資訊，可以點選以下選項進一步查詢唷{emoji_downinfo}"
    else: 
        content += '\n'
    return content

# --------- 畫近一年股價走勢圖
def stock_trend(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    end = datetime.datetime.now()
    date = end.strftime("%Y%m%d")
    year = str(int(date[0:4]) - 1)
    month = date[4:6]
    stock = pdr.DataReader(stockNumber+'.TW', 'yahoo', start= year+"-"+month,end=end)
    plt.figure(figsize=(12, 6))
    plt.plot(stock["Close"], '-' , label="收盤價")
    plt.plot(stock["High"], '-' , label="最高價")
    plt.plot(stock["Low"], '-' , label="最低價")
    plt.title(stock_name + '  收盤價年走勢',loc='center', fontsize=20, fontproperties=font_path)# loc->title的位置
    plt.xlabel('日期', fontsize=20, fontproperties=font_path)
    plt.ylabel('價格', fontsize=20, fontproperties=font_path)
    plt.grid(True, axis='y') # 網格線
    plt.legend(fontsize=14, prop=font_path)
    plt.savefig(msg + '.png') #存檔
    plt.show()
    plt.close() 
    return Imgur.showImgur(msg)

#股票收益率: 代表股票在一天交易中的價值變化百分比
def show_return(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    end = datetime.datetime.now()
    date = end.strftime("%Y%m%d")
    year = str(int(date[0:4]) - 1)
    month = date[4:6]
    stock = pdr.DataReader(stockNumber + '.TW', 'yahoo', start= year+"-"+month,end=end)
    stock['Returns'] = stock['Close'].pct_change()
    stock_return = stock['Returns'].dropna()
    plt.figure(figsize=(12, 6))
    plt.plot(stock_return, label="報酬率")
    plt.title(stock_name + '  年收益率走勢',loc='center', fontsize=20, fontproperties=font_path)# loc->title的位置
    plt.xlabel('日期', fontsize=20, fontproperties=font_path)
    plt.ylabel('報酬率', fontsize=20, fontproperties=font_path)
    plt.grid(True, axis='y') # 網格線
    plt.legend(fontsize=14, prop=font_path)
    plt.savefig(msg+'.png') #存檔
    plt.show()
    return Imgur.showImgur(msg)

# --------- 畫股價震盪圖
def show_fluctuation(stockNumber, msg):
    stock_name = get_stock_name(stockNumber)
    end = datetime.datetime.now()
    date = end.strftime("%Y%m%d")
    year = str(int(date[0:4]) - 1)
    month = date[4:6]
    stock = pdr.DataReader(stockNumber + '.TW', 'yahoo', start= year+"-"+month,end=end)
    stock['stock_fluctuation'] = stock["High"] - stock["Low"]
    max_value = max(stock['stock_fluctuation'][:]) # 最大價差
    min_value = min(stock['stock_fluctuation'][:]) # 最小價差
    plt.figure(figsize=(12, 6))
    plt.plot(stock['stock_fluctuation'], '-' , label="波動度", color="orange")
    plt.title(stock_name + '  收盤價年波動度',loc='center', fontsize=20, fontproperties=font_path)# loc->title的位置
    plt.xlabel('日期', fontsize=20, fontproperties=font_path)
    plt.ylabel('價格', fontsize=20, fontproperties=font_path)
    plt.grid(True, axis='y') # 網格線
    plt.legend(fontsize=14, prop= font_path)
    plt.savefig(msg + '.png') #存檔
    plt.show()
    plt.close() 
    return Imgur.showImgur(msg)
