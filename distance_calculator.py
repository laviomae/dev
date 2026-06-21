"""
Carbon inventory distance calculator.
Reads addresses from columns A and B of an Excel/CSV file,
calculates the geodesic distance (km) between each pair,
and writes the result to column C.

Usage:
    pip install geopy openpyxl pandas
    python distance_calculator.py input.xlsx          # writes to input_with_distances.xlsx
    python distance_calculator.py input.xlsx -o out.xlsx
    python distance_calculator.py input.csv           # CSV supported too
"""

import argparse
import time
import sys
from pathlib import Path

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


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


def calculate_distances(input_path: str, output_path: str | None = None) -> None:
    path = Path(input_path)
    if not path.exists():
        sys.exit(f"File not found: {input_path}")

    # Load file
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)

    # Expect at least 2 columns; use first two as address columns
    col_a, col_b = df.columns[0], df.columns[1]
    print(f"Address columns: '{col_a}' (origin) and '{col_b}' (destination)")
    print(f"Rows to process: {len(df)}\n")

    geolocator = Nominatim(user_agent="ghg_inventory_distance_calc")
    coord_cache: dict[str, tuple[float, float] | None] = {}

    distances = []

    for i, row in df.iterrows():
        addr_a = str(row[col_a]).strip()
        addr_b = str(row[col_b]).strip()

        print(f"[{i+1}/{len(df)}] {addr_a}  →  {addr_b}")

        # Geocode with cache to avoid redundant API calls
        if addr_a not in coord_cache:
            coord_cache[addr_a] = geocode_address(geolocator, addr_a)
            time.sleep(1)  # Nominatim rate limit: 1 request/second
        if addr_b not in coord_cache:
            coord_cache[addr_b] = geocode_address(geolocator, addr_b)
            time.sleep(1)

        coords_a = coord_cache[addr_a]
        coords_b = coord_cache[addr_b]

        if coords_a and coords_b:
            dist_km = round(geodesic(coords_a, coords_b).kilometers, 2)
            print(f"  Distance: {dist_km} km")
        else:
            dist_km = None
            if not coords_a:
                print(f"  Could not geocode: '{addr_a}'")
            if not coords_b:
                print(f"  Could not geocode: '{addr_b}'")

        distances.append(dist_km)

    df["Distance_km"] = distances

    # Save output
    if output_path is None:
        output_path = str(path.parent / (path.stem + "_with_distances" + path.suffix))

    if Path(output_path).suffix.lower() == ".csv":
        df.to_csv(output_path, index=False)
    else:
        df.to_excel(output_path, index=False)

    geocoded = sum(1 for d in distances if d is not None)
    failed = len(distances) - geocoded
    print(f"\nDone. {geocoded}/{len(distances)} distances calculated.")
    if failed:
        print(f"  {failed} row(s) could not be geocoded — check addresses and retry.")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate distances between address pairs.")
    parser.add_argument("input", help="Input Excel (.xlsx) or CSV file")
    parser.add_argument("-o", "--output", help="Output file path (optional)")
    args = parser.parse_args()

    calculate_distances(args.input, args.output)
