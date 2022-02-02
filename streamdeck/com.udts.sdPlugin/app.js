var knownButtons = {}
$SD.on('connected', (jsonObj) => connected(jsonObj));

function connected(jsn) {
    // Subscribe to the willAppear and other events
    $SD.on('com.udts.team1win.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.team2win.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.swapsides.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.forceupdate.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.undo.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.team1win.willDisappear', (jsonObj) => action.onWillDisappear(jsonObj));
    $SD.on('com.udts.team2win.willDisappear', (jsonObj) => action.onWillDisappear(jsonObj));
    $SD.on('com.udts.swapsides.willDisappear', (jsonObj) => action.onWillDisappear(jsonObj));
    $SD.on('com.udts.forceupdate.willDisappear', (jsonObj) => action.onWillDisappear(jsonObj));
    $SD.on('com.udts.undo.willDisappear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.team1win.keyUp', (jsonObj) => action.onKeyUp(jsonObj));
    $SD.on('com.udts.team2win.keyUp', (jsonObj) => action.onKeyUp(jsonObj));
    $SD.on('com.udts.swapsides.keyUp', (jsonObj) => action.onKeyUp(jsonObj));
    $SD.on('com.udts.forceupdate.keyUp', (jsonObj) => action.onKeyUp(jsonObj));
    $SD.on('com.udts.undo.keyUp', (jsonObj) => action.onKeyUp(jsonObj));
};

const action = {
    onWillAppear: function (jsn) {
        knownButtons[jsn.action] = jsn
        if (jsn.action == "com.udts.swapsides") {
            this.setTitle(jsn, "Swap\nRed/Blue");
            this.updateSides(jsn)  // This is here because I want it to only run once. Placing it elsewhere will make it run multiple times, so here is the next best place.
        }
        else if (jsn.action == "com.udts.forceupdate") {
            this.setTitle(jsn, "Force\nUpdate");
        }
        else if (jsn.action == "com.udts.undo") {
            this.setTitle(jsn, "Undo")
        }
    },

    onWillDisappear: function (jsn) {
        delete knownButtons[jsn.action]
    },

    onKeyUp: function (jsn) {
        if (jsn.action == "com.udts.team1win") {
            fetch("http://localhost:8000/win/team1")
            .then(response => response.json())
        }
        else if (jsn.action == "com.udts.team2win") {
            fetch("http://localhost:8000/win/team2")
            .then(response => response.json())
        }
        else if (jsn.action == "com.udts.swapsides") {
            fetch("http://localhost:8000/sideswap")
            .then(response => response.json())
        }

        else if (jsn.action == "com.udts.undo"){
            fetch("http://localhost:8000/undo")
            .then(response => response.json())
        }
        this.updateSides(jsn)
    },

    setTitle: function(jsn, new_name) {
        $SD.api.setTitle(jsn.context, new_name)
    },

    updateSides: function(jsn) {
        let team_1_tricode;
        let team_2_tricode;
        fetch("http://localhost:8000/match/current/")
            .then(response => response.json())
            .then((data) => {
                console.log(data)
                team_1_tricode = data["teams"][0]["tricode"] + "\nWin"
                team_1_logo = data["teams"][0]["logo_small"]
                if (team_1_tricode == "") {
                    team_1_tricode = "Team 1\nWin"
                }
                team_2_tricode = data["teams"][1]["tricode"] + "\nWin"
                team_2_logo = data["teams"][1]["logo_small"]
                if (team_2_tricode == "") {
                    team_2_tricode = "Team 2\nWin"
                }
                this.setTitle(knownButtons["com.udts.team1win"], team_1_tricode)
                this.setTitle(knownButtons["com.udts.team2win"], team_2_tricode)
            })
            .catch(error => {
                team_1_tricode = "Team 1\nWin"
                team_2_tricode = "Team 2\nWin"
                this.setTitle(knownButtons["com.udts.team1win"], team_1_tricode)
                this.setTitle(knownButtons["com.udts.team2win"], team_2_tricode)
            })
    }
};

