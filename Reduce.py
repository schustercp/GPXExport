import influxdb_client
import os
import time
import haversine
import datetime
import dateutil
import gpxpy
import gpxpy.gpx

def myFunc(e):
  return e.time

filename = "2024-10-03"

gpx_file = open('/Users/schustercp/workspace/GPXExport/' + filename + '.gpx', 'r')

original_gpx = gpxpy.parse(gpx_file)

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

# removePoints: list[gpxpy.gpx.GPXTrackPoint] = []

letsgo = True

while letsgo:
  letsgo = False
  for y in range(1, len(newPoints)):
    distance = haversine.haversine((newPoints[y-1].latitude, newPoints[y-1].longitude), (newPoints[y].latitude, newPoints[y].longitude))
    if distance > 0.1:
      print("Large Dist jump: ", distance)
      print(" Point Name: ", newPoints[y-1].name)
      print(" Point Name: ", newPoints[y].name)
      #removePoints.append(newPoints[y-1])
      #removePoints.append(newPoints[y])
      #letsgo = True
  #for rmP in removePoints:
  #    newPoints.remove(rmP)

  print("New Points: ", len(newPoints))
  # removePoints.clear()

gpx_segment.points.extend(newPoints)
print('Original Points: ', original_points)
print('Reduced Number: ', new_points)

filename = f"Reduced_" + filename + ".gpx"
with open(filename, 'w') as textfile:
  textfile.write(new_gpx.to_xml())
print('Created GPX: ', filename)