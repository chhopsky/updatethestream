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
6. Create the environment: `pipenv install --dev --python "C:\Users\<your user>\AppData\Local\Programs\Python\Python38\python.exe"` (your python location)
7. Run the app: `pipenv run udts.py`

## Finding your python location for step 6

Finding your python location is easy.  
1. Open your Windows Start Menu, then search for "Python".
2. Right-click the Python app and click "Open File Location".
3. Right-click Python 3.8 and click "Open File Location" again, from within the explorer.
4. Click the folder at the top left of the URL bar, and you should see the path like so:

![image](https://user-images.githubusercontent.com/24707802/149632381-3b27a0d6-856e-46b4-931f-15f3d3e94984.png)

![image](https://user-images.githubusercontent.com/24707802/149632261-e699a3a7-bf4f-4516-9485-1f45043641c3.png)

5. Copy and paste that path, adding "\python.exe" at the end of it, and you have your entire python location!
