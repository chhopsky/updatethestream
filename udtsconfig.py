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
    "REARRANGE_MIXED_FINISH_STATE" : {
        "title": "Can't swap mixed match states!",
        "message": "Cannot swap a match that's finished with one that's not, or one that's in progress with one that's not started. Consider undoing your results first."
    },
    "CLIENT_OUT_OF_DATE" : {
        "title": "New Update Available!",
        "message": "Get new features, bugfixes, and more in our latest update, available at https://github.com/chhopsky/updatethestream/releases"
    }
}
