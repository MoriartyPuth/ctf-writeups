import math

# Coordinates from Wikipedia:
# 1. Santa Clara, California (SCU Center/Pedestal):
sc_lat = 37.354444
sc_lon = -121.969167

# 2. Winnemucca, Nevada (First Photo - I-80 Exit 176):
wm_lat = 40.968333
wm_lon = -117.726667

# 3. Kansas City, Missouri (Second Photo - I-35 Downtown Loop entrance):
kc_lat = 39.099722
kc_lon = -94.578333

def haversine_distance(lat1, lon1, lat2, lon2, radius_miles=3958.8):
    """Calculates spherical distance in miles using Haversine formula."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return radius_miles * c

def vincenty_distance(lat1, lon1, lat2, lon2):
    """Calculates ellipsoidal distance in miles using Vincenty formula."""
    # WGS-84 ellipsoid parameters
    a = 6378137.0  # semi-major axis in meters
    f = 1 / 298.257223563  # flattening
    b = (1 - f) * a  # semi-minor axis
    
    L = math.radians(lon2 - lon1)
    U1 = math.atan((1 - f) * math.tan(math.radians(lat1)))
    U2 = math.atan((1 - f) * math.tan(math.radians(lat2)))
    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)
    
    lam = L
    for i in range(100):
        sinLam = math.sin(lam)
        cosLam = math.cos(lam)
        sinSigma = math.sqrt((cosU2 * sinLam) ** 2 + (cosU1 * sinU2 - sinU1 * cosU2 * cosLam) ** 2)
        if sinSigma == 0:
            return 0.0  # coincident points
        cosSigma = sinU1 * sinU2 + cosU1 * cosU2 * cosLam
        sigma = math.atan2(sinSigma, cosSigma)
        sinAlpha = cosU1 * cosU2 * sinLam / sinSigma
        cosSqAlpha = 1 - sinAlpha ** 2
        cos2SigmaM = cosSigma - 2 * sinU1 * sinU2 / cosSqAlpha if cosSqAlpha != 0 else 0
        C = f / 16 * cosSqAlpha * (4 + f * (4 - 3 * cosSqAlpha))
        lamPrev = lam
        lam = L + (1 - C) * f * sinAlpha * (sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM ** 2)))
        if abs(lam - lamPrev) < 1e-12:
            break
            
    uSq = cosSqAlpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
    B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))
    deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma * (-1 + 2 * cos2SigmaM ** 2) - B / 6 * cos2SigmaM * (-3 + 4 * sinSigma ** 2) * (-3 + 4 * cos2SigmaM ** 2)))
    
    s = b * A * (sigma - deltaSigma)
    
    # Convert meters to miles (1 meter = 0.000621371 miles)
    return s * 0.000621371

def main():
    print("--- Haversine Formula (Spherical Earth, R = 3958.8 miles) ---")
    d1_h = haversine_distance(sc_lat, sc_lon, wm_lat, wm_lon)
    d2_h = haversine_distance(wm_lat, wm_lon, kc_lat, kc_lon)
    d3_h = haversine_distance(kc_lat, kc_lon, sc_lat, sc_lon)
    total_h = d1_h + d2_h + d3_h
    print(f"SC to Winnemucca: {d1_h:.2f} miles")
    print(f"Winnemucca to KC: {d2_h:.2f} miles")
    print(f"KC to SC:         {d3_h:.2f} miles")
    print(f"Total Round-Trip: {total_h:.2f} miles")
    print(f"Rounded to nearest 25: {int(round(total_h / 25.0) * 25)} miles")
    
    print("\n--- Vincenty Formula (WGS-84 Ellipsoid) ---")
    d1_v = vincenty_distance(sc_lat, sc_lon, wm_lat, wm_lon)
    d2_v = vincenty_distance(wm_lat, wm_lon, kc_lat, kc_lon)
    d3_v = vincenty_distance(kc_lat, kc_lon, sc_lat, sc_lon)
    total_v = d1_v + d2_v + d3_v
    print(f"SC to Winnemucca: {d1_v:.2f} miles")
    print(f"Winnemucca to KC: {d2_v:.2f} miles")
    print(f"KC to SC:         {d3_v:.2f} miles")
    print(f"Total Round-Trip: {total_v:.2f} miles")
    print(f"Rounded to nearest 25: {int(round(total_v / 25.0) * 25)} miles")

if __name__ == "__main__":
    main()
