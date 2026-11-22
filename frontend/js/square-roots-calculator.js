
const squareRootsForm = document.getElementById("square-roots-form");

let lastSquareRootsResult = null;
let lastSquareRootsLatex = "";
async function renderSquareRoots(result, originalLatex) {
    const container = document.getElementById("square-roots-steps");
    const answer = document.getElementById("square-roots-answer");
    const resultSection = document.getElementById("square-roots-result");
    await waitForMathJax();
    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, answer]);
    }
    container.replaceChildren();
    answer.replaceChildren();
    result.steps.forEach((step, index) => {
        const section = document.createElement("section");
        section.className = "square-roots-solution-step";
        const heading = document.createElement("h3");
        heading.textContent = `${index + 1}) ${t(step.title)}`;
        const maths = document.createElement("div");
        maths.className = "square-roots-maths";
        const latex = index === 0
            ? originalLatex
            : step.latex;
        maths.textContent = `\\[${latex}\\]`;
        section.appendChild(heading);
        section.appendChild(maths);
        container.appendChild(section);
    });
    answer.textContent =
        `\\[\\boxed{${result.final_answer_latex}}\\]`;

    resultSection.hidden = false;

    await window.MathJax.typesetPromise([
        container,
        answer
    ]);
}
if (squareRootsForm) {
    const editor = document.getElementById("equation");
    const button = squareRootsForm.querySelector('button[type="submit"]');
    const errorBox = document.getElementById("square-roots-error");
    const resultSection = document.getElementById("square-roots-result");
    editor.addEventListener("keydown", event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();
            event.stopPropagation();

            if (!button.disabled) {
                squareRootsForm.requestSubmit();
            }
        }
    }, true);
    squareRootsForm.addEventListener(
        "submit",
        async event => {
            event.preventDefault();
            if (button.disabled) return;
            button.disabled = true;
            errorBox.textContent = "";
            resultSection.hidden = true;
            lastSquareRootsResult = null;
            try {
                if (typeof editor.getValue !== "function") {
                    throw new Error(t("mathEditorLoading"));
                }
                const originalLatex = editor.value;
                const expression = latexToEquation(
                    originalLatex,
                    true
                );
                if (!expression.trim()) {
                    throw new Error(t("invalidMathExpression"));
                }
                const result = await requestSolution(
                    "square_roots",
                    expression
                );
                await renderSquareRoots(
                    result,
                    originalLatex
                );
                lastSquareRootsResult = result;
                lastSquareRootsLatex = originalLatex;
            } catch (error) {
                resultSection.hidden = true;

                errorBox.textContent = t(
                    error.message || "calculationFailed"
                );

            } finally {
                button.disabled = false;
            }
        }
    );
    document.querySelectorAll(
        ".square-roots-example"
    ).forEach(example => {
        example.addEventListener("click", () => {
            editor.value = example.dataset.latex;
            editor.focus();
        });
    });
}
document.addEventListener("languagechange", () => {
    if (lastSquareRootsResult) {
        renderSquareRoots(
            lastSquareRootsResult,
            lastSquareRootsLatex
        ).catch(error => {
            document.getElementById(
                "square-roots-error"
            ).textContent = error.message;
        });
    }
});
document.addEventListener("calculatorcleared", () => {
    lastSquareRootsResult = null;
});
