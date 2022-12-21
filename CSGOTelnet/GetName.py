requests_installed = True
try:
	import requests
except:
	requests_installed = False

class PlayerNameResponse:
	def __init__(self, success, status_code, reason, name):
		self.success = success
		self.status_code = status_code
		self.reason = reason
		self.name = name

def get_name(apikey, steamid):
	if not requests_installed:
		return PlayerNameResponse(False, -1, "Couldn't import requests to make HTTP request to Steam API", None)

	params = {
		"key": apikey,
		"steamids": steamid
	}

	response = requests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/", params=params)
	if response.status_code != 200:
		return PlayerNameResponse(False, response.status_code, response.reason, None)

	json = response.json()
	players = json["response"]["players"]
	if len(players) < 1:
		return PlayerNameResponse(False, response.status_code, "Steam API returned no players for given Steam ID", None)

	if "personaname" not in players[0]:
		return PlayerNameResponse(False, response.status_code, "Player doesn't have personaname.", None)

	return PlayerNameResponse(True, response.status_code, response.reason, players[0]["personaname"])
