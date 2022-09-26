function getLongitudeAndLatitude (e) {
        lngLat = JSON.stringify(e.lngLat.wrap());
        return [e.lngLat.lng, e.lngLat.lat];
};