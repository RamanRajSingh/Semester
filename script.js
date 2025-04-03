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