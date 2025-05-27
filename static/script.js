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


function toggleInputs(className) {
    const inputs = document.querySelector(`.input-container.${className}`);
    const currentDisplay = window.getComputedStyle(inputs).display;
    if (currentDisplay === "none") {
        inputs.style.display = "flex";
        document.querySelector(`.input-container.${className}`).parentNode.classList.remove("autoShow");
    } else {
        inputs.style.display = "none";
    }
}


function ok(event) {
    // Prevent default form action if called from button in a form
    if (event) event.preventDefault();

    const allInputs = document.querySelectorAll("input[type='text']");
    let data = {};

    allInputs.forEach(input => {
        const container = input.closest(".input-container");
        if (container && window.getComputedStyle(container).display !== "none") {
            const key = input.placeholder.trim().replace(/ /g, "_").toLowerCase();
            data[key] = input.value.trim();
        }
    });

    // Send data to Flask route '/index'
    fetch('/index', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (response.ok) {
                alert("Data Submitted Successfully!");
            } else {
                alert("Error submitting data!");
            }
        })
        .catch(error => {
            console.error("Fetch error:", error);
            alert("An error occurred during submission!");
        });
};
function updateCheckedSections() {
    let checked = [];
    document.querySelectorAll('input[name="section"]:checked').forEach(cb => {
        checked.push(cb.value);
    });
    document.getElementById('checkedSections').value = checked.join('_');
}
// Optional: update immediately on page load if needed
window.onload = updateCheckedSections;

// Send data to Flask
fetch('/index', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
}).then(response => {
    if (response.ok) {
        alert("Data Submitted Successfully!");
    } else {
        alert("Error submitting data!");
    }
});

