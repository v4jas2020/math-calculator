const factoriseForm = document.getElementById("factorise-form")

let lastFactoriseResult = null;
let lastFactoriseLatex = "";

async function renderFactoriseSolution(result, originalLatex) {
    const container = document.getElementById("factorise-steps");
    const answer = document.getElementById("factorise-answer");
    const resultSection = document.getElementById("factorise-result");
    await waitForMathJax();
    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, answer]);
    }
    container.replaceChildren();
    answer.replaceChildren();

    result.steps.forEach((step, index) => {
        const section = document.createElement("section");
        section.className = "factorise-solution-step";
        const heading = document.createElement("h3");
        heading.textContent = `${index + 1}) ${t(step.title)}`;
        const maths = document.createElement("div");
        maths.className = "factorise-maths";
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
    resultSection.hidden = false;
}
if (factoriseForm) {
    const editor = document.getElementById("equation");
    const button = factoriseForm.querySelector(
        'button[type=submit]'
    );
    const errorBox = document.getElementById("factorise-error");
    const resultSection = document.getElementById("factorise-result");
    editor.addEventListener("keydown", event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();
            event.stopImmediatePropagation();
            if (!button.disabled) {
                factoriseForm.requestSubmit();
            }
        }
    }, true);
    factoriseForm.addEventListener("submit", async event => {
        event.preventDefault();
        if (button.disabled) return;
        button.disabled = true;
        errorBox.textContent = "";
        resultSection.hidden = true;
        lastFactoriseResult = null;

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
                "factorise",
                expression
            );
            await renderFactoriseSolution(
                result,
                originalLatex
            );
            lastFactoriseResult = result;
            lastFactoriseLatex = originalLatex;
        } catch (error) {
            resultSection.hidden = true;
            errorBox.textContent = t(
                error.message || "calculationFailed"
            );
        } finally {
            button.disabled = false;
        }
    });
    document.querySelectorAll(".factorise-example").forEach(
        example => {
            example.addEventListener("click", () => {
                editor.value = example.dataset.latex;
                editor.focus();
            });
        }
    );
}
document.addEventListener("languagechange", () => {
    if (lastFactoriseResult) {
        renderFactoriseSolution(
            lastFactoriseResult,
            lastFactoriseLatex
        ).catch(error => {
            document.getElementById(
                "factorise-error"
            ).textContent = error.message;
        });
    }
});
document.addEventListener("calculatorcleared", () => {
    lastFactoriseResult = null;
});




