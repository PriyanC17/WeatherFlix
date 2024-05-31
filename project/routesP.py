import requests
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required

from project import app, db
from project.forms import RegistrationForm, LoginForm, UpdateAccountForm
from project.models import User
from datetime import datetime, timedelta
from project.news import newsapi, get_sources_and_domains
from project.MLmodel import backtest
import folium
import pickle
import pandas as pd

bcrypt = Bcrypt(app)


# Home Page
@app.route("/")
@app.route("/index2")
def home():
    return render_template('index2.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    # In case user has registered no need of register page,
    # so when user clicks register it redirects to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, city=form.city.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # Easy method to send a one-time alert,second argument=category
        flash(f'Your Account has been created! You are now able to log in ', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title="Register", form=form)


def get_weather_data(city, predictions,weather):
    weather_data = {
        'city': city.strip().title(),
        'wind': predictions.loc[city.strip().title(),'prediction_target_wind_mph'][0],
        'temperature': predictions.loc[city.strip().title(),'prediction_target_temperature_celsius'][0],
        'humidity': predictions.loc[city.strip().title(),'prediction_target_humidity'][0],
        'date': datetime.utcnow() + timedelta(hours=5, minutes=30),  # Assuming predictions contain current date
        'visibility': predictions.loc[city.strip().title(),'prediction_target_visibility_km'][0],
        # 'description':predictions.loc[city,'prediction_target_description'][0],
        'feels_like': predictions.loc[city.strip().title(),'prediction_target_feels_like_celsius'][0],
    }
    return weather_data


# def weather_for_5_days(city, predictions,weather):
#     forecast_data = []
#     for prediction in predictions:
#         forecast_data.append({
#             # 'timestamp': prediction['timestamp'],
#             'wind': weather['target_wind_mph'],
#             # 'temperature': prediction.get('target_temperature_celsius'),
#             'humidity': weather['target_humidity'],
#             # 'icon': prediction.get('icon'),
#             'visibility': weather['target_visibility_km'],
#             # 'description': weather['target_condition_text'],
#             'feels_like': weather['target_feels_like_celsius']
#         })
#     return forecast_data

# print(get_weather_data('Surat',predictions,weather))
# print(predictions.columns)
# print(weather.columns)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Checks the credentials entered are correct or not
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))

        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title="Login", form=form)

weather = pd.read_csv("C:\\Users\\BAPS\\PycharmProjects\\WeatherFlix\\venv\\WFlix\\project\\IndianWeatherRepository_2.csv",
                      index_col="location_name")

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

rr = Ridge(alpha=.1)

# Define predictors
predictors = weather.columns[~weather.columns.isin(
    ["target", "region", "country", "timezone", "condition_text", "wind_direction", "moon_phase", "sunrise",
     "sunset", "moonrise", "moonset"])]

# Convert 'last_updated' to numeric
weather['last_updated'] = pd.to_datetime(weather['last_updated'], format='mixed', dayfirst=True)
weather.last_updated = pd.to_numeric(weather.last_updated)


@app.route("/weather_forecast")
@login_required
def weather_forecast():
    if current_user.is_authenticated:
        user_city = current_user.city
        weather_predictions = backtest(weather, rr, predictors, start=3650, step=90)  # Obtain predictions from backtest
        # if (weather_predictions == 0).all().all():
        weather_data = get_weather_data(user_city, weather_predictions,weather)
        # weather_for_5 = weather_for_5_days(user_city, weather_predictions,weather)
        # if weather_data and weather_for_5:
        if weather_data :
            # Get the current time
            current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
            # next_5_days_forecast = weather_for_5[::8]
            # print(next_5_days_forecast)
            return render_template('weather_data.html', weather_data=weather_data)
        else:
            flash('Weather information not available for this city.', 'warning')
            return redirect(url_for('home'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    # flash("You have been Logged out!",'success')
    return redirect(url_for('home'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # if form.picture.data:
        #     picture_file = save_picture(form.picture.data)
        #     Updates the currrent profile picture with picture_file
        #     current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    # This populates the form with old i.e. before updated data
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    # image_file=url_for('static',filename="profile_pics/"+current_user.image_file)
    return render_template('account.html', title='Account', form=form)

@app.route("/maps")
def display_maps():
    API_KEY = '7cb1f7de7481335e10d504a4dc2aa82c'

    m1 = folium.Map(location=[0, 0], zoom_start=2)
    z = 2
    x = 0
    y = 0

    tile_layer = folium.TileLayer(
        f'https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid={API_KEY}',
        attr='OpenWeatherMap')
    tile_layer.add_to(m1)
    map1 = m1._repr_html_()

    m4 = folium.Map(location=[0, 0], zoom_start=2)
    z = 2
    x = 0
    y = 0

    tile_layer = folium.TileLayer(
        f'https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid={API_KEY}',
        attr='OpenWeatherMap')
    tile_layer.add_to(m4)
    map4 = m4._repr_html_()

    m3 = folium.Map(location=[0, 0], zoom_start=2)
    z = 2
    x = 0
    y = 0

    tile_layer = folium.TileLayer(
        f'https://tile.openweathermap.org/map/pressure_new/{z}/{x}/{y}.png?appid={API_KEY}',
        attr='OpenWeatherMap')
    tile_layer.add_to(m3)
    map3 = m3._repr_html_()

    m5 = folium.Map(location=[0, 0], zoom_start=2)
    z = 2
    x = 0
    y = 0

    tile_layer = folium.TileLayer(
        f'https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid={API_KEY}',
        attr='OpenWeatherMap')
    tile_layer.add_to(m5)
    map5 = m5._repr_html_()

    page = request.args.get('page', 1, type=int)
    maps = [map1, map4, map3, map5]
    name = ['Cloud', 'Temperature', 'Pressure', 'Wind']
    per_page = 1
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (len(maps) + per_page - 1) // per_page
    paginated_maps = maps[start:end]
    # Pass the paths of downloaded images to the HTML template
    return render_template('maps.html', maps=paginated_maps, page=page, total_pages=total_pages, name=name)
    # return render_template('maps.html', maps=maps)

@app.route("/news", methods=['GET', 'POST'])
def news():
    if request.method == "POST":
        sources, domains = get_sources_and_domains()
        keyword = request.form["keyword"]
        related_news = newsapi.get_everything(q=keyword,
                                              sources=sources,
                                              domains=domains,
                                              language='en',
                                              sort_by='relevancy')
        no_of_articles = related_news['totalResults']
        if no_of_articles > 100:
            no_of_articles = 100
        all_articles = newsapi.get_everything(q=keyword,
                                              sources=sources,
                                              domains=domains,
                                              language='en',
                                              sort_by='relevancy',
                                              page_size=no_of_articles)['articles']
        return render_template("news.html", all_articles=all_articles,
                               keyword=keyword)
    else:
        top_headlines = newsapi.get_top_headlines(country="in", language="en")
        total_results = top_headlines['totalResults']
        if total_results > 100:
            total_results = 100
        all_headlines = newsapi.get_top_headlines(country="in",
                                                  language="en",
                                                  page_size=total_results)['articles']
    return render_template("news.html")

@app.route("/features")
def features():
    return render_template("Features.html")



