"""
Python bindings to odesk API
python-odesk version 0.5
(C) 2010-2011 oDesk
"""
from odesk.exceptions import APINotImplementedException
from odesk.namespaces import Namespace


class HR(Namespace):
    """
    HR API
    """
    api_url = 'hr/'
    version = 2

    '''user api'''

    def get_user(self, user_reference):
        """
        Retrieve the user object from the user reference

        Parameters:
          user_reference    The user reference
        """
        url = 'users/%s' % str(user_reference)
        result = self.get(url)
        return result['user']

    '''company api'''

    def get_companies(self):
        """
        Retrieves the list of companies to which the current authorized user
        has access
        """
        url = 'companies'
        result = self.get(url)
        return result['companies']

    def get_company(self, company_referece):
        """
        Retrieve the company object from the company reference

        Parameters:
          company_reference     The company reference (can be found using
            get_companies method)
        """
        url = 'companies/%s' % str(company_referece)
        result = self.get(url)
        return result['company']

    def get_company_teams(self, company_referece):
        """
        Retrieve a list of teams within the company being referenced
        (as long as the user has access to the referenced company)

        Parameters
          company_reference     The company reference (can be found using
            get_companies method)
        """
        url = 'companies/%s/teams' % str(company_referece)
        result = self.get(url)
        return result['teams']

    def get_company_tasks(self, company_referece):
        """
        API doesn't support this call yet
        """
        raise APINotImplementedException("API doesn't support this call yet")

    def get_company_users(self, company_referece, active=True):
        """
        Retrieve a list of all users within the referenced company.
        (only available for users with hiring privileges for the company)

        Parameters
          company_reference     The company reference (can be found using
            get_companies method)
          active                True/False (default True)
        """
        url = 'companies/%s/users' % str(company_referece)
        if active:
            data = {'status_in_company': 'active'}
        else:
            data = {'status_in_company': 'inactive'}
        result = self.get(url, data)
        return result['users']

    '''team api'''

    def get_teams(self):
        """
        Retrieve a list of all the teams that a user has acccess to.
        (this will return teams across all companies to which the current
            user has access)
        """
        url = 'teams'
        result = self.get(url)
        return result['teams']

    def get_team(self, team_reference, include_users=False):
        """
        Retrieve the team information

        Parameters
          team_reference    The team reference
          include_users     Whether to include details of users
                            (default: False)
        """
        url = 'teams/%s' % str(team_reference)
        result = self.get(url, {'include_users': include_users})
        #TODO: check how included users returned
        return result['team']

    def get_team_tasks(self, team_reference):
        """
        API doesn't support this call yet
        """
        raise APINotImplementedException("API doesn't support this call yet")

    def get_team_users(self, team_reference, active=True):
        """
        get_team_users(team_reference, active=True)
        """
        url = 'teams/%s/users' % str(team_reference)
        if active:
            data = {'status_in_team': 'active'}
        else:
            data = {'status_in_team': 'inactive'}
        result = self.get(url, data)
        return result['users']

    def post_team_adjustment(self, team_reference, engagement_reference,
                             amount, comments, notes):
        '''
        Add bonus to an engagement

        Parameters
          team_reference        The Team reference
          engagement_reference  The Engagement reference
          amount                The adjustment/bonus amount
          comments              Comments
          notes                 Notes
        '''
        url = 'teams/%s/adjustments' % str(team_reference)
        data = {'engagement__reference': engagement_reference,
                'amount': amount,
                'comments': comments,
                'notes': notes}
        result = self.post(url, data)
        return result['adjustment']

    '''task api'''

    def get_tasks(self):
        "API doesn't support this call yet"
        raise APINotImplementedException("API doesn't support this call yet")

    '''userrole api'''

    def get_user_role(self, user_reference=None, team_reference=None,
                      sub_teams=False):
        '''
        Retrieve a complete list of all roles the reference user
        has within the referenced team/sub teams.

        Parameters
          user_reference    The User reference (optional: defaults to API user)
          team_reference    The team reference (optional)
          sub_teams         Whether to include sub team info (optional:
                            defaults to False)
        '''
        data = {}
        if user_reference:
            data['user__reference'] = user_reference
        if team_reference:
            data['team__reference'] = team_reference
        data['include_sub_teams'] = sub_teams
        url = 'userroles'
        result = self.get(url, data)
        return result['userroles']

    '''job api'''

    def get_jobs(self, buyer_team_reference=None,
                 include_sub_teams=False,
                 status=None, created_by=None, created_time_from=None,
                 created_time_to=None, page_offset=0, page_size=20,
                 order_by=None):
        """
        Retrieves all jobs that a user has manage_recruiting accesss to.
        This API call can be used to find the reference ID of a specific jobi

        Parameters
          buyer_team_reference  (optional)
          include_sub_teams     (optional: defaults to False)
          status                (optional)
          created_by            Creator's user_id (optional)
          created_time_from     timestamp (optional)
          created_time_to       timestamp (optional)
          page_offset           Number of entries to skip (optional)
          page_size             Page size in number of entries
                                (optional: default 20)
          order_by              (optional)
        """
        url = 'jobs'

        data = {}
        if buyer_team_reference:
            data['buyer_team__reference'] = buyer_team_reference

        data['include_sub_teams'] = False
        if include_sub_teams:
            data['include_sub_teams'] = include_sub_teams

        if status:
            data['status'] = status

        if created_by:
            data['created_by'] = created_by

        if created_time_from:
            data['created_time_from'] = created_time_from

        if created_time_to:
            data['created_time_to'] = created_time_to

        data['page'] = '%d;%d' % (page_offset, page_size)

        if order_by is not None:
            data['order_by'] = order_by

        result = self.get(url, data)
        return result['jobs']

    def get_job(self, job_reference):
        """
        Retrieve the complete job object for the referenced job.
        This is only available to users with manage_recruiting
        permissions
        within the team that the job is posted in.

        Parameters
          job_reference     Job reference
        """
        url = 'jobs/%s' % str(job_reference)
        result = self.get(url)
        return result['job']

    def post_job(self, job_data):
        """
        Post a job

        Parameters
          job_data      Details of the job
        """
        url = 'jobs'
        job_data_dict = {}
        for k, v in job_data.items():
            job_data_dict['job_data['+k+']']=v
        result = self.post(url, job_data_dict)
        return result

    def update_job(self, job_id, job_data):
        """
        Update a job

        Parameters
          job_id        Job reference
          job_data      New details of the job
        """
        url = 'jobs/%s' % str(job_id)
        return self.put(url, {'job_data': job_data})

    def delete_job(self, job_id, reason_code):
        """
        Delete a job

        Parameters
          job_id        Job reference
          readon_code   The reason code
        """
        url = 'jobs/%s' % str(job_id)
        return self.delete(url, {'reason_code': reason_code})

    '''offer api'''

    def get_offers(self, buyer_team_reference=None, status=None,
                   job_ref=None, include_sub_teams=None,
                   provider_ref=None, agency_ref=None,
                   created_time_from=None, created_time_to=None,
                   page_offset=0, page_size=20, order_by=None):
        """
        Retrieve a list of all the offers on a specific job or within
                a specific team

        Parameters
          buyer_team_reference  The team reference (optional)
          status                active/filled (optional: defaults to active)
          job_ref               The job reference (optional)
          include_sub_teams     Include sub teams (optional)
          provider_ref          (optional)
          agency_ref            (optional)
          created_time_from     timestamp e.g.'2008-09-09 00:00:01' (optional)
          created_time_to       timestamp e.g.'2008-09-09 00:00:01' (optional)
          page_offset           Number of entries to skip (optional)
          page_size             Page size in number of entries
                                (optional: default 20)
          order_by              (optional)
        """
        url = 'offers'
        data = {}
        if buyer_team_reference:
            data['buyer_team__reference'] = buyer_team_reference

        if status:
            data['status'] = status

        if job_ref:
            data['job__reference'] = job_ref

        if include_sub_teams:
            data['include_sub_teams'] = include_sub_teams

        if provider_ref:
            data['provider__reference'] = provider_ref

        if agency_ref:
            data['agency_team__reference'] = agency_ref

        if created_time_from:
            data['created_time_from'] = created_time_from

        if created_time_to:
            data['created_time_to'] = created_time_to

        data['page'] = '%d;%d' % (page_offset, page_size)

        if order_by is not None:
            data['order_by'] = order_by

        result = self.get(url, data)
        return result['offers']

    def get_offer(self, offer_reference):
        """
        Retrieve the referenced offer

        Parameters
          offer_reference   Offer reference
        """
        url = 'offers/%s' % str(offer_reference)
        result = self.get(url)
        return result['offer']

    '''engagement api'''

    def get_engagements(self, buyer_team_reference=None,
                        include_sub_teams=False,
                        status=None, provider_ref=None, agency_ref=None,
                        created_time_from=None, created_time_to=None,
                        page_offset=0, page_size=20, order_by=None):
        """
        Retrieve engagements

        Parameters
          buyer_team_reference  The team reference (optional)
          include_sub_teams     (optional: default False)
          status                active/filled (optional: defaults to active)
          provider_ref          (optional)
          agency_ref            (optional)
          created_time_from     timestamp e.g.'2008-09-09 00:00:01' (optional)
          created_time_to       timestamp e.g.'2008-09-09 00:00:01' (optional)
          page_offset           Number of entries to skip (optional)
          page_size             Page size in number of entries
                                (optional: default 20)
          order_by              (optional)
        """
        url = 'engagements'

        data = {}
        if buyer_team_reference:
            data['buyer_team__reference'] = buyer_team_reference

        data['include_sub_teams'] = False
        if include_sub_teams:
            data['include_sub_teams'] = include_sub_teams

        if status:
            data['status'] = status

        if provider_ref:
            data['provider_ref'] = provider_ref

        if agency_ref:
            data['agency_ref'] = agency_ref

        if created_time_from:
            data['created_time_from'] = created_time_from

        if created_time_to:
            data['created_time_to'] = created_time_to

        data['page'] = '%d;%d' % (page_offset, page_size)

        if order_by is not None:
            data['order_by'] = order_by

        result = self.get(url, data)
        return result['engagements']

    def get_engagement(self, engagement_reference):
        """
        Retrieve referenced engagement

        Parameters
          engagement_reference
        """
        url = 'engagements/%s' % str(engagement_reference)
        result = self.get(url)
        return result['engagement']

    '''candidacy api'''

    def get_candidacy_stats(self):
        """
        Retrieve candidacy stats
        """
        url = 'candidacies/stats'
        result = self.get(url)
        return result['candidacy_stats']
