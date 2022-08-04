function getLongitudeAndLatitude (e) {
    
    // View longitude and latitude in console:
    //map.on('click', (e) => {
        // document.getElementById('info').innerHTML =
        // `e.point` is the x, y coordinates of the `mousemove` event relative to the top-left corner of the map.
        //clickPosition = JSON.stringify(e.point);
        //console.log("Click position: " + clickPosition);
        // `e.lngLat` is the longitude, latitude geographical position of the event.
        lngLat = JSON.stringify(e.lngLat.wrap());

        return [e.lngLat.lng, e.lngLat.lat];

        // get_place(e.lngLat.lng, e.lngLat.lat); // from scripts/reverse_geocoder.js
        
    //});

};