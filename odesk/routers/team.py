"""
Python bindings to odesk API
python-odesk version 0.5
(C) 2010-2011 oDesk
"""
from odesk.namespaces import Namespace


class Team(Namespace):

    api_url = 'team/'
    version = 1

    def get_snapshot(self, company_id, user_id, datetime=None):
        """
        Retrieve a company's user snapshots during given time or 'now'

        Parameters:
          company_id    The Company ID
          user_id       The User ID
          datetime      (default 'now') Timestamp either a datetime
                        object
                        or a string in ISO 8601 format (in UTC)
                        yyyymmddTHHMMSSZ
                        or a string with UNIX timestamp (number of
                        seconds after epoch)
        """
        url = 'snapshots/%s/%s' % (str(company_id), str(user_id))
        if datetime:   # date could be a list or a range also
            url += '/%s' % datetime.isoformat()
        result = self.get(url)
        if 'snapshot' in result:
            snapshot = result['snapshot']
        else:
            snapshot = []
        return snapshot

    def update_snapshot(self, company_id, user_id, datetime=None,
                        memo=''):
        """
        Update a company's user snapshot memo at given time or 'now'

        Parameters:
          company_id    The Company ID
          user_id       The User ID
          datetime      (default 'now') Timestamp either a datetime
                        object
                        or a string in ISO 8601 format (in UTC)
                        yyyymmddTHHMMSSZ
                        or a string with UNIX timestamp (number of
                        seconds after epoch)
          memo          The Memo text
        """
        url = 'snapshots/%s/%s' % (str(company_id), str(user_id))
        if datetime:
            url += '/%s' % datetime.isoformat()
        return self.post(url, {'memo': memo})

    def delete_snapshot(self, company_id, user_id, datetime=None):
        """
        Delete a company's user snapshot memo at given time or 'now'

        Parameters:
          company_id    The Company ID
          user_id       The User ID
          datetime      (default 'now') Timestamp either a datetime
                        object
                        or a string in ISO 8601 format (in UTC)
                        yyyymmddTHHMMSSZ
                        or a string with UNIX timestamp (number of
                        seconds after epoch)
        """
        url = 'snapshots/%s/%s' % (str(company_id), str(user_id))
        if datetime:
            url += '/%s' % datetime.isoformat()
        return self.delete(url)

    def get_workdiaries(self, team_id, username, date=None):
        """
        Retrieve a team member's workdiaries for given date or today

        Parameters:
          team_id       The Team ID
          username      The Team Member's username
          date          A datetime object or a string in yyyymmdd
                        format (optional)
        """
        url = 'workdiaries/%s/%s' % (str(team_id), str(username))
        if date:
            url += '/%s' % str(date)
        result = self.get(url)
        snapshots = result.get('snapshots', {}).get('snapshot', [])
        if not isinstance(snapshots, list):
            snapshots = [snapshots]
        #not sure we need to return user
        return result['snapshots']['user'], snapshots

    def get_stream(self, team_id, user_id=None,\
                   from_ts=None):
        """
        get_stream(team_id, user_id=None, from_ts=None)
        """
        url = 'streams/%s' % (team_id)
        if user_id:
            url += '/%s' % (user_id)
        if from_ts:
            data = {'from_ts': from_ts}
        else:
            data = {}
        result = self.get(url, data)
        return result['streams']['snapshot']

    def get_teamrooms(self, target_version=1):
        """
        Retrieve all teamrooms accessible to the authenticated user

        Parameters:
            target_version      Version of future requested API
        """
        url = 'teamrooms'

        current_version = self.version
        if target_version != current_version:
            self.version = target_version
        result = self.get(url)
        if 'teamrooms' in result and 'teamroom' in result['teamrooms']:
            teamrooms = result['teamrooms']['teamroom']
        else:
            teamrooms = []
        if not isinstance(teamrooms, list):
            teamrooms = [teamrooms]
        if target_version != current_version:
            self.version = current_version
        return teamrooms

    def get_snapshots(self, team_id, online='now', target_version=1):
        """
        Retrieve team member snapshots

        Parameters:
          team_id           The Team ID
          online            'now' / 'last_24h' / 'all' (default 'now')
                            Filter for logged in users / users active in
                            last 24 hours / all users
          target_version    Version of future requested API
        """
        url = 'teamrooms/%s' % team_id
        current_version = self.version
        if target_version != current_version:
            self.version = target_version
        result = self.get(url, {'online': online})
        if 'teamroom' in result and 'snapshot' in result['teamroom']:
            snapshots = result['teamroom']['snapshot']
        else:
            snapshots = []
        if not isinstance(snapshots, list):
            snapshots = [snapshots]
        if target_version != current_version:
            self.version = current_version
        return snapshots
