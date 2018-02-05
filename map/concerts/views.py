from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
import spotipy
import spotipy.oauth2 as oauth2
import bs4
import urllib.request as url
import json
import dateutil.parser

# Create your views here.

CLIENT_ID = 'd08338fcf59640419f47f75fc0e924c2'
CLIENT_SECRET = '729483f1e7e3408bb8f53d1db65ccadf'
REDIRECT_URI = 'http://127.0.0.1:8000/concerts/table/'
SCOPE = 'user-top-read'
TIME_RANGE = 'long_term'
LIMIT = 20
CACHE_PATH = ".cache-info"

SP_OAUTH = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE, cache_path=CACHE_PATH)

def index(request):
    
    authorize_url = SP_OAUTH.get_authorize_url()
    return render(request, 'concerts/index.html', {'authorize_url': authorize_url})

def table(request):

    token_info = SP_OAUTH.get_cached_token()

    if not token_info:
        code = request.GET.get('code')
        token_info = SP_OAUTH.get_access_token(code)

    token = token_info['access_token']
    top_artists = []
    sp = spotipy.Spotify(auth=token)
    items = sp.current_user_top_artists(time_range=TIME_RANGE, limit=LIMIT)['items']
    for item in items:
        artist = item['name']
        top_artists.append((artist, get_identifier(artist)))

    return render(request, 'concerts/table.html', {'top_artists': top_artists})

def map(request, identifier):

    data = get_info(identifier)

    return render(request, 'concerts/map.html', {'data': data})

def suffix(d):
    #https://stackoverflow.com/questions/5891555/display-the-date-like-may-5th-using-pythons-strftime
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def get_identifier(artist):
    '''
    Given an artists name, returns a list of lists, each containing the 
    latitude and longitude of the venue where the artist is performing
    and a html tag containg the ticket information and time of the show.
    
    Inputs: 
        artist (str): the name of the artist
    
    Returns: list of lists
    '''
    response = url.urlopen('http://api.songkick.com/api/3.0/search/artists.json?apikey=cXZIiAYhAxu4hSUU&query={}'
                           .format(url.quote(artist.replace(' ', '_'))))
    html = response.read()
    results = json.loads(html)['resultsPage']['results']
    if results:
        artist = results['artist'][0]
        if artist['onTourUntil']:
            return artist['id']
        else:
            return None
    return None

def get_info(identifier):
    response = url.urlopen('http://api.songkick.com/api/3.0/artists/{}/calendar.json?apikey=cXZIiAYhAxu4hSUU'
                           .format(identifier))
    html = response.read()
    events = json.loads(html)['resultsPage']['results']['event']
    data = [['Lat', 'Long', 'Link']]
    for event in events:
        lat = event['location']['lat']
        lng = event['location']['lng']
        uri = event['uri']
        ISO_8601 = event['start']['datetime']
        if ISO_8601:
            datetime = dateutil.parser.parse(ISO_8601)
            time = datetime.strftime('%A %B %-d{} at %-I:%M %p'.format(suffix(datetime.day)))
        else:
            date = event['start']['date']
            datetime = dateutil.parser.parse(date)
            time = datetime.strftime('%A %B %-d{}'.format(suffix(datetime.day)))
        data.append([lat, lng, "<a target=_blank href='{}'>{}</a>".format(uri, time)])
    return data
    return []