#Import all my dependencies at once
import matplotlib
from matplotlib import style
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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

# Calculate the date 1 year ago from the last data point in the database
newestdate = (session.query(Measurement.date).order_by(Measurement.date.desc()).first())
newestdate = newestdate[0]
year = newestdate.split('-')[0]
monf = newestdate.split('-')[1]
day = newestdate.split('-')[2]
yearold = int(year) - 1
yearago = dt.datetime(yearold, int(monf), int(day))

@app.route("/")
def home():
    return (f"SQLAlchemy Homework - Climate App<br/><br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations => List of stations<br/>"
            f"/api/v1.0/precipitaton => Precipitation data from the last year<br/>"
            f"/api/v1.0/temperature => Temperature data from the last year<br/><br/>"
            f"/api/v1.0/datesearch/XXXX-XX-XX => Temperature data for date given and newer<br/>"
            f"/api/v1.0/datesearch/XXXX-XX-XX/2016-01-30 => Temperature data for dates given and inbetween <br/>"
            )

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.name).all()
    #all_stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    percip = (session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > yearBefore)
            .order_by(Measurement.date).all())
    
    # preciparray = []
    # for row in percip:
    #     precipDict = {result.date: result.prcp, "Station": result.station}
    #     precipData.append(precipDict)

    return jsonify(percip)

@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)

@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)