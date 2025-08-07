from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

# digipin_utils.py

DIGIPIN_GRID = [
    ['F', 'C', '9', '8'],
    ['J', '3', '2', '7'],
    ['K', '4', '5', '6'],
    ['L', 'M', 'P', 'T']
]

BOUNDS = {
    'minLat': 2.5,
    'maxLat': 38.5,
    'minLon': 63.5,
    'maxLon': 99.5
}

def get_digipin(lat, lon):
    if lat < BOUNDS['minLat'] or lat > BOUNDS['maxLat']:
        raise ValueError('Latitude out of range')
    if lon < BOUNDS['minLon'] or lon > BOUNDS['maxLon']:
        raise ValueError('Longitude out of range')

    min_lat = BOUNDS['minLat']
    max_lat = BOUNDS['maxLat']
    min_lon = BOUNDS['minLon']
    max_lon = BOUNDS['maxLon']

    digi_pin = ''

    for level in range(1, 11):
        lat_div = (max_lat - min_lat) / 4
        lon_div = (max_lon - min_lon) / 4

        row = 3 - int((lat - min_lat) / lat_div)
        col = int((lon - min_lon) / lon_div)

        row = max(0, min(row, 3))
        col = max(0, min(col, 3))

        digi_pin += DIGIPIN_GRID[row][col]

        if level == 3 or level == 6:
            digi_pin += '-'

        max_lat = min_lat + lat_div * (4 - row)
        min_lat = min_lat + lat_div * (3 - row)

        min_lon = min_lon + lon_div * col
        max_lon = min_lon + lon_div

    return digi_pin


def get_lat_lng_from_digipin(digi_pin):
    pin = digi_pin.replace('-', '')
    if len(pin) != 10:
        raise ValueError('Invalid DIGIPIN')

    min_lat = BOUNDS['minLat']
    max_lat = BOUNDS['maxLat']
    min_lon = BOUNDS['minLon']
    max_lon = BOUNDS['maxLon']

    for char in pin:
        found = False
        ri = ci = -1

        for r in range(4):
            for c in range(4):
                if DIGIPIN_GRID[r][c] == char:
                    ri, ci = r, c
                    found = True
                    break
            if found:
                break

        if not found:
            raise ValueError('Invalid character in DIGIPIN')

        lat_div = (max_lat - min_lat) / 4
        lon_div = (max_lon - min_lon) / 4

        lat1 = max_lat - lat_div * (ri + 1)
        lat2 = max_lat - lat_div * ri
        lon1 = min_lon + lon_div * ci
        lon2 = min_lon + lon_div * (ci + 1)

        min_lat = lat1
        max_lat = lat2
        min_lon = lon1
        max_lon = lon2

    center_lat = round((min_lat + max_lat) / 2, 6)
    center_lon = round((min_lon + max_lon) / 2, 6)

    return {
        'latitude': center_lat,
        'longitude': center_lon
    }

def encode_digipin_view(request):
    lat = float(request.GET.get("lat"))
    lon = float(request.GET.get("lon"))
    digi_pin = get_digipin(lat, lon)
    return JsonResponse({"digipin": digi_pin})

def decode_digipin_view(request):
    digi_pin = request.GET.get("digipin")
    coords = get_lat_lng_from_digipin(digi_pin)
    return JsonResponse(coords)
