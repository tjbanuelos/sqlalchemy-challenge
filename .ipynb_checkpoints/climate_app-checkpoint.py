# Import the dependencies.
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return(
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Avaliable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.,/p/"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitaion data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.dat(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation over last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    
    # Close the session
    session.close()

    #Create dictionary with date as key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}

    # Return the results as a Json
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all the stations"""
    results = session.query(Station.station).all()
    
    
    # Close the session
    session.close()

    # Unravel the results and convert to a list
    stations = list(np.ravel(results))

    # Return the results as a Json
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def monthly_temp():
    """Return the tobs for previous year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.dat(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary staion for all tobs from last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    
    # Close the session
    session.close()

    # Unravel the results and convert to a list
    temps = list(np.ravel(results))

    # Return the resulsts as a Json
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX"""

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Calculate TMIN, TAVG, TMAX with start
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
    
        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    # Calculate TMIN, TAVG, TMAX with start and stop 
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    session.close()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()