# Devil's Centroid (OSINT)

## Challenge Description
Rumors speak of a treasure buried in the center of a specific triangle. Three people have sent me locations where they are, but there's a problem. I think they're all possessed by the devil.

All they gave me 3 different pieces of information:
1. I'm at a place called Devil's Isle
2. I found myself near a haunted sentry box
3. This one just went "Nunca podrán dominarla La buena música no engaña"

The coordinates of the cities themselves on Wikipedia should give me a decent estimate.

**Flag Format:** `bronco{XX(N or S),XX(E or W)}`, Rounded down to the nearest whole number after all of the calculations. Example: `bronco{06N,66E}`

---

## Solution Walkthrough

### Step 1: Geolocation OSINT Analysis
By analyzing the clues pointing to three locations associated with "the devil," we can reconstruct a geographic triangle (known famously as the **Bermuda Triangle** or the *Devil's Triangle*):

1. **"Devil's Isle"**: Historically, early explorers and sailors nicknamed **Bermuda** the *Isle of Devils* due to the dangerous reefs and the haunting calls of native cahow birds.
2. **"haunted sentry box"**: Located at Castillo San Cristóbal in Old **San Juan, Puerto Rico**, *La Garita del Diablo* (The Devil's Sentry Box) is a historic sentry box where soldiers reportedly vanished mysteriously.
3. **"Nunca podrán dominarla La buena música no engaña"**: This is a direct quote from the song *"Miami 666"* by the Panamanian band Señor Loop. The song title and references point to **Miami, Florida**.

### Step 2: Retrieve Wikipedia Coordinates
Using the official Wikipedia coordinate values for each city's center:
* **Hamilton, Bermuda** (Bermuda's capital): `32°17′39″N 64°46′55″W` $\rightarrow$ `32.294167° N, 64.781944° W`
* **San Juan, Puerto Rico**: `18°24′23″N 66°3′50″W` $\rightarrow$ `18.406389° N, 66.063889° W`
* **Miami, Florida**: `25°46′27″N 80°11′37″W` $\rightarrow$ `25.774167° N, 80.193611° W`

### Step 3: Compute the Centroid
The centroid of a triangle on a flat plane is calculated by taking the average of the latitudes and longitudes of the three vertices:
$$\text{Latitude}_{\text{avg}} = \frac{32.294167 + 18.406389 + 25.774167}{3} \approx 25.491574^\circ\text{ N}$$
$$\text{Longitude}_{\text{avg}} = \frac{-64.781944 + -66.063889 + -80.193611}{3} \approx -70.346481^\circ\text{ W}$$

Following the challenge constraints:
* Round down to the nearest whole number (taking the floor of the absolute value):
  * $\lfloor 25.491574 \rfloor = 25\text{ N}$
  * $\lfloor 70.346481 \rfloor = 70\text{ W}$

This results in: `25N` and `70W`.

---

## Flag
`bronco{25N,70W}`

---

## Solver Code
The calculations can be verified programmatically using the provided script [`solve.py`](solve.py):

```python
import math

def dms_to_dd(d, m, s, direction):
    dd = d + m/60.0 + s/3600.0
    if direction in ['S', 'W']:
        dd = -dd
    return dd

def main():
    hamilton = {
        'lat': dms_to_dd(32, 17, 39, 'N'),
        'lon': dms_to_dd(64, 46, 55, 'W')
    }
    san_juan = {
        'lat': dms_to_dd(18, 24, 23, 'N'),
        'lon': dms_to_dd(66, 3, 50, 'W')
    }
    miami = {
        'lat': dms_to_dd(25, 46, 27, 'N'),
        'lon': dms_to_dd(80, 11, 37, 'W')
    }

    lat_avg = (hamilton['lat'] + san_juan['lat'] + miami['lat']) / 3.0
    lon_avg = (hamilton['lon'] + san_juan['lon'] + miami['lon']) / 3.0

    lat_dir = 'N' if lat_avg >= 0 else 'S'
    lon_dir = 'E' if lon_avg >= 0 else 'W'

    r_lat = int(math.floor(abs(lat_avg)))
    r_lon = int(math.floor(abs(lon_avg)))

    flag = f"bronco{{{r_lat:02d}{lat_dir},{r_lon:02d}{lon_dir}}}"
    print(f"Calculated Centroid: Lat = {lat_avg:.6f}, Lon = {lon_avg:.6f}")
    print(f"Flag: {flag}")

if __name__ == "__main__":
    main()
```
