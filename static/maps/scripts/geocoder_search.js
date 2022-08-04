function geocoder_search_engine () {
    map.addControl(
        new MapboxGeocoder({
            accessToken: mapboxgl.accessToken,
            mapboxgl: mapboxgl,
            placeholder: 'Place (ex. Lviv, Ukraine)',
        })
    );
};