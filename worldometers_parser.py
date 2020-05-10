import requests
from collections import defaultdict
from bs4 import BeautifulSoup

# Adapted from https://github.com/GoBig87/corona_virus_tracker/blob/31334a849ca837d9a989e2a8f728533f0652c465/web_scraping/world_meters_parser.py
class WorldMetersParser(object):
    '''
    Simple Web parser to crawl Worldometers coronavirus data and place into a dictionary
    This can be ran as a cron job by simply running the 'get_data' method.
    Due to the hackish nature of web crawling this can break if anything changes to the host website
    Data is extracted into the country_dict where you can get the data back as country_data[country][key]
    keys are
        dates
        total-currently-infected-linear
        deaths-cured-outcome-small
        coronavirus-cases-linear
        coronavirus-cases-log
        graph-cases-daily
        graph-active-cases-total
        coronavirus-deaths-linear
        coronavirus-deaths-log
        graph-deaths-daily
        deaths-cured-outcome
    '''
    def __init__(self):
        self.base_url = "https://www.worldometers.info/coronavirus/country/"
        self.country_list = ['us', 'china', 'italy', 'south-korea', 'france', 'spain', 'germany', 'uk', 'united-arab-emirates', 'saudi-arabia']
        self.country_dict = defaultdict()

        self.get_data()

    def get_data(self):
        for country in self.country_list:
            self.country_data(country)

    def country_data(self, country):
        self.country_dict[country] = defaultdict()

        url = self.base_url + country + '/'
        outs = requests.get(url=url)
        parsed = BeautifulSoup(outs.text, 'html.parser')
        scripts = parsed.find_all("script")

        for script in scripts:
            # inside the script sections look for the Highcharts javascript code that makes the graphs
            if 'Highcharts.chart' in script.text:
                # these if statements catch each type of graph on the web page and capture the data
                if 'total-currently-infected-linear' in script.text:
                    dates, total_currently_infected_linear = self._find_data(script, 'total-currently-infected-linear', 4)
                    self.country_dict[country]['total-currently-infected-linear'] = total_currently_infected_linear

                if 'deaths-cured-outcome-small' in script.text:
                    dates, deaths_cured_outcome_small = self._find_data(script, 'deaths-cured-outcome-small', 3)
                    self.country_dict[country]['total-currently-infected-linear'] = deaths_cured_outcome_small

                if 'coronavirus-cases-linear' in script.text:
                    dates, coronavirus_cases_linear = self._find_data(script, 'coronavirus-cases-linear', 3)
                    self.country_dict[country]['coronavirus-cases-linear'] = coronavirus_cases_linear

                if 'coronavirus-cases-log' in script.text:
                    dates, coronavirus_cases_log = self._find_data(script, 'coronavirus-cases-log', 3)
                    self.country_dict[country]['coronavirus-cases-log'] = coronavirus_cases_log

                if 'graph-cases-daily' in script.text:
                    dates, graph_cases_daily = self._find_data(script, 'graph-cases-daily', 3)
                    self.country_dict[country]['graph-cases-daily'] = graph_cases_daily

                if 'graph-active-cases-total' in script.text:
                    dates, graph_active_cases_total = self._find_data(script, 'graph-active-cases-total', 3)
                    self.country_dict[country]['graph-active-cases-total'] = graph_active_cases_total

                if 'coronavirus-deaths-linear' in script.text:
                    dates, coronavirus_death_linear = self._find_data(script, 'coronavirus-deaths-linear', 3)
                    self.country_dict[country]['coronavirus-deaths-linear'] = coronavirus_death_linear

                if 'coronavirus-deaths-log' in script.text:
                    dates, coronavirus_death_log = self._find_data(script, 'coronavirus-deaths-log', 3)
                    self.country_dict[country]['coronavirus-deaths-log'] = coronavirus_death_log

                if 'graph-deaths-daily' in script.text:
                    dates, graph_cured_daily = self._find_data(script, 'graph-deaths-daily', 3)
                    self.country_dict[country]['graph-deaths-daily'] = graph_cured_daily
                    dates = [date[1:-1] for date in dates]
                    self.country_dict[country]['dates'] = dates

                if 'deaths-cured-outcome' in script.text:
                    dates, deaths_cured_outcome = self._find_data(script, 'deaths-cured-outcome', 3)
                    self.country_dict[country]['deaths-cured-outcome'] = deaths_cured_outcome


    def _find_data(self, script, graph_name, array_element):
        # If things break this is most likely where they will break
        # This method tries to parse out the x and y axis of the chart
        temp_script = script.text.split('Highcharts.chart')[-1]
        temp_script = str(temp_script.split("('" + graph_name + "', ")[-1])
        temp_script_array = temp_script.split('[')
        dates = temp_script_array[1].split(']')[0].split(',')
        values = temp_script_array[array_element].split(']')[0].split(',')
        for i in range(0, len(values)):
            if values[i] in ['null', '"nan"']:
                values[i] = 0
            else:
                values[i] = float(values[i])
        return dates, values




