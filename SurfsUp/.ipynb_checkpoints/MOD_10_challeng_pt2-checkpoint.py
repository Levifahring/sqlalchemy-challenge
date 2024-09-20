from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Set up Flask
app = Flask(__name__)

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session (link) from Python to the database
session = Session(engine)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last data point in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation
    precipitation_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary from the row data and append to a list
    precipitation_dict = {date: prcp for date, prcp in precipitation_results}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    station_results = session.query(Station.station).all()

    # Convert the query results to a list
    stations_list = list(np.ravel(station_results))
    
    return jsonify(stations_list)

#@app.route("/api/v1.0/tobs")
#def tobs():
    # Find the most active station
    #most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Query the temperature observations for the most active station for the last year
    #one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()

@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

# Query the temperature observations for the most active station for the last year
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    tobs_list = [{date: tobs} for date, tobs in tobs_results]
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_stats(start, end=None):
    # Select the start and end dates for the temperature stats query
    if end:
        temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    # Convert the query results to a list
    temp_stats_list = list(np.ravel(temp_stats))
    
    return jsonify(temp_stats_list)

if __name__ == '__main__':
    app.run(debug=True)

#Explanation of Routes:
#/api/v1.0/precipitation: Returns a JSON dictionary of precipitation data for the last 12 months.
#/api/v1.0/stations: Returns a JSON list of all weather stations.
#/api/v1.0/tobs: Returns a JSON list of temperature observations for the most active station.
#/api/v1.0/<start> and /api/v1.0/<start>/<end>: Returns the minimum, maximum, and average temperatures for the given date range.