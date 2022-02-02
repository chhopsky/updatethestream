var knownButtons = {};
var teams = {};
var baseUrl = "http://localhost:8000";
$SD.on('connected', (jsonObj) => connected(jsonObj));

function connected(jsn) {
    // Subscribe to the willAppear and other events
    $SD.on('com.udts.team1win.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.team2win.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.swapsides.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.forcerefreshstream.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.undo.willAppear', (jsonObj) => action.onWillAppear(jsonObj));
    $SD.on('com.udts.team1win.willDisappear', (jsonObj) => action.onWillDisappear(jsonObj));
    $SD.on('com.udts.team2win.willDisappear', (jsonObj) => action.onWillDisappear(jsonObj));
    $SD.on('com.udts.swapsides.willDisappear', (jsonObj) => action.onWillDisappear(jsonObj));
    $SD.on('com.udts.forcerefreshstream.willDisappear', (jsonObj) => action.onWillDisappear(jsonObj));
    $SD.on('com.udts.undo.willDisappear', (jsonObj) => action.onWillDisappear(jsonObj));
    $SD.on('com.udts.team1win.keyDown', (jsonObj) => onClick("/win/team1"));
    $SD.on('com.udts.team2win.keyDown', (jsonObj) => onClick("/win/team2"));
    $SD.on('com.udts.swapsides.keyDown', (jsonObj) => onClick("/sideswap"));
    $SD.on('com.udts.undo.keyDown', (jsonObj) => onClick("/undo"));
    $SD.on('com.udts.forcerefreshstream.keyDown', (jsonObj) => onClick("/stream/refresh"));
};

function onClick(path) {
    let url = baseUrl + path;
    fetch(url)
    .then(function (response) {
        return response.json();
      })
      .then(function(){
        currentmatch_call()
      })
      .catch(function (error) {
        console.log("Error: " + error);
      });
}

function currentmatch_call()
{
    let url = baseUrl + "/match/current"
    fetch(url)
    .then(function (response) {
        return response.json();
    })
    .then(function (status) {
        updateSides(status)
    })
    .catch(function (error) {
        console.log("Error: " + error);
        team_1_tricode = "Team 1\nWin"
        team_2_tricode = "Team 2\nWin"
        setTitle(knownButtons["com.udts.team1win"], team_1_tricode)
        setTitle(knownButtons["com.udts.team2win"], team_2_tricode)
    });
}


function get_scores(status){
    if(typeof status["match"]["scores"][0] === 'undefined'){
      return "0 - 0"
    }
    else {
      return status["match"]["scores"][0] + " - " + status["match"]["scores"][1]
    }
}
    
function get_match_participants(status) {
    team1 = status["teams"][0]
    team2 = status["teams"][1]
    return get_team_name(team1) + " vs " + get_team_name(team2)
    }
    
function get_team_name(team){
      if (team["name"] !== "") {
        return team["name"];
      }
      else {
        return team["tricode"];
      }
}
    
function get_team_tricode(team){
      if (team["tricode"] !== "") {
        console.log(team)
        return team["tricode"];   
      }
      else {
        return team["name"];
      }
}

function get_team_uuid(team) {
  return team["id"]
}

function set_team_logo(team_uuid, team_index) {
  let url = baseUrl + "/teams/all"
  let fmt_to_b64 = {
    "png": "data:image/png;base64,",
    "jpg": "data:image/jpg;base64,",
    "jpeg": "data:image/jpeg;base64,",
    "bmp": "data:image/bmp;base64,",
    undefined: null
  }
  fetch(url)
    .then(function (response) {
      return response.json()
    })
    .then(function (data) {
      let logo = null
      let team = data["teams"][team_uuid]
      let logo_url = team["logo_small"].toString()
      console.log(team, logo_url)
      if (logo_url) {
        let logo_fmt = logo_url.split(".").slice(-1)[0]  // This is so cursed.
        logo = fmt_to_b64[logo_fmt] + team["logo_small_b64"]
      }
      console.log(logo)
      if (team_index == 0) {
        setImage(knownButtons["com.udts.team1win"], logo)
      }
      else {
        setImage(knownButtons["com.udts.team2win"], logo)
      }
    })
    .catch(function (error){
      console.log("Error: " + error);
    })
}

function updateSides(data) {
    let team_1 = data["teams"][0]
    let team_2 = data["teams"][1]
    let team_1_tricode = get_team_tricode(data["teams"][0])
    if (team_1_tricode == "") {
        team_1_tricode = "Team 1"
    }
    let team_2_tricode = get_team_tricode(data["teams"][1])
    if (team_2_tricode == "") {
        team_2_tricode = "Team 2"
    } 
    let team_1_uuid = get_team_uuid(team_1)
    let team_2_uuid = get_team_uuid(team_2)
    set_team_logo(team_1_uuid, 0)
    set_team_logo(team_2_uuid, 1)
    setTitle(knownButtons["com.udts.team1win"], team_1_tricode + "\nWin")
    setTitle(knownButtons["com.udts.team2win"], team_2_tricode + "\nWin")
}

function setTitle(jsn, new_name) {
    $SD.api.setTitle(jsn.context, new_name)
}

function setImage(jsn, image) {
    $SD.api.setImage(jsn.context, image)
}
const action = {
    onWillAppear: function (jsn) {
        knownButtons[jsn.action] = jsn
        if (jsn.action == "com.udts.swapsides") {
            setTitle(jsn, "Swap\nRed/Blue");
            currentmatch_call()
        }
        else if (jsn.action == "com.udts.forcerefreshstream") {
            setTitle(jsn, "Force\nRefresh\nStream");
        }
        else if (jsn.action == "com.udts.undo") {
            setTitle(jsn, "Undo")
        }
        else if (jsn.action == "com.udts.team1win") {
            setTitle(jsn, "Team 1\nWin")
        }
        else if (jsn.action == "com.udts.team1win") {
            setTitle(jsn, "Team 2\nWin")
        }
    },

    onWillDisappear: function (jsn) {
        delete knownButtons[jsn.action]
    },
};

