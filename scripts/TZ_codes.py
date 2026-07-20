# Receives a job location string and returns: ET, CT, MT, PT
# or: None if timezone cannot be determined

import re
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

geolocator = Nominatim(user_agent="JR")
tf = TimezoneFinder()

TZ_MAP = {
    "America/New_York": "ET",
    "America/Chicago": "CT",
    "America/Denver": "MT",
    "America/Phoenix": "MT",
    "America/Los_Angeles": "PT",}

def get_timezone(location: str):
    if not location:
        return None

    loc = location.strip()

    # Remote jobs have no specific timezone
    if "remote" in loc.lower():
        return None

    # Remove common job-board noise
    loc = re.sub(r"\(.*?\)", "", loc)  # remove (HQ), (Hybrid), etc.
    loc = loc.replace("United States of America", "")
    loc = loc.replace("United States", "")
    loc = loc.replace("USA", "")
    loc = loc.replace("US", "")

    # Keep first location if multiple locations are listed
    for separator in [";", "|", "•"]:
        if separator in loc:
            loc = loc.split(separator)[0]

    loc = loc.strip()

    if not loc:
        return None

    try:
        result = geolocator.geocode(loc,timeout=10)

        if result is None:
            return None

        timezone = tf.timezone_at(lng=result.longitude,lat=result.latitude)

        if timezone is None:
            return None

        return TZ_MAP.get(timezone)

    except Exception:
        return None