"""
Python bindings to odesk API
python-odesk version 0.5
(C) 2010 oDesk
"""

from datetime import date


class Q(object):
    '''Simple query constructor'''

    def __init__(self, arg1, operator=None, arg2=None):
        self.arg1 = arg1
        self.operator = operator
        self.arg2 = arg2

    def __and__(self, other):
        return self.__class__(self, 'AND', other)

    def __or__(self, other):
        return self.__class__(self, 'OR', other)

    def __eq__(self, other):
        return self.__class__(self, '=', other)

    def __lt__(self, other):
        return self.__class__(self, '<', other)

    def __le__(self, other):
        return self.__class__(self, '<=', other)

    def __gt__(self, other):
        return self.__class__(self, '>', other)

    def __ge__(self, other):
        return self.__class__(self, '>=', other)

    def arg_to_string(self, arg):
        if isinstance(arg, self.__class__):
            if arg.operator:
                return '(%s)' % arg
            else:
                return arg
        elif isinstance(arg, str):
            return "'%s'" % arg
        elif isinstance(arg, date):
            return "'%s'" % arg.isoformat()
        else:
            return str(arg)

    def __str__(self):
        if self.operator:
            str1 = self.arg_to_string(self.arg1)
            str2 = self.arg_to_string(self.arg2)
            return '%s %s %s' % (str1, self.operator, str2)
        else:
            return self.arg1


class Query(object):
    '''Simple query'''

    DEFAULT_TIMEREPORT_FIELDS = ['worked_on',
                                 'team_id',
                                 'team_name',
                                 'task',
                                 'memo',
                                 'hours']
    DEFAULT_FINREPORT_FIELDS = ['reference',
                                'date',
                                'buyer_company__id',
                                'buyer_company_name',
                                'buyer_team__id',
                                'buyer_team_name',
                                'provider_company__id',
                                'provider_company_name',
                                'provider_team__id',
                                'provider_team_name',
                                'provider__id',
                                'provider_name',
                                'type',
                                'subtype',
                                'amount']

    def __init__(self, select, where=None, order_by=None):
        self.select = select
        self.where = where
        self.order_by = order_by

    def __str__(self):
        select = self.select
        select_str = 'SELECT ' + ', '.join(select)
        where_str = ''
        if self.where:
            where_str = ' WHERE %s' % self.where
        order_by_str = ''
        if self.order_by:
            order_by_str = ' ORDER BY ' + ','.join(self.order_by)
        return ''.join([select_str, where_str, order_by_str])


class Table(object):

    """
    A helper class to access cryptic GDS response as a list of dictionaries
    """

    def __init__(self, data):
        self._cols = data['cols']   # Original data
        self._rows = data['rows']
        self.cols = [col['label'] for col in data['cols']]
        self.rows = []
        if data['rows']:
            if data['rows'][0] != '':   # Empty response
                for row in [row['c'] for row in data['rows']]:
                    self.rows.append([cell['v'] for cell in row])

    def __getitem__(self, key):
        if not isinstance(key, (slice, int)):
            raise TypeError
        if isinstance(key, slice):
            return [dict(zip(self.cols, row)) for row in self.rows[key]]
        else:
            return dict(zip(self.cols, self.rows[key]))

    def __len__(self):
        return len(self.rows)
