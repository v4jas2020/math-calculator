
async function renderSolution(result) {
    const container = document.getElementById("solution-steps");
    const finalAnswer = document.getElementById("final-answer");
    if (window.MathJax && window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, finalAnswer]);
    }
    container.replaceChildren();
    finalAnswer.replaceChildren();
    for (const step of result.steps) {
        const section = document.createElement("section");
        const title = document.createElement("h3");
        title.textContent = step.title;
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
    if (window.MathJax && window.MathJax.typesetPromise) {
        await window.MathJax.typesetPromise([
            container,
            finalAnswer
        ]);
    }
}
