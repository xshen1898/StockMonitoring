#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author shen.charles@hotmail.com

import time
import subprocess

import requests
import prettytable


def add_market_code(x):
    y = '0.' + x
    if x.startswith('6'):
        y = '1.' + x
    return y


def get_data(stock_codes):
    stock_codes = list(map(add_market_code, stock_codes))
    stock_codes = ','.join(stock_codes)

    endpoint = 'http://push2.eastmoney.com/api/qt/ulist.np/get'
    var1 = '?fields=f2,f3,f14,f12,f13,f19'
    var2 = '&invt=2&fltt=2&fid=f3'
    var3 = '&ut=bd1d9ddb04089700cf9c27f6f7426281&cb=&secids='
    url = '{0}{1}{2}{3}{4}'.format(endpoint, var1, var2, var3, stock_codes)
    response = requests.get(url)
    data = response.json()
    return data['data']['diff']


def speak(text):
    text = text.replace('-', '负').replace('.', '点')
    cmd = 'espeak -vzh {}'.format(text)
    subprocess.call(cmd, shell=True, stderr=subprocess.PIPE)
    return True


def hyphen_to_zero(x):
    for k, v in x.items():
        if v == '-':
            x[k] = 0.0
    return x


def main(stock_codes):
    tb = prettytable.PrettyTable()
    tb.field_names = ['股票代码', '股票名称', '最新价', '涨跌幅', '警报']

    stock_list = get_data(stock_codes)
    stock_list = list(map(hyphen_to_zero, stock_list))
    stock_list = sorted(stock_list, key=lambda x: x['f3'], reverse=True)
    alarms = []

    for stock in stock_list:
        msg = ''
        # 针对所有自选股票的判断条件
        if stock['f3'] > 9.8:
            if stock['f12'] not in []:
                msg = '{}涨停'.format(stock['f14'])
        elif stock['f3'] > 5.0:
            # 屏蔽某些股票的报警，例如'002158'
            if stock['f12'] not in ['002158']:
                msg = '{}涨幅{}'.format(stock['f14'], stock['f3'])
        elif stock['f3'] < -5.0:
            if stock['f12'] not in []:
                msg = '{}跌幅{}'.format(stock['f14'], stock['f3'])
        elif stock['f3'] < -9.0:
            if stock['f12'] not in []:
                msg = '{}跌停'.format(stock['f14'])
        # 针对某些自选股票的判断条件
        if stock['f12'] in ['002158']:
            if stock['f3'] < 9.8:
                msg = '{}开板'.format(stock['f14'])
        # 针对某个自选股票的判断条件
        if stock['f12'] == '000063':
            if stock['f2'] < 32.0:
                msg = '{}价格小于32'.format(stock['f14'])
        if msg:
            alarms.append(msg)
        row = [stock['f12'], stock['f14'], stock['f2'], stock['f3']]
        row.append(msg)
        tb.add_row(row)

    print(tb)
    for alarm in alarms:
        speak(alarm)


if __name__ == '__main__':
    stock_codes = [
        '000063',
        '002902',
        '600410',
        '000862',
        '603738',
        '600604',
        '000536',
        '601330',
        '603169',
    ]

    while True:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        try:
            main(stock_codes)
        except:
            print('Failed')
        time.sleep(5)
