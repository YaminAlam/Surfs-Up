import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Setup Database

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

#Create references to Measurement and Station tables

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


#Flask app
app = Flask(__name__)


#Flask Routes


@app.route("/")
def home():
    #list of all routes
    return(
        f"Available Routes:<br/>"
        f"(Note: Most recent available date is 2017-08-23 while the latest is 2010-01-01).<br/>"

        f"/api/v1.0/precipitation<br/>"
        f"- Query dates and temperature from the last year. <br/>"

        f"/api/v1.0/stations<br/>"
        f"- Returns a json list of stations. <br/>"

        f"/api/v1.0/tobs<br/>"
        f"- Returns list of Temperature Observations(tobs) for previous year. <br/>"

        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"- Returns an Average, Max, and Min temperature for given date.<br/>"

        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd/<br/>"
        f"- Returns an Aveage Max, and Min temperature for given period.<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    prcp_measures = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>=query_date).\
        order_by(Measurement.date.desc())

    #Return the JSON representation of your dictionary
    prcp_dict = {}
    for result in prcp_measures:
        prcp_dict[result[0]] = result[1]

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations from the dataset.
    results = session.query(Station.name).all()

    station_list = []
    for result in results:
        station_list.append(result)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temp_obs():
    #query for the dates and temperature observations from a year from the last data point.
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Station.name, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= query_date).\
        all()
    #Return a JSON list of Temperature Observations (tobs) for the previous year.
    tobs_list = []
    for result in results:
        row = {}
        row["Date"] = result[1]
        row["Station"] = result[0]
        row["Temperature"] = int(result[2])
        tobs_list.append(row)

    return jsonify(tobs_list)

@app.route('/api/v1.0/<date>/')
def given_date(date):
    """Return the average temp, max temp, and min temp for the date"""
    results = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date == date).all()

#Create JSON
    data_list = []
    for result in results:
        row = {}
        row['Date'] = result[0]
        row['Average Temperature'] = float(result[1])
        row['Highest Temperature'] = float(result[2])
        row['Lowest Temperature'] = float(result[3])
        data_list.append(row)

    return jsonify(data_list)

@app.route('/api/v1.0/<start_date>/<end_date>/')
def query_dates(start_date, end_date):
    """Return the avg, max, min, temp over a specific time period"""
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    data_list = []
    for result in results:
        row = {}
        row["Start Date"] = start_date
        row["End Date"] = end_date
        row["Average Temperature"] = float(result[0])
        row["Highest Temperature"] = float(result[1])
        row["Lowest Temperature"] = float(result[2])
        data_list.append(row)
    return jsonify(data_list)


if __name__ == '__main__':
    app.run(debug=True)