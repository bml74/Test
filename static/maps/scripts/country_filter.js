function getCountryFile(country) {
    switch (country) {
        case 'ukraine':
            filterCountry = ['match', ['get', 'primary_country_name'], ['ukraine'], true, false];
            /* map.flyTo({
                center: e.features[0].geometry.coordinates
            }); */
            // map.setZoom(10);
            break;
        case 'belarus':
            filterCountry = ['match', ['get', 'primary_country_name'], ['belarus'], true, false];
            break;
        case 'romania':
            filterCountry = ['match', ['get', 'primary_country_name'], ['romania'], true, false];
            break; 
        case 'country':
        default:
            filterCountry = ['!=', ['string', ['get', 'primary_country_name']], 'placeholder'];
    }
    return filterCountry;
}
