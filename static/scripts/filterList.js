function filterList(input_id, list_id, list_item_class, list_item_title_class) {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById(input_id);
    filter = input.value.toUpperCase();
    ul = document.getElementById(list_id);
    li = ul.querySelectorAll("." + list_item_class);
    let num_results = 0;
    for (i = 0; i < li.length; i++) {
        a = li[i].querySelector("." + list_item_title_class);
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
            num_results += 1;
        } else {
            li[i].style.display = "none";
        }
    }
    document.getElementById("num_results").innerHTML = num_results;
}