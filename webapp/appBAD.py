
from flask import Flask, render_template, request, jsonify
import openrouteservice
import shapely.geometry
import logging

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_intersection', methods=['POST'])
def get_intersection():
    nodes = request.json.get('nodes')

    client = openrouteservice.Client(key='ors_api_key')
    # Parameters for isochrones
    radius_increment = 500
    max_radius = 10000
    isochrones = []

    # Generate isochrones
    for node in nodes:
        for radius in range(radius_increment, max_radius + 1, radius_increment):
            isochrone = client.isochrones(
                locations=[node],
                profile='foot-walking',
                range=[radius],
                attributes=['total_pop']
            )
            isochrone_geom = shapely.geometry.shape(isochrone['features'][0]['geometry'])
            isochrones.append(isochrone_geom)

    # Calculate intersection of all isochrones
    intersection = shapely.ops.cascaded_union(isochrones)

    # Return intersection if found
    if not intersection.is_empty:
        intersection_geometry = shapely.geometry.mapping(intersection)
        return jsonify({"geometry": intersection_geometry, "nodes": nodes})

    # If no intersection found, return empty geometry
    return jsonify({"geometry": None, "nodes": nodes})

if __name__ == '__main__':
    app.run(debug=True)
