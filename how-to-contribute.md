### Project Setup

Setup instructions are for Windows. If you're running Linux you can
probably figure out how to do this without my help.

1. Install [VSCode](https://code.visualstudio.com/download) or the IDE of your choice
2. Install [Git](https://gitforwindows.org/), and git bash. Defaults should be fine.
3. Install [Python 3.8](https://www.python.org/ftp/python/3.8.8/python-3.8.8-amd64.exe). On the main install screen, check the box that says you want to add it to the path.
4. Run Git Bash by hitting start and typing git bash.
5. You probably want to set up in c:\github\ so: `cd c:` then `mkdir github` then `cd github`
6. Clone the repository into a folder: `git clone https://github.com/chhopsky/updatethestream.git`
7. Install pipenv: `pip install pipenv` (this lets you isolate your development environment from the rest of your pc)
8. Create a lock file: `pipenv lock` (this tells the environment installer what packages you need)
9. Sync the environment: `pipenv sync` (this installs everything from the lock file)
10. Activate the pipenv development environment: `pipenv shell` (this activates your development environment)
11. Open VSCode and open a folder. Navigate to `c:\github\updatethestream` or wherever you put the updatethestream folder containing the project.
12. In the bottom left corner, there's a small box that says 'main'. Click it and a popup will appear at the top in the middle. This is letting you select which branch of the repository you're on. `main` is the current public release, you want `development.
13. Hit the button with the circled arrows in the bottom left to refresh
14. Optional: Log into [challonge.com], go to the [developer console](https://challonge.com/settings/developer), and generate an API key. Save it in creds/challonge-api-key
15. Go to the console and type `python udts.py`. This runs the program.
16. Alternately, go to the Run menu and hit Start Debugging. This will let you set breakpoints and inspect state when a crash happens.

## Setup without VSCode

A bit more in-depth, but avoids installing VSCode if you don't want to.  You can still collect Traceback output by running it from the command prompt.

1. Install [Git](https://gitforwindows.org/)
2. Install [Python 3.8](https://www.python.org/ftp/python/3.8.8/python-3.8.8-amd64.exe)
3. Clone the repository into a folder: `git clone https://github.com/chhopsky/updatethestream.git`
4. Install `pipenv`: `pip install pipenv`
5. Create the environment: `pipenv install`
6. Activate the development environment: `pipenv shell`
7. Run the program: `python udts.py`
