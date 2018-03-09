from django.shortcuts import render
import spotipy.oauth2 as oauth2
import spotipy

CLIENT_ID = 'd08338fcf59640419f47f75fc0e924c2'
CLIENT_SECRET = '729483f1e7e3408bb8f53d1db65ccadf'
REDIRECT_URI = 'http://127.0.0.1:8000/concerts/form/'
SCOPE = 'user-top-read'
# We use mutable global variables to store data 
# in case the user reloads the page or presses 
# the back button. Such data should really be 
# stored in a user session, but this app is 
# only intended for one user at a time.
FORM = [10, "long_term"]
CODE = ['']
INFO = ['', '']

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
        code = request.POST['code']
        FORM[0] = limit
        FORM[1] = time_range
    else:
        limit = FORM[0]
        time_range = FORM[1]
        code = CODE[0]

    # If the code has changed, this means 
    # that a different user has logged on.
    # In this case, we request a new token 
    # from spotify, and store it in cache 
    # so we don't have to request it again
    # for this user.
    if CODE[0] != code:
        token_info = SP_OAUTH.get_access_token(code)
        token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)
        SP_OAUTH.cache_path = '.cache-{}'.format(sp.me()['id'])
        SP_OAUTH._save_token_info(token_info)
        CODE[0] = code
    else:
        token_info = SP_OAUTH.get_cached_token()
        token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)

    artist_info = []
    items = sp.current_user_top_artists(time_range=time_range, limit=limit)['items']
    
    for item in items:
        image_url = item['images'][0]['url']
        name = item['name']
        artist_info.append((name, image_url))

    return render(request, 'concerts/table.html', {'artist_info': artist_info, 'code': code})

def map(request, ident):
    if request.POST:
        name = request.POST['name']
        image_url = request.POST['image_url']
        INFO[0] = name
        INFO[1] = image_url
    else:
        name = INFO[0]
        image_url = INFO[1]
        
    return render(request, 'concerts/map.html', {'ident': ident, 'name': name, 'image_url': image_url})
