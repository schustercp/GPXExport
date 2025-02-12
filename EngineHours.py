import influxdb_client
import os
import time
import haversine
import datetime
import dateutil
import gpxpy
import gpxpy.gpx
from haversine import haversine

from typing import NamedTuple

class EngineEvent(NamedTuple):
    start: datetime.datetime
    stop: datetime.datetime
    runtime: datetime.timedelta

def getTime(thisdict):
  return thisdict["time"]

#url = "http://192.168.0.106:8086"
#token = "3lljy_xWQiw6f7bHrOmdY_Cbm2d9lKyZIxJc5TIvrtdnuPgH9yuCWU-UviLQbP1C-jPM9_EtB726dNmFl1Pkdw=="

url = "http://192.168.0.50:8086"
#HeiheiRere.1v8 -- token = "10uZUSzNsU9c31fuQKIZV8gjmZfKOuLvAm25mIulp3UuRlOPi0OBlRQ3sawTMdIu01uAV-ITcsFC5lfkOyUECQ=="
#HeiheiRere Readonly Token
token = "umFBOGjBXOA5a7OXifHOmsDOduL8m4qRIzltjaqUgib2jysszASWIPea79P2ywt_th39g1zBSLJEpCNuXVVsCg=="
org = "HeiheiRere"

#token = "10uZUSzNsU9c31fuQKIZV8gjmZfKOuLvAm25mIulp3UuRlOPi0OBlRQ3sawTMdIu01uAV-ITcsFC5lfkOyUECQ=="

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, timeout=60000)

query_api = client.query_api()

startDate = datetime.datetime(2022, 1, 1, 0, 0, 0, 0, tzinfo = datetime.timezone.utc)
stopDate = datetime.datetime(2025, 12, 31, 23, 59, 59, 9999, tzinfo = datetime.timezone.utc)

strStartDate = startDate.strftime('%Y-%m-%dT%H:%M:%SZ')
strStopDate = stopDate.strftime('%Y-%m-%dT%H:%M:%SZ')

#|> range(start: today()) 
#|> drop(columns: ["s2_cell_id"])
# and r.source == "1.115"
# and r._value > 0.0
# query = f"""from(bucket: "HeiheiRere.1v8" ) 
# starboard or port
query = f"""from(bucket: "HeiheiRere") 
            |> range(start: {strStartDate}, stop: {strStopDate})
            |> filter(fn: (r) => r._measurement == "propulsion.port.oilPressure")
            """

print(f'Query: \n {query}')

tables = query_api.query(query=query, org=org)

prevTime: datetime.datetime
engineStart = datetime.datetime.now()
engineStop = datetime.datetime.now()
engineTime = engineStop - engineStart
prevPressure = -1.0
engineRun = False
engineEvents = []

print("N Tables: ", len(tables))
for table in tables:
  print("N Records: ", len(table.records))
  # print(table.records[0])
  # EngineOilPress = table.records[0].get_value()
  # EngineOilPressPSI = EngineOilPress / 6894.76
  # print("Oil Pressure: ", EngineOilPressPSI)
  #for record in table.records:
  #  print(record)

  # records are saved for every second.
  engineRun = False
  for x in range(0, len(table.records)):
    time1 = table.records[x].get_time()
    EngineOilPress = table.records[x].get_value()
    EngineOilPressPSI = EngineOilPress / 6894.76
    if x > 0:
      timeDiff1 = time1 - prevTime
      if timeDiff1.total_seconds() < 0:
        print("Time Went Backwards.")
      if timeDiff1.total_seconds() > 100.0:
        print("Time Jump: ", x, engineRun, time1)
        engineRun = False
      else:
        if engineRun:
          if EngineOilPressPSI < 1.0:
            engineRun = False
            engineStop = time1
            runTime = engineStop - engineStart
            engineTime += runTime
            print("Engine Stop: ", engineStop, "Run Time: ", runTime)
            print("    Engine Stop Pressure: ", EngineOilPressPSI)
            event = EngineEvent(engineStart, engineStop, runTime)
            engineEvents.append(event)
        else:
          if EngineOilPressPSI > 4.0:
            if engineRun == False:
              engineRun = True
              engineStart = time1
              print("Engine Start: ", engineStart, EngineOilPressPSI)
    prevTime = time1
    prevPressure = EngineOilPressPSI


print("")
print("")
print("Engine Hours: ", engineTime.total_seconds() / 3600.0)
print("")
print("")

for t in range(0, len(engineEvents)):
  if t == 0:
    Year = engineEvents[t].start.year
    Month = engineEvents[t].start.month
    MonthRunTime = engineEvents[t].runtime
  else:
    if Year != engineEvents[t].start.year or Month != engineEvents[t].start.month:
      print("Run Time for ", Month, " :: ", Year, " -> ", MonthRunTime.total_seconds() / 3600.0)
      Year = engineEvents[t].start.year
      Month = engineEvents[t].start.month
      MonthRunTime = engineEvents[t].runtime
    else:
      MonthRunTime = MonthRunTime + engineEvents[t].runtime

print("Run Time for ", Month, " :: ", Year, " -> ", MonthRunTime.total_seconds() / 3600.0)

client.close()
