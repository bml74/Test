function getDayFilter(day) {
    switch (day) {
        case 'all':
            filterDay = ['!=', ['string', ['get', 'day']], 'placeholder'];
            break;
        case 'weekday':
            filterDay = ['match', ['get', 'day'], ['Sat', 'Sun'], false, true];
            break;
        case 'weekend':
            filterDay = ['match', ['get', 'day'], ['Sat', 'Sun'], true, false];
            break;
        case 'Mon':
        case 'Tue':
        case 'Wed':
        case 'Thu':
        case 'Fri':
        case 'Sat':
        case 'Sun':
            filterDay = ['match', ['get', 'day'], [day], true, false];
            break;
        default:
            filterDay = ['!=', ['string', ['get', 'day']], 'placeholder'];
    }
    return filterDay;
}
