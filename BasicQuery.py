import influxdb_client
import os
import time
import haversine
import datetime
import dateutil
import gpxpy
import gpxpy.gpx

#url = "http://192.168.0.106:8086"
#token = "3lljy_xWQiw6f7bHrOmdY_Cbm2d9lKyZIxJc5TIvrtdnuPgH9yuCWU-UviLQbP1C-jPM9_EtB726dNmFl1Pkdw=="

url = "http://192.168.0.50:8086"
#HeiheiRere.1v8 -- token = "10uZUSzNsU9c31fuQKIZV8gjmZfKOuLvAm25mIulp3UuRlOPi0OBlRQ3sawTMdIu01uAV-ITcsFC5lfkOyUECQ=="
#HeiheiRere Readonly Token
token = "umFBOGjBXOA5a7OXifHOmsDOduL8m4qRIzltjaqUgib2jysszASWIPea79P2ywt_th39g1zBSLJEpCNuXVVsCg=="
org = "HeiheiRere"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, timeout=60000)

query_api = client.query_api()

# query = """from(bucket: "HeiheiRere") 
#             |> range(start: -1d) 
#             |> filter(fn: (r) => r._measurement == "navigation.gnss.satellites")"""

# print(f'Query: \n {query}')

# tables = query_api.query(query=query, org=org)

# print("N Tables: ", len(tables))
# for table in tables:
#   print("N Records: ", len(table.records))
#   print(table.records[-1])
#  for record in table.records:
#    print(record)

#***********************************************************************
query = """
import "timezone"
import "strings"
option location = timezone.location(name:"America/New_York")
from(bucket: "HeiheiRere") 
            |> range(start: today()) 
            |> filter(fn: (r) => r._measurement == "environment.moon.times.rise")
            |> last()
            |> map(fn: (r) => ({r with _value: strings.trim(v: r._value, cutset: "\\\"")}))
            |> toTime()
            |> drop(columns: ["_time", "tag"])"""

# query = """from(bucket: "HeiheiRere") 
#             |> range(start: -1d) 
#             |> filter(fn: (r) => r.source == "signalk-barometer-trend")"""

print(f'Query: \n {query}')

tables = query_api.query(query=query, org=org)

print("N Tables: ", len(tables))
for table in tables:
  print("N Records: ", len(table.records))
  print(table.records[-1])
  # for record in table.records:
  #   print(record)

client.close()