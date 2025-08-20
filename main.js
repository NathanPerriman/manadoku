document.addEventListener("DOMContentLoaded", fetchAndRenderGrid);

document.addEventListener("DOMContentLoaded", () => {
    const modalElements = {
        modal: document.getElementById("inputModal"),
        promptText: document.getElementById("promptText"),
        userInput: document.getElementById("userInput"),
        submitButton: document.getElementById("submitButton"),
        closeButton: document.getElementById("closeButton"),
    };

    document.getElementById("rulesButton").addEventListener("click", () => {
        openModal(modalElements, null, null, "rules");
    });

    document.getElementById("newGameButton").addEventListener("click", () => {
        openModal(modalElements, null, null, "newGame");
    });
});

function fetchAndRenderGrid() {
    fetch("https://manadoku.onrender.com/get_strings")
        .then(response => response.json())
        .then(data => {
            console.log("Data received from backend:", data);

            const grid = data.grid;
            const gridContainer = document.getElementById("grid");

            const modalElements = {
                modal: document.getElementById("inputModal"),
                promptText: document.getElementById("promptText"),
                userInput: document.getElementById("userInput"),
                submitButton: document.getElementById("submitButton"),
                closeButton: document.getElementById("closeButton"),
            };

            let currentRow = null;
            let currentCol = null;
            let currentRowObject = null;
            let currentColObject = null;

            for (let row = 0; row < 4; row++) {
                for (let col = 0; col < 4; col++) {

                    //THIS IS WHERE I MAKE A FLIPPABLE CARD
                    const gridItem = document.createElement("div");
                    gridItem.classList.add("grid-item");

                    const cardInner = document.createElement("div");
                    cardInner.classList.add("card-inner");

                    const cardFront = document.createElement("div");
                    cardFront.classList.add("card-front");
                    const frontImg = document.createElement("img");
                    frontImg.src = "cardback-greyscale.png";
                    frontImg.alt = "Card Back";
                    frontImg.style.width = "100%";
                    frontImg.style.height = "100%";
                    frontImg.style.objectFit = "contain";
                    cardFront.appendChild(frontImg);

                    const cardBack = document.createElement("div");
                    cardBack.classList.add("card-back"); //will be filled later

                    cardInner.appendChild(cardFront);
                    cardInner.appendChild(cardBack);
                    gridItem.appendChild(cardInner);

                    const itemIndex = getGridItemIndex(row, col);
                    if (itemIndex !== undefined && grid[itemIndex]) {
                        gridItem.innerText = formatGridItem(grid[itemIndex]);
                    } else {
                        gridItem.classList.add("empty");
                        gridItem.addEventListener("click", () => {
                            currentRow = row;
                            currentCol = col;
                            currentRowObject = grid[row];
                            currentColObject = grid[3 + col];
                            openModal(modalElements, currentRowObject, currentColObject);
                        });
                    }

                    gridContainer.appendChild(gridItem);
                }
            }

            setupModalHandlers(modalElements, () => {
                const userAnswer = modalElements.userInput.value;
                const answerData = {
                    answer: userAnswer,
                    row: currentRow,
                    col: currentCol,
                    rowObject: currentRowObject,
                    colObject: currentColObject
                };
                handleSubmitAnswer(answerData, modalElements);
            });
        })
        .catch(error => {
            console.error("Error fetching grid values:", error);
            document.getElementById("grid").innerHTML = "<p>Error loading grid. Please try again.</p>";
        });
}

function getGridItemIndex(row, col) {
    if (col === 0 && row < 4) return row;
    if (row === 0 && col > 0 && col < 4) return 3 + col;
    return undefined;
}

function formatGridItem(item) {
    if (typeof item === "string") {
        return labelForDifficulty(item);
    } else {
        return `${item.name}: ${item.challenge}`;
    }
}

function labelForDifficulty(value) {
    return {
        "1": "Easy",
        "2": "Medium",
        "3": "Hard"
    }[value] || value;
}

function openModal(modalElements, rowLabel, colLabel, mode = "answer") {
    const { modal, promptText, userInput, submitButton, closeButton } = modalElements;

    modal.classList.remove("hidden");

    // Clear old handlers so they don't stack
    submitButton.replaceWith(submitButton.cloneNode(true));
    closeButton.replaceWith(closeButton.cloneNode(true));

    const newSubmitButton = modal.querySelector("#submitButton");
    const newCloseButton = modal.querySelector("#closeButton");

    if (mode === "answer") {
        const formattedRowLabel = typeof rowLabel === "string"
            ? labelForDifficulty(rowLabel)
            : `${rowLabel.name}: ${rowLabel.challenge}`;

        const formattedColLabel = typeof colLabel === "string"
            ? labelForDifficulty(colLabel)
            : `${colLabel.name}: ${colLabel.challenge}`;

        promptText.innerText = `Row: ${formattedRowLabel}, Column: ${formattedColLabel}`;
        userInput.classList.remove("hidden");
        userInput.value = "";
        newSubmitButton.innerText = "Submit";
        newCloseButton.style.display = "inline-block";

        newSubmitButton.addEventListener("click", () => {
            // TODO: use userInput.value for your answer logic
            modal.classList.add("hidden");
        });
    }
    else if (mode === "rules") {
        promptText.innerText = `Manadoku is a grid guessing game, inspired by sites like Immaculate Grid and Pokedoku, based on Magic: The Gathering.
        The goal is to try to find a card that fits each of the 9 spots in the grid, given the grid's vertical and horizontal clues.
        Clicking on one of the card backs shows the 2 requirements that space needs to meet,
        and gives you a text box to type the name of a card that may fit there.
        For example, if the two clues were "Power: 6" and "Keyword: Trample", you could type "Colossal Dreadmaw" to fit that space.
        Try to fill out all 9 spaces in order to win!`;
        userInput.classList.add("hidden");
        newSubmitButton.innerText = "Close";
        newCloseButton.style.display = "none";

        newSubmitButton.addEventListener("click", () => {
            modal.classList.add("hidden");
        });
    }
    else if (mode === "newGame") {
        promptText.innerText = `Are you sure you want to start a new game? (This will reset your progress)`;
        userInput.classList.add("hidden");
        newSubmitButton.innerText = "Start New Game";
        newCloseButton.style.display = "inline-block";

        newSubmitButton.addEventListener("click", () => {
            // TODO: reset game logic
            modal.classList.add("hidden");
        });
    }

    newCloseButton.addEventListener("click", () => {
        modal.classList.add("hidden");
    });
}


function setupModalHandlers(modalElements, onSubmit) {
    modalElements.closeButton.addEventListener("click", () => {
        modalElements.modal.classList.add("hidden");
        modalElements.userInput.value = "";
    });

    modalElements.submitButton.addEventListener("click", () => {
        onSubmit();
        modalElements.modal.classList.add("hidden");
        modalElements.userInput.value = "";
    });

    modalElements.userInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            modalElements.submitButton.click();
        }
    });
}

function handleSubmitAnswer(data, modalElements) {
    fetch("https://manadoku.onrender.com/submit_answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            console.log("Submission result:", result);
            updateGridOnSubmission(result);
        })
        .catch(error => console.error("Error submitting answer:", error));
}

function updateGridOnSubmission(result) {
    const gridItems = document.querySelectorAll(".grid-item");
    const targetBox = gridItems[result.row * 4 + result.col];

    if (result.success) {
        targetBox.classList.remove("incorrect");
        targetBox.classList.add("completed");
        const img = document.createElement("img");
        img.src = result.img;
        img.alt = "Card Image";
        img.style.maxWidth = "100%";
        img.style.maxHeight = "100%";
        img.style.objectFit = "contain";
        img.style.display = "block";

        const cardBack = targetBox.querySelector(".card-back");
        cardBack.innerHTML = "";
        cardBack.appendChild(img);

        targetBox.classList.add("flipped");
    } else {
        targetBox.classList.add("incorrect");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("rulesButton").addEventListener("click", () => {
        openModal(modalElements, null, null, "rules");
    });

    document.getElementById("newGameButton").addEventListener("click", () => {
        openModal(modalElements, null, null, "newGame");
    });
});
