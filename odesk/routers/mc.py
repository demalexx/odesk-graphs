"""
Python bindings to odesk API
python-odesk version 0.5
(C) 2010-2011 oDesk
"""

import urllib

from odesk.namespaces import Namespace


class MC(Namespace):
    api_url = 'mc/'
    version = 1

    def get_trays(self, username=None, paging_offset=0, paging_count=20):
        """
        Retrieve a list of all active trays and a message count for each

        Parameters
          username          User name
        """
        url = 'trays'
        if paging_offset or not paging_count == 20:
            data = {'paging': '%s;%s' % (str(paging_offset),
                                         str(paging_count))}
        else:
            data = {}

        if username:
            url += '/%s' % str(username)
        result = self.get(url, data=data)
        return result["trays"]

    def get_tray_content(self, username, tray, paging_offset=0,
                         paging_count=20):
        """
        Retrieve tray contents

        Parameters
          username          User name
          tray              Tray
          paging_offset     Start of page (number of results to skip)
          paging_count      Page size (number of results)
        """
        url = 'trays/%s/%s' % (str(username), str(tray))
        if paging_offset or not paging_count == 20:
            data = {'paging': '%s;%s' % (str(paging_offset),
                                         str(paging_count))}
        else:
            data = {}

        result = self.get(url, data=data)
        return result["current_tray"]["threads"]

    def get_thread_content(self, username, thread_id, paging_offset=0,
                           paging_count=20):
        """
        List details of a specific thread

        Parameters
          username          User name
          thread_id         Thread ID
          paging_offset     Start of page (number of results to skip)
          paging_count      Page size (number of results)
        """
        url = 'threads/%s/%s' % (str(username), (thread_id))
        if paging_offset or not paging_count == 20:
            data = {'paging': '%s;%s' % (str(paging_offset),
                                         str(paging_count))}
        else:
            data = {}

        result = self.get(url, data=data)
        return result["thread"]

    def _generate_many_threads_url(self, url, threads_ids):
        return ';'.join(urllib.quote(str(i)) for i in threads_ids)

    def put_threads_read_unread(self, username, thread_ids, read=True):
        """
        Marks threads as read/unread

        Parameters
          username          User name
          thread_ids        must be a list, even of 1 item
          read              True/False (optional: default True)
        """
        if isinstance(thread_ids, (list, tuple)):
            thread_ids = ';'.join(map(str, thread_ids))
        url = 'threads/%s/%s' % (username, thread_ids)

        if read:
            data = {'read': 'true'}
        else:
            data = {'read': 'false'}

        return self.put(url, data=data)

    def put_threads_read(self, username, thread_ids):
        """
        Marks threads as read

        Parameters
          username          User name
          thread_ids        must be a list, even of 1 item
        """
        return self.put_threads_read_unread(username, thread_ids, read=True)

    def put_threads_unread(self, username, thread_ids):
        """
        Marks threads as unread

        Parameters
          username          User name
          thread_ids        must be a list, even of 1 item
        """
        return self.put_threads_read_unread(username, thread_ids, read=False)

    def put_threads_starred_or_unstarred(self, username, thread_ids,
                                         starred=True):
        """
        Marks threads as starred/not starred

        Parameters
          username          User name
          thread_ids        must be a list, even of 1 item
          starred           True/False (optional: default True)
        """
        if isinstance(thread_ids, (list, tuple)):
            thread_ids = ';'.join(map(str, thread_ids))
        url = 'threads/%s/%s' % (username, thread_ids)

        if starred:
            data = {'starred': 'true'}
        else:
            data = {'starred': 'false'}

        return self.put(url, data=data)

    def put_threads_starred(self, username, thread_ids):
        """
        Marks threads as starred

        Parameters
          username          User name
          thread_ids        must be a list, even of 1 item
        """
        return self.put_threads_starred_or_unstarred(username,
                                            thread_ids, starred=True)

    def put_threads_unstarred(self, username, thread_ids):
        """
        Marks threads as unstarred

        Parameters
          username          User name
          thread_ids        must be a list, even of 1 item
        """
        return self.put_threads_starred_or_unstarred(username,
                                            thread_ids, starred=False)

    def put_threads_deleted_or_undeleted(self, username, thread_ids,
                                         deleted=True):
        """
        Marks threads as deleted/not deleted

        Parameters
          username          User name
          thread_ids        must be a list, even of 1 item
          deleted           True/False (optional: default True)
        """
        if isinstance(thread_ids, (list, tuple)):
            thread_ids = ';'.join(map(str, thread_ids))
        url = 'threads/%s/%s' % (username, thread_ids)

        if deleted:
            data = {'deleted': 'true'}
        else:
            data = {'deleted': 'false'}

        return self.put(url, data=data)

    def put_threads_deleted(self, username, thread_ids):
        """
        Marks threads as deleted

        Parameters
          username          User name
          thread_ids        must be a list, even of 1 item
        """
        return self.put_threads_deleted_or_undeleted(username, thread_ids,
                                                     deleted=True)

    def put_threads_undeleted(self, username, thread_ids):
        """
        Marks threads as not deleted

        Parameters
          username          User name
          thread_ids        must be a list, even of 1 item
        """
        return self.put_threads_deleted_or_undeleted(username, thread_ids,
                                                     deleted=False)

    def post_message(self, username, recipients, subject, body,
                     thread_id=None):
        """
        Send a new message (creating a new thread) or reply to an existing
        thread

        Parameters
          username      User name (of sender)
          recipients    Recipient(s)  (a single string or a list/tuple)
          subject       Message subject
          body          Message text
          thread_id     The thread id if replying to an existing thread
                        (optional)
        """
        url = 'threads/%s' % str(username)
        if not isinstance(recipients, (list, tuple)):
            recipients = [recipients]
        recipients = ','.join(map(str, recipients))
        if thread_id:
            url += '/%s' % str(thread_id)
        return self.post(url, data={'recipients': recipients,
                                      'subject': subject,
                                      'body': body})
