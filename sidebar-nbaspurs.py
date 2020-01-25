import config_nbaspurs
import requests
import traceback
import json
import praw
from datetime import date, timedelta, datetime
from tabulate import tabulate
import re
import random
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

sched = BlockingScheduler({'apscheduler.timezone': 'UTC'})
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

#Team Dictionary helps to make urls for boxscore and for full-forms of abbrevation of teams
teamDict = {
    "ATL": ["Atlanta Hawks", "01", "atlanta-hawks-", "/r/atlantahawks", "1610612737", "Hawks"],
    "BKN": ["Brooklyn Nets", "17", "brooklyn-nets-", "/r/gonets", "1610612751", "Nets"],
    "BOS": ["Boston Celtics", "02", "boston-celtics-", "/r/bostonceltics", "1610612738", "Celtics"],
    "CHA": ["Charlotte Hornets", "30", "charlotte-hornets-", "/r/charlottehornets", "1610612766", "Hornets"],
    "CHI": ["Chicago Bulls", "04", "chicago-bulls-", "/r/chicagobulls", "1610612741", "Bulls"],
    "CLE": ["Cleveland Cavaliers", "05", "cleveland-cavaliers-", "/r/clevelandcavs", "1610612739", "Cavaliers"],
    "DAL": ["Dallas Mavericks", "06", "dallas-mavericks-", "/r/mavericks", "1610612742", "Mavericks"],
    "DEN": ["Denver Nuggets", "07", "denver-nuggets-", "/r/denvernuggets", "1610612743", "Nuggets"],
    "DET": ["Detroit Pistons", "08", "detroit-pistons-", "/r/detroitpistons", "1610612765", "Pistons"],
    "GSW": ["Golden State Warriors", "09", "golden-state-warriors-", "/r/warriors", "1610612744", "Warriors"],
    "HOU": ["Houston Rockets", "10", "houston-rockets-", "/r/rockets", "1610612745", "Rockets"],
    "IND": ["Indiana Pacers", "11", "indiana-pacers-", "/r/pacers", "1610612754", "Pacers"],
    "LAC": ["Los Angeles Clippers", "12", "los-angeles-clippers-", "/r/laclippers", "1610612746", "Clippers"],
    "LAL": ["Los Angeles Lakers", "13", "los-angeles-lakers-", "/r/lakers", "1610612747", "Lakers"],
    "MEM": ["Memphis Grizzlies", "29", "memphis-grizzlies-", "/r/memphisgrizzlies", "1610612763", "Grizzlies"],
    "MIA": ["Miami Heat", "14", "miami-heat-", "/r/heat", "1610612748", "Heat"],
    "MIL": ["Milwaukee Bucks", "15", "milwaukee-bucks-", "/r/mkebucks", "1610612749", "Bucks"],
    "MIN": ["Minnesota Timberwolves", "16", "minnesota-timberwolves-", "/r/timberwolves", "1610612750", "Timberwolves"],
    "NOP": ["New Orleans Pelicans", "03", "new-orleans-pelicans-", "/r/nolapelicans", "1610612740", "Pelicans"],
    "NYK": ["New York Knicks", "18", "new-york-knicks-", "/r/nyknicks", "1610612752", "Knicks"],
    "OKC": ["Oklahoma City Thunder", "25", "oklahoma-city-thunder-", "/r/thunder", "1610612760", "Thunder"],
    "ORL": ["Orlando Magic", "19", "orlando-magic-", "/r/orlandomagic", "1610612753", "Magic"],
    "PHI": ["Philadelphia 76ers", "20", "philadelphia-76ers-", "/r/sixers", "1610612755", "76ers"],
    "PHX": ["Phoenix Suns", "21", "phoenix-suns-", "/r/suns", "1610612756", "Suns"],
    "POR": ["Portland Trail Blazers", "22", "portland-trail-blazers-", "/r/ripcity", "1610612757", "Trail Blazers"],
    "SAC": ["Sacramento Kings", "23", "sacramento-kings-", "/r/kings", "1610612758", "Kings"],
    "SAS": ["San Antonio Spurs", "24", "san-antonio-spurs-", "/r/nbaspurs", "1610612759", "Spurs"],
    "TOR": ["Toronto Raptors", "28", "toronto-raptors-", "/r/torontoraptors", "1610612761", "Raptors"],
    "UTA": ["Utah Jazz", "26", "utah-jazz-", "/r/utahjazz", "1610612762", "Jazz"],
    "WAS": ["Washington Wizards", "27", "washington-wizards-", "/r/washingtonwizards", "1610612764, ", "Wizards"],
    "ADL": ["Adelaide 36ers", "00", "adelaide-36ers", "/r/nba", "15019"],
    "SLA": ["Buenos Aires San Lorenzo", "00", "buenos-aires-san-lorenzo", "/r/nba", "12330"],
    "FRA": ["Franca Franca", "00", "franca-franca", "/r/nba", "12332"],
    "GUA": ["Guangzhou Long-Lions", "00", "guangzhou-long-lions", "/r/nba", "15018"],
    "MAC": ["Haifa Maccabi Haifa", "00", "haifa-maccabi-haifa", "/r/nba", "93"],
    "MEL": ["Melbourne United", "00", "melbourne-united", "/r/nba", "15016"],
    "NZB": ["New Zealand Breakers", "00", "new-zealand-breakers", "/r/nba", "15020"],
    "SDS": ["Shanghai Sharks", "00", "shanghai-sharks", "/r/nba", "12329"]
}
gLeagueTeamDict = {
  "CPS": ["College Park Skyhawks", "/r/atlantahawks"],
  "LIN": ["Long Island Nets","/r/gonets"],
  "MNE": ["Maine Red Claws", "/r/bostonceltics"],
  "GBO": ["Greensboro Swarm","/r/charlottehornets"],
  "WCB": ["Windy City Bulls","/r/chicagobulls"],
  "CTN": ["Canton Charge","/r/clevelandcavs"],
  "TEX": ["Texas Legends","/r/mavericks"],
  "DEN": ["Denver Nuggets", "07", "denver-nuggets-","/r/denvernuggets"],
  "GRD": ["Grand Rapids", "/r/detroitpistons"],
  "SCW": ["Santa Cruz Warriors", "/r/warriors"],
  "RGV": ["Rio Grande Valley Vipers", "/r/rockets"],
  "FWN": ["Fort Wayne Mad Ants", "/r/pacers"],
  "ACC": ["Agua Caliente Clippers", "/r/laclippers"],
  "SBL": ["South Bay Lakers", "/r/lakers"],
  "MHU": ["Memphis Hustle", "/r/memphisgrizzlies"],
  "SXF": ["Sioux Falls Skyforce", "/r/heat"],
  "WIS": ["Wisconsin Herd", "/r/mkebucks"],
  "IWA": ["Iowa Wolves", "/r/timberwolves"],
  "ERI": ["Erie Bayhawks", "/r/nolapelicans"],
  "WES": ["Westchester", "/r/nyknicks"],
  "OKL": ["Oklahoma City Blue", "/r/thunder"],
  "LAK": ["Lakeland", "/r/orlandomagic"],
  "DEL": ["Delaware Bue Coats", "/r/sixers"],
  "NAS": ["Northern Arizona Suns", "/r/suns"],
  "POR": ["Portland Trail Blazers", "22", "portland-trail-blazers-", "/r/ripcity"],
  "STO": ["Stockton Kings", "/r/kings"],
  "AUS": ["Austin Spurs", "/r/nbaspurs"],
  "RAP": ["Raptors 905", "/r/torontoraptors"],
  "SLC": ["Salt Lake City Stars", "/r/utahjazz"],
  "CCG": ["Capital City Go-Go", "/r/washingtonwizards"]
}

#Sidebar body starts here
sidebarBody = '''[Pounding the Rock](http://www.poundingtherock.com/) | [Spurstalk](http://www.spurstalk.com/forums/) | [Spurs Discord](https://discord.gg/rcvBDQ6)

------
**[2019-2020 Spurs Schedule](http://www.nba.com/spurs/schedule/) | Record: '''

rulesAndBanners = '''\n\n**Spurs Related content**

Content must be directly related to the Spurs, whether it be in the links content, or body in the case of self posts. Memes are allowed, as long as both image and text are related to the Spurs. Bots, novelty, and spam accounts are not allowed and will be permanently banned

**Posting Guidelines**

Hate/Troll threads will be removed, trolls will be hit with permanent bans. Posting intentionally misleading headlines/titles will result in permanent bans. Threads meant to communicate to other redditors will be removed (Use pms.)

**Threats, Suggestions of harm, Personal insults**

We do not tolerate this kind of behavior whether it's directed at players or people, any of which will be met with bans.

**Racist, Sexist, Homophobic language**

Homophobic, Racist, Sexist, and or comments are all permanent bans.

**Flamebait, Trolling, Harassment**

Light trash talk is permitted, if things get excessive or personal this might lead to a ban. Do not incite, provoke or antagonize; This includes visitors from other subs.

**Comments/Posts with Personal Information**

Self explanatory; don't do it. Posting such information is not only against subreddit rules, but site wide rules. Doing so will lead to a permanent ban.

**Comment Full Edits**

Do not change or alter comments to troll, advertise, or joke such comments are subject to removal.

**Be Civil and Respectful**

Don't be offensive for the sole purpose of being offensive. Please respect one another.

**Spoilers, Gore, Porn**

Not the place, do not post, insta ban.

**No Politics**

This is a subreddit meant for sports, specifically basketball, no politics are allowed unless directly related to the Spurs.


* [](http://en.wikipedia.org/wiki/1998%E2%80%9399_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2002%E2%80%9303_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2004%E2%80%9305_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2006%E2%80%9307_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2013%E2%80%9314_San_Antonio_Spurs_season)
* [](http://en.wikipedia.org/wiki/2017%E2%80%9318_San_Antonio_Spurs_season)

1. [](http://en.wikipedia.org/wiki/James_Silas)
2. [](http://en.wikipedia.org/wiki/George_Gervin)
3. [](http://en.wikipedia.org/wiki/Johnny_Moore_%28basketball%29)
4. [](http://en.wikipedia.org/wiki/David_Robinson_%28basketball%29)
5. [](http://en.wikipedia.org/wiki/Sean_Elliott)
6. [](http://en.wikipedia.org/wiki/Avery_Johnson)
7. [](http://en.wikipedia.org/wiki/Bruce_Bowen)
8. [](http://en.wikipedia.org/wiki/Tim_Duncan)
9. [](http://en.wikipedia.org/wiki/Manu_Ginobili)
10. [](http://en.wikipedia.org/wiki/Tony_Parker)

* [](https://en.wikipedia.org/wiki/1999_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2003_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2005_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2007_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2013_NBA_Playoffs)
* [](https://en.wikipedia.org/wiki/2014_NBA_Playoffs)\n\n'''
    
def appendPlusMinus(someStat):
    """
    someStat is any stat
    appendPlusMinus just appends sign in front of stat in question 
    and returns it
    """
    if someStat.isdigit():
        if int(someStat) > 0:
            return "+" + str(someStat)
        return str(someStat)
    else:
        return str(someStat)


#logging in to get reddit class
reddit = praw.Reddit(username = config_nbaspurs.username, 
                    password = config_nbaspurs.password,
                    client_id = config_nbaspurs.client_id, 
                    client_secret = config_nbaspurs.client_secret,
                    user_agent = "nbaspurs sidebar (by /u/f1uk3r)")

#change it to "nbaspurs" for update on main subreddit
sub = "nbaspurs"

#finding player's name when player's ID is given, dataPlayersLeague is a list of all players
def findPlayerName(dataPlayersLeague, playerId):
    for each in dataPlayersLeague:
        if each["personId"] == playerId:
            return each["firstName"] + " " + each["lastName"]

#getting json data from requsted url
def requestApi(url):
    req = requests.get(url)
    return req.json()

#getting players data for players table
def playerDataList(dataPlayersLeague, playerId):
    playerData = requestApi("http://data.nba.net/prod/v1/2019/players/" + str(playerId) + "_profile.json")
    playerCurrentData = playerData["league"]["standard"]["stats"]["latest"]
    if playerCurrentData["ppg"] != "-1":
        playerRequiredData = [findPlayerName(dataPlayersLeague, playerId), playerCurrentData["ppg"],playerCurrentData["rpg"],playerCurrentData["apg"],playerCurrentData["spg"],playerCurrentData["bpg"]]
        return playerRequiredData
    return []

def get_conference_standings():
    """
    Returns conference standing markup
    """
    #getting record from another json (can be improved by getting this record from schedule.json)
    data_standing = requestApi("http://data.nba.net/prod/v1/current/standings_conference.json")
    west_standing = data_standing["league"]["standard"]["conference"]["west"]
    for eachTeam in west_standing:
        if eachTeam["teamId"] == "1610612759":
            standing_markup = eachTeam["win"] + "-" + eachTeam["loss"] + "**\n---------"
    standing_markup += f"""\n\n\n|WEST|||
|:---:|:---:|:---:|
|**TEAM**|*W/L*|*GB*|\n"""
    for i in range(8):
        standing_markup += f'|{i+1} [](/{west_standing[i]["teamSitesOnly"]["teamTricode"]})| {west_standing[i]["win"]}-{west_standing[i]["loss"]} | {west_standing[i]["gamesBehind"]} |\n'
    for i in range(8, len(west_standing)):
        standing_markup += f'| [](/{west_standing[i]["teamSitesOnly"]["teamTricode"]})| {west_standing[i]["win"]}-{west_standing[i]["loss"]} | {west_standing[i]["gamesBehind"]} |\n'
    print(f"exiting conference standing block {datetime.now()}")
    return standing_markup

def get_players_stats():
    #getting informations of players through API since the boxscore API lacks name of players
    dataPlayers = requestApi("http://data.nba.net/prod/v1/2019/players.json")
    dataPlayersLeague = dataPlayers["league"]["standard"] + dataPlayers["league"]["africa"] + dataPlayers["league"]["sacramento"] + dataPlayers["league"]["vegas"] + dataPlayers["league"]["utah"]
    #getting roster of spurs
    teamData = requestApi("http://data.nba.net/prod/v1/2019/teams/1610612759/roster.json")
    teamPlayers = teamData["league"]["standard"]["players"]
    player_stats_markup = '''\n\n| | | | | | | |
|--:|:--:|:--:|:--:|:--:|:--:|:--:|
**Player** | **PTS** | **REB** | **AST** | **STL** | **BLK** |'''
    #body is appended with the data of players
    for each in teamPlayers:
        players = playerDataList(dataPlayersLeague, each["personId"])
        if players != []:
            player_stats_markup += "\n"
            for every in players:
                player_stats_markup +=  every + " | "
    print(f"exiting players stat block {datetime.now()}")
    return player_stats_markup

def get_schedule(teamDict):
    #getting whole NBA Schedule
    spursSchedule = requestApi("http://data.nba.net/prod/v1/2019/teams/1610612759/schedule.json")
    allSpursGames = spursSchedule["league"]["standard"]

    #finding date of games
    now = date.today()
    yesterday = date.today() - timedelta(1)
    dateToday = now.strftime("%Y%m%d") #check the date before using script
    dateYesterday = yesterday.strftime("%Y%m%d")
    #print(date)

    #getting games which are to be displayed from all 82 games
    for i in range(len(allSpursGames)):
        if allSpursGames[i]["startDateEastern"] == dateToday or allSpursGames[i]["startDateEastern"] == dateYesterday:
            if i+5<len(allSpursGames):
                requiredSpursGames = [allSpursGames[i-2],allSpursGames[i-1],allSpursGames[i],allSpursGames[i+1],allSpursGames[i+2],allSpursGames[i+3],allSpursGames[i+4],allSpursGames[i+5]]
            else:
                requiredSpursGames = [allSpursGames[i-2],allSpursGames[i-1]]
                for j in range(i, len(allSpursGames)):
                    requiredSpursGames.append(allSpursGames[j])
    schedule_markup = ">\n"
    #schedule part of the body
    for each in requiredSpursGames:
        if each["gameUrlCode"][9:12] == "SAS":
            schedule_markup += f"- []({teamDict[each['gameUrlCode'][12:15]][3]})"
        else:
            schedule_markup += f"- []({teamDict[each['gameUrlCode'][9:12]][3]})"
        schedule_markup += f"[{each['gameUrlCode'][9:12]} @ {each['gameUrlCode'][12:15]}](#T)"
        gameStartTime = datetime.strptime(each["startTimeUTC"][:19], '%Y-%m-%dT%H:%M:%S')
        startDate = datetime.strptime(each["startDateEastern"], '%Y%m%d')
        schedule_markup += f"[{startDate.strftime('%a %b %d')}](#D)"
        today_game_full = requestApi(f"http://data.nba.net/prod/v1/{each['homeStartDate']}/{each['gameId']}_boxscore.json")
        gameData = today_game_full['basicGameData']
        if gameData["isGameActivated"] == True:
            gameThreadUrl = ""
            schedule_markup += f"[{gameData['clock']} {gameData['period']['current']}Q](#TI)[{gameData['vTeam']['score']}-{gameData['hTeam']['score']}](#SC)"
            for submission in (reddit.subreddit('nbaspurs').search("game thread", sort="new", time_filter="day")):
                if f"[Game Thread] The San Antonio Spurs" in submission.title:
                        gameThreadUrl = submission.url
            if gameThreadUrl != "":
                schedule_markup += f"[Game Thread]({submission.url})\n"
            else:
                schedule_markup += "\n"
        else:
            postGameThreadUrl = ""
            gameStartTime = datetime.strptime(gameData["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S')
            if datetime.utcnow() < gameStartTime:
                if each["isHomeTeam"]:
                    finalCol = gameData["watch"]["broadcast"]["broadcasters"]["hTeam"][0]["shortName"]
                    schedule_markup += f"[{gameData['startTimeEastern']}](#TI)[](#SC)[{finalCol}](#BC)\n"
                elif len(gameData["watch"]["broadcast"]["broadcasters"]["vTeam"])!=0:
                    finalCol = gameData["watch"]["broadcast"]["broadcasters"]["vTeam"][0]["shortName"]
                    schedule_markup += f"[{gameData['startTimeEastern']}](#TI)[](#SC)[{finalCol}](#BC)\n"
                else:
                    schedule_markup += f"[{gameData['startTimeEastern']}](#TI)[](#SC)[](#BC)\n"
            else:
                if gameData["period"]["current"] == 5:
                    schedule_markup += f"[FINAL-OT](#TI)[{gameData['vTeam']['score']}-{gameData['hTeam']['score']}](#SC)[Game Thread]"
                elif gameData["period"]["current"] > 5:
                    numOT = gameData['period']['current']-4
                    schedule_markup += f'[FINAL-{numOT} OT](#TI)[{gameData["vTeam"]["score"]}-{gameData["hTeam"]["score"]}](#SC)[Game Thread]'
                else:
                    schedule_markup += f"[FINAL](#TI)[{gameData['vTeam']['score']}-{gameData['hTeam']['score']}](#SC)[Game Thread]"
                if each["isHomeTeam"]:
                    otherTeam = f"{teamDict[each['gameUrlCode'][9:12]][0]}"
                else:
                    otherTeam = f"{teamDict[each['gameUrlCode'][12:15]][0]}"
                for submission in (reddit.subreddit('nbaspurs').search("game thread", sort="new", time_filter="week")):
                    if f"[Game Thread] The San Antonio Spurs" in submission.title and otherTeam in submission.title:
                        schedule_markup += f"({submission.url})"
                for submission in (reddit.subreddit('nbaspurs').search("post game thread", sort="new", time_filter="week")):
                    if ("[Post Game Thread]" in submission.title and "San Antonio Spurs" in submission.title and otherTeam in submission.title):
                        postGameThreadUrl = submission.url
                if postGameThreadUrl != "":
                    schedule_markup += f"[Post Game Thread]({submission.url})\n"
                else:
                    schedule_markup += "\n"
    print(f"exiting schedule block {datetime.now()}")
    return schedule_markup

def update_sidebar(sidebarBody, standing_markup, players_stats_markup, schedule_markup, rulesAndBanners):
    """
    Reads sidebar content from wiki and replaces placeholders with markup blocks
    updates sidebar, returns nothing
    """
    sidebarBody += standing_markup
    sidebarBody += players_stats_markup
    sidebarBody += rulesAndBanners
    sidebarBody += schedule_markup
    reddit.subreddit(sub).mod.update(description=sidebarBody)
    print(f"sidebar updated {datetime.now()}")

def games_inactive_update_sidebar_first_run(sidebarBody, teamDict, endTime, startTimeNextGame, rulesAndBanners):
    """
    Variables top_submission_markup, standing_markup, schedule_markup are self explainatory
    Variable redditThreadList have game threads and post game threads links against each game
    variable endTime have the endtime for today's last game
    variable startTimeNextGame has starting time of tomorrow's first game
    Updates sidebar and schedule job to update sidebar every 2 hours when games are inactive
    """
    standing_markup = get_conference_standings()
    players_stats_markup = get_players_stats()
    schedule_markup = get_schedule(teamDict)
    update_sidebar(sidebarBody, standing_markup, players_stats_markup, schedule_markup, rulesAndBanners)
    sched.add_job(game_inactive_update_sidebar_in_interval, 'interval', hours=24, max_instances=15, start_date=endTime, end_date=startTimeNextGame, args=[sidebarBody, standing_markup, players_stats_markup, schedule_markup, rulesAndBanners])

def game_inactive_update_sidebar_in_interval(sidebarBody, schedule_markup, rulesAndBanners):
    """
    Variable redditThreadList have game threads and post game threads links against each game
    Variables game_thread_vbar is self explainatory
    Updates sidebar when games are inactive
    """
    standing_markup = get_conference_standings()
    players_stats_markup = get_players_stats()
    update_sidebar(sidebarBody, standing_markup, players_stats_markup, schedule_markup, rulesAndBanners)

def games_active_update_sidebar(sidebarBody, teamDict, rulesAndBanners):
    """
    Variables top_submission_markup, standing_markup, schedule_markup are self explainatory
    Variable redditThreadList have game threads and post game threads links against each game
    variable endTime have the endtime for today's last game
    variable startTimeNextGame has starting time of tomorrow's first game
    Updates sidebar and schedule job to update sidebar every 2 hours when games are inactive
    """
    standing_markup = get_conference_standings()
    players_stats_markup = get_players_stats()
    schedule_markup = get_schedule(teamDict)
    update_sidebar(sidebarBody, standing_markup, players_stats_markup, schedule_markup, rulesAndBanners)


def process_sidebar():
    spursSchedule = requestApi("http://data.nba.net/prod/v1/2019/teams/1610612759/schedule.json")
    allSpursGames = spursSchedule["league"]["standard"]
    for i in range(len(allSpursGames)):
        if (allSpursGames[i]["vTeam"]["score"] == "" and allSpursGames[i]["hTeam"]["score"] == ""):
            startTime = datetime.strptime(allSpursGames[i]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(minutes=45)
            endTime = datetime.strptime(allSpursGames[i]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') + timedelta(hours=4)
            startTimeNextGame = datetime.strptime(allSpursGames[i+1]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(hours=2)
            break
    sched.add_job(games_active_update_sidebar, 'interval', minutes=2, max_instances=15, start_date=startTime, end_date=endTime, args=[sidebarBody, teamDict, rulesAndBanners])
    sched.add_job(games_inactive_update_sidebar_first_run, 'date', run_date=endTime, args=[sidebarBody, teamDict, endTime, startTimeNextGame, rulesAndBanners])
    sched.add_job(process_sidebar, 'date', run_date=startTimeNextGame)
    print("process_sidebar is scheduled for next date")


def boxScoreText(boxScoreData, bodyText, date, teamDict):
    """
    Variable boxScoreData have live data
    Variable bodyText have body when the post was originally created
    Variable date is today's date
    Variable teamDict is the variable Dictionary at the top
    Returns whole bodyText for editing
    """
    basicGameData = boxScoreData["basicGameData"]
    allStats = boxScoreData["stats"]
    vTeamBasicData = basicGameData["vTeam"]
    hTeamBasicData = basicGameData["hTeam"]
    nbaUrl = ("http://www.nba.com/games/" + date + "/"
              + vTeamBasicData["triCode"]
              + hTeamBasicData["triCode"] + "#/boxscore")
    yahooUrl = ("http://sports.yahoo.com/nba/"
                + teamDict[vTeamBasicData["triCode"]][2]
                + teamDict[hTeamBasicData["triCode"]][2]
                + date + teamDict[hTeamBasicData["triCode"]][1])
    playerStats = allStats["activePlayers"]
    body = bodyText + """
||		
|:-:|		
|[](/{vTeamLogo}) **{vTeamScore} -  {hTeamScore}** [](/{hTeamLogo})|
|**Box Scores: [NBA]({nbaurl}) & [Yahoo]({yahoourl})**|
""".format(
        vTeamLogo=vTeamBasicData["triCode"],
        vTeamScore=vTeamBasicData["score"],
        hTeamScore=hTeamBasicData["score"],
        hTeamLogo=hTeamBasicData["triCode"],
        nbaurl=nbaUrl,
        yahoourl=yahooUrl
    )

    body += """

||
|:-:|											
|&nbsp;|		
|**GAME SUMMARY**|
|**Location:** {arena}({attendance}), **Clock:** {clock}|
|**Officials:** {referee1}, {referee2} and {referee3}|

""".format(
        arena=basicGameData["arena"]["name"],
        attendance=basicGameData["attendance"],
        clock=basicGameData["clock"],
        referee1=basicGameData["officials"]["formatted"][0]["firstNameLastName"],
        referee2=basicGameData["officials"]["formatted"][1]["firstNameLastName"],
        referee3=basicGameData["officials"]["formatted"][2]["firstNameLastName"]
    )

    body += """|**Team**|**Q1**|**Q2**|**Q3**|**Q4**|**"""
    # Condition for normal games
    if len(vTeamBasicData["linescore"]) == 4:
        body += """Total**|
|:---|:--|:--|:--|:--|:--|
|""" + teamDict[vTeamBasicData["triCode"]][0] + "|" + vTeamBasicData["linescore"][0]["score"] + "|" + \
                vTeamBasicData["linescore"][1]["score"] + "|" + vTeamBasicData["linescore"][2][
                    "score"] + "|" + vTeamBasicData["linescore"][3]["score"] + "|" + vTeamBasicData[
                    "score"] + """|
|""" + teamDict[hTeamBasicData["triCode"]][0] + "|" + hTeamBasicData["linescore"][0]["score"] + "|" + \
                hTeamBasicData["linescore"][1]["score"] + "|" + hTeamBasicData["linescore"][2][
                    "score"] + "|" + hTeamBasicData["linescore"][3]["score"] + "|" + hTeamBasicData[
                    "score"] + "|\n"
    # condition for OT game
    elif len(vTeamBasicData["linescore"]) > 4:
        # appending OT columns
        for i in range(4, len(vTeamBasicData["linescore"])):
            body += "OT" + str(i - 3) + "**|**"
        body += """Total**|
|:---|:--|:--|:--|:--|:--|"""
        # increase string ":--|" according to number of OT
        for i in range(4, len(vTeamBasicData["linescore"])):
            body += ":--|"
        body += "\n|" + teamDict[vTeamBasicData["triCode"]][0] + "|"
        for i in range(len(vTeamBasicData["linescore"])):
            body += vTeamBasicData["linescore"][i]["score"] + "|"
        body += vTeamBasicData["score"] + """|
|""" + teamDict[hTeamBasicData["triCode"]][0] + "|"
        for i in range(len(hTeamBasicData["linescore"])):
            body += hTeamBasicData["linescore"][i]["score"] + "|"
        body += hTeamBasicData["score"] + "|\n"

    body += """
||		
|:-:|		
|&nbsp;|		
|**TEAM STATS**|

|**Team**|**PTS**|**FG**|**FG%**|**3P**|**3P%**|**FT**|**FT%**|**OREB**|**TREB**|**AST**|**PF**|**STL**|**TO**|**BLK**|
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
|{vTeamName}|{vpts}|{vfgm}-{vfga}|{vfgp}%|{vtpm}-{vtpa}|{vtpp}%|{vftm}-{vfta}|{vftp}%|{voreb}|{vtreb}|{vast}|{vpf}|{vstl}|{vto}|{vblk}|
|{hTeamName}|{hpts}|{hfgm}-{hfga}|{hfgp}%|{htpm}-{htpa}|{htpp}%|{hftm}-{hfta}|{hftp}%|{horeb}|{htreb}|{hast}|{hpf}|{hstl}|{hto}|{hblk}|

|**Team**|**Biggest Lead**|**Longest Run**|**PTS: In Paint**|**PTS: Off TOs**|**PTS: Fastbreak**|
|:--|:--|:--|:--|:--|:--|
|{vTeamName}|{vlead}|{vrun}|{vpaint}|{vpto}|{vfb}|
|{hTeamName}|{hlead}|{hrun}|{hpaint}|{hpto}|{hfb}|
""".format(
        vTeamName=teamDict[vTeamBasicData["triCode"]][0],
        vpts=allStats["vTeam"]["totals"]["points"],
        vfgm=allStats["vTeam"]["totals"]["fgm"],
        vfga=allStats["vTeam"]["totals"]["fga"],
        vfgp=allStats["vTeam"]["totals"]["fgp"],
        vtpm=allStats["vTeam"]["totals"]["tpm"],
        vtpa=allStats["vTeam"]["totals"]["tpa"],
        vtpp=allStats["vTeam"]["totals"]["tpp"],
        vftm=allStats["vTeam"]["totals"]["ftm"],
        vfta=allStats["vTeam"]["totals"]["fta"],
        vftp=allStats["vTeam"]["totals"]["ftp"],
        voreb=allStats["vTeam"]["totals"]["offReb"],
        vtreb=allStats["vTeam"]["totals"]["totReb"],
        vast=allStats["vTeam"]["totals"]["assists"],
        vpf=allStats["vTeam"]["totals"]["pFouls"],
        vstl=allStats["vTeam"]["totals"]["steals"],
        vto=allStats["vTeam"]["totals"]["turnovers"],
        vblk=allStats["vTeam"]["totals"]["blocks"],
        hTeamName=teamDict[hTeamBasicData["triCode"]][0],
        hpts=allStats["hTeam"]["totals"]["points"],
        hfgm=allStats["hTeam"]["totals"]["fgm"],
        hfga=allStats["hTeam"]["totals"]["fga"],
        hfgp=allStats["hTeam"]["totals"]["fgp"],
        htpm=allStats["hTeam"]["totals"]["tpm"],
        htpa=allStats["hTeam"]["totals"]["tpa"],
        htpp=allStats["hTeam"]["totals"]["tpp"],
        hftm=allStats["hTeam"]["totals"]["ftm"],
        hfta=allStats["hTeam"]["totals"]["fta"],
        hftp=allStats["hTeam"]["totals"]["ftp"],
        horeb=allStats["hTeam"]["totals"]["offReb"],
        htreb=allStats["hTeam"]["totals"]["totReb"],
        hast=allStats["hTeam"]["totals"]["assists"],
        hpf=allStats["hTeam"]["totals"]["pFouls"],
        hstl=allStats["hTeam"]["totals"]["steals"],
        hto=allStats["hTeam"]["totals"]["turnovers"],
        hblk=allStats["hTeam"]["totals"]["blocks"],
        vlead=appendPlusMinus(allStats["vTeam"]["biggestLead"]),
        vrun=allStats["vTeam"]["longestRun"],
        vpaint=allStats["vTeam"]["pointsInPaint"],
        vpto=allStats["vTeam"]["pointsOffTurnovers"],
        vfb=allStats["vTeam"]["fastBreakPoints"],
        hlead=appendPlusMinus(allStats["hTeam"]["biggestLead"]),
        hrun=allStats["hTeam"]["longestRun"],
        hpaint=allStats["hTeam"]["pointsInPaint"],
        hpto=allStats["hTeam"]["pointsOffTurnovers"],
        hfb=allStats["hTeam"]["fastBreakPoints"]
    )

    body += """
||		
|:-:|		
|&nbsp;|		
|**TEAM LEADERS**|

|**Team**|**Points**|**Rebounds**|**Assists**|
|:--|:--|:--|:--|
|{vTeam}|**{vpts}** {vply1}|**{vreb}** {vply2}|**{vast}** {vply3}|
|{hTeam}|**{hpts}** {hply1}|**{hreb}** {hply2}|**{hast}** {hply3}|
""".format(
        vTeam=teamDict[vTeamBasicData["triCode"]][0],
        vpts=allStats["vTeam"]["leaders"]["points"]["value"],
        vply1=allStats["vTeam"]["leaders"]["points"]["players"][0]["firstName"] + " " +
              allStats["vTeam"]["leaders"]["points"]["players"][0]["lastName"],
        vreb=allStats["vTeam"]["leaders"]["rebounds"]["value"],
        vply2=allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["firstName"] + " " +
              allStats["vTeam"]["leaders"]["rebounds"]["players"][0]["lastName"],
        vast=allStats["vTeam"]["leaders"]["assists"]["value"],
        vply3=allStats["vTeam"]["leaders"]["assists"]["players"][0]["firstName"] + " " +
              allStats["vTeam"]["leaders"]["assists"]["players"][0]["lastName"],
        hTeam=teamDict[hTeamBasicData["triCode"]][0],
        hpts=allStats["hTeam"]["leaders"]["points"]["value"],
        hply1=allStats["hTeam"]["leaders"]["points"]["players"][0]["firstName"] + " " +
              allStats["hTeam"]["leaders"]["points"]["players"][0]["lastName"],
        hreb=allStats["hTeam"]["leaders"]["rebounds"]["value"],
        hply2=allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["firstName"] + " " +
              allStats["hTeam"]["leaders"]["rebounds"]["players"][0]["lastName"],
        hast=allStats["hTeam"]["leaders"]["assists"]["value"],
        hply3=allStats["hTeam"]["leaders"]["assists"]["players"][0]["firstName"] + " " +
              allStats["hTeam"]["leaders"]["assists"]["players"][0]["lastName"]
    )

    body += """
||		
|:-:|		
|&nbsp;|		
|**PLAYER STATS**|

**[](/{vTeamLogo}) {vTeamName}**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
""".format(
        vTeamLogo=vTeamBasicData["triCode"],
        vTeamName=teamDict[vTeamBasicData["triCode"]][0].rsplit(None, 1)[-1].upper()
    )

    # players stats are filled here, only starters have "pos" property (away team)
    for i in range(len(playerStats)):
        stats = playerStats[i]
        if stats["teamId"] == vTeamBasicData["teamId"] and stats["pos"] != "":
            body += "|{pname}^{pos}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                pname=stats["firstName"] + " " + stats["lastName"],
                pos=stats["pos"],
                min=stats["min"],
                fgm=stats["fgm"],
                fga=stats["fga"],
                tpm=stats["tpm"],
                tpa=stats["tpa"],
                ftm=stats["ftm"],
                fta=stats["fta"],
                oreb=stats["offReb"],
                dreb=stats["defReb"],
                treb=stats["totReb"],
                ast=stats["assists"],
                stl=stats["steals"],
                blk=stats["blocks"],
                to=stats["turnovers"],
                pf=stats["pFouls"],
                pm=appendPlusMinus(stats["plusMinus"]),
                pts=stats["points"]
            )
        elif stats["teamId"] == vTeamBasicData["teamId"]:
            body += "|{pname}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                pname=stats["firstName"] + " " + stats["lastName"],
                min=stats["min"],
                fgm=stats["fgm"],
                fga=stats["fga"],
                tpm=stats["tpm"],
                tpa=stats["tpa"],
                ftm=stats["ftm"],
                fta=stats["fta"],
                oreb=stats["offReb"],
                dreb=stats["defReb"],
                treb=stats["totReb"],
                ast=stats["assists"],
                stl=stats["steals"],
                blk=stats["blocks"],
                to=stats["turnovers"],
                pf=stats["pFouls"],
                pm=appendPlusMinus(stats["plusMinus"]),
                pts=stats["points"]
            )
    body += """\n**[](/{hTeamLogo}) {hTeamName}**|**MIN**|**FGM-A**|**3PM-A**|**FTM-A**|**ORB**|**DRB**|**REB**|**AST**|**STL**|**BLK**|**TO**|**PF**|**+/-**|**PTS**|
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
""".format(
        hTeamLogo=hTeamBasicData["triCode"],
        hTeamName=teamDict[hTeamBasicData["triCode"]][0].rsplit(None, 1)[-1].upper()
    )
    # home team players
    for i in range(len(playerStats)):
        stats = playerStats[i]
        if stats["teamId"] != vTeamBasicData["teamId"] and stats["pos"] != "":
            body += "|{pname}^{pos}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                pname=stats["firstName"] + " " + stats["lastName"],
                pos=stats["pos"],
                min=stats["min"],
                fgm=stats["fgm"],
                fga=stats["fga"],
                tpm=stats["tpm"],
                tpa=stats["tpa"],
                ftm=stats["ftm"],
                fta=stats["fta"],
                oreb=stats["offReb"],
                dreb=stats["defReb"],
                treb=stats["totReb"],
                ast=stats["assists"],
                stl=stats["steals"],
                blk=stats["blocks"],
                to=stats["turnovers"],
                pf=stats["pFouls"],
                pm=appendPlusMinus(stats["plusMinus"]),
                pts=stats["points"]
            )
        elif playerStats[i]["teamId"] != vTeamBasicData["teamId"] and playerStats[i]["pos"] == "":
            body += "|{pname}|{min}|{fgm}-{fga}|{tpm}-{tpa}|{ftm}-{fta}|{oreb}|{dreb}|{treb}|{ast}|{stl}|{blk}|{to}|{pf}|{pm}|{pts}|\n".format(
                pname=stats["firstName"] + " " + stats["lastName"],
                min=stats["min"],
                fgm=stats["fgm"],
                fga=stats["fga"],
                tpm=stats["tpm"],
                tpa=stats["tpa"],
                ftm=stats["ftm"],
                fta=stats["fta"],
                oreb=stats["offReb"],
                dreb=stats["defReb"],
                treb=stats["totReb"],
                ast=stats["assists"],
                stl=stats["steals"],
                blk=stats["blocks"],
                to=stats["turnovers"],
                pf=stats["pFouls"],
                pm=appendPlusMinus(stats["plusMinus"]),
                pts=stats["points"]
            )
    # footer
    return body

#game thread fuctions starts from here
def initialGameThreadText(basicGameData, date, teamDict, dateTitle):
    """
    Variable basicGameData have live data
    Variable date is today's date
    Variable teamDict is the variable Dictionary at the top
    Function beforeGamePost setups the body of the thread before game starts
    and return body and title of the post
    """
    try:
        timeEasternRaw = basicGameData["startTimeEastern"]
        timeOnlyEastern = timeEasternRaw[:5]
        if timeOnlyEastern[:2].isdigit():
            timeEasternHour = int(timeOnlyEastern[:2])
            timeMinute = timeOnlyEastern[3:]
        else:
            timeEasternHour = int(timeOnlyEastern[:1])
            timeMinute = timeOnlyEastern[2:]
        timeCentralHourFinal = timeEasternHour - 1
        timeMountainHourFinal = timeCentralHourFinal - 1
        broadcasters = basicGameData['watch']['broadcast']['broadcasters']
        if broadcasters['national']==[]:
            nationalBroadcaster = "-"
        else:
            nationalBroadcaster = broadcasters['national'][0]['shortName']
        if basicGameData['hTeam']['triCode'] == "SAS":
            spursBroadcaster = broadcasters['hTeam'][0]['shortName']
            otherBroadcaster = broadcasters['vTeam'][0]['shortName']
            otherSubreddit = teamDict[basicGameData["vTeam"]["triCode"]][3]
            homeAwaySign = "vs"
            spursWinLossRecord = f"({basicGameData['hTeam']['win']}-{basicGameData['hTeam']['loss']})"
            otherWinLossRecord = f"({basicGameData['vTeam']['win']}-{basicGameData['vTeam']['loss']})"
            otherTeamName = teamDict[basicGameData["vTeam"]["triCode"]][0]
        else:
            spursBroadcaster = broadcasters['vTeam'][0]['shortName']
            otherBroadcaster = broadcasters['hTeam'][0]['shortName']
            otherSubreddit = teamDict[basicGameData["hTeam"]["triCode"]][3]
            homeAwaySign = "@"
            spursWinLossRecord = f"({basicGameData['vTeam']['win']}-{basicGameData['vTeam']['loss']})"
            otherWinLossRecord = f"({basicGameData['hTeam']['win']}-{basicGameData['hTeam']['loss']})"
            otherTeamName = teamDict[basicGameData["hTeam"]["triCode"]][0]
        nbaGameThreadLink =""
        for submission in (reddit.subreddit('nba').search("game thread", sort="new", time_filter="day")):
            if f"GAME THREAD: {teamDict[basicGameData['vTeam']['triCode']][0]}" in submission.title and teamDict[basicGameData['hTeam']['triCode']][0] in submission.title:
                nbaGameThreadLink = submission.url
    

        beforeGameBody = f"""##General Information
    **TIME**     |**BROADCAST**                            |**Location and Subreddit**        |
    :------------|:------------------------------------|:-------------------|
    {timeEasternHour}:{timeMinute} PM Eastern |{spursBroadcaster}|{basicGameData["arena"]["name"]}| 
    {timeCentralHourFinal}:{timeMinute} PM Central |{otherBroadcaster}|{otherSubreddit}|
    {timeMountainHourFinal}:{timeMinute} PM Mountain|{nationalBroadcaster}|r/nba|

-----
[Reddit Stream](https://reddit-stream.com/comments/auto) (You must click this link from the comment page.)

[r/NBA Game Thread]({nbaGameThreadLink})
"""

        title = f"[Game Thread] The San Antonio Spurs {spursWinLossRecord} {homeAwaySign} The {otherTeamName} {otherWinLossRecord} - ({dateTitle})"
        return beforeGameBody, title
    except:
        return "", ""

def createGameThread(dateToday, gameId):
    dateTitle = datetime.utcnow().strftime("%B %d, %Y")
    dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday
                              + "/" + gameId + "_boxscore.json")
    basicGameData = dataBoxScore["basicGameData"]
    bodyPost, title = initialGameThreadText(basicGameData, dateToday, teamDict, dateTitle)
    if bodyPost == "" or title == "":
        sched.add_job(createGameThread, args=[dateToday, gameId], run_date=datetime.utcnow() + timedelta(minutes=1))
    else:
        response = reddit.subreddit(sub).submit(title, selftext=bodyPost, send_replies=False)
        response.mod.distinguish(how="yes")
        response.mod.sticky()
        sched.add_job(updateGameThread, 'date', run_date=datetime.utcnow() + timedelta(minutes=60), max_instances=15,
                      args=[gameId, dateToday, bodyPost], kwargs={'response': response})
        print(gameId + " thread created")


def updateGameThread(gameId, dateToday, bodyPost, response=None):
    dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday + "/" + gameId + "_boxscore.json")
    try:
        response.edit(boxScoreText(dataBoxScore, bodyPost, dateToday, teamDict))
    except Exception:
        traceback.print_exc()
    if checkIfGameIsFinished(gameId, dateToday):
        print(gameId + " game finished")
    else:
        sched.add_job(updateGameThread, 'date', run_date=datetime.utcnow() + timedelta(minutes=1), max_instances=15,
                      args=[gameId, dateToday, bodyPost], kwargs={'response': response})
        print(gameId + " thread edited")


def checkIfGameIsFinished(gameId, dateToday):
    dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday + "/" + gameId + "_boxscore.json")
    basicGameData = dataBoxScore["basicGameData"]
    if ((basicGameData["clock"] == "0.0" or basicGameData["clock"] == "")
            and basicGameData["period"]["current"] >= 4
            and (basicGameData["vTeam"]["score"] != basicGameData["hTeam"]["score"])):
        return True
    else:
        return False


def processGameThread():
    spursSchedule = requestApi("http://data.nba.net/prod/v1/2019/teams/1610612759/schedule.json")
    allSpursGames = spursSchedule["league"]["standard"]
    for i in range(len(allSpursGames)):
        if i < len(allSpursGames)-1:
            if (allSpursGames[i]["vTeam"]["score"] == "" and allSpursGames[i]["hTeam"]["score"] == ""):
                startTime = datetime.strptime(allSpursGames[i]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(minutes=45)
                startTimeNextGame = datetime.strptime(allSpursGames[i+1]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(hours=2)
                sched.add_job(createGameThread, args=[allSpursGames[i]['startDateEastern'], allSpursGames[i]['gameId']], run_date=startTime)
                sched.add_job(processGameThread, run_date=startTimeNextGame)
                break
        else:
            if (allSpursGames[i]["vTeam"]["score"] == "" and allSpursGames[i]["hTeam"]["score"] == ""):
                startTime = datetime.strptime(allSpursGames[i]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(minutes=45)
                sched.add_job(createGameThread, args=[allSpursGames[i]['startDateEastern'], allSpursGames[i]['gameId']], run_date=startTime)
    print("processGameThread() is scheduled to run tomorrow")


def createTitleOfPostGameThread(dateToday, gameId):
    defeatSynonyms = ['defeat', 'beat', 'triumph over', 'blow out', 'level out', 'destroy', 'crush', 'walk all over', 'exterminate', 'slaughter', 'massacre' 'obliterate', 'eviscerate', 'annihilate', 'edge out', 'steal one against', 'hang on to defeat', 'snap']
    dataBoxScore = requestApi("http://data.nba.net/prod/v1/" + dateToday + "/" + gameId + "_boxscore.json")
    basicGameData = dataBoxScore["basicGameData"]
    visitorTeamScore = basicGameData["vTeam"]["score"]
    homeTeamScore = basicGameData["hTeam"]["score"]
    if (basicGameData['hTeam']['triCode'] == "SAS" and homeTeamScore > visitorTeamScore) or (basicGameData['vTeam']['triCode'] == "SAS" and homeTeamScore < visitorTeamScore):
        if (abs(int(visitorTeamScore)-int(homeTeamScore))<3):
            defeatWord = random.choice(defeatSynonyms[14:16])
        elif (abs(int(visitorTeamScore)-int(homeTeamScore))<6):
            defeatWord = random.choice(defeatSynonyms[16:])
        elif (abs(int(visitorTeamScore)-int(homeTeamScore))>20):
            defeatWord = random.choice(defeatSynonyms[3:9])
        elif (abs(int(visitorTeamScore)-int(homeTeamScore))>40):
            defeatWord = random.choice(defeatSynonyms[9:14])
        else:
            defeatWord = random.choice(defeatSynonyms[:3])
    else:
        defeatWord = random.choice(defeatSynonyms[:2])
    print(defeatWord)

    #when game is activated, win-loss fields aren't updated. Check isGameActivated and update win-loss manually.
    if basicGameData["isGameActivated"] == False:
        visitorTeam = teamDict[basicGameData["vTeam"]["triCode"]][0] + " (" + basicGameData["vTeam"]["win"] + "-" + basicGameData["vTeam"]["loss"] + ")"
        homeTeam = teamDict[basicGameData["hTeam"]["triCode"]][0] + " (" + basicGameData["hTeam"]["win"] + "-" + basicGameData["hTeam"]["loss"] + ")"
    elif basicGameData["isGameActivated"] == True and ((int(visitorTeamScore) > int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])>=4):
        visitorTeam = teamDict[basicGameData["vTeam"]["triCode"]][0] + " (" + str(int(basicGameData["vTeam"]["win"])+1) + "-" + basicGameData["vTeam"]["loss"] + ")"
        homeTeam = teamDict[basicGameData["hTeam"]["triCode"]][0] + " (" + basicGameData["hTeam"]["win"] + "-" + str(int(basicGameData["hTeam"]["loss"])+1) + ")"
    elif basicGameData["isGameActivated"] == True and ((int(visitorTeamScore) < int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])>=4):
        visitorTeam = teamDict[basicGameData["vTeam"]["triCode"]][0] + " (" + basicGameData["vTeam"]["win"] + "-" + str(int(basicGameData["vTeam"]["loss"])+1) + ")"
        homeTeam = teamDict[basicGameData["hTeam"]["triCode"]][0] + " (" + str(int(basicGameData["hTeam"]["win"])+1) + "-" + basicGameData["hTeam"]["loss"] + ")"
    print(visitorTeam, homeTeam)

    #title is created here, 
    if (int(visitorTeamScore) > int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])==4:
        title = f"[Post Game Thread] The {visitorTeam} {defeatWord} the {homeTeam}, {visitorTeamScore}-{homeTeamScore}"
    elif (int(visitorTeamScore) > int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])==5:
        title = f"[Post Game Thread] The {visitorTeam} {defeatWord} the {homeTeam} in OT, {visitorTeamScore}-{homeTeamScore}"
    elif (int(visitorTeamScore) > int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])>5:
        title = f"[Post Game Thread] The {visitorTeam} {defeatWord} the {homeTeam} in {len(basicGameData['vTeam']['linescore'])-4}OTs, {visitorTeamScore}-{homeTeamScore}"
    elif (int(visitorTeamScore) < int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])==4:
        title = f"[Post Game Thread] The {homeTeam} {defeatWord} the visiting {visitorTeam}, {homeTeamScore}-{visitorTeamScore}"
    elif (int(visitorTeamScore) < int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])==5:
        title = f"[Post Game Thread] The {homeTeam} {defeatWord} the visiting {visitorTeam} in OT, {homeTeamScore}-{visitorTeamScore}"
    elif (int(visitorTeamScore) < int(homeTeamScore)) and len(basicGameData["vTeam"]["linescore"])>5:
        title = f"[Post Game Thread] The {homeTeam} {defeatWord} the visiting {visitorTeam} in {len(basicGameData['vTeam']['linescore'])-4}OTs, {homeTeamScore}-{visitorTeamScore}"
    print(title)
    return(title)

def createPostGameThread(dateToday, gameId):
    boxScoreData = requestApi("http://data.nba.net/prod/v1/" + dateToday + "/" + gameId + "_boxscore.json")
    body = boxScoreText(boxScoreData, '', dateToday, teamDict)
    title = createTitleOfPostGameThread(dateToday, gameId)
    if body == "" or title == "":
        sched.add_job(createPostGameThread, args=[dateToday, gameId], run_date=datetime.utcnow() + timedelta(minutes=1))
    else:
        response = reddit.subreddit(sub).submit(title, selftext=body, send_replies=False)
        response.mod.distinguish(how="yes")
        response.mod.sticky()
        print(gameId + " Post game thread created")
    return response

def checkGameStatusForPGT(dateToday, gameId):
    if checkIfGameIsFinished(gameId, dateToday):
        sched.add_job(createPostGameThread, 'date', run_date=datetime.utcnow() + timedelta(minutes=1), args=[dateToday, gameId])
    else:
        sched.add_job(checkGameStatusForPGT, 'date', run_date=datetime.utcnow() + timedelta(minutes=1), max_instances=15, args=[dateToday, gameId])
    print("pgt status checked")

def processPostGameThread():
    spursSchedule = requestApi("http://data.nba.net/prod/v1/2019/teams/1610612759/schedule.json")
    allSpursGames = spursSchedule["league"]["standard"]
    for i in range(len(allSpursGames)):
        if i < len(allSpursGames)-1:
            if (allSpursGames[i]["vTeam"]["score"] == "" and allSpursGames[i]["hTeam"]["score"] == ""):
                startTime = datetime.strptime(allSpursGames[i]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') + timedelta(minutes=90)
                startTimeNextGame = datetime.strptime(allSpursGames[i+1]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(hours=2)
                sched.add_job(checkGameStatusForPGT, args=[allSpursGames[i]['startDateEastern'], allSpursGames[i]['gameId']], run_date=startTime)
                sched.add_job(processPostGameThread, run_date=startTimeNextGame)
                break
        else:
            if (allSpursGames[i]["vTeam"]["score"] == "" and allSpursGames[i]["hTeam"]["score"] == ""):
                startTime = datetime.strptime(allSpursGames[i]["startTimeUTC"][:19],'%Y-%m-%dT%H:%M:%S') - timedelta(minutes=45)
                sched.add_job(checkGameStatusForPGT, args=[allSpursGames[i]['startDateEastern'], allSpursGames[i]['gameId']], run_date=startTime)

def get_game_thread_austin(basicGameData, gLeagueTeamDict, dateTitle):
    """
    Variable basicGameData have live data
    Variable teamDict is the variable Dictionary at the top
    Function beforeGamePost setups the body of the thread before game starts
    and return body and title of the post
    """
    try:
        timeEastern = datetime.strptime(basicGameData["etm"],'%Y-%m-%dT%H:%M:%S')
        timeCentral = timeEastern - timedelta(1)
        timeMountain = timeCentral - timedelta(1)
        broadcasters = basicGameData['bd']['b']
        if len(broadcaster) == 1:
            spursBroadcaster = broadcasters[0]["disp"]
            otherBroadcaster = "-"
            nationalBroadcaster = "-"
        elif len(broadcasters) == 2:
            spursBroadcaster = broadcasters[0]["disp"]
            otherBroadcaster = broadcasters[1]["disp"]
            nationalBroadcaster = "-"
        elif len(broadcasters) == 3:
            spursBroadcaster = broadcasters[0]["disp"]
            otherBroadcaster = broadcasters[1]["disp"]
            nationalBroadcaster = broadcasters[2]['disp']
        elif len(broadcaster) == 0:
            spursBroadcaster = "-"
            otherBroadcaster = "-"
            nationalBroadcaster = "-"
        if basicGameData['h']['ta'] == "AUS":
            homeAwaySign = "vs"
            spursWinLossRecord = f"({basicGameData['h']['re']})"
            otherWinLossRecord = f"({basicGameData['v']['re']})"
            otherTeamName = gLeagueTeamDict[basicGameData["v"]["ta"]][0]
        else:
            homeAwaySign = "@"
            spursWinLossRecord = f"({basicGameData['v']['re']})"
            otherWinLossRecord = f"({basicGameData['hTeam']['re']})"
            otherTeamName = gLeagueTeamDict[basicGameData["hTeam"]["triCode"]][0]

        beforeGameBody = f"""##General Information
    **TIME**     |**BROADCAST**                            |**Location and Subreddit**        |
    :------------|:------------------------------------|:-------------------|
    {timeEastern.strftime("%I:%M %p")} Eastern |{spursBroadcaster}|{basicGameData["an"]}| 
    {timeCentral.strftime("%I:%M %p")} Central |{otherBroadcaster}|-|
    {timeMountain.strftime("%I:%M %p")} Mountain|{nationalBroadcaster}|r/nba|

    -----
    [Reddit Stream](https://reddit-stream.com/comments/auto) (You must click this link from the comment page.)
    """

        title = f"[Game Thread] The Austin Spurs {spursWinLossRecord} {homeAwaySign} The {otherTeamName} {otherWinLossRecord} - ({dateTitle})"

        return beforeGameBody, title
    except:
        return "", ""

def create_austin_game_thread(basicGameData):
    gameDate = datetime.strptime(basicGameData["etm"],'%Y-%m-%dT%H:%M:%S')
    dateTitle = gameDate.strftime("%B %d, %Y")
    bodyPost, title = get_game_thread_austin(basicGameData, gLeagueTeamDict, dateTitle)
    if bodyPost == "" or title == "":
        sched.add_job(createGameThread, args=[basicGameData], run_date=datetime.utcnow() + timedelta(minutes=1))
    else:
        response = reddit.subreddit('nbaspurs').submit(title, selftext=bodyPost, send_replies=False)
        print("austin game thread created")


def process_austin_game_thread():
    austinSchedule = requestApi("https://s.data.nba.com/data/10s/v2015/json/mobile_teams/dleague/2019/teams/spurs_schedule.json")
    allAustinGames = austinSchedule["gscd"]["g"]
    for i in range(len(allAustinGames)):
        if i < len(allAustinGames)-1:
            if (allAustinGames[i]["v"]["s"] == "" and allAustinGames[i]["h"]["s"] == ""):
                startTime = datetime.strptime(allAustinGames[i]["etm"],'%Y-%m-%dT%H:%M:%S') + timedelta(hours=4)
                startTimeNextGame = datetime.strptime(allAustinGames[i+1]["etm"],'%Y-%m-%dT%H:%M:%S') + timedelta(hours=3)
                sched.add_job(create_austin_game_thread, args=[allAustinGames[i]], run_date=startTime)
                sched.add_job(process_austin_game_thread, run_date=startTimeNextGame)
                break
        else:
            if (allAustinGames[i]["v"]["s"] == "" and allAustinGames[i]["h"]["s"] == ""):
                startTime = datetime.strptime(allAustinGames[i]["etm"],'%Y-%m-%dT%H:%M:%S') + timedelta(hours=4)
                sched.add_job(create_austin_game_thread, args=[allAustinGames[i]], run_date=startTime)
    print("process_austin_game_thread() is scheduled to run tomorrow")

process_sidebar()
processGameThread()
processPostGameThread()
process_austin_game_thread()
sched.start()
