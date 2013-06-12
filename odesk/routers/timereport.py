"""
Python bindings to odesk API
python-odesk version 0.5
(C) 2010-2011 oDesk
"""
from odesk.namespaces import GdsNamespace


class TimeReport(GdsNamespace):
    api_url = 'timereports/'
    version = 1

    def get_provider_report(self, provider_id, query, hours=False):
        '''
        Get caller's specific time report
        The caller of this API must be the provider himself

        Parameters
          provider_id   The provider_id of the caller
          query         The GDS query string
          hours         Limits the query to hour specific elements and
                        hides all
                        financial details (optional: defaults to False)
        '''
        url = 'providers/%s' % str(provider_id)
        if hours:
            url += '/hours'
        tq = str(query)
        result = self.get(url, data={'tq': tq})
        return result

    def get_company_report(self, company_id, query, hours=False):
        """
        Generate company wide time reports. All reporting fields available
        except earnings related fields. In order to access this API the
        authorized user needs either hiring or finance permissions to all
        teams within the company

        Parameters
          company_id    Company ID
          query         The GDS query string
          hours         Limits the query to hour specific
                        elements and hides all
                        financial details (optional: defaults to False)
        """
        url = 'companies/%s' % str(company_id)
        if hours:
            url += '/hours'
        tq = str(query)
        result = self.get(url, data={'tq': tq})
        return result

    def get_team_report(self, company_id, team_id, query, hours=False):
        """
        Generate team specific time reports.

        Parameters
          company_id    The Company ID
          team_id       The Team ID
          query         The GDS query string
          hours         Limits the query to hour specific elements and hides
                        all financial details (optional: defaults to False)
        """
        url = 'companies/%s/teams/%s' % (str(company_id), str(team_id))
        if hours:
            url += '/hours'
        tq = str(query)
        result = self.get(url, data={'tq': tq})
        return result

    def get_agency_report(self, company_id, agency_id, query, hours=False):
        """
        Generate agency specific time reports.

        Parameters
          company_id    The Company ID
          agency_id     The Agency ID
          query         The GDS query string
          hours         Limits the query to hour specific elements and hides
                        all financial details (optional: defaults to False)
        """
        url = 'companies/%s/agencies/%s' % (str(company_id), str(agency_id))
        if hours:
            url += '/hours'
        tq = str(query)
        result = self.get(url, data={'tq': tq})
        return result
