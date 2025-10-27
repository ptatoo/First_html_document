const search_type = [
    "Subject Area",
    "Class Units",
    "Class ID",
    "Instructor",
    "GE Classes",
    "Writing II Classes",
    "Diversity Classes",
    "College Honors Classes",
    "Fiat Lux Classes",
    "Community-Engaged Learning Classes",
    "USIE Seminars",
    "Law Classes",
    "Online - Classes Not Recorded",
    "Online - Classes Recorded",
    "Online - Asynchronous"
]; 

function toggleSearchContent() {
    let element = document.getElementById("search_button_content")
    if (element.style.display == "none") {
        element.style.display = "block";
    }
    else {
        element.style.display = "none";
    }
}

for (let i = 0; i < search_type.length; i ++) {
    let value = search_type[i];
    let elem = document.createElement("div");
    elem.innerText = value;
    elem.classList.add('search_button_content_item');
    elem.addEventListener("click", function() {
        document.getElementById("search_bar").placeholder = value;
        document.getElementById("search_button_text").textContent = value;
        toggleSearchContent();
    });
    document.getElementById("search_button_content").appendChild(elem);
}

document.getElementById("search_button_content").style.display = "none";


document.body.addEventListener("click", (e) => {
    if (e.target.id == "search_button" || e.target.id == "search_button_text") {
        toggleSearchContent();
    }
});