import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import gpxpy
import gpxpy.gpx
from haversine import haversine
import datetime
import dateutil
import xml
import xml.etree.ElementTree
import math

#url = "http://192.168.0.106:8086"
#token = "3lljy_xWQiw6f7bHrOmdY_Cbm2d9lKyZIxJc5TIvrtdnuPgH9yuCWU-UviLQbP1C-jPM9_EtB726dNmFl1Pkdw=="

url = "http://192.168.0.50:8086"
token = "FxdLWnZjqCDK4W1I0LA6LDYk0kCyoQL3YspavANthG5QdJch-Sgm4hJNnosx3NSbbahGFM6zjzV0vZytH4Egvg=="

org = "HeiheiRere"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, timeout=600000)

bucket="HeiheiRere"

query_api = client.query_api()

# query = """from(bucket: "HeiheiRere") |> range(start: -10d) |> filter(fn: (r) => r._measurement == "navigation.position" and r_field == "lat")"""

#tables = query_api.query(query, org="HeiheiRere")

#for table in tables:
#  for record in table.records:
    #print(record.get_value())
    #print(record.get_time())
#    print(record)

#query = """import "influxdata/influxdb/schema"
#from(bucket: "HeiheiRere")
#  |> range(start: -10d)
#  |> filter(fn: (r) => if r._measurement == "navigation.position" then r._field == "lat" or r._field == "lon" else false)"""
#  |> schema.fieldsAsCols()
#  |> group()
#  |> sort(columns: ["_time"])
#"""

startDate = datetime.datetime(2024, 8, 18, 0, 0, 0, 0, tzinfo = datetime.timezone.utc)
stopDate = datetime.datetime(2024, 8, 18, 23, 59, 59, 9999, tzinfo = datetime.timezone.utc)

strStartDate = startDate.strftime('%Y-%m-%dT%H:%M:%SZ')
strStopDate = stopDate.strftime('%Y-%m-%dT%H:%M:%SZ')
#query = f"""import "influxdata/influxdb/schema"
#from(bucket: "HeiheiRere")
#  |> range(start: {strStartDate}, stop: {strStopDate})
#  |> filter(fn: (r) => r._measurement == "navigation.position" and r.source == "1.115")
#  |> schema.fieldsAsCols()"""
#  |> group()
#  |> sort(columns: ["_time"])
#"""
#'source': '1.115'
#'source': '1.0'
#
#print(f'Query: \n {query}')
#tables = query_api.query(query, org="HeiheiRere")

    #print(record)


for x in range(1, 0, -1):
  # Creating a new file:
  # --------------------
  gpx = gpxpy.gpx.GPX()
  rCount = 0
  localStartDate = startDate  #- datetime.timedelta(days=x)
  localStopDate = stopDate #- datetime.timedelta(days=x)

  strStartDate = localStartDate.strftime('%Y-%m-%dT%H:%M:%SZ')
  strStopDate = localStopDate.strftime('%Y-%m-%dT%H:%M:%SZ')
  query = f"""import "influxdata/influxdb/schema"
  from(bucket: "HeiheiRere")
    |> range(start: {strStartDate}, stop: {strStopDate})
    |> filter(fn: (r) => r._measurement == "navigation.position" and r.source == "1.115")
    |> schema.fieldsAsCols()"""
  print(f'Query: \n {query}')
  tables = query_api.query(query, org="HeiheiRere")

  # Create points:
  for table in tables:
    print("New Table: ", rCount)
    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Coordinates in decimal degrees
    latLast, lonLast = 0.0, 0.0 
    lastTime = datetime.datetime(2017, 6, 21, 18, 25, 30)

    print("Record Count: ", rCount)
    print(table.records[0])

    for record in table.records:
      
      lat = record.values.get("lat")
      lon = record.values.get("lon")
      posTime = record.get_time()
      if latLast > 0.0 and abs(lat) > 0.0:
        distance = haversine((lat, lon), (latLast, lonLast))
        timediff = posTime - lastTime
        timediffMinutes = timediff.total_seconds() / 60
        timediffHours = timediffMinutes / 60
        speed = distance/timediffHours
        if timediffMinutes > 1:
          # Create first segment in our GPX track:
          print("Add new Segment.")
          gpx_segment = gpxpy.gpx.GPXTrackSegment()
          gpx_track.segments.append(gpx_segment)
          
        if abs(distance) > 0.0001:
          gpx_point = gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=lon, time=posTime)
          # Create extension (hr)
          # gpxpy.gpx.GPXExtensionsField
          xmlText = f"""<Heiheirere>
                        <distance>{distance}</distance>
                        <timediff>{timediff.total_seconds()}</timediff>
                        <speed>{speed}</speed>
                        </Heiheirere>"""
          gpx_extension_hr = xml.etree.ElementTree.fromstring(xmlText)
          gpx_point.extensions.append(gpx_extension_hr)
          gpx_segment.points.append(gpx_point)
          rCount += 1
      latLast = lat
      lonLast = lon
      lastTime = posTime

  if rCount > 0:
    strDate = localStartDate.date().isoformat()
    filename = f"HeiheiRere_{strDate}.gpx"
    with open(filename, 'w') as textfile:
      textfile.write(gpx.to_xml())
    print('Created GPX: ', filename)
  
client.close()
