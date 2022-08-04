function get_place (lng, lat) {
    // Input location name (ex. Paris). Returns coordinates.
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + lng + "%2C%20" + lat + ".json?access_token=" + mapboxgl.accessToken;
    fetch(url)
    .then(response => response.json())
    .then(function (data) {
        // console.log(typeof data.features);
        // console.log(data.features);
        // console.log(typeof data.features);

        loc_data = new Object();
        for (feature of data.features) {
            loc_data[feature.place_type[0].toUpperCase()] = feature.place_name;
        };
        console.log(loc_data);

        return "HELLO";

        // return loc_data;

    });
};