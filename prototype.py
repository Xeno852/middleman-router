import openrouteservice
import shapely.geometry

# Set up OpenRouteService with your API key
client = openrouteservice.Client(key="your_ors_api_key_here")

# Define the coordinates of your nodes [(lon1, lat1), (lon2, lat2), ...]
nodes = [
    (-79.3871, 43.6426),  # Example coordinates, replace with yours
    (-79.3972, 43.6536),
    (-79.3802, 43.6503)
]

# Radius increment (in meters) for isochrones
radius_increment = 500

# Maximum radius (in meters) you want to search for intersections
max_radius = 10000

# List to store isochrones
isochrones = []

# Generate isochrones
for node in nodes:
    for radius in range(radius_increment, max_radius + 1, radius_increment):
        isochrone = client.isochrones(
            locations=[node],
            profile='foot-walking',  # or 'driving-car', depending on your use case
            range=[radius],
            attributes=['total_pop']
        )
        isochrone_geom = shapely.geometry.shape(isochrone['features'][0]['geometry'])
        isochrones.append(isochrone_geom)

        # Check if there's an intersection with all other isochrones
        intersection = isochrone_geom
        for other_isochrone in isochrones[:-1]:
            intersection = intersection.intersection(other_isochrone)
            if intersection.is_empty:
                break
        
        # If an intersection is found with all isochrones, this is the intersection area
        if not intersection.is_empty:
            print(f"Intersection found at radius {radius} meters")
            print(intersection)
            exit()

print("No intersection found within the maximum radius")
