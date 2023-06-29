# Backend for isochrone-intersection.html which calculates the intersection of isochrones generated from a set of nodes.
 
from flask import Flask, render_template, request, jsonify
import openrouteservice
import shapely.geometry
import logging
import os
from dotenv import load_dotenv

load_dotenv()
ors_api_key = os.getenv('ORS_API_KEY')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_intersection', methods=['POST'])
def get_intersection():
    nodes = request.json.get('nodes')
    show_isochrones = request.json.get('show_isochrones')
    starting_radius = int(request.json.get('starting_radius', 500))
    radius_increment = int(request.json.get('radius_increment', 500))
    max_distance = int(request.json.get('max_distance', 10000))
    
    client = openrouteservice.Client(key=ors_api_key)
    
    logging.info(f'Received nodes: {nodes}')
    logging.info(f'Show isochrones: {show_isochrones}')
    logging.info(f'Starting Radius: {starting_radius}')
    logging.info(f'Radius Increment: {radius_increment}')
    logging.info(f'Max Distance: {max_distance}')

    radius = starting_radius
    intersection = None

    # Keep trying with an increased radius until an intersection is found or max_distance is reached
    while radius <= max_distance:
        isochrones = []
        # Collect isochrones for all nodes with the current radius
        for node in nodes:
            logging.info(f'Processing node: {node}')
            isochrone = client.isochrones(
                locations=[node],
                profile='foot-walking',
                range=[radius],
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

            # If intersection is found, break the loop
            if not intersection.is_empty:
                break
        
        # Increment radius
        radius += radius_increment
    
    # Return intersection if found
    if intersection and not intersection.is_empty:
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







