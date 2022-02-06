ERRORS = {
    "UNKNOWN": {
        "title": "Unexpected error!", 
        "message": "UDTS encountered an error, and could not determine why."
        },
    "BAD_UNKNOWN": {
        "title": "Unexpected error!", 
        "message": "UDTS encountered an error. Additionally, the error code it tried to display is not valid."
        },
    "CHALLONGE_LOAD_FAIL": {
        "title": "Challonge load error!", 
        "message": "The challonge tournament could not be loaded. Please check your code."},
    "CHALLONGE_PARSE_FAIL": {
        "title": "Challonge parse error!", 
        "message": "The challonge tournament loaded, but UDTS couldn't parse it. Check the tournament page is working properly, or report this error. UDTS may need to update its challonge module."},
    "SAVE_FILE_ERROR": {
        "title": "Could not load from file!", 
        "message": "The file you selected could not be loaded. It might be the wrong file, or have been saved in an old version of UDTS."},
    "SAVE_FILE_MISSING": {
        "title": "Could not load from file!", 
        "message": "The default tournament configuration file could not be found. Loading empty tournament."},
    "CHALLONGE_WARNING" : {
        "title": "Please read!",
        "message": "Challonge does NOT inform us as to how many games are in a match. Please double check your imported matches, and be sure to adjust the best-ofs appropriately."
    },
    "FACEIT_LOAD_FAIL" : {
        "title": "FACEIT load error!",
        "message": "Something went wrong trying to load data from FACEIT. Please try again later, or send us a copy of your log file if the error persists."
    },
    "REARRANGE_MIXED_FINISH_STATE" : {
        "title": "Can't swap mixed match states!",
        "message": "Cannot swap a match that's finished with one that's not, or one that's in progress with one that's not started. Consider undoing your results first."
    },
    "CLIENT_OUT_OF_DATE" : {
        "title": "New Update Available!",
        "message": "Get new features, bugfixes, and more in our latest update, available at https://github.com/chhopsky/updatethestream/releases"
    },
    "CANT_USE_TBD_HERE" : {
        "title": "TBD team not allowed.",
        "message": "Can't set a match that's already happened or is in progress to contain a TBD team."
    },
    "SAME_TEAM_BOTH_SIDES" : {
        "title": "Team vs itself?",
        "message": "A team can't play against itself."
    },
    "BACKEND_ERROR": {
        "title": "Backend error.",
        "message": "The tournament engine experienced an error processing your request. Please check the log file for details, and consider reloading the program."
    }
}

BLANK_IMAGE_B64 = "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAACXBIWXMAAAsTAAALEwEAmpwYAAADHUlEQVR4nO3UMQEAIAzAMMC/5yFjRxMFvXpn5gBNbzsA2GMAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEGYAEPYB58oE/VhFU1IAAAAASUVORK5CYII="