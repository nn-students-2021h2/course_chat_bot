# -*- coding: utf-8 -*-
from datetime import date, timedelta

from data_parser import DataParser


class DiseaseDynamics:
    def __init__(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        day_before_yesterday = today - timedelta(days=2)
        url_yesterday_date = yesterday.strftime('%m-%d-%Y')
        url_day_before_yesterday_date = day_before_yesterday.strftime('%m-%d-%Y')
        self.today_stats = DataParser(url_yesterday_date)
        self.yesterday_stats = DataParser(url_day_before_yesterday_date)

    def get_disease_dynamic(self) -> list:
        today_stats = self.today_stats.retrieve_all()
        yesterday_stats = self.yesterday_stats.retrieve_all()
        dynamics = []
        for province in today_stats:
            yesterday_stats_by_province = self.find_record(province, yesterday_stats)
            if yesterday_stats_by_province is None:
                continue
            province_dynamic = {
                'Country': province['Country_Region'],
                'State': province['Province_State'],
                'Confirmed': province['Confirmed'],
                'Dynamic': int(province['Confirmed']) - int(yesterday_stats_by_province['Confirmed']) if
                yesterday_stats_by_province['Confirmed'] else province['Confirmed'],
            }
            dynamics.append(province_dynamic)
        return dynamics

    def get_top_five(self):
        reply_msg = ''
        dynamics = self.get_disease_dynamic()
        sorted_data = sorted(dynamics, key=lambda x: x['Dynamic'], reverse=True)
        for data in sorted_data[:5:]:
            reply_msg += f'{data["Country"]}, {data["State"]}: {data["Confirmed"]} ({"+" + str(data["Dynamic"])})\n'
        return reply_msg

    @staticmethod
    def find_record(province, yesterday_stats):
        for state in yesterday_stats:
            if province['Country_Region'] == state['Country_Region'] and \
                    province['Province_State'] == state['Province_State']:
                return state
        return None
