BaseClass methods
=================

The BaseClass is a vital class for the framework. It ensures a given set of features while staying as flexible as
possible. It also gives an extended feature set which helps with basic tasks necessary with every bot, i. e. logging in
a bot into reddit, providing the standard config or testing against single, manually input threads and comments.

Abstract methods
----------------

Within the Base are a couple of abstract methids, all of which have to be overwritten. The plugin won't be imported if
those core features are not overwritten.

.. py:class:: core.BaseClass.Base(database, bot_name, setup_from_config=True)

.. py:function:: execute_submission(self, submission)

    Class Method which receives a single ``praw.objects.Submission`` object resulting from a self.post on Reddit.

    :param self: Object pointer
    :param submission: A single submission which includes a textbody (self.post)
    :rtype: Bool or NoneType


.. py:function:: execute_link(self, link_submission):

    Class Method which receives a single ``praw.objects.Submission`` object resulting from a link post on Reddit.

    :param self: Object pointer
    :param submission: A single submission which includes an url. (link post)
    :rtype: Bool or NoneType

.. py:function:: execute_titlepost(self, title_only):

    Class Method which receives a single ``praw.objects.Submission`` object, which has neither a text body nor an url.
    It is basically just the title of a submission.

    :param self: Object pointer
    :param submission: A single submission which has neither text nor url.
    :rtype: Bool or NoneType

.. py:function:: execute_comment(self, comment):

    Class Method which receives a single ``praw.objects.Comment`` object from a comment on a thread.

    :param self: Object pointer
    :param submission: A single comment.
    :rtype: Bool or NoneType

.. py:function:: update_procedure(self, thing_id, created, lifetime, last_updated, interval):

    Gets called when you stored a comment or a submission in the update table.

    :param self: Object pointer
    :param thing_id: A single comment.
    :param created: Moment of creation of this entry
    :type created: time.struct_time
    :param lifetime: Moment when entry outlived his update interval
    :type lifetime: time.struct_time
    :param last_updated: Moment when the entry has been updated last
    :type last_updated: time.struct_time
    :param interval: Update interval in seconds
    :type interval: Integer
    :rtype: Bool or NoneType

.. py:function:: on_new_message(self, message):

    Class Method that gets called whenever the bot received a new message.

    :params self: Object pointer
    :param message: A PRAW Message
    :type message: praw.objects.Message


















