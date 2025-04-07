const texts = ["Workforce Attrition Prediction"];

const textContainer = document.querySelector(".head"); // Selects the text container

let lineIndex = 0;
let charIndex = 0;
let isTyping = false; // To prevent multiple clicks from interfering

function typeEffect() {
    if (isTyping) return; // Prevent multiple clicks from overlapping the effect
    isTyping = true; // Lock function while typing effect is running

    lineIndex = 0;
    charIndex = 0;
    textContainer.innerHTML = ""; // Clear previous text

    function typeLine() {
        if (lineIndex < texts.length) {
            if (charIndex === 0) {
                textContainer.innerHTML = ""; // Clear previous line
            }

            if (charIndex < texts[lineIndex].length) {
                textContainer.innerHTML += texts[lineIndex][charIndex];
                charIndex++;
                setTimeout(typeLine, 100); // Typing speed
            } else {
                setTimeout(() => {
                    charIndex = 0;
                    lineIndex++;
                    typeLine();
                }, 1000); // Delay before next line starts
            }
        } else {
            isTyping = false; // Unlock function after all lines are typed
        }
    }

    typeLine(); // Start typing effect
}

// Run typing effect when the page loads
typeEffect();


var clicked = false;
function disableMe() {
    if (document.getElementsByClassName) {
        if (!clicked) {
            document.getElementsByClassName("button").value = "thank you";
            clicked = true;
            return true;
        } else {
            return false;
        }
    } else {
        return true;
    }
}
// This function is for the button toggle and checkbox tick on-click event
function toggleInputs(className) {
    const inputs = document.querySelector(`.input-container.${className}`);
    const currentDisplay = window.getComputedStyle(inputs).display;

    if (currentDisplay === "none") {
        inputs.style.display = "flex"; // Show the inputs
    } else {
        inputs.style.display = "none"; // Hide the inputs
    }
}
// This function is for the predict button 
function ok() {
    const inputs = document.querySelectorAll('.input1');
    const data = {
        employee_number: inputs[0].value,
        employee_age: inputs[1].value,
        gender: inputs[2].value,
        marital_status: inputs[3].value
    };

    fetch('http://localhost:3000/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(res => res.text())
        .then(response => {
            alert(response);
        })
        .catch(err => {
            console.error("Error:", err);
        });
}