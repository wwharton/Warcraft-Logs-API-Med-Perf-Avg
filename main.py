import requests
import statistics
import collections
import math
import sys


#queries API to get (up to) 500 players, per class, who participated in encounter 709 (Skeram)
def get_player_list(params_Characters, api_root, Classes):
    players = []
    for baz in Classes:
        params_Characters['class'] = baz
        for i in range(5):
            params_Characters['page'] = i + 1
            print(params_Characters['page'])
            foo = requests.get(f"{api_root}/rankings/encounter/1114", params=params_Characters)
            if foo.status_code != 200:
                break
            data = foo.json()
            for x in range(100):
                try:
                    players.append(data["rankings"][x]["name"])
                except:
                    pass
    return players


#Takes the player list and writes to a file
def write_player_list(players):
    with open('PlayerList.txt', 'w', encoding='utf-8') as f:
        for player in players:
            print(player, file=f)


# Populates encounters dict for a player with: keys = encounters (boss names), and values = lists of all scores
def create_entry_dict(data):
    encounters = collections.defaultdict(list)
    for entry in data:
        encounterName = entry["encounterName"]
        percentile = entry['percentile']
        encounters[encounterName].append(percentile)
    return encounters


# Writes final output to text file (character name and mean of scores)
def write_player_data(player, meds):
    with open('output.txt', 'a') as f:
        print(player, file=f)
        print('median perf avg', file=f)
        # print(meds, sep='\n', file=f)
        print(statistics.mean(meds), file=f)
        print('', file=f)

# Find the difference between two text files
# Used here to find player names that are present on the master list, but not the "completed" list
# In other words: Find players who have yet to be scanned.
def difference(OutputList, CompletedList) -> list:
    MissingActors = OutputList
    MissingActors = list(set(MissingActors) - set(CompletedList))
    while('' in MissingActors):
        MissingActors.remove('')
    with open('MissingActors.txt', 'w', encoding='utf-8') as f:
        print(MissingActors, file=f)
    return MissingActors


# Reads from player file and delivers a list of players for the script to parse
def populate_player_list() -> list:
    with open('PlayerList.txt', 'r', encoding='utf-8') as f1:
        PlayerList_ref = []
        for line in f1.readlines():
            PlayerList_ref.append(line.strip('\n'))
        print('output list ', PlayerList_ref)
    return PlayerList_ref


# Reads from completed file and delivers a list of players which remain to be parsed
def populate_completed_list():
    with open('Completed.txt', 'r', encoding='utf-8') as f2:
        CompletedList = []
        for line in f2.readlines():
            CompletedList.append(line.strip('\n'))
        print('completed list ', CompletedList)
    return CompletedList


# Creates a dictionary of combat encounter data for every player on this list by querying Warcraft Logs API
def create_player_encounters_dict(player, api_root, params_Parses) -> dict:
    rest_response = requests.get(f"{api_root}/parses/character/{player}/Atiesh/us", params=params_Parses)
    data = rest_response.json()
    encounters = create_entry_dict(data)
    return encounters


# Loop for calculating median peformance average and then printing scores in a specific range
def process_all_data(MissingActors, api_root, params_Parses):
    TotalCount = len(MissingActors)
    Progress = 1
    for player in MissingActors:
        encounters = create_player_encounters_dict(player, api_root, params_Parses)
        print(Progress, '/', TotalCount)
        Progress += 1
        AllEncounterMedians = calculate_player_scores(encounters)

        # This last func takes the mean of the players median averages
        # and then prints it if within the desired range
        check_score_range(player, AllEncounterMedians)


# Calculates median performance average across all bosses killed
def calculate_player_scores(encounters) -> list:
    AllEncounterMedians = []
    for encounter in encounters.keys():
        AllScoresForSingleEncounter = encounters[encounter]
        MedianForEncounter = statistics.median(AllScoresForSingleEncounter)
        AllEncounterMedians.append(MedianForEncounter)
    return AllEncounterMedians


# Takes the mean of the players median averages and then writes to file if within the desired range
def check_score_range(player, AllEncounterMedians):
    with open('Completed.txt', 'a', encoding='utf-8') as Completed_txt:
        print(player, file=Completed_txt)
        try:
            # Range here can be adjusted, int values = median performance averages
            if 100 >= statistics.mean(AllEncounterMedians) >= 1:
                write_player_data(player, AllEncounterMedians) #write data could contain the writing to completed text
        except:
            # Except captures players who have not killed every boss - thus it cannot calculate a median performance
            pass

def main():
    api_key = "Generate your own API Key by creating an account at warcraftlogs.com"

    if api_key == "Generate and provide your own API Key by creating an account at warcraftlogs.com":
        print(f'Refer to code in main loop: {api_key}')
        exit()

    Classes = [2, 3, 4, 6, 7, 8, 9, 10, 11]

    # Shorter class list, or list containing specific class code can be used alternatively
    # Example below captures only druids.
    #Classes = [2]

    api_root = "https://classic.warcraftlogs.com:443/v1"

    params_Characters = {
        'api_key' : api_key,
        'page' : '1',
        'region' : 'US',
        'server' : 'Atiesh',
        'class' : Classes
    }

    params_Parses = {
        'api_key' : api_key,
        'timeframe' : 'historical',
        'compare' : '0',
        'zone' : '1005',
        'metric' : 'bossdps',
    }

    # Generate List of Players
    players = get_player_list(params_Characters, api_root, Classes)
    write_player_list(players)
    PlayerList_ref = populate_player_list()

    # Check for and against any completed entries (In case of interruption during mass query)
    CompletedList = populate_completed_list()
    MissingActors = difference(PlayerList_ref, CompletedList)

    # Capture Performance Medians and write to file
    # Filter by performance by adjusting the values in the check_score_range() func
    process_all_data(MissingActors, api_root, params_Parses)

if __name__ == '__main__':
    main()



#put functions in a class, include a function to open all the files
#set properties on the class, so when we need the files later, we can reference the instance variables for the files
#self.completed text as file, self.output text as file, etc.,








