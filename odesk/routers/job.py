"""
Python bindings to odesk API
python-odesk version 0.5
(C) 2010-2012 oDesk
"""
from odesk.namespaces import Namespace


class Job(Namespace):
    api_url = 'profiles/'
    version = 1

    def get_job_profile(self, job_key):
        """Returns detailed profile information about job(s).
        Docmented at 'http://developers.odesk.com/w/page/49065901/Job Profile'

        Parameters
        job_key     The job key or a list of keys, separated by ";",
                    number of keys per request is limited by 20.
                    You can access profile by job recno, in that case
                    you can't specify a list of jobs, only one profile
                    per request is available.

        """
        max_keys = 20
        url = 'jobs/%s'
        # Check job key(s)
        if not job_key.__class__ in [str, int, list, tuple]:
            raise ValueError(
                'Invalid job key. Job recno, key or list of keys expected, ' +
                '%s given' % job_key.__class__)
        elif job_key.__class__ in [list, tuple]:
            if len(job_key) > max_keys:
                raise ValueError('Number of keys per request is limited by %s'
                    % max_keys)
            elif filter(lambda x: not str(x).startswith('~~'), job_key):
                raise ValueError(
                    'List should contain only job keys not recno.')
            else:
                url %= ';'.join(job_key)
        else:
            url %= job_key
        result = self.get(url)
        return result.get('profiles', result)['profile']
