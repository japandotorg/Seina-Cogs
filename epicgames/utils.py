import requests

FREE_GAMES = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=CA&allowCountries=CA"

def _fetch_free_games():
    response = requests.get(FREE_GAMES).json()
    return response
