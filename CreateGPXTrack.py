import influxdb_client
import os
import time
import haversine
import datetime
import dateutil
import gpxpy
import gpxpy.gpx
import haversine
import calendar

def myFunc1(thisdict):
  return thisdict["time"]

def myFunc2(gpxPoint):
  return gpxPoint.time

def CreateGPXFile(gpx_segment, latTable, lonTable):  
  #time Tracking
  prevTime: datetime.datetime
  prevLat = 0.0
  prevLon = 0.0

  pCount = 0
  for x in range(0, len(latTable.records)):
    lat = latTable.records[x].get_value()
    lon = lonTable.records[x].get_value()
    posTime1 = latTable.records[x].get_time()
    posTime2 = lonTable.records[x].get_time()
    distance = haversine.haversine((lat, lon), (prevLat, prevLon), unit=haversine.Unit.KILOMETERS, normalize=True, check=True)

    if abs(lat) > 0.0 and abs(lon) > 0.0:
      gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=lon, time=posTime1))
      #gpx_segment.points[0].time
      pCount += 1

    if posTime1 != posTime2:
      print("Time mismatch.")
      return

    if x > 0:
      timeDiff1 = posTime1 - prevTime
      if timeDiff1.total_seconds() < 0:
        print("Time Went Backwards.")
        print("TD1: ", timeDiff1.total_seconds())
        print("Distance: ", distance)
      if timeDiff1.total_seconds() > 60:
        print("Greater than one min time jump.")

    prevTime = posTime1
    prevLat = lat
    prevLon = lon
  
  # if pCount > 0:
  #   strDate = latTable.records[0].get_time().date().isoformat()
  #   filename = f"{name}_{strDate}.gpx"
  #   with open(filename, 'w') as textfile:
  #     textfile.write(gpx.to_xml())
  #   print('Created GPX: ', filename)
  # else:
  #   print('No valid positions.')
  # return

def ReduceGPXFile(original_gpx, filename):
  pointIndex = 0

  new_gpx = gpxpy.gpx.GPX()
  gpx_track = gpxpy.gpx.GPXTrack()
  new_gpx.tracks.append(gpx_track)

  # Create first segment in our GPX track:
  gpx_segment = gpxpy.gpx.GPXTrackSegment()
  gpx_track.segments.append(gpx_segment)

  original_points = 0
  new_points = 0

  newPoints: list[gpxpy.gpx.GPXTrackPoint] = []

  for track in original_gpx.tracks:
      for segment in track.segments:
          for point in segment.points:
              original_points += 1
              if pointIndex == 0: 
                new_points += 1
                point.name = str(new_points)
                newPoints.append(point)
              pointIndex += 1
              if pointIndex > 9:
                pointIndex = 0

  for y in range(1, len(newPoints)):
    distance = haversine.haversine((newPoints[y-1].latitude, newPoints[y-1].longitude), (newPoints[y].latitude, newPoints[y].longitude), unit=haversine.Unit.KILOMETERS, normalize=True, check=True)
    if distance > 0.1:
      print("Large Dist jump: ", distance)
      print(" Point Name: ", newPoints[y-1].name)
      print(" Point Name: ", newPoints[y].name)

  print("New Points: ", len(newPoints))

  gpx_segment.points.extend(newPoints)
  print('Original Points: ', original_points)
  print('Reduced Number: ', new_points)

  with open(filename, 'w') as textfile:
    textfile.write(new_gpx.to_xml())
  print('Created GPX: ', filename)

#url = "http://192.168.0.106:8086"
#token = "3lljy_xWQiw6f7bHrOmdY_Cbm2d9lKyZIxJc5TIvrtdnuPgH9yuCWU-UviLQbP1C-jPM9_EtB726dNmFl1Pkdw=="

url = "http://192.168.0.50:8086"
#HeiheiRere.1v8 -- token = "10uZUSzNsU9c31fuQKIZV8gjmZfKOuLvAm25mIulp3UuRlOPi0OBlRQ3sawTMdIu01uAV-ITcsFC5lfkOyUECQ=="
#HeiheiRere Readonly Token
token = "umFBOGjBXOA5a7OXifHOmsDOduL8m4qRIzltjaqUgib2jysszASWIPea79P2ywt_th39g1zBSLJEpCNuXVVsCg=="
org = "HeiheiRere"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, timeout=60000)

query_api = client.query_api()

MonthOfInterest = 1
MonthsToFollow = 4
YearOfInterest = 2025

for m in range(MonthOfInterest, MonthOfInterest + MonthsToFollow):
  days_in_month = calendar.monthrange(YearOfInterest, m)[1] + 1
  for d in range(1, days_in_month):
    startDate = datetime.datetime(YearOfInterest, m, d, 0, 0, 0, 0, tzinfo = datetime.timezone.utc)
    stopDate = datetime.datetime(YearOfInterest, m, d, 23, 59, 59, 9999, tzinfo = datetime.timezone.utc)

    strStartDate = startDate.strftime('%Y-%m-%dT%H:%M:%SZ')
    strStopDate = stopDate.strftime('%Y-%m-%dT%H:%M:%SZ')

    GPSSources = ['1.115', '1.0', '1.2']
    for GPSSource in GPSSources:

      #|> range(start: today()) 
      #|> drop(columns: ["s2_cell_id"])
      # and r.source == "1.115"
      query = f"""from(bucket: "HeiheiRere") 
                  |> range(start: {strStartDate}, stop: {strStopDate})
                  |> filter(fn: (r) => r._measurement == "navigation.position" and r.source == "{GPSSource}")
                  """

      print(f'Query: \n {query}')

      tables = query_api.query(query=query, org=org)

      print("N Tables: ", len(tables))
      for table in tables:
        print("N Records: ", len(table.records))
        print(table.records[0])
        #for record in table.records:
        #   print(record)

      #Create GPX File
      gpx = gpxpy.gpx.GPX()
      gpx_track = gpxpy.gpx.GPXTrack()
      gpx.tracks.append(gpx_track)
      # Create first segment in our GPX track:
      gpx_segment = gpxpy.gpx.GPXTrackSegment()
      gpx_track.segments.append(gpx_segment)

      dtList = []

      #find the earliest Date
      for y in range(len(tables) - 1, 0, -2):
        nTime = tables[y].records[0].get_time()
        thisdict = dict(time = nTime, table = tables[y], index = y)
        dtList.append(thisdict)
        print("Added Time to list: ", nTime)

      dtList.sort(key=myFunc1)

      for q in dtList:
        print("nTime: ", q["time"])
        print("index: ", q["index"])
        y = q["index"]
        if tables[y].records[0].get_field() == 'lat' and tables[y-1].records[0].get_field() == 'lon':
          latTable = tables[y]
          lonTable = tables[y-1]
        elif tables[y-1].records[0].get_field() == 'lat' and tables[y].records[0].get_field() == 'lon':
          latTable = tables[y-1]
          lonTable = tables[y]
        CreateGPXFile(gpx_segment, latTable, lonTable)

      gpx_segment.points.sort(key=myFunc2)

      # for y in range(0, len(tables), 2):
      # for y in range(len(tables) - 1, 0, -2):
      #   print("index: ", y)
      #   if tables[y].records[0].get_field() == 'lat' and tables[y-1].records[0].get_field() == 'lon':
      #     latTable = tables[y]
      #     lonTable = tables[y-1]
      #   elif tables[y-1].records[0].get_field() == 'lat' and tables[y].records[0].get_field() == 'lon':
      #     latTable = tables[y-1]
      #     lonTable = tables[y]
      #   CreateGPXFile(y, gpx_segment, latTable, lonTable)

      if len(tables):
        strDate = latTable.records[0].get_time().date().isoformat()
        filename = f"./GPXFiles/HeiheiRere_{GPSSource}_{strDate}_RAW.gpx"
        with open(filename, 'w') as textfile:
          textfile.write(gpx.to_xml())
        print('Created GPX: ', filename)
        filename = f"./GPXFiles/HeiheiRere_{GPSSource}_{strDate}_Reduced.gpx"
        ReduceGPXFile(gpx, filename)

client.close()