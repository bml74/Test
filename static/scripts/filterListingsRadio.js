function resetFilter() {

    let all_listings = document.querySelectorAll(".listing");

    // First reset all listings' visibility so that they are displayed:
    for (listing of all_listings) {
        listing.style.display = 'block';
    }

    // let radios = radio_div.querySelectorAll(".listing-type-radio");
    // for(var i=0;i<radios.length;i++) {
    //     radios[i].checked = false;
    // }

    return all_listings;
}


function filterListingsByType() {

    all_listings = resetFilter();

    radio_divs = document.querySelectorAll(".listing-type-radio-div");
    for (radio_div of radio_divs) {
        radio = radio_div.querySelector(".listing-type-radio");
        if (radio.checked) {
            label = radio_div.querySelector("label").innerHTML
            for (listing of all_listings) {
                if (!listing.classList.contains(label)) {
                    listing.style.display = 'none';
                }
            }
            break;
        }
    }

}

/*
// FOR MULTIPLE LISTING TYPES SELECTED
function filterListingsByType() {

    let all_listings = document.querySelectorAll(".listing");

    // First reset all listings' visibility so that they are displayed:
    for (listing of all_listings) {
        listing.style.display = 'block';
    }

    console.log(all_listings.length);

    checkbox_divs = document.querySelectorAll(".listing-type-radio-div");
    let categories_checked = [];
    for (checkbox_div of checkbox_divs) {
        checkbox = checkbox_div.querySelector(".listing-type-radio");
        if (checkbox.checked) {
            // console.log(checkbox_div.querySelector("label").innerHTML); 
            categories_checked.push(checkbox_div.querySelector("label").innerHTML); // This guves us an array, or list, containing the labels of all the categories that have been selected. Example: ['Consulting', 'Tutoring']
        }
    }

    console.log(categories_checked);

    
    for (listing of all_listings) {
        let hide = false;
        for (category of categories_checked) {
            if (!listing.classList.contains(category)) { // If the category (the current element in the for loop) is not one of the class names of the listing.
                hide = true;
                break;
            }
        }
        if (hide) { listing.style.display = 'none'; }
    }

}
*/
