"""
Carbon inventory distance calculator.
Reads addresses from columns A and B of an Excel/CSV file,
calculates road distance (km) via OSRM and geodesic distance as fallback,
and writes results to columns C and D.

Usage:
    pip install geopy openpyxl pandas requests
    python distance_calculator.py input.xlsx          # writes to input_with_distances.xlsx
    python distance_calculator.py input.xlsx -o out.xlsx
    python distance_calculator.py input.csv           # CSV supported too
    python distance_calculator.py input.xlsx --mode geodesic  # force geodesic only
"""

import argparse
import time
import sys
import requests
from pathlib import Path

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Public OSRM instance (OpenStreetMap data, free, no API key needed)
OSRM_URL = "http://router.project-osrm.org/route/v1/driving/{lon_a},{lat_a};{lon_b},{lat_b}?overview=false"


def geocode_address(geolocator, address: str, retries: int = 3) -> tuple[float, float] | None:
    """Return (lat, lon) for an address, or None if not found."""
    for attempt in range(retries):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
            return None
        except GeocoderTimedOut:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
        except GeocoderServiceError as e:
            print(f"  Geocoder error for '{address}': {e}")
            return None
    return None


def road_distance_osrm(coords_a: tuple, coords_b: tuple, retries: int = 3) -> float | None:
    """Return road distance in km between two (lat, lon) points using OSRM."""
    lat_a, lon_a = coords_a
    lat_b, lon_b = coords_b
    url = OSRM_URL.format(lat_a=lat_a, lon_a=lon_a, lat_b=lat_b, lon_b=lon_b)

    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == "Ok":
                meters = data["routes"][0]["distance"]
                return round(meters / 1000, 2)
            return None
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  OSRM error: {e}")
                return None
    return None


def calculate_distances(input_path: str, output_path: str | None = None, mode: str = "road") -> None:
    path = Path(input_path)
    if not path.exists():
        sys.exit(f"File not found: {input_path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    col_a, col_b = df.columns[0], df.columns[1]
    print(f"Address columns: '{col_a}' (origin) and '{col_b}' (destination)")
    print(f"Mode: {'road (OSRM) + geodesic fallback' if mode == 'road' else 'geodesic only'}")
    print(f"Rows to process: {len(df)}\n")

    geolocator = Nominatim(user_agent="ghg_inventory_distance_calc")
    coord_cache: dict[str, tuple[float, float] | None] = {}

    road_distances = []
    geodesic_distances = []

    for i, row in df.iterrows():
        addr_a = str(row[col_a]).strip()
        addr_b = str(row[col_b]).strip()

        print(f"[{i+1}/{len(df)}] {addr_a}  →  {addr_b}")

        if addr_a not in coord_cache:
            coord_cache[addr_a] = geocode_address(geolocator, addr_a)
            time.sleep(1)  # Nominatim rate limit: 1 req/sec
        if addr_b not in coord_cache:
            coord_cache[addr_b] = geocode_address(geolocator, addr_b)
            time.sleep(1)

        coords_a = coord_cache[addr_a]
        coords_b = coord_cache[addr_b]

        if not coords_a:
            print(f"  Could not geocode: '{addr_a}'")
        if not coords_b:
            print(f"  Could not geocode: '{addr_b}'")

        if coords_a and coords_b:
            geo_km = round(geodesic(coords_a, coords_b).kilometers, 2)
            geodesic_distances.append(geo_km)

            if mode == "road":
                road_km = road_distance_osrm(coords_a, coords_b)
                if road_km:
                    print(f"  Road: {road_km} km  |  Geodesic: {geo_km} km")
                else:
                    print(f"  Road: N/A (OSRM failed, geodesic fallback)  |  Geodesic: {geo_km} km")
                road_distances.append(road_km)
            else:
                print(f"  Geodesic: {geo_km} km")
        else:
            geodesic_distances.append(None)
            if mode == "road":
                road_distances.append(None)

    if mode == "road":
        df["Road_distance_km"] = road_distances
        df["Geodesic_distance_km"] = geodesic_distances
    else:
        df["Geodesic_distance_km"] = geodesic_distances

    if output_path is None:
        output_path = str(path.parent / (path.stem + "_with_distances" + path.suffix))

    if Path(output_path).suffix.lower() == ".csv":
        df.to_csv(output_path, index=False)
    else:
        df.to_excel(output_path, index=False)

    total = len(geodesic_distances)
    ok = sum(1 for d in geodesic_distances if d is not None)
    failed = total - ok
    print(f"\nDone. {ok}/{total} distances calculated.")
    if failed:
        print(f"  {failed} row(s) could not be geocoded — check the addresses.")
    if mode == "road":
        osrm_ok = sum(1 for d in road_distances if d is not None)
        osrm_fail = ok - osrm_ok
        if osrm_fail:
            print(f"  {osrm_fail} road distance(s) fell back to geodesic (OSRM unreachable or no route found).")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate distances between address pairs for GHG inventories.")
    parser.add_argument("input", help="Input Excel (.xlsx) or CSV file")
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    parser.add_argument(
        "--mode",
        choices=["road", "geodesic"],
        default="road",
        help="'road' uses OSRM routing (default), 'geodesic' uses straight-line distance",
    )
    args = parser.parse_args()

    calculate_distances(args.input, args.output, args.mode)
