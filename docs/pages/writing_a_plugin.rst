Writing a plugin
================

This tutorial will cover the bare basics to get a plugin properly imported and running. We're going to write a simple
plugin, that will us inform if someone talked about reddit.

This is a tutorial to show you the basic structure a plugin needs to be properly imported and receiving data. There
are file-templates withing ``misc/Pycharm File Templates`` that help you develop way faster if you're a pycharm user.
A future update will remove the existing plugins and give you two examples.

The basic structure
-------------------

RedditRovers plugins have three very important (and a fourth optional) sections:

1. The import of the base class.
2. An object that inherits from the base class and implements abstract methods.
3. A function that instantiates the object and returns it.
4. *(An external instantiating to test a plugin on your own.)

1. Importing the base class
---------------------------
RedditRover checks always if your plugin is inherited from the baseclass. It gives you a set of features and makes
maintaining code really simple. First you import the base class:

.. code-block:: python

    from core.BaseClass import Base

2. Object from Base
-------------------
Now comes the real part: Every plugin needs to inherit from the base class and has to implement a specific set of
methods to function properly. This would look like this:

.. code-block:: python

    class MyPlugin(Base):

        def __init__(self, database):
            super().__init__(database, 'MyBotName')

        def execute_comment(self, comment):
            if 'reddit' in comment.body.lower():
                self.logger.info('{} said reddit here: {}'.format(comment.author.name, comment.permalink))

        def execute_link(self, link_submission):
            pass

        def execute_titlepost(self, title_only):
            pass

        def execute_submission(self, submission):
            if 'reddit' in submission.selftext.lower():
                self.logger.info('{} said reddit here: {}'.format(submission.author.name, submission.permalink))

        def update_procedure(self, thing_id, created, lifetime, last_updated, interval):
            pass

        def on_new_message(self, message):
            pass

3. Function for instantiating the plugin
----------------------------------------
Next is an init-call to initialize the plugin, setup whatever you need to and return the object that inherits from
``BaseClass/Base``. This is a design decision to make it easy, run init-tasks and give a fixed return object back.
Also you can define if you need access to the database storage for example.

All you need to do is following:

.. code-block:: python

    def init(database):
        return MyPlugin(database)

4. Test Block (optional)
------------------------
And at last there is the optional test block. ``BaseClass/Base`` features two functions to load a single submission or
comment by id to test your bot against real world data and test cases. You can now execute the plugin itself.

.. code-block:: python

    if __name__ == '__main__':
        my_plugin = MyPlugin(None)  # Remember: We don't always need the database.
        my_plugin.test_single_submission('3iyxxt')  # See: https://redd.it/29f2ah
        my_plugin.test_single_comment('cukvign')  # See:

About PRAW objects
------------------
I cannot teach you how to program or how to use PRAW objects to its fullest, but I can give you a good hint. In general
it's a good advice lookup all steps in the python console or in iPython. A close look at `PRAWs objects
<http://praw.readthedocs.org/en/stable/pages/code_overview.html#module-praw.objects>`_ is helpful too.

.. code-block:: pycon

    >>> from praw import Reddit
    >>> r = Reddit(user_agent='Some user agent for you.')
    >>> comment = r.get_info(thing_id='t1_cukvign')
    >>> submission = r.get_info(thing_id='t3_3iyxxt')
    >>> dir(comment)
    >>> dir(submission)
    >>> comment.author
    >>> submission.author


The entire code:
----------------
In case you struggle with assembling the code, here is it as full set:

.. code-block:: python

    from core.BaseClass import Base


    class MyPlugin(Base):

        def __init__(self, database):
            super().__init__(database, 'MyBotName')

        def execute_comment(self, comment):
            if 'reddit' in comment.body.lower():
                self.logger.info('{} said reddit here: {}'.format(comment.author.name, comment.permalink))

        def execute_link(self, link_submission):
            pass

        def execute_titlepost(self, title_only):
            pass

        def execute_submission(self, submission):
            if 'reddit' in submission.selftext.lower():
                self.logger.info('{} said reddit here: {}'.format(submission.author.name, submission.permalink))

        def update_procedure(self, thing_id, created, lifetime, last_updated, interval):
            pass

        def on_new_message(self, message):
            pass


    def init(database):
        return MyPlugin(database)


    if __name__ == '__main__':
        my_plugin = MyPlugin(None)  # Remember: We don't always need the database.
        my_plugin.test_single_submission('3iyxxt')  # See: https://redd.it/29f2ah
        my_plugin.test_single_comment('cukvign')  # See:
