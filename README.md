# My Stock Dashboard

* You can view the finished app on [Heroku] https://my-stock-dashboard-app.herokuapp.com/
* To create this dashboard, I used Dash by Plotly.  To launch it, I used the python web server gunicorn, and used Heroku's free dyno to host it.
* The app works by using a stock api called yfinance.
* For the graph, each time an input is changed, a callback will fire and the app will pull historical pricing data.
* For the market mover tables, I used the AP Scheduler library to create a cron job with a second worker that pulls financial data once a day. From there, the data is organized into % change per stock, and the top 10 and bottom 10 stocks are put on the table.
* Since Dash doesn't allow global variables, I used pickle to store my dictionary of dataframes.
* One bug that I ran into is that after 30 minutes of inactivity, Heroku shuts the app, including all background activity and cron jobs running.  
* This meant that my yfinance pull stopped happening unless the app was constantly running.
* To solve this, I ran an scheduled an interval job to ping the website so that it stays online.
* Since Heroku limits online hours per month, I implemented a periodic downtime for a few hours once a day.
