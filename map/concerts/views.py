from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
import spotipy
import spotipy.oauth2 as oauth2
import bs4
import urllib.request as url
import json
import dateutil.parser

CLIENT_ID = 'd08338fcf59640419f47f75fc0e924c2'
CLIENT_SECRET = '729483f1e7e3408bb8f53d1db65ccadf'
REDIRECT_URI = 'http://127.0.0.1:8000/concerts/form/'
SCOPE = 'user-top-read'
FORM = [10, "long_term"]
CODE = ['', '']

SP_OAUTH = oauth2.SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE)

def index(request):
    authorize_url = SP_OAUTH.get_authorize_url()
    return render(request, 'concerts/index.html', {'authorize_url': authorize_url})

def form(request):
    code = request.GET.get('code')
    return render(request, 'concerts/form.html', {'code': code})

def table(request):

    if request.POST:
        limit = request.POST['limit']
        time_range = request.POST['time_range']
        FORM[0] = limit
        FORM[1] = time_range
    else:
        limit = FORM[0]
        time_range = FORM[1]

    CODE[1] = request.GET.get('code')
    if CODE[0] != CODE[1]:
        token_info = SP_OAUTH.get_access_token(CODE[1])
        token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)
        SP_OAUTH.cache_path = '.cache-{}'.format(sp.me()['id'])
        SP_OAUTH._save_token_info(token_info)
        CODE[0] = CODE[1]
    else:
        token_info = SP_OAUTH.get_cached_token()
        token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)

    top_artists = []
    items = sp.current_user_top_artists(time_range=time_range, limit=limit)['items']
    
    for item in items:
        artist = item['name']
        top_artists.append(artist) #((artist, get_identifier(artist)))

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
    html = response.read().decode('utf-8')
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
    html = response.read().decode('utf-8')
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