from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
import spotipy
import spotipy.oauth2 as oauth2
import bs4
import urllib.request as url

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

    data = get_data('bruno mars')

    return render(request, 'concerts/map.html', {'data': data})

def get_data(artist):
    '''
    Given an artists name, returns a list of lists, each containing the address of the venue where the artist is performing
    and a html tag containg the ticket information and time of the show.

    Inputs: 
        artist (str): the name of the artist

    Returns: list of lists 
    '''

    response_1 = url.urlopen('https://www.songkick.com/search?utf8=%E2%9C%93&type=initial&query={}'.format(url.quote(artist)))
    html_1 = response_1.read()
    soup_1 = bs4.BeautifulSoup(html_1, 'html.parser')

    is_artist = soup_1.find('li', class_='artist')

    if is_artist:

        artist_url = 'https://www.songkick.com' + is_artist.find('a', class_='thumb')['href']

        response_2 = url.urlopen(artist_url)
        html_2 = response_2.read()
        soup_2 = bs4.BeautifulSoup(html_2, 'html.parser')

        on_tour = soup_2.find('li', class_='ontour').get_text()

        if on_tour == 'On tour: yes':

            concerts_url = artist_url + '/calendar'

            response_3 = url.urlopen(concerts_url)
            html_3 = response_3.read()
            soup_3 = bs4.BeautifulSoup(html_3, 'html.parser')

            times = [tag.get_text(strip=True) for tag in soup_3.find_all('li', class_="with-date")]
            tickets = ['https://www.songkick.com' + tag.parent['href'] for tag in soup_3.find_all('span', class_='button buy-tickets')]
            addresses = [' '.join(tag.next_sibling.next_sibling.stripped_strings) for tag in soup_3.find_all('span', class_="venue-name")]

            return [[address, "<a target=_blank href='{}'>{}</a>".format(ticket, time)] for address, ticket, time in zip(addresses, tickets, times)]

    return []