import random
import string

VOWELS = "AEIOUaeiou _-"

def consonants_only(teamname):
    new_teamname = ""
    for letter in teamname:
        if letter not in VOWELS:
            new_teamname += letter
    return new_teamname

def strip_team_prefix(teamname):
    return teamname.lstrip("TEAM").lstrip("_").lstrip(" ").lstrip("-")

def is_tricode_unique(teamname, tricodelist):
    if teamname in tricodelist or len(teamname) < 2 or " " in teamname:
        return False
    else:
        return True

def generate_random_tricode_from_name(teamname, anything=False):
    i = []
    source_string = teamname
    if anything:
        source_string = string.ascii_uppercase
    
    i.append(random.choice(range(len(source_string))))
    i.append(random.choice(range(len(source_string))))
    i.append(random.choice(range(len(source_string))))
    new_tricode = source_string[i[0]] + source_string[i[1]] + source_string[i[2]]
    return new_tricode

def determine_tricode(teamname, tricodelist):
    teamname = teamname.upper()
    if " " in teamname or "_" in teamname or "-" in teamname:
        new_teamname = teamname.replace("_", " ").replace("-"," ")
        teamname_split = new_teamname.split(" ")
        if len(teamname_split) > 1:
            if len(teamname_split) >= 3:
                if len(teamname_split[0]) and len(teamname_split[1]) and len(teamname_split[2]):
                    if is_tricode_unique(f"{teamname_split[0][0:1]}{teamname_split[1][0:1]}{teamname_split[2][0:1]}", tricodelist):
                        return f"{teamname_split[0][0:1]}{teamname_split[1][0:1]}{teamname_split[2][0:1]}"
            if len(teamname_split) == 2:
                if len(teamname_split[0]) and len(teamname_split[1]):
                    if is_tricode_unique(f"{teamname_split[0][0:1]}{teamname_split[1][0:1]}", tricodelist):
                        return f"{teamname_split[0][0:1]}{teamname_split[1][0:1]}"
                    if len(teamname_split[0]) > 1 and len(teamname_split[1]) > 1:
                        if is_tricode_unique(f"{teamname_split[0][0:2]}{teamname_split[1][0:1]}", tricodelist) and not teamname_split[0].startswith("TEAM"):
                            return f"{teamname_split[0][0:2]}{teamname_split[1][0:1]}"
                        if is_tricode_unique(f"{teamname_split[0][0:1]}{teamname_split[1][0:2]}", tricodelist) and not teamname_split[0].startswith("TEAM"):
                            return f"{teamname_split[0][0:1]}{teamname_split[1][0:2]}"
    if "." in teamname:
        teamname_split = teamname.split(".")
        if len(teamname_split) > 1:
            if len(teamname_split[0]) and len(teamname_split[1]):
                if is_tricode_unique(f"{teamname_split[0:1]}{teamname_split[1][0:2]}", tricodelist):
                    return f"{teamname_split[0][0:1]}{teamname_split[1][0:2]}"
    if teamname.startswith("TEAM"):
        new_teamname = strip_team_prefix(teamname)
        if is_tricode_unique(f"T{new_teamname[0:2]}", tricodelist):
            return f"T{new_teamname[0:2]}"
        if is_tricode_unique(f"T{new_teamname[0:1]}{new_teamname[2:3]}", tricodelist) and len(new_teamname) > 2:
            return f"T{new_teamname[0:1]}{new_teamname[2:3]}"
        if is_tricode_unique(f"T{new_teamname[0:1]}{new_teamname[-1:]}", tricodelist) and len(new_teamname) > 2:
            return f"T{new_teamname[0:1]}{new_teamname[-1:]}"
    if len(teamname) > 2:
        attempt = f"T{consonants_only(strip_team_prefix(teamname))[0:2]}"
        if teamname.startswith("TEAM") and is_tricode_unique(attempt, tricodelist):
            if len(attempt) > 1 and is_tricode_unique(attempt, tricodelist):
                return attempt
    teamname = f"{teamname}".replace(" ", "")
    if " " in teamname[0:3] and len(teamname) > 2:
        if is_tricode_unique(new_teamname[0:3], tricodelist):
            return new_teamname[0:3]
        attempt = f"{new_teamname[0:1]}{consonants_only(new_teamname[2:4])}"
        if is_tricode_unique(attempt, tricodelist) and len(attempt) > 1:
            return attempt
    if is_tricode_unique(teamname[0:3], tricodelist):
        return teamname[0:3]
    if len(teamname) > 2:
        if is_tricode_unique(consonants_only(teamname)[0:3], tricodelist):
            if len(f"{consonants_only(teamname)[0:3]}") > 1:
                return consonants_only(teamname)[0:3]
    if len(teamname) > 3:
        if is_tricode_unique(f"{teamname[0:0]}{teamname[-1:]}", tricodelist):
            return f"{teamname[0:0]}{teamname[-1:]}"
        if is_tricode_unique(f"{teamname[0:0]}{teamname[-2:]}", tricodelist):
            return f"{teamname[0:0]}{teamname[-2:]}"
    
    found_tricode = False
    random_tricode = False
    i=0
    while found_tricode is not True:
        new_tricode = generate_random_tricode_from_name(teamname, anything=random_tricode)
        if is_tricode_unique(new_tricode, tricodelist):
            found_tricode = True
            return new_tricode
        if i > 10:
            random_tricode = True
        if i > 100:
            return "ERR"
        i += 1