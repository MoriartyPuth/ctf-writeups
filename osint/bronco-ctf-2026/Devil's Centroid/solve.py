import math

def dms_to_dd(d, m, s, direction):
    dd = d + m/60.0 + s/3600.0
    if direction in ['S', 'W']:
        dd = -dd
    return dd

def main():
    # Retrieve coordinates from Wikipedia for the three vertices of the Bermuda Triangle
    # 1. Hamilton, Bermuda (historically "Isle of Devils"): 32°17′39″N 64°46′55″W
    hamilton = {
        'lat': dms_to_dd(32, 17, 39, 'N'),
        'lon': dms_to_dd(64, 46, 55, 'W')
    }

    # 2. San Juan, Puerto Rico (home to Castillo San Cristóbal, "La Garita del Diablo"): 18°24′23″N 66°3′50″W
    san_juan = {
        'lat': dms_to_dd(18, 24, 23, 'N'),
        'lon': dms_to_dd(66, 3, 50, 'W')
    }

    # 3. Miami, Florida (from the song "Miami 666" by Señor Loop): 25°46′27″N 80°11′37″W
    miami = {
        'lat': dms_to_dd(25, 46, 27, 'N'),
        'lon': dms_to_dd(80, 11, 37, 'W')
    }

    # Calculate Cartesian average centroid
    lat_avg = (hamilton['lat'] + san_juan['lat'] + miami['lat']) / 3.0
    lon_avg = (hamilton['lon'] + san_juan['lon'] + miami['lon']) / 3.0

    lat_dir = 'N' if lat_avg >= 0 else 'S'
    lon_dir = 'E' if lon_avg >= 0 else 'W'

    # Round down to the nearest whole number (floor of absolute values)
    r_lat = int(math.floor(abs(lat_avg)))
    r_lon = int(math.floor(abs(lon_avg)))

    flag = f"bronco{{{r_lat:02d}{lat_dir},{r_lon:02d}{lon_dir}}}"
    print(f"Calculated Centroid: Lat = {lat_avg:.6f}, Lon = {lon_avg:.6f}")
    print(f"Flag: {flag}")

if __name__ == "__main__":
    main()
