from distutils.core import setup

setup(
    name='MassdropBot',
    version='0.6',
    packages=['core', 'config', 'plugins', 'misc'],
    url='https://github.com/DarkMio/Massdrop-Reddit-Bot',
    license='MIT',
    author='Martin Zier',
    author_email='miostarkid@gmail.com',
    description='MassdropBot is a framework to host multiple bots that trigger on comments or submissions on reddit.',
    install_requires=['praw', 'praw-OAuth2Util']
)
