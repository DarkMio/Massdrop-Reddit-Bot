# Reddit Rover

Reddit Rover is a plugin-based framework to host multiple Reddit bots at once.

- ```Massdrop.py``` skips the login wall of Massdrop.
- ```JiffierBot.py``` fixes gfycat links to save bandwidth.
- ```SmallSubBot.py``` links small subreddits named in the title - aiding mobile users.
- ```LeafeatorBot.py``` is a simple shitposting bot.

Please don't run those plugins not on your own. They're most likely removed with the next release and uploaded on a
different repository to avoid multiple hoster running the same bots.

## Installation & Usage
Running on Python 3+:

    pip install praw --upgrade
    pip install praw-oauth2util
    
All other dependencies are standard builtins. To be able to run this framework,
you will need to run ```praw-multiprocess``` to avoid higher API usage than from Reddits guidelines.

## Debugging
Bot features are written in Abstract Base Classes. Inherit from it and execute one of the test functions:
```test_single_submission(submission_id)```, ```test_single_comment(comment_id)``` or ```__test_single_thing(thing_id)```.
Other than that, use atomic tests of your features however you please. Instantiating a plugin on its own works and 
supposed to test your features. Read into the documentation to get a detailed guide how this bot works and what you bot has to do.

## Version & Changelog
This bot is now again under development. Way less complex code, more segmentation and more single responsibility principle.

```
v0.6: Recode of the bot. A trillion of new features, which I will document soon™
--------------------------------------------------------------------------------------------------------------
v0.5: Added more bots - and then it kept fucking up.
v0.4: Should now load infinite amounts of links, represent them with the website title and respond accordingly.
v0.3: Fixing behaviour with non-escaped chars in links and stopping the self-spam.
v0.2: Methods to query with referrer-link and stuff like that
v0.1: Initial Commit
```

## Planned features & work in progress
- Debugger-Features and startup commands.
- Rewriting some chunks of the Massdrop-Plugin, it's nesting and separation of concerns is horrible currently.

##### Planned Massdrop Features
- Unit Order Limit

## Help, questions, contribution
Check out the [FAQ](https://github.com/DarkMio/Massdrop-Reddit-Bot/wiki/FAQ), which should cover most issues at first. Feel free to mail me, even here on GitHub.

Thanks for your interest and have a good time.
