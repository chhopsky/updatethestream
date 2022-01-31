### Project Setup

Setup instructions are for Windows. If you're running Linux you can
probably figure out how to do this without my help.

1. Install [VSCode](https://code.visualstudio.com/download) or the IDE of your choice
2. Install [Git](https://gitforwindows.org/)
3. Install [Python 3.8](https://www.python.org/ftp/python/3.8.8/python-3.8.8-amd64.exe)
4. Clone the repository into a folder: `git clone https://github.com/chhopsky/updatethestream.git`
5. Install `pipenv`: `pip install pipenv`
6. Create a lock file: `pipenv lock`
7. Sync the environment: `pipenv sync`
8. Activate the pipenv development environment: `pipenv shell`
9. Open VSCode and open the updatethestream folder containing the project.
10. Optional: Log into [challonge.com], go to the [developer console](https://challonge.com/settings/developer), and generate an API key. Save it in creds/challonge-api-key
11. Go to the console and type `python udts.py`. This runs the program.
12. Alternately, go to the Run menu and hit Start Debugging. This will let you set breakpoints and inspect state when a crash happens.

## Setup without VSCode

A bit more in-depth, but avoids installing VSCode if you don't want to.  You can still collect Traceback output by running it from the command prompt.

1. Install [Git](https://gitforwindows.org/)
2. Install [Python 3.8](https://www.python.org/ftp/python/3.8.8/python-3.8.8-amd64.exe)
3. Clone the repository into a folder: `git clone https://github.com/chhopsky/updatethestream.git`
4. Install `pipenv`: `pip install pipenv`
5. Create a lock file: `pipenv lock`
6. Create the environment: `pipenv install --python 3.8`
7. Activate the development environment: `pipenv shell`
8. Run the program: `python udts.py`
