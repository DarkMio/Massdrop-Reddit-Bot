# Massdrop Reddit Bot
In case you're interested in writing reddit bots and like to see how different bots operate, you can view and preview this bot here. Please respect my work and don't run it extensively on your own.

```Massdrop.py``` is a sample feature which you should not use. I will break it soon on purpose, so it won't run at all for you. However, it shows the capabilities.


## Progress

![Feature Complete](http://progressed.io/bar/100?title=Feature%20Complete)
![Database Provider](http://progressed.io/bar/100?title=Database%20Provider)
![Framework](http://progressed.io/bar/100?title=Framework)
![Threading](http://progressed.io/bar/100?title=Threading)
![Modules](http://progressed.io/bar/100?title=Modules)

## Installation & Usage
Running on Python 3:

    pip install praw --upgrade
    pip install praw-oauth2util
    
All other dependencies are standard builtins.

## Debugging
Bot features are written in Abstract Base Classes. Inherit them properly and then test them extensively with strings.

## Version & Changelog
This bot is now again under development. Way less complex code, more segmentation and more single responsibility principle.

```
v0.6: Recode of the bot. A trillion of new features, which I will document soon™
--------------------------------------------------------------------------------------------------------------
v0.5: Added more bots - and then it kept fucking up.
v0.4: Should now load inifite amounts of links, represent them with the website title and respond accordingly.
v0.3: Fixing behaviour with non-escaped chars in links and stopping the self-spam.
v0.2: Methods to query with referer-link and stuff like that
v0.1: Initial Commit
```

## Planned features & work in progress
- Debugger-Features and startup commands.
- Rewriting some chunks of the Massdrop-Plugin, it's nesting and seperation of concerns is horrible currently.

##### Planned Massdrop Features
- Unit Order Limit

## Help, questions, contribution
Feel free to mail me, even here on GitHub.

Thanks for your interest and have a good time.
