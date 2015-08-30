.. _main_page:

Reddit Rover
============

.. begin_description


RedditRover is a bot modular bot framework that makes it easy to host all kinds of reddit bots at once.
It is intended to make it easy for new and experienced Programmers to host a variety of bots that can react to Reddits
content without having to mangle with all ins and outs of reddit, praw and API limitations. Running it is easy:

.. code-block:: bash

    $ praw-multiprocess

.. code-block:: bash

    $ RedditRover/main.py

That will already do start the entire hosting and loading process - given you have already written a plugin,
it will start shortly after to fire content to your plugin.

.. end_description

.. begin_installation

Installation & Usage
--------------------

Running on Python 3+:

.. code-block:: python

    pip install praw --upgrade
    pip install praw-oauth2util

All other dependencies are standard builtins. To be able to run this framework,
you will need to run ``praw-multiprocess`` to avoid higher API usage than from Reddits guidelines.

.. end_installation

Debugging
---------
Bot features are written in Abstract Base Classes. Inherit from it and execute one of the test functions:
``test_single_submission(submission_id)``, ``test_single_comment(comment_id)`` or ``__test_single_thing(thing_id)``.
Other than that, use atomic tests of your features however you please. Instantiating a plugin on its own works and
supposed to test your features. Read into the documentation to get a detailed guide how this bot works and what you bot has to do.

Version & Changelog
-------------------
This bot is now again under development. Way less complex code, more segmentation and more single responsibility principle.

``
v0.6: Recode of the bot. A trillion of new features, which I will document soon™
--------------------------------------------------------------------------------------------------------------
v0.5: Added more bots - and then it kept fucking up.
v0.4: Should now load infinite amounts of links, represent them with the website title and respond accordingly.
v0.3: Fixing behaviour with non-escaped chars in links and stopping the self-spam.
v0.2: Methods to query with referrer-link and stuff like that
v0.1: Initial Commit
``

.. begin_future

Planned features & work in progress
-----------------------------------
- Debugger-Features and startup commands.
- Rewriting some chunks of the Massdrop-Plugin, it's nesting and separation of concerns is horrible currently.

Planned Massdrop Features
+++++++++++++++++++++++++
- Unit Order Limit

.. end_future

.. begin_faq

Help, questions, contribution
-----------------------------
Check out the [FAQ](https://github.com/DarkMio/Massdrop-Reddit-Bot/wiki/FAQ), which should cover most issues at first. Feel free to mail me, even here on GitHub.

.. end_faq

Thanks for your interest and have a good time.
