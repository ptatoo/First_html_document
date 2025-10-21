const buttonvalues = [
    "AC", "+/-", "%", "/",
    "7", "8", "9", "x",
    "4", "5", "6", "-",
    "0", ".", "="
];
const rightSymbols = ["/", "x", "-", "+", "="];
const topSymbols = ["AC", "+/-", "%"];

for (let i = 0; i < buttonvalues.length; i++) {
    //create button
    let value = buttonvalues[i];
    let button = document.createElement("Button");
    button.innerText = value;

    //styling button colors
    if (value == "0") {
        button.style.width = "180px";
        button.style.gridColumn = "span 2";
    }
    if (rightSymbols.includes(value)) {
        button.style.backgroundColor = "#FF9500";
    }
    else if (topSymbols.includes(value)) {
        button.style.backgroundColor = "#D4D4D2";
        button.style.color = "#1c1c1c";
    }

    //add button to calculator
    document.getElementById("buttons").appendChild(button);
}