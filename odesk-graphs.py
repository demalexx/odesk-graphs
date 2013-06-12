from os.path import isfile
from datetime import datetime, timedelta, date
from random import choice, randint
from dateutil.relativedelta import relativedelta
from json import dumps, loads

from bottle import route, run, template, request, redirect, response, static_file

from odesk import Client
from odesk.utils import Query, Q


# Global config for web-app
CONFIG = {}


class ODeskStats(object):
    """
    Class gets data from oDesk, extracts stats and returns it as dict with
    json data ready to be used by chart (Highcharts)
    """

    def __init__(self, client):
        super(ODeskStats, self).__init__()

        self.client = client
        self.weeks = []
        self.months = []

        self.data = {}
        self.teams = {}

    def get_data_json(self, provider_id, from_date, to_date=None):
        """Main method to get data from oDesk in Highcharts-ready format"""

        to_date = to_date or date.today()

        # Get data from oDesk
        self.data, self.teams = self._get_odesk_data(provider_id, from_date, to_date)

        # Prepare helpers: list of weeks and months
        self.weeks = self._get_weeks(from_date, to_date)
        self.months = self._get_months(from_date, to_date)

        # Process oDesk data, group it by weeks/months etc. This is main source
        # for following processing
        data_by_weeks = self._group_by_weeks()
        data_by_months = self._group_by_months()
        data_total = self._get_total_data()

        # Convert processed data to Highcharts-ready format
        # First process main charts data (columns, lines etc)
        hours_by_days_series = self._data_to_graph_series(self.data, u'days', u'hours')
        hours_by_weeks_series = self._data_to_graph_series(data_by_weeks, u'weeks', u'hours')
        earnings_by_week_series = self._data_to_graph_series(data_by_weeks, u'weeks', u'earnings')
        hours_by_months_series = self._data_to_graph_series(data_by_months, u'months', u'hours')
        earnings_by_months_series = self._data_to_graph_series(data_by_months, u'months', u'earnings')

        total_hours_pie = self._data_to_graph_pie(data_total[u'by_teams'], u'hours')
        total_earnings_pie = self._data_to_graph_pie(data_total[u'by_teams'], u'earnings')

        # Then process aux charts data - vertical lines as months delimiters etc
        weeks_categories = self._weeks_to_graph_categories()
        months_categories = self._months_to_graph_categories()

        weekends_plot_bands = self._weekends_to_graph_bands()
        months_for_days_plot_lines = self._months_for_days_to_graph_lines()
        months_plot_lines = self._months_to_graph_lines()
        years_plot_lines = self._years_to_graph_lines()

        # Convert Highchart-ready data to json, ready to include in Highcharts
        # config
        res = self._to_json_items({u'hours_by_days_series': hours_by_days_series,
                                   u'hours_by_weeks_series': hours_by_weeks_series,
                                   u'earnings_by_weeks_series': earnings_by_week_series,
                                   u'hours_by_months_series': hours_by_months_series,
                                   u'earnings_by_months_series': earnings_by_months_series,
                                   u'weeks_categories': weeks_categories,
                                   u'months_categories': months_categories,
                                   u'weekends_plot_bands': weekends_plot_bands,
                                   u'months_for_days_plot_lines': months_for_days_plot_lines,
                                   u'months_plot_lines': months_plot_lines,
                                   u'years_plot_lines': years_plot_lines,
                                   u'total_hours_pie': total_hours_pie,
                                   u'total_earnings_pie': total_earnings_pie})

        res[u'total_hours'] = int(data_total[u'hours'])
        res[u'total_earnings'] = int(data_total[u'earnings'])

        return res

    def _to_json(self, data):
        """
        Convert object to json with some features:
        - `date` instances will be represented as native JS Date objects (not
          as strings);
        """
        def json_handler(obj):
            """
            Represent `date` instances as "Date.UTC(year, month, day)", so this date
            could be used as native JS date. Also put this representation in
            extra quotes so they could be removed (to get Date.UTC(...) with no quotes -
            JS Date, and not "Date.UTC(...)" with quotes - JS string)
            """
            if isinstance(obj, date):
                return u"'''Date.UTC(%d, %d, %d)'''" % (obj.year, obj.month - 1, obj.day)

        return dumps(data, indent=4, default=json_handler) \
            .replace('"\'\'\'', '') \
            .replace('\'\'\'"', '')

    def _to_json_items(self, source_dict):
        """Convert all items of given dict to json"""
        res = {}
        for k, v in source_dict.items():
            res[k] = self._to_json(v)
        return res

    def _get_weeks(self, from_date, end_date):
        """
        Return list of weeks starting from given `from_date` till `end_date`
        (default is today), aligned by week start/end.
        E.g. if `from_date` is 08.06.2013 (saturday), then first week would be
        03 - 09 June (monday-sunday).
        Result has format `[[week_start_w, week_end_w], ...]`
        """
        weeks = []
        week_start = from_date - timedelta(days=from_date.weekday())
        week_end = week_start + timedelta(days=7)
        while week_start < end_date:
            weeks.append([week_start, week_end])

            week_start = week_end
            week_end = week_start + timedelta(days=7)

        return weeks

    def _get_months(self, from_date, end_date):
        """
        Similar to `get_weeks`, but return a list of months, aligned by month
        start/end
        """
        months = []
        month_start = from_date - timedelta(days=from_date.day - 1)
        month_end = month_start + relativedelta(months=1)
        while month_start < end_date:
            months.append([month_start, month_end])

            month_start = month_end
            month_end = month_start + relativedelta(months=1)

        return months

    def _get_odesk_data(self, provider_id, from_date, to_date):
        """
        Get report data from oDesk (in Google Data Services language), convert
        it to local format, also extract all teams. Return tuple with data and
        teams as dicts:

        {<day_d>: {<team_id_t>: {'hours': <hours-worked-at-day_f>,
                                 'earnings': <earned-money-at-day-f>},
                   ...}
        },
        {<team_id_t>: <team_name_t>,
         ...,
        }
        """
        q = Query(select=[u'worked_on', u'sum(hours)', u'sum(earnings)', u'team_id', u'team_name'],
                  where=(Q(u'worked_on') >= from_date) & (Q(u'worked_on') <= to_date),
                  order_by=(u'worked_on',))
        data = self.client.timereport.get_provider_report(provider_id, q)

        res_data = {}
        res_teams = {}
        for row in data[u'table'][u'rows']:
            cols = row['c']

            worked_on_date = datetime.strptime(cols[0][u'v'], u'%Y%m%d').date()
            hours = float(cols[1][u'v'])
            earnings = float(cols[2][u'v'])
            team_id = cols[3][u'v']
            team_name = cols[4][u'v']

            if team_id not in res_teams:
                res_teams[team_id] = team_name

            if worked_on_date not in res_data:
                res_data[worked_on_date] = {}

            res_data[worked_on_date][team_id] = {u'hours': hours,
                                                 u'earnings': earnings}

        return res_data, res_teams

    def _get_fake_data(self, from_date, to_date):
        res_data = {}
        res_teams = {u'google': u'Google',
                     u'fb': u'Facebook',
                     u'li': u'LinkedIn',
                     u'apple': u'Apple'}

        d = from_date
        while d < to_date:
            res_data[d] = {}

            teams_to_choice = res_teams.copy()
            for i in range(randint(1, 3)):
                team_key = choice(teams_to_choice.keys())

                hours = randint(1, 4)
                res_data[d][team_key] = {u'hours': hours,
                                         u'earnings': hours * randint(15, 25)}

                del teams_to_choice[team_key]

            d += timedelta(days=randint(1, 3))

        return res_data, res_teams

    def _group_by_weeks(self):
        """
        Group data in local format by weeks. Result format:
        {<week_w>: {<team_id_t>: {'hours': <hours_worked_on_week_w>,
                                  'earnings': <earned_money_on_week_w>},
                    ...}
         ...
        }
        """
        res = {}
        for day, day_data in self.data.items():
            week_index, week = self._get_week_by_date(day)

            if week_index not in res:
                res[week_index] = {}

            for team_id, team_data in day_data.items():
                if team_id not in res[week_index]:
                    res[week_index][team_id] = {u'hours': 0.0,
                                                u'earnings': 0.0}

                res[week_index][team_id][u'hours'] += team_data[u'hours']
                res[week_index][team_id][u'earnings'] += team_data[u'earnings']

        return res

    def _group_by_months(self):
        """
        Group data in local format by months. Result format:
        {<month_m>: {<team_id_t>: {'hours': <hours_worked_on_month_m>,
                                   'earnings': <earned_money_on_month_m>},
                     ...}
         ...
        }
        """
        res = {}
        for day, day_data in self.data.items():
            month_index, month = self._get_month_by_date(day)

            if month_index not in res:
                res[month_index] = {}

            for team_id, team_data in day_data.items():
                if team_id not in res[month_index]:
                    res[month_index][team_id] = {u'hours': 0.0,
                                                 u'earnings': 0.0}

                res[month_index][team_id][u'hours'] += team_data[u'hours']
                res[month_index][team_id][u'earnings'] += team_data[u'earnings']

        return res

    def _get_total_data(self):
        """
        Return total hours and earnings and totals grouped by team.
        Result format:
        {'hours': <total_worked_hours_in_all_teams>,
         'earnings': <total_earned_money_in_all_teams>,
         'by_teams': {<team_id_t>: {'hours': <total_hours_worked_for_team_t>,
                                    'earnings': <total_earned_money_for_team_t>},
                      ...}
         }
        }
        """
        total_hours = 0.0
        total_earnings = 0.0
        by_teams = {}
        for day, day_data in self.data.items():
            for team_id, team_data in day_data.items():
                if team_id not in by_teams:
                    by_teams[team_id] = {u'hours': 0.0,
                                         u'earnings': 0.0}

                by_teams[team_id][u'hours'] += team_data[u'hours']
                by_teams[team_id][u'earnings'] += team_data[u'earnings']

                total_hours += team_data[u'hours']
                total_earnings += team_data[u'earnings']

        return {u'hours': total_hours,
                u'earnings': total_earnings,
                u'by_teams': by_teams}

    def _data_to_graph_series(self, data, group, value_type):
        """
        Convert data from local format to HighCharts series format.
        `data` is grouped by `group` data;
        `group` is one of "days", "weeks", "months";
        `value_type` is value to get, one of "hours", "earnings".
        Result format:
        [{'name': <team_id_t>,
          'data': [1, 2, 3, ...]
         },
         ...
        ]
        """
        if group == u'weeks':
            group_source = self.weeks
        elif group == u'months':
            group_source = self.months
        elif group == u'days':
            group_source = data.keys()
            group_source.sort()
        else:
            return []

        res = []
        for team_id, team_name in self.teams.items():
            values = []

            for group_index, group_data in enumerate(group_source):
                if group == u'days':
                    data_index = group_data
                else:
                    data_index = group_index

                cur_group_data = data.get(data_index)

                value = 0.0
                if cur_group_data:
                    value = cur_group_data.get(team_id, {}).get(value_type, 0.0)

                if group == u'days':
                    values.append([group_data, value])
                else:
                    values.append(value)

            res.append({u'name': team_name,
                        u'data': values})

        return res

    def _data_to_graph_pie(self, data, value_type):
        """Convert data from local format to HighCharts pie format"""
        values = []
        for team_id, team_data in data.items():
            values.append([self.teams[team_id], team_data[value_type]])

        return [{u'type': u'pie',
                 u'data': values}]

    def _weeks_to_graph_categories(self):
        """
        Return list of weeks as HighChart axis categories. Used as X axis of
        "by weeks" graphs.
        """
        return [[week[0], week[1]] for week in self.weeks]

    def _months_to_graph_categories(self):
        """
        Return list of months as HighChart axis categories. Used as X axis of
        "by months" graphs.
        """
        return [month[0] for month in self.months]

    def _weekends_to_graph_bands(self):
        """
        Return list of weekends as HighChart plot bands. Used on "by days"
        graphs
        """
        res = []
        for week in self.weeks:
            res.append({u'from': week[0] + timedelta(days=5),
                        u'to': week[0] + timedelta(days=7),
                        u'color': u'#fcffc5'})
        return res

    def _months_for_days_to_graph_lines(self):
        """
        Return list of months as HighChart plot lines. Used to mark months and
        years start as vertical line on "by days" graphs. Mark months with light
        line and years with darker line.
        """
        res = []

        for week_index, week in enumerate(self.weeks):
            if week[0].year != week[1].year:
                color = u'gray'
            elif week[0].month != week[1].month:
                color = u'lightgray'
            else:
                color = None

            if color:
                res.append({u'value': week[1] - timedelta(days=week[1].day - 1),
                            u'width': 1.0,
                            u'color': color,
                            u'zIndex': 1})

        return res

    def _months_to_graph_lines(self):
        """
        Return list of months as HighChart plot lines. Used to mark months and
        years starts as vertical lines on "by weeks" graphs. Mark months with
        light line and years with darker line.
        """
        res = []

        for week_index, week in enumerate(self.weeks):
            if week[0].year != week[1].year:
                color = 'gray'
            elif week[0].month != week[1].month:
                color = 'lightgray'
            else:
                color = None

            if color:
                res.append({u'value': week_index + 0.5,
                            u'width': 1.0,
                            u'color': color,
                            u'zIndex': 1})

        return res

    def _years_to_graph_lines(self):
        """
        Return list of years as HighChart plot lines. Used to mark years starts
        as vertical lines on "by months" graphs.
        """
        res = []
        for i, m in enumerate(self.months):
            if m[0].month == 1:
                res.append({u'value': i - 0.5,
                            u'width': 1.0,
                            u'color': u'gray'})

        return res

    def _get_week_by_date(self, d):
        for i, w in enumerate(self.weeks):
            if w[0] <= d < w[1]:
                return i, w

    def _get_month_by_date(self, d):
        for i, m in enumerate(self.months):
            if m[0] <= d < m[1]:
                return i, m


# Web-app functions

def load_config():
    if isfile(u'config.json'):
        with open(u'config.json', u'r') as f:
            return loads(f.read())
    return {}


def save_config():
    with open(u'config.json', u'w') as f:
        f.write(dumps(CONFIG))


def is_configured():
    return {u'key', u'secret', u'oauth_access_token',
            u'oauth_access_token_secret', u'provider_id'} <= set(CONFIG.keys())


def get_client():
    return Client(CONFIG[u'key'], CONFIG[u'secret'], auth=u'oauth',
                  oauth_access_token=CONFIG[u'oauth_access_token'],
                  oauth_access_token_secret=CONFIG[u'oauth_access_token_secret'])


def get_logged_user_info():
    return get_client().hr.get_user(u'me')


def str_to_date(date_str):
    try:
        return datetime.strptime(date_str, u'%d.%m.%Y').date()
    except ValueError:
        pass

# Bottle part - views

@route(u'/')
def index():
    if not is_configured():
        return redirect(u'/setup')

    from_date_str = request.GET.get(u'from_date')
    to_date_str = request.GET.get(u'to_date')

    if from_date_str:
        from_date = str_to_date(from_date_str)
        to_date = str_to_date(to_date_str)

        stats = ODeskStats(get_client())
        data = stats.get_data_json(CONFIG[u'provider_id'], from_date, to_date)
    else:
        data = {}

    return template(u'templates/index.html',
                    title=u'oDesk provider %s stats' % CONFIG[u'provider_id'],
                    data=data,
                    from_date=from_date_str,
                    to_date=to_date_str)


@route(u'/setup', method=[u'GET', u'POST'])
def setup():
    steps = {
        u'keys': {
            u'completed': False
        },
        u'authorize': {
            u'completed': False,
            u'authorize_url': u''
        },
        u'last': {
            u'user_info': {}
        }
    }

    if u'key' in CONFIG and u'secret' in CONFIG:
        steps[u'keys'][u'completed'] = True

        if u'oauth_access_token' in CONFIG and u'oauth_access_token_secret' in CONFIG:
            steps[u'authorize'][u'completed'] = True

            steps[u'last'][u'user_info'] = get_logged_user_info()
        else:
            client = Client(CONFIG[u'key'], CONFIG[u'secret'], auth=u'oauth')
            steps[u'authorize'][u'authorize_url'] = \
                client.auth.get_authorize_url(u'%s://%s/auth-callback' %
                                              (request.urlparts.scheme, request.urlparts.netloc))

            response.set_cookie('request_token', client.auth.request_token)
            response.set_cookie('request_token_secret', client.auth.request_token_secret)

    if request.method == u'POST':
        CONFIG[u'key'] = request.forms.get(u'key')
        CONFIG[u'secret'] = request.forms.get(u'secret')

        save_config()

        return redirect(u'/setup')

    return template(u'templates/setup.html',
                    title=u'Initial configuration',
                    steps=steps)


@route(u'/auth-callback')
def auth_callback():
    client = Client(CONFIG[u'key'], CONFIG[u'secret'], auth=u'oauth')
    client.auth.request_token = request.cookies[u'request_token']
    client.auth.request_token_secret = request.cookies[u'request_token_secret']

    verifier = request.GET[u'oauth_verifier']
    access_token, access_token_secret = client.auth.get_access_token(verifier)

    CONFIG[u'oauth_access_token'] = access_token
    CONFIG[u'oauth_access_token_secret'] = access_token_secret
    CONFIG[u'provider_id'] = get_logged_user_info()[u'id']

    save_config()

    return redirect(u'/setup')


@route(u'/static/<path:path>')
def callback(path):
    return static_file(path, u'templates/static')


if __name__ == u'__main__':
    CONFIG = load_config()

    run(reloader=True, debug=True)