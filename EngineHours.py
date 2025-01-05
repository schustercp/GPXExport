import influxdb_client
import os
import time
import haversine
import datetime
import dateutil
import gpxpy
import gpxpy.gpx
from haversine import haversine

def getTime(thisdict):
  return thisdict["time"]

#url = "http://192.168.0.106:8086"
#token = "3lljy_xWQiw6f7bHrOmdY_Cbm2d9lKyZIxJc5TIvrtdnuPgH9yuCWU-UviLQbP1C-jPM9_EtB726dNmFl1Pkdw=="

url = "http://192.168.0.50:8086"
#HeiheiRere.1v8 -- token = "10uZUSzNsU9c31fuQKIZV8gjmZfKOuLvAm25mIulp3UuRlOPi0OBlRQ3sawTMdIu01uAV-ITcsFC5lfkOyUECQ=="
#HeiheiRere Readonly Token
token = "umFBOGjBXOA5a7OXifHOmsDOduL8m4qRIzltjaqUgib2jysszASWIPea79P2ywt_th39g1zBSLJEpCNuXVVsCg=="
org = "HeiheiRere"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, timeout=60000)

query_api = client.query_api()

startDate = datetime.datetime(2024, 1, 1, 0, 0, 0, 0, tzinfo = datetime.timezone.utc)
stopDate = datetime.datetime(2024, 12, 31, 23, 59, 59, 9999, tzinfo = datetime.timezone.utc)

strStartDate = startDate.strftime('%Y-%m-%dT%H:%M:%SZ')
strStopDate = stopDate.strftime('%Y-%m-%dT%H:%M:%SZ')

#|> range(start: today()) 
#|> drop(columns: ["s2_cell_id"])
# and r.source == "1.115"
# and r._value > 0.0
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
  for x in range(0, len(table.records)):
    time1 = table.records[x].get_time()
    EngineOilPress = table.records[x].get_value()
    EngineOilPressPSI = EngineOilPress / 6894.76
    if x > 0:
      timeDiff1 = time1 - prevTime
      if timeDiff1.total_seconds() < 0:
        print("Time Went Backwards.")
      if timeDiff1.total_seconds() > 100.0:
        print("Time Jump: ", x, engineRun)
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
        else:
          if EngineOilPressPSI > 4.0:
            if engineRun == False:
              engineRun = True
              engineStart = time1
              print("Engine Start: ", engineStart, EngineOilPressPSI)
    prevTime = time1
    prevPressure = EngineOilPressPSI

  #  double EngineOilPressPSI = EngineOilPress / 6894.76;

# dtList = []
print("Engine Hours: ", engineTime.total_seconds() / 3600.0)

#find the earliest Date
# for y in range(len(tables) - 1, 0, -2):
#   nTime = tables[y].records[0].get_time()
#   thisdict = dict(time = nTime, table = tables[y], index = y)
#   dtList.append(thisdict)
#   print("Added Time to list: ", nTime)

# dtList.sort(key=getTime)

# for q in dtList:
#   print("nTime: ", q["time"])
#   print("index: ", q["index"])
#   y = q["index"]


client.close()
