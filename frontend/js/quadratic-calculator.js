const quadraticForm = document.getElementById("quadratic-form");

let lastQuadraticResult = null;
let lastQuadraticLatex = "";

async function renderQuadraticSolution(result, originalLatex) {
    const container = document.getElementById("quadratic-steps");
    const answer = document.getElementById("quadratic-answer");
    const resultSection = document.getElementById("quadratic-result");

    await waitForMathJax();
    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, answer]);
    }
    container.replaceChildren();
    answer.replaceChildren();
    const steps = result.steps.filter(
        step => step.title !== "Final answer"
    );
    steps.forEach((step, index) => {
        const section = document.createElement("section");
        section.className = "quadratic-solution-step";
        const heading = document.createElement("h3");
        heading.textContent = `${index + 1}) ${t(step.title)}`;
        const maths = document.createElement("div");
        maths.className = "quadratic-maths";
        const latex = index === 0 && originalLatex
            ? originalLatex
            : step.latex;
        maths.textContent = `\\[${latex}\\]`;
        section.append(heading, maths);
        if (step.explanation) {
            const explanation = document.createElement("p");
            explanation.textContent = t(step.explanation);
            section.appendChild(explanation);
        }
        container.appendChild(section);
    });
    let finalLatex = result.final_answer_latex;
    if (finalLatex === "\\text{No real roots") {
        finalLatex = `\\text{${t("noRealRoots")}}`;
    }
    answer.textContent = `\\[\\boxed{${finalLatex}}\\]`;
    await window.MathJax.typesetPromise([
        container,
        answer
    ]);
    resultSection.hidden = false;
}
if (quadraticForm) {
    const editor = document.getElementById("equation");
    const button = quadraticForm.querySelector(
        'button[type="submit"]'
    );
    const errorBox = document.getElementById("quadratic-error");
    const resultSection = document.getElementById("quadratic-result");
    editor.addEventListener("keydown", event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();
            event.stopPropagation();
            if (!button.disabled) {
                quadraticForm.requestSubmit();
            }
        }
    }, true)
    quadraticForm.addEventListener("submit", async event => {
        event.preventDefault();
        if (button.disabled) return;
        button.disabled = true;
        errorBox.textContent = "";
        resultSection.hidden = true;
        lastQuadraticResult = null;

        try {
            if (typeof editor.getValue !== "function") {
                throw new Error(t("mathEditorLoading"));
            }
            const originalLatex = editor.value;
            const equation = latexToEquation(originalLatex);

            if (!equation.trim()) {
                throw new Error(t("invalidMathExpression"));
            }
            const result = await requestSolution(
                "quadratic",
                equation
            );
            await renderQuadraticSolution(result, originalLatex)
            lastQuadraticResult = result;
            lastQuadraticLatex = originalLatex;
        } catch (error) {
            resultSection.hidden = true;
            errorBox.textContent = t(
                error.message || "calculationFailed"
            );
        } finally {
            button.disabled = false;
        }
    });
    document.querySelectorAll(".quadratic-example").forEach(
        example => {
            example.addEventListener("click", () => {
                editor.value = example.dataset.latex;
                editor.focus();
            });
        }
    );
}
document.addEventListener("languagechange", () => {
    if (lastQuadraticResult) {
        renderQuadraticSolution(
            lastQuadraticResult,
            lastQuadraticLatex
        ).catch(error => {
            document.getElementById(
                "quadratic-error"
            ).textContent = error.message;
        });
    }
});