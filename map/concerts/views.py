from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
import spotipy
import spotipy.oauth2 as oauth2

# Create your views here.

CLIENT_ID = 'd08338fcf59640419f47f75fc0e924c2'
CLIENT_SECRET = '729483f1e7e3408bb8f53d1db65ccadf'
REDIRECT_URI = 'http://127.0.0.1:8000/concerts/map/'
SCOPE = 'user-top-read'
TIME_RANGE = 'long_term'
LIMIT = 50
CACHE_PATH = ".cache-info"

SP_OAUTH = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE, cache_path=CACHE_PATH)

def index(request):
    authorize_url = SP_OAUTH.get_authorize_url()
    return render(request, 'concerts/index.html', {'authorize_url': authorize_url})

def map(request):
    token_info = SP_OAUTH.get_cached_token()

    if not token_info:
        code = request.GET.get('code')
        token_info = SP_OAUTH.get_access_token(code)
    
    token = token_info['access_token']
    top_artists = []
    sp = spotipy.Spotify(auth=token)
    items = sp.current_user_top_artists(time_range=TIME_RANGE, limit=LIMIT)['items']
    for item in items:
        top_artists.append(item['name'])

    sample_addresses = [['Address', 'Artist'],
                        ['Portland, OR, US 1401 North Wheeler Avenue', '<a target="_blank" href="https://google.com">Vince Staples</a>']]

    return render(request, 'concerts/map.html', {'sample_addresses': sample_addresses})