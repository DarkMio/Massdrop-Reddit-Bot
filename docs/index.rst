RedditRover - the Reddit Multibot Framework
===========================================

RedditRover is a bot modular bot framework that makes it easy to host all kinds of reddit bots at once.
It is intended to make it easy for new and experienced Programmers to host a variety of bots that can react to Reddits
content without having to mangle with all ins and outs of reddit, praw and API limitations. Running it is easy:

.. code-block:: bash

    $ praw-multiprocess

.. code-block:: bash

    $ RedditRover/main.py

That will already do start the entire hosting and loading process - given you have already written a plugin,
it will start shortly after to fire content to your plugin.

Contents:

.. toctree::
   :maxdepth: 2


This is something I want to say that is not in the docstring.

.. automodule:: core/RedditRover.py

.. autoclass:: RedditRover
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

