import requests

# Example: Get weekly player stats (Sleeper API mock)
def get_player_stats_sleeper(player_id, week=1, season=2025):
    url = f"https://api.sleeper.app/v1/stats/nfl/regular/{season}/{week}"
    response = requests.get(url)
    data = response.json()
    
    # Find stats for the given player_id
    for player in data:
        if player["player_id"] == player_id:
            return player["stats"]
    
    return {}
