function get_coordinates (loc) {
    // Input location name (ex. Paris). Returns coordinates.
    fetch('https://api.mapbox.com/geocoding/v5/mapbox.places/' + loc + '.json?access_token=' + mapboxgl.accessToken)
    .then(response => response.json())
    .then(function (data) {
        console.log(data);
        return data;
    });
};