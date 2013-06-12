"""
Python bindings to odesk API
python-odesk version 0.5
(C) 2010-2011 oDesk
"""
import urllib


from odesk.namespaces import Namespace


class Task(Namespace):
    api_url = 'otask/'
    version = 1

    def get_company_tasks(self, company_id):
        """
        Retrieve a list of all tasks assigned within a company
        The user authenticated must have been granted the appropriate
        hiring manager permissions

        Parameters
          company_id    Company ID
        """
        url = 'tasks/companies/%s/tasks' % str(company_id)
        result = self.get(url)
        return result["tasks"] or []

    def get_team_tasks(self, company_id, team_id):
        """
        Retrieve a list of all tasks assigned to a team
        The user authenticated must have been granted the appropriate
        hiring manager permissions

        Parameters
          company_id    Company ID
          team_id       Team ID
        """
        url = 'tasks/companies/%s/teams/%s/tasks' % (str(company_id),
                                                     str(team_id))
        result = self.get(url)
        return result["tasks"] or []

    def get_user_tasks(self, company_id, team_id, user_id):
        """
        Retrieve a list of all tasks assigned to a team member
        The user authenticated must have been granted the appropriate
        hiring manager permissions

        Parameters
          company_id    Company ID
          team_id       Team ID
          user_id       User ID
        """
        url = 'tasks/companies/%s/teams/%s/users/%s/tasks' % (str(company_id),
                                                    str(team_id), str(user_id))
        result = self.get(url)
        return result["tasks"] or []

    def get_company_tasks_full(self, company_id):
        """
        Retrieve full list of all tasks assigned within a company (with detail
        of level at which the task is assigned)
        The user authenticated must have been granted the appropriate
        hiring manager permissions

        Parameters
          company_id    Company ID
        """
        url = 'tasks/companies/%s/tasks/full_list' % str(company_id)
        result = self.get(url)
        return result["tasks"] or []

    def get_team_tasks_full(self, company_id, team_id):
        """
        Retrieve a list of all tasks assigned to a team (with detail of level
        at which the task is assigned)
        The user authenticated must have been granted the appropriate
        hiring manager permissions

        Parameters
          company_id    Company ID
          team_id       Team ID
        """
        url = 'tasks/companies/%s/teams/%s/tasks/full_list' %\
                                             (str(company_id), str(team_id))
        result = self.get(url)
        return result["tasks"] or []

    def get_user_tasks_full(self, company_id, team_id, user_id):
        """
        Retrieve a list of all tasks assigned to a team member (with detail of
        level at which the task is assigned)
        The user authenticated must have been granted the appropriate
        hiring manager permissions

        Parameters
          company_id    Company ID
          team_id       Team ID
          user_id       User ID
        """
        url = 'tasks/companies/%s/teams/%s/users/%s/tasks/full_list' %\
                                (str(company_id), str(team_id), str(user_id))
        result = self.get(url)
        return result["tasks"] or []

    def _generate_many_tasks_url(self, task_codes):
        return ';'.join(urllib.quote(str(c)) for c in task_codes)

    def get_company_specific_tasks(self, company_id, task_codes):
        """
        Return a specific task record within a company

        Parameters
          company_id    Company ID
          task_codes    Task codes (must be a list, even of 1 item)
        """
        if isinstance(task_codes, (list, tuple)):
            task_codes = ';'.join(map(str, task_codes))
        url = 'tasks/companies/%s/tasks/%s' % (company_id, task_codes)
        result = self.get(url)
        return result["tasks"]

    def get_team_specific_tasks(self, company_id, team_id, task_codes):
        """
        Return a specific task record within a team

        Parameters
          company_id    Company ID
          team_id       Team ID
          task_codes    Task codes (must be a list, even of 1 item)
        """
        if isinstance(task_codes, (list, tuple)):
            task_codes = ';'.join(map(str, task_codes))
        url = 'tasks/companies/%s/teams/%s/tasks/%s' %\
                                (company_id, team_id, task_codes)
        result = self.get(url)
        return result["tasks"] or []

    def get_user_specific_tasks(self, company_id, team_id, user_id,
                                task_codes):
        """
        Return a specific task record for a team member

        Parameters
          company_id    Company ID
          team_id       Team ID
          user_id       User ID
          task_codes    Task codes (must be a list, even of 1 item)
        """
        if isinstance(task_codes, (list, tuple)):
            task_codes = ';'.join(map(str, task_codes))
        url = 'tasks/companies/%s/teams/%s/users/%s/tasks/%s' %\
                                (company_id, team_id, user_id, task_codes)
        result = self.get(url)
        return result["tasks"] or []

    def post_company_task(self, company_id, code, description, url):
        """
        Create a company task
        The authenticated user needs to have hiring manager privileges

        Parameters
          company_id    Company ID
          code          Task code
          description   Task description
          url           Task URL
        """
        url = 'tasks/companies/%s/tasks' % str(company_id)
        data = {'code': code,
                'description': description,
                'url': url}
        result = self.post(url, data)
        return result

    def post_team_task(self, company_id, team_id, code, description, url):
        """
        Create a team task
        The authenticated user needs to have hiring manager privileges

        Parameters
          company_id    Company ID
          team_id       Team ID
          code          Task code
          description   Task description
          url           Task URL
        """
        post_url = 'tasks/companies/%s/teams/%s/tasks' % (
            str(company_id), str(team_id))
        data = {'code': code,
                'description': description,
                'url': url}
        result = self.post(post_url, data)
        return result

    def post_user_task(self, company_id, team_id, user_id, code, description,
                       url):
        """
        Create a task assigned to self

        Parameters
          company_id    Company ID
          team_id       Team ID
          user_id       User ID
          code          Task code
          description   Task description
          url           Task URL
        """
        post_url = 'tasks/companies/%s/teams/%s/users/%s/tasks' % (
            str(company_id), str(team_id), str(user_id))
        data = {'code': code,
                'description': description,
                'url': url}
        result = self.post(post_url, data)
        return result

    def put_company_task(self, company_id, code, description, url):
        """
        Update a company task
        The authenticated user needs to have hiring manager privileges

        Parameters
          company_id    Company ID
          code          Task code
          description   Task description
          url           Task URL
        """
        put_url = 'tasks/companies/%s/tasks/%s' % (str(company_id), str(code))
        data = {'code': code,
                'description': description,
                'url': url}
        result = self.put(put_url, data)
        return result

    def put_team_task(self, company_id, team_id, code, description, url):
        """
        Update a team task
        The authenticated user needs to have hiring manager privileges

        Parameters
          company_id    Company ID
          team_id       Team ID
          code          Task code
          description   Task description
          url           Task URL
        """
        put_url = 'tasks/companies/%s/teams/%s/tasks/%s' % (
            str(company_id), str(team_id), str(code))
        data = {'code': code,
                'description': description,
                'url': url}
        result = self.put(put_url, data)
        return result

    def put_user_task(self, company_id, team_id, user_id, code,
                      description, url):
        """
        Update a task assigned to self

        Parameters
          company_id    Company ID
          team_id       Team ID
          user_id       User ID
          code          Task code
          description   Task description
          url           Task URL
        """
        put_url = 'tasks/companies/%s/teams/%s/users/%s/tasks/%s' % (
            str(company_id), str(team_id), str(user_id), str(code))
        data = {'code': code,
                'description': description,
                'url': url}
        result = self.put(put_url, data)
        return result

    def delete_company_task(self, company_id, task_codes):
        """
        Delete specific tasks within a company

        Parameters
          company_id    Company ID
          task_codes    Task codes (must be a list, even of 1 item)
        """
        if isinstance(task_codes, (list, tuple)):
            task_codes = ';'.join(map(str, task_codes))
        url = 'tasks/companies/%s/tasks/%s' % (company_id, task_codes)
        return self.delete(url, {})

    def delete_team_task(self, company_id, team_id, task_codes):
        """
        Delete specific tasks within a team

        Parameters
          company_id    Company ID
          team_id       Team ID
          task_codes    Task codes (must be a list, even of 1 item)
        """
        if isinstance(task_codes, (list, tuple)):
            task_codes = ';'.join(map(str, task_codes))
        url = 'tasks/companies/%s/teams/%s/tasks/%s' %\
                                (company_id, team_id, task_codes)
        return self.delete(url, {})

    def delete_user_task(self, company_id, team_id, user_id, task_codes):
        """
        Delete specific tasks assigned to a team member

        Parameters
          company_id    Company ID
          team_id       Team ID
          user_id       User ID
          task_codes    Task codes (must be a list, even of 1 item)
        """
        if isinstance(task_codes, (list, tuple)):
            task_codes = ';'.join(map(str, task_codes))
        url = 'tasks/companies/%s/teams/%s/users/%s/tasks/%s' %\
                                 (company_id, team_id, user_id, task_codes)
        return self.delete(url, {})

    def delete_all_company_tasks(self, company_id):
        """
        Delete all tasks within a company

        Parameters
          company_id    Company ID
          task_codes    Task codes (must be a list, even of 1 item)
        """
        url = 'tasks/companies/%s/tasks/all_tasks' % (str(company_id))
        return self.delete(url, {})

    def delete_all_team_tasks(self, company_id, team_id):
        """
        Delete all tasks within a team

        Parameters
          company_id    Company ID
          team_id       Team ID
          task_codes    Task codes (must be a list, even of 1 item)
        """
        url = 'tasks/companies/%s/teams/%s/tasks/all_tasks' % (str(company_id),
                                                      str(team_id))
        return self.delete(url, {})

    def delete_all_user_tasks(self, company_id, team_id, user_id):
        """
        Delete all tasks assigned to a team member

        Parameters
          company_id    Company ID
          team_id       Team ID
          user_id       User ID
          task_codes    Task codes (must be a list, even of 1 item)
        """
        url = 'tasks/companies/%s/teams/%s/users/%s/tasks/all_tasks' %\
                     (str(company_id), str(team_id), str(user_id))
        return self.delete(url, {})

    def update_batch_tasks(self, company_id, csv_data):
        """
        Batch update tasks using csv file contents.
        This process actually deletes the corresponding tasks and replaces
        them with the newly specified details

        Parameters
          company_id    Company ID
          csv_data      Contents of the csv file
        """
        url = 'tasks/companies/%s/tasks/batch:%s' % (str(company_id), csv_data)
        return self.put(url, {})
