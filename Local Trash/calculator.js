const buttonvalues = [
    "AC", "+/-", "%", "/",
    "7", "8", "9", "x",
    "4", "5", "6", "-",
    "1", "2", "3", "+",
    "0", ".", "="
];
const rightSymbols = ["/", "x", "-", "+", "="];
const topSymbols = ["AC", "+/-", "%"];

let A = 0;
let operator = null;
let B = null;

const display = document.getElementById("display");

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

    button.addEventListener("click", function() {
        if (rightSymbols.includes(value)) {
            if (value == "AC") {

            }
            else if (value == "+/-") {
                display.value = Number(display.value) * -1;
            }
            else if (value == "%") {
                display.value = Number(display.value)/100;
                console.log("here");
            }
        }
        else if (topSymbols.includes(value)) {

        }
        else {
            if (value == ".") {
                if(display.value != "" && !display.value.includes(value)) {
                    display.value += value;
                }
            }
            else if (display.value == "0") {
                display.value = value;
            }
            else {
            display.value += value;
            }
        }
    });

    //add button to calculator
    document.getElementById("buttons").appendChild(button);
}