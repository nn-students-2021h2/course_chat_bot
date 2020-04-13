# -*- coding: utf-8 -*-
import csv
import os
from datetime import date, timedelta

import requests


class DataParser:
    def __init__(self, url_date=None):
        if not url_date:
            today = date.today()
            yesterday = today - timedelta(days=1)
            url_date = yesterday.strftime('%m-%d-%Y')
        self.url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
                   'csse_covid_19_daily_reports/' + url_date + '.csv'
        self.path_to_file = os.path.join(os.curdir, f'{url_date}.csv')

    def serialize_data(self) -> None:
        if os.path.exists(self.path_to_file):
            return
        try:
            req = requests.get(self.url)
            if req.ok:
                with open(self.path_to_file, 'wb') as stat_file:
                    stat_file.write(req.content)
        except Exception as err:
            print(f'Error occurred: {err}')

    def get_most_diseased(self) -> str:
        res = ''
        most_diseased = self.retrieve_top_five()
        for province in most_diseased:
            res += f'{province["Country_Region"]}, {province["Province_State"]}: {province["Confirmed"]}\n'
        return res

    def retrieve_top_five(self) -> list:
        self.serialize_data()
        with open(self.path_to_file, newline='') as csvfile:
            rd = csv.DictReader(csvfile, delimiter=',')
            sorted_data = sorted(rd, key=lambda x: int(x['Confirmed']), reverse=True)
            return sorted_data[:5:]

    def retrieve_all(self) -> list:
        self.serialize_data()
        with open(self.path_to_file, newline='') as csvfile:
            rd = csv.DictReader(csvfile, delimiter=',')
            return sorted(rd, key=lambda x: int(x['Confirmed']), reverse=True)
