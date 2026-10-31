
async function renderSolution(result) {
    const container = document.getElementById("solution-steps");
    const finalAnswer = document.getElementById("final-answer");
    await waitForMathJax();
    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, finalAnswer]);
    }
    container.replaceChildren();
    finalAnswer.replaceChildren();
    const groups = {
        setup: [],
        discriminant: [],
        root1: [],
        root2: []
    };
    for (const step of result.steps) {
        if (step.title === "Final answer") {
            continue;
        }
        groups[getStepGroup(step.title)].push(step);
    }
    const groupTitles = {
        setup: "1) Rearrange and identify coefficients",
        discriminant: "2) Discriminant",
        root1: "3) First root",
        root2: "4) Second root"
    };
    for (const groupName of Object.keys(groups)) {
        if (!groups[groupName].length) {
            continue;
        }
        const section = document.createElement("section");
        section.className = "solution-group solution-group--" + groupName;
        const title = document.createElement("h3");
        title.textContent = groupTitles[groupName];
        section.appendChild(title);
        const lines = document.createElement("div");
        lines.className = "solution-lines";
        for (const step of groups[groupName]) {
            const line = document.createElement("div");
            line.className = "solution-line";
            const maths = document.createElement("div");
            maths.textContent = "\\[" + step.latex + "\\]";
            line.appendChild(maths);
            if (step.explanation) {
                const explanation = document.createElement("p");
                explanation.textContent = step.explanation;
                line.appendChild(explanation);
            }
            lines.appendChild(line);
        }
        section.appendChild(lines);
        container.appendChild(section);
    }
    finalAnswer.textContent =
        "\\[" + result.final_answer_latex + "\\]";
    try {
        await window.MathJax.typesetPromise([
            container,
            finalAnswer
        ]);
    } catch (error) {
        container.replaceChildren();
        finalAnswer.replaceChildren();
        throw new Error("Mathematical notation could not be rendered.");
    }
}

function getStepGroup(title) {
    if (title.startsWith("Root 1:")) {
        return "root1";
    }
    if (title.startsWith("Root 2:")) {
        return "root2";
    }
    if (
        title === "Discriminant formula" ||
        title === "Substitute a, b and c" ||
        title === "Square and multiply" ||
        title === "Discriminant result" ||
        title === "Recognise the square" ||
        title === "Take the exact square root" ||
        title === "Interpret the discriminant"
    ) {
        return "discriminant";
    }
    return "setup";
}

function waitForMathJax() {
    return new Promise((resolve, reject) => {
        const deadline = Date.now() + 5000;
        const check = () => {
            if (window.MathJax && window.MathJax.typesetPromise) {
                resolve();
            } else if (Date.now() >= deadline) {
                reject(new Error(
                    "Mathematical notation could not be loaded. Please try again."
                ));
            } else {
                window.setTimeout(check, 50);
            }
        };
        check();
    });
}
