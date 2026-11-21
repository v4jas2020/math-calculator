const addSubtractCalculator = document.getElementById("add-subtract-form");

let lastAddSubtractResult = null;
let lastAddSubtractLatex = "";

async function renderAddSubtractSolution(result, originalLatex) {
    const container = document.getElementById("add-subtract-step");
    const answer = document.getElementById("add-subtract-answer");
    const resultSection = document.getElementById("add-subtract-result");

    await waitForMathJax();
    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, answer]);
    }
    container.replaceChildren();
    answer.replaceChildren();

    result.steps.forEach((step, index) => {
        const section = document.createElement("section");
        section.className = "add-subtract-solution-step";

        const heading = document.createElement("h3");
        heading.textContent = `${index + 1}) ${t(step.title)}`;

        const maths = document.createElement("div");
        maths.className = "add-subtract-maths";

        const latex = index === 0
            ? originalLatex
            : step.latex;
        maths.textContent = `\\[${latex}\\]`;

        section.append(heading, maths);
        container.appendChild(section);
    });
    answer.textContent =
        `\\[\\boxed{${result.final_answer_latex}}\\]`;
    await window.MathJax.typesetPromise([
        container,
        answer
    ]);
    result.hidden = false;
}

if (addSubtractForm) {
    const editor = document.getElementById("equation");
    const button = addSubtractForm.querySelector(
        'button[type="submit"]'
    );
    const errorBox = document.getElementById("add-subtract-error");
    const resultSection = document.getElementById("add-subtract-result");

    editor.addEventListener("keydown", event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();
            event.stopPropagation();

            if (!button.disabled) {
                addSubtractForm.requestSubmit();
            }
        }
    }, true);

    addSubtractForm.addEventListener("submit", async event => {
        event.preventDefault();
        if (button.disabled) return;
        button.disabled = true;
        errorBox.textContent = "";
        resultSection.hidden = true;
        lastAddSubtractResult = null;

        try {
            if (typeof editor.getValue !== "function") {
                throw new Error(t("mathEditorLoading"));
            }
            const originalLatex = editor.value;
            const expression = latexToEquation(originalLatex);
            if (!expression.trim()) {
                throw new Error(t("invalidMathExpression"));
            }
            const result = await requestSolution(
                "add_subtract",
                expression
            );
            await renderAddSubtractSolution(
                result,
                originalLatex
            );
            lastAddSubtractResult = result;
            lastAddSubtractLatex = originalLatex;
        } catch (error) {
            resultSection.hidden = true;
            errorBox.textContent = t(
                error.message || "calculationFailed"
            );
        } finally {
            button.disabled = false;
        }
    });
    document.querySelectorAll(".add-subtract-example").forEach(
        example => {
            example.addEventListener("click", () => {
                editor.value = example.dataset.latex;
                editor.focus();
            });
        }
    );
}
document.addEventListener("languagechange", () => {
    if (lastAddSubtractResult) {
        renderAddSubtractSolution(
            lastAddSubtractResult,
            lastAddSubtractLatex
        ).catch(error => {
            document.getElementById(
                "add-subtract-error"
            ).textContent = error.message;
        });
    }
});

document.addEventListener("calculatorcleared", () => {
    lastAddSubtractResult = null;
});