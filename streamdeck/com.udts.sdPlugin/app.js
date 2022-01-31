var knownButtons = []
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
    settings:{},
    onWillAppear: function (jsn) {
        for (button of knownButtons) {
            if (button.action == jsn.action) {
                var button_already_exists = true
            }
        }
        if (!button_already_exists) {
            knownButtons.push(jsn)
        }
        button_already_exists = false
        this.settings = jsn.payload.settings;
        fetch("http://localhost:8000/match/current/")
            .then(response => response.json())
            .then((data) => {
                let team_1_tricode = data["teams"][0]["tricode"];
                let team_2_tricode = data["teams"][1]["tricode"];
                if (jsn.action == "com.udts.team1win") {
                    this.settings.mynameinput = team_1_tricode + "\nWin";
                    this.setTitle(jsn);
                }
                else if (jsn.action == "com.udts.team2win") {
                    this.settings.mynameinput = team_2_tricode + "\nWin";
                    this.setTitle(jsn);
                }
            })
            .catch(error => {
                if (jsn.action == "com.udts.team1win") {
                    this.settings.mynameinput = "Team 1\nWin"
                    this.setTitle(jsn)
                }
                else if (jsn.action == "com.udts.team2win") {
                    this.settings.mynameinput = "Team 2\nWin"
                    this.setTitle(jsn)
                }
            })
        if (jsn.action == "com.udts.swapsides") {
            this.settings.mynameinput = "Swap\nRed/Blue";
            this.setTitle(jsn);
        }
        else if (jsn.action == "com.udts.forceupdate") {
            this.settings.mynameinput = "Force\nUpdate";
            this.setTitle(jsn);
        }
        else if (jsn.action == "com.udts.undo") {
            this.settings.mynameinput = "Undo"
            this.setTitle(jsn)
        }
    },

    onWillDisappear: function (jsn) {
        let index_num = 0
        for (button of knownButtons) {
            if (button["action"] == jsn.action) {
                knownButtons.splice(index_num, 1);
            }
            index_num++ 
        }
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
        fetch("http://localhost:8000/match/current/")
            .then(response => response.json())
            .then((data) => {
                let team_1_tricode = data["teams"][0]["tricode"] + "\nWin";
                let team_2_tricode = data["teams"][1]["tricode"] + "\nWin";
                for (button of knownButtons) {
                    if (button.action == "com.udts.team1win") {
                        this.setTitle(button, team_1_tricode)
                    }
                    else if (button.action == "com.udts.team2win") {
                        this.setTitle(button, team_2_tricode)
                    }
                }
            })
    },

    setTitle: function(jsn, new_name = "") {
        if (this.settings && this.settings.hasOwnProperty('mynameinput') && new_name == "") {
            $SD.api.setTitle(jsn.context, this.settings.mynameinput);
        }
        else {
            $SD.api.setTitle(jsn.context, new_name)
        }
    },

};

