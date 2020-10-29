# My Stock Dashboard

* You can view the finished app on [Heroku] https://my-stock-dashboard-app.herokuapp.com/
* The layout for my app is built in app.py
* The background and blocking schedulers are in clock.py
* Worker.py does the api pulls and database updating (In the background)

### Libaries, Frameworks, and Other Tools
* To create this dashboard, I used Dash by Plotly.
* To launch it, I used the python web server gunicorn, and used Heroku's free dyno to host it.
* The app works by using a stock api called yfinance, which I use to pull historical stock information.
* For the graph, each time an input is changed, a callback will fire and the app will pull historical pricing data.
* For the market mover tables, I used the AP Scheduler library to create a cron job with a second worker that pulls financial data once a day. From there, the data is organized into % change per stock, and the top 10 and bottom 10 stocks are put on the table.
* Since Dash doesn't allow global variables, I initially used pickle to store my dictionary of dataframes.
* However, I ran into a problem with Heroku.  Since Heroku an ephemeral hard drive, my files won't actually end up saving on the disk.
* Because of this, I ended up using a postgresql database to store my information.  I used the Sqlalchemy library in python to write and read from the database.

### Using Heroku
* To host the app, I used the heroku free plan (pulling my code from github).
* I only used one heroku addon, which was the postgresql addon so that I could store my daily data pulls.
* One bug that I ran into is that after 30 minutes of inactivity, Heroku shuts the app, including all background activity and cron jobs running.  
* This meant that my yfinance pull stopped happening unless the app was constantly running.
* To solve this, I ran an scheduled an interval job to ping the website so that it stays online.
* Since Heroku limits online hours per month, I implemented a periodic downtime for a few hours once a day.
