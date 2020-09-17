#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author shen.charles@hotmail.com

import json

import requests
import prettytable


def get_data():
    url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'nufm.dfcfw.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    }
    params = {
        'type': 'ct',
        'st': '(FFRank)',
        'sr': 1,
        'p': 1,
        'ps': 4000,
        'js': '{"data":[(x)]}',
        'token': '894050c76af8597a853f5b408b759f5d',
        'cmd': 'C._AB',
        'sty': 'DCFFITAM'
    }
    response = requests.get(url, params=params, headers=headers, verify=False)
    data_byte = response.content
    data_str = data_byte.decode('utf-8')
    data_dict = json.loads(data_str)
    return data_dict['data']


if __name__ == '__main__':
    stock_data = get_data()
    tb = prettytable.PrettyTable()
    tb.field_names = ['股票代码', '股票名称', '最新价', '主力持仓占比', '今日排名', '今日涨跌', '5日涨跌', '所属板块']
    stock_list = []
    for data in stock_data:
        items = data.split(',')
        values = list(
            map(lambda x: 0 if x == '-' else (x.strip('%') if '%' in x else x), items)
        )
        if 9.8 < float(values[6]):
            stock = values[1:7]
            stock.append(values[9])
            stock.append(values[13])
            stock_list.append(stock)
    stock_list = sorted(stock_list, key=lambda x: float(x[-3]))
    stock_codes = []
    for row in stock_list:
        tb.add_row(row)
        stock_codes.append(row[0])
    print(tb)
    print(stock_codes)
