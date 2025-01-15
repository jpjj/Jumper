import time
from geopy.geocoders import Nominatim
from geopy import distance


def geocode_address(address):
    geolocator = Nominatim(user_agent="Simon_TWTSP")
    geocode = []
    time.sleep(1)
    location = geolocator.geocode(address)
    if location:
        geocode.append((location.latitude, location.longitude))
    else:
        raise ValueError(f"Could not find geocode for address {address}")
    return geocode


def fetch_distance_matrix(geocodes):
    origins = geocodes
    destinations = geocodes
    matrix = [
        [0 for _ in range(len(origins))] for _ in range(len(destinations))
    ]
    for i, origin in enumerate(origins):
        for j, destination in enumerate(destinations):
            if origin != (None, None) and destination != (None, None):
                matrix[i][j] = int(
                    distance.distance(origin, destination).km / 80 * 3600
                )  # 80 km/h, counting the seconds
            else:
                matrix[i][j] = float("inf")
    return matrix
