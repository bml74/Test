document.getElementById('languages').addEventListener('change', (event) => {
    let language = event.target.value; 
    map.setLayoutProperty('country-label', 'text-field', [
    'get',
    `name_${language}`
    ]);
});
