from sqlalchemy import create_engine
from sqlalchemy.orm import session
from sqlalchemy.ext import automap
from sqlalchemy import inspect
from sqlalchemy import func
import numpy as np
from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap.automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs_MostActiveStation<br/>"
        f"/api/v1.0/input start date here<br/>"
        f"/api/v1.0/input start date here/input end date here"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    sess = session.Session(bind=engine)
    last_date_obs = sess.query(func.max(Measurement.date)).first()

    prcp_results = sess.query(Measurement.date, Measurement.prcp).\
                filter((Measurement.date <= last_date_obs[0])
              & (Measurement.date > "2016-08-23")).all()

    sess.close()

    prcp_list = [{"Date": date, "Prcp": prcp} for date, prcp in prcp_results]

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    sess = session.Session(bind=engine)
    results = sess.query(Station.station, Station.name).group_by(Station.station).all()
    sess.close()

    result_list = [{"Station": station, "Name": name} for station, name in results]

    return jsonify(result_list)

@app.route("/api/v1.0/tobs_MostActiveStation")
def tobs():
    sess = session.Session(bind=engine)
    results = sess.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= "2016-08-23").\
                filter(Measurement.station == "USC00519281")
    sess.close()
    
    result_list = [{"Date": date, "Temp Obs": tobs} for date, tobs in results]

    return jsonify(result_list)

@app.route("/api/v1.0/<start>")
def temp_stats_v1(start):
    sess = session.Session(bind=engine)
    results = sess.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start)
    sess.close()

    result_list = [{"Min Temp": tmin, "Max Temp": tmax, "Avg Temp": tavg} for tmin, tavg, tmax in results]
    return jsonify(result_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_v2(start, end):
    sess = session.Session(bind=engine)
    results = sess.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    sess.close()

    result_list = [{"Min Temp": tmin, "Max Temp": tmax, "Avg Temp": tavg} for tmin, tavg, tmax in results]
    return jsonify(result_list)

if __name__ == "__main__":
    app.run(debug=True)




