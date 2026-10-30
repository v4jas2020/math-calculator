
async function renderSolution(result) {
    const container = document.getElementById("solution-steps");
    const finalAnswer = document.getElementById("final-answer");
    await waitForMathJax();
    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, finalAnswer]);
    }
    container.replaceChildren();
    finalAnswer.replaceChildren();
    let stepNumber = 0;
    for (const step of result.steps) {
        if (step.title === "Final answer") {
            continue;
        }
        stepNumber += 1;
        const section = document.createElement("section");
        const title = document.createElement("h3");
        title.textContent = "Step " + stepNumber + ": " + step.title;
        section.appendChild(title);

        const maths = document.createElement("div");
        maths.textContent = "\\[" + step.latex + "\\]";
        section.appendChild(maths);
        if (step.explanation) {
            const explanation = document.createElement("p");
            explanation.textContent = step.explanation;
            section.appendChild(explanation);
        }
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
