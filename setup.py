from setuptools import setup

setup(
    name='MassdropBot',
    version='0.6',
    packages=['core', 'config', 'plugins', 'misc'],
    url='https://github.com/DarkMio/Massdrop-Reddit-Bot',
    license='MIT',
    author='Martin Zier',
    author_email='miostarkid@gmail.com',
    description='MassdropBot is a framework to host multiple bots that trigger on comments or submissions on reddit.',
    install_requires=['praw>=3.1.0', 'praw-OAuth2Util>=0.2.2'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ]
)
