# Crowed Trip (OSINT)

## Challenge Description
Our lovely mascot Bucky the Bronco went on a super fun road trip last summer! He started from his pedestal at SCU and drove east, passing through 2 places shown in the photos.

His buddy Craig the crow wants to visit those same places too and then fly back. Can you calculate the total round-trip distance for Craig "as the crow flies"?

Round to the nearest 25 miles.

---

## Solution Walkthrough

### Step 1: Geolocate the Photos
We are given two photos representing stops on Bucky's trip:
1. **Photo 1**: Displays a highway exit sign: `"EXIT 176 64 CABLE CHANNELS Super 8"`. 
   * OSINT search on Exit 176 on Interstate 80 reveals this is in **Winnemucca, Nevada**, where a Super 8 is located directly off the exit on Winnemucca Blvd.
2. **Photo 2**: Displays a highway view entering a downtown skyline with exit signs for `"St. Joseph / Des Moines"` and `"Downtown 1/4 MILE"`.
   * The skyline features the landmark *Kansas City Power and Light Building* and *One Kansas City Place*. 
   * This is I-35 North entering **Kansas City, Missouri**.

### Step 2: Retrieve Wikipedia Coordinates
Using the official coordinates from Wikipedia for each city's center:
* **Santa Clara, California (SCU)**: `37°21′16″N 121°58′09″W` $\rightarrow$ `37.354444° N, 121.969167° W`
* **Winnemucca, Nevada**: `40°58′06″N 117°43′36″W` $\rightarrow$ `40.968333° N, 117.726667° W`
* **Kansas City, Missouri**: `39°05′59″N 94°34′42″W` $\rightarrow$ `39.099722° N, 94.578333° W`

### Step 3: Round-Trip Distance Calculation
The route forms a closed loop: Santa Clara $\rightarrow$ Winnemucca $\rightarrow$ Kansas City $\rightarrow$ Santa Clara. We compute the geodesic distance ("as the crow flies") using both the Haversine formula (spherical Earth model) and the Vincenty formula (ellipsoidal Earth model):

#### Haversine Formula (Spherical Earth, R = 3958.8 miles):
* Santa Clara $\rightarrow$ Winnemucca: $337.56$ miles
* Winnemucca $\rightarrow$ Kansas City: $1227.77$ miles
* Kansas City $\rightarrow$ Santa Clara: $1485.96$ miles
* **Total Distance**: $3051.29$ miles $\rightarrow$ **3050** miles (rounded to the nearest 25)

#### Vincenty Formula (WGS-84 Ellipsoid):
* Santa Clara $\rightarrow$ Winnemucca: $337.64$ miles
* Winnemucca $\rightarrow$ Kansas City: $1230.79$ miles
* Kansas City $\rightarrow$ Santa Clara: $1489.48$ miles
* **Total Distance**: $3057.90$ miles $\rightarrow$ **3050** miles (rounded to the nearest 25)

Both methods agree on the final rounded value.

---

## Flag
`3050` (or `bronco{3050}`)

---

## Solver Code
The calculation is implemented in [`solve.py`](solve.py):

```python
import math

sc_lat = 37.354444
sc_lon = -121.969167

wm_lat = 40.968333
wm_lon = -117.726667

kc_lat = 39.099722
kc_lon = -94.578333

def haversine_distance(lat1, lon1, lat2, lon2, radius_miles=3958.8):
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return radius_miles * c

def main():
    d1 = haversine_distance(sc_lat, sc_lon, wm_lat, wm_lon)
    d2 = haversine_distance(wm_lat, wm_lon, kc_lat, kc_lon)
    d3 = haversine_distance(kc_lat, kc_lon, sc_lat, sc_lon)
    total = d1 + d2 + d3
    print(f"Total distance: {total:.2f} miles")
    print(f"Rounded to nearest 25: {int(round(total / 25.0) * 25)}")

if __name__ == "__main__":
    main()
```
