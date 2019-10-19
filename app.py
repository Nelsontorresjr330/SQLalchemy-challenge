#Import all my dependencies at once
import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Create an engine for the `hawaii.sqlite` database
engine = create_engine("sqlite:///Homework 10/Resources/hawaii.sqlite")

#Create the base for sqlalchemy
Base = automap_base()
Base.prepare(engine, reflect=True)

#Save the tables into variables
Measure = Base.classes.measurement
Station = Base.classes.station

#Create the session
session = Session(engine)

#Create the app
app = Flask(__name__)

#Calculate the date 1 year ago from the last data point in the database
newestdate = (session.query(Measure.date).order_by(Measure.date.desc()).first())
newestdate = newestdate[0]
year = newestdate.split('-')[0]
monf = newestdate.split('-')[1]
day = newestdate.split('-')[2]
yearold = int(year) - 1
yearago = dt.datetime(yearold, int(monf), int(day))

@app.route("/index")
def index():
    #Displays a homepage menu
    return (f"SQLAlchemy Homework - Climate App<br/><br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations => List of stations<br/>"
            f"/api/v1.0/precipitation => Precipitation data from the last year<br/>"
            f"/api/v1.0/temperature => Temperature data from the last year<br/><br/>"
            f"/api/v1.0/datesearch/XXXX-XX-XX => Temperature data for date given and newer<br/>"
            f"/api/v1.0/datesearch/XXXX-XX-XX/XXXX-XX-XX => Temperature data for dates given and inbetween <br/>"
            )

@app.route("/api/v1.0/stations")
def stations():
    #Queries and prints all the station names
    session = Session(engine)
    stationquery = session.query(Station.name).all()
    return jsonify(stationquery)

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Queries and prints the percipation from the last year
    session = Session(engine)
    percip = (session.query(Measure.date, Measure.prcp).filter(Measure.date >= yearago)
            .order_by(Measure.date).all())
    return jsonify(percip)

@app.route("/api/v1.0/tobs")
def temperature():
    #Queries and prints the temperature from the last year
    session = Session(engine)
    tempquery = (session.query(Measure.date, Measure.tobs).filter(Measure.date >= yearago)
                      .order_by(Measure.date).all())
    return jsonify(tempquery)

@app.route('/api/v1.0/<start>')
def start(start):
    #Queries and prints min, avg, and max after a certain date
    session = Session(engine)
    datequery =  (session.query(Measure.date, func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs))
                .filter(Measure.date >= start).group_by(Measure.date).all())
    return jsonify(datequery)

@app.route('/api/v1.0/<start>/<end>')
def startEnd(start, end):
    #Queries and prints min, avg, and max in between two dates
    session = Session(engine)
    datequery =  (session.query(Measure.date, func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs))
                .filter(Measure.date >= start).filter(Measure.date <= end).group_by(Measure.date).all())
    return jsonify(datequery)

if __name__ == "__main__":
    app.run(debug=True)