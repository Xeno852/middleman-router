from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import openrouteservice
import shapely.geometry
import logging


app = Flask(__name__)
CORS(app)  # handle Cross origin resource sharing

logging.basicConfig(level=logging.INFO)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_intersection', methods=['POST'])
def get_intersection():
    data = request.get_json(force=True)
    nodes = request.json.get('nodes')
    radius = request.json.get('radius', 500)  # Default value is 500 meters
    increment = request.json.get('increment', 500)  # Default value is 500 meters
    show_isochrones = request.json.get('show_isochrones', True)
    
    client = openrouteservice.Client(key=ors_api_key)
    isochrones = []

    logging.info(f'Received nodes: {nodes}')
    logging.info(f'Starting Radius: {radius} meters')
    logging.info(f'Radius Increment: {increment} meters')
    logging.info(f'Show isochrones: {show_isochrones}')

    # Collect isochrones for all nodes
    for node in nodes:
        logging.info(f'Processing node: {node}')
        isochrone = client.isochrones(
            locations=[node],
            profile='foot-walking',
            range=[int(radius)],
            attributes=['total_pop']
        )
        isochrone_geom = shapely.geometry.shape(isochrone['features'][0]['geometry'])
        isochrones.append(isochrone_geom)

    # Calculate intersection
    if isochrones:
        intersection = isochrones[0]
        for isochrone in isochrones[1:]:
            intersection = intersection.intersection(isochrone)
            if intersection.is_empty:
                break

        logging.info(f'Intersection geometry: {intersection}')

        if not intersection.is_empty:
            final_isochrones = [shapely.geometry.mapping(iso) for iso in isochrones]
            intersection_geometry = shapely.geometry.mapping(intersection)
            logging.info(f'Returning intersection geometry: {intersection_geometry}')
            logging.info(f'Final isochrones: {final_isochrones}')
            return jsonify({"geometry": intersection_geometry, "final_isochrones": final_isochrones if show_isochrones else None})

    logging.info('No intersection found')
    return jsonify({"geometry": None, "final_isochrones": None})



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)







