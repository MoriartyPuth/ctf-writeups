# Challenge 2: Digital Crumbs

## Category
OSINT / Reconnaissance

## Description
A file called `CoffeeMill.jpg` was provided — an image of a coffee shop storefront. The goal is to identify the location and find a specific number hidden in the "digital crumbs."

## Files
- `CoffeeMill.jpg`

## Tools Used
- Web browser (Google Maps, Google Search)
- Python 3 (for image metadata, optional)

## Reasoning & Walkthrough

### Step 1: Analyze the Image

Opening `CoffeeMill.jpg` reveals a photo of a coffee shop with the sign:

> **"Oakland's Oldest Coffee House"**

The storefront also shows the business name and some additional details. This is the primary clue.

### Step 2: Identify the Business

A quick Google search for `"Oakland's Oldest Coffee House"` leads to:

> **The Coffee Mill**
> 3363 Grand Ave, Oakland, CA 94610

This is a well-known coffee shop in the Lake Merritt / Grand Ave area of Oakland.

### Step 3: Explore the Location

Using Google Maps, we can explore the area around 3363 Grand Ave, Oakland. The challenge name "Digital Crumbs" suggests looking for nearby digital or tech-related clues.

Looking across the street (or nearby) from The Coffee Mill, we find:

> **Domino's Pizza**
> 3360 Grand Ave, Oakland, CA 94610

The address number **3360** is the key piece of information.

### Step 4: Verify

The flag format is `bronco{...}`. The number `3360` fits as a concise answer — typical for beginner OSINT challenges where the flag is a specific detail (address, zip code, phone number, etc.) found through reconnaissance.

### Walkthrough Summary

1. **Read the image**: Identify the business name and tagline from the storefront.
2. **Search online**: Use Google to find the exact business and its address.
3. **Use map exploration**: Look at surrounding businesses and addresses.
4. **Find the "crumb"**: The address number across the street (3360) is the flag content.
5. **Format the flag**: Wrap in `bronco{3360}`.

## Flag

```
bronco{3360}
```

## Key Takeaway
OSINT challenges often start with a single visual clue in an image. Business names, landmarks, street signs, and architectural details can all be used to pinpoint exact locations. Google Maps satellite/street view is your best friend for location-based challenges.
