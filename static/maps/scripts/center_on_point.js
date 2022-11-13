map.on('click', 'collisions', (e) => {
    // Center on feature (https://docs.mapbox.com/mapbox-gl-js/example/center-on-feature/)
    map.flyTo({
        center: e.features[0].geometry.coordinates
    });
}); 