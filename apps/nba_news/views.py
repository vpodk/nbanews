from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt, requests, json
from .models import User, UserManager, Comment, Article

apikey = '46bd8a2eb02c485ba51cea891e1f0b1b'
espnurl = 'https://newsapi.org/v2/top-headlines?sources=espn&apiKey=46bd8a2eb02c485ba51cea891e1f0b1b'
bleacherreporturl = 'https://newsapi.org/v2/everything?sources=bleacher-report&apiKey=46bd8a2eb02c485ba51cea891e1f0b1b'
nbaPlayerStats = 'http://data.nba.net/10s/prod/v1/2016/players.json'
keywords = {'Basketball', 'basketball', 'NBA', 'Kobe' 'Curry', 'Jordan', 'LeBron'}

def index(request):
    return render (request, 'nba_news/index.html')

def login(request):
    email = request.POST["email"]
    password = request.POST["password"]
    check = User.objects.login(email, password)
    if check == True:
        user = User.objects.get(email = email)
        request.session["current_user"] = user.id
        return redirect('/nbanews')
    else:
        messages.warning(request, check[0])
        return redirect('/')

def logout(request):
    request.session['current_user'] = 0
    return redirect('/')

def registration(request):
    first_name = request.POST["first_name"]
    last_name = request.POST["last_name"]
    email = request.POST["email"]
    password = request.POST["password"]
    confirm_password = request.POST["confirm_password"]
    check = User.objects.register(first_name, last_name, email, password, confirm_password)
    if check == True:
        print '&' *100
        pwhashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User.objects.create(first_name = first_name, last_name = last_name, email = email, password = pwhashed)
        request.session["current_user"] = user.id
        return redirect("/nbanews")
    else:
        print '*' *100
        for i in range(0, len(check)):
            messages.warning(request, check[i])
        return redirect("/")

def create_comment(request):
    check = Comment.objects.create_comment(request.POST['create_comment'])
    if check:
        Comment.objects.create_comment(create_comment = request.POST['create_comment'])
        return redirect('/')
    else:
        for i in range(0, len(check)):
            messages.warning(request, check[i])
        return redirect('/')

def nbanews(request):
    current_user = User.objects.get(id = request.session['current_user'])
    newapi(espnurl)
    newapi(bleacherreporturl)
    espn = []
    bleacher = []
    for i in Article.objects.raw("SELECT * FROM nba_news_Article"):
        if i.source == 'Bleacher Report':
            bleacher.append(i)
        if i.source == 'ESPN':
            espn.append(i)
    context = {
                'current_user': current_user
                }

    return render(request, 'nba_news/nbanews.html', context)


def newapi(url):
    getapi = requests.get(url).text
    converttojson = json.load(getapi)['articles']
    for i in range(len(converttojson)):
        description = converttojson[i]['description']
        if any(x in converttojson for x in keywords):
            url = converttojson[i]['url']
            url_image = converttojson[i]['urlToImage']
            author = converttojson[i]['author']
            source = converttojson[i]['source']['name']
            title = converttojson[i]['title']
            Article.objects.nesw_artical(url, url_image, author, source, description, title)
        i+=1