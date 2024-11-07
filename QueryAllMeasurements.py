import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from haversine import haversine
import datetime
import dateutil

#url = "http://192.168.0.106:8086"
#token = "3lljy_xWQiw6f7bHrOmdY_Cbm2d9lKyZIxJc5TIvrtdnuPgH9yuCWU-UviLQbP1C-jPM9_EtB726dNmFl1Pkdw=="

url = "http://192.168.0.50:8086"
token = "10uZUSzNsU9c31fuQKIZV8gjmZfKOuLvAm25mIulp3UuRlOPi0OBlRQ3sawTMdIu01uAV-ITcsFC5lfkOyUECQ=="

org = "HeiheiRere"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org, timeout=60000)

query_api = client.query_api()

#"""
#Query to all measurements
#"""
query = f"""
import \"influxdata/influxdb/schema\"

schema.measurements(bucket: "HeiheiRere")
"""

print(f'Query: \n {query}')

tables = query_api.query(query=query, org=org)

# Flatten output tables into list of measurements
measurements = [row.values["_value"] for table in tables for row in table]

print('Measurements: ')
print()
print(measurements)

client.close()