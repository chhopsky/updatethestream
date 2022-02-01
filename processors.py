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
    tn = teamname.upper()
    # tn: original teamname, tn_s: teamname, split by something
    # First, if it's a two or three word name, people expect the first letters
    if " " in tn or "_" in tn or "-" in tn:
        new_tn = tn.replace("_", " ").replace("-"," ")
        tn_s = new_tn.split(" ")
        if len(tn_s) > 1:
            # if it's a three word name, take the first letter of each word
            if len(tn_s) >= 3:
                if len(tn_s[0]) and len(tn_s[1]) and len(tn_s[2]):
                    if is_tricode_unique(f"{tn_s[0][0:1]}{tn_s[1][0:1]}{tn_s[2][0:1]}", tricodelist):
                        return f"{tn_s[0][0:1]}{tn_s[1][0:1]}{tn_s[2][0:1]}"
            # if it's a two word name
            if len(tn_s) == 2:
                # try the first letters of the two words
                if len(tn_s[0]) == 3:
                    if is_tricode_unique(f"{tn_s[0]}", tricodelist):
                        return f"{tn_s[0]}"
                    if len(tn_s[1]):
                        if is_tricode_unique(f"{tn_s[0][0:1]}{tn_s[0][2:3]}{tn_s[1][0:1]}", tricodelist):
                            return f"{tn_s[0][0:1]}{tn_s[0][2:3]}{tn_s[1][0:1]}"
                if len(tn_s[0]) and len(tn_s[1]):
                    if is_tricode_unique(f"{tn_s[0][0:1]}{tn_s[1][0:1]}", tricodelist):
                        return f"{tn_s[0][0:1]}{tn_s[1][0:1]}"
                    # if that's taken, check if both words are more than 1 char
                    if len(tn_s[0]) > 1 and len(tn_s[1]):
                        # try the first two chars from the first word, and first char of the second
                        if is_tricode_unique(f"{tn_s[0][0:2]}{tn_s[1][0:1]}", tricodelist) and not tn_s[0].startswith("TEAM"):
                            return f"{tn_s[0][0:2]}{tn_s[1][0:1]}"
                    if len(tn_s[0]) and len(tn_s[1]) > 1:
                        # if that's taken, try the first char from the first word, and the first two of the second
                        if is_tricode_unique(f"{tn_s[0][0:1]}{tn_s[1][0:2]}", tricodelist) and not tn_s[0].startswith("TEAM"):
                            return f"{tn_s[0][0:1]}{tn_s[1][0:2]}"
    # if there's a "." its probably a domain name, use first letter + suffix
    # make sure the split worked, and that both suffix and prefix are at least one and two chars
    if "." in tn:
        tn_s = tn.split(".")
        if len(tn_s) > 1 and len(tn_s[0]) and len(tn_s[1]) > 1:
            if is_tricode_unique(f"{tn_s[0:1]}{tn_s[1][0:2]}", tricodelist):
                return f"{tn_s[0][0:1]}{tn_s[1][0:2]}"
    # FACEIT teams often get formed with "team_playername" for the captain.
    # if a team falls through the first block for uniqueness, it gets caught here
    if tn.startswith("TEAM"):
        new_tn = strip_team_prefix(tn)
        # T + first two chars of second word
        if is_tricode_unique(f"T{new_tn[0:2]}", tricodelist):
            return f"T{new_tn[0:2]}"
        # T + first and third
        if is_tricode_unique(f"T{new_tn[0:1]}{new_tn[2:3]}", tricodelist) and len(new_tn) > 2:
            return f"T{new_tn[0:1]}{new_tn[2:3]}"
        # T + first and last
        if is_tricode_unique(f"T{new_tn[0:1]}{new_tn[-1:]}", tricodelist) and len(new_tn) > 2:
            return f"T{new_tn[0:1]}{new_tn[-1:]}"
    # try to strip vowels from teams with a team prefix
    if len(tn) > 2:
        attempt = f"T{consonants_only(strip_team_prefix(tn))[0:2]}"
        if tn.startswith("TEAM") and is_tricode_unique(attempt, tricodelist) and len(attempt) > 1:
            return attempt
    # just take the first three. single word names will fall through to here
    if is_tricode_unique(tn[0:3], tricodelist):
        return tn[0:3]
    # ditch the spaces. 
    tn = f"{tn}".replace(" ", "")
    if len(tn) > 2:
        # try first letter + next two consonants
        attempt = f"{tn[0:1]}{consonants_only(tn[2:4])}"
        if is_tricode_unique(attempt, tricodelist) and len(attempt) > 1:
            return attempt
    # try first three consonants only
    if len(tn) > 2:
        if is_tricode_unique(consonants_only(tn)[0:3], tricodelist) and len(f"{consonants_only(tn)[0:3]}") > 1:
            return consonants_only(tn)[0:3]
    # if at least four characters, try first and last character
    if len(tn) > 3:
        if is_tricode_unique(f"{tn[0:0]}{tn[-1:]}", tricodelist):
            return f"{tn[0:0]}{tn[-1:]}"
        # then try first and last two
        if is_tricode_unique(f"{tn[0:0]}{tn[-2:]}", tricodelist):
            return f"{tn[0:0]}{tn[-2:]}"
    
    found_tricode = False
    random_tricode = False
    i=0
    # get desperate. pick random characters from the name
    while found_tricode is not True:
        new_tricode = generate_random_tricode_from_name(tn, anything=random_tricode)
        if is_tricode_unique(new_tricode, tricodelist):
            found_tricode = True
            return new_tricode
        # if we havent found anything ten tries later, pick three random letters up to 90 more times
        if i > 10:
            random_tricode = True
        # escape and return error if we didnt find anything in 100 random attempts. this should never happen
        if i > 100:
            return "ERR"
        i += 1