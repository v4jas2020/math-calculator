const powersForm = document.getElementById("powers-form")

let lastPowersResult = null;
let lastPowersLatex = "";

async function renderPowers(result, originalLatex) {
    const container = document.getElementById("powers-steps")
    const answer = document.getElementById("powers-answer");
    const resultSection = document.getElementById("powers-result")

    await waitForMathJax();

    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, answer]);
    }
    container.replaceChildren();
    answer.replaceChildren();

    result.steps.forEach((step, index) => {
        const section = document.createElement("section");
        section.className = "powers-solution-step";
        const heading = document.createElement("h3");
        heading.textContent = `${index + 1}) ${t(step.title)}`;
        const maths = document.createElement("div");
        maths.className = "powers-maths";

        const latex = index === 0
            ? originalLatex
            : step.latex;
        maths.textContent = `\\[${latex}\\]`;

        section.appendChild(heading, maths);
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
if (powersForm) {
    const editor = document.getElementById("equation");
    const button = powersForm.querySelector('button[type="submit"]');
    const errorBox = document.getElementById("powers-error");
    const resultSection = document.getElementById("powers-result");
    editor.addEventListener("keydown", event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();
            event.stopPropagation();

            if (!button.disabled) {
                powersForm.requestSubmit();
            }
        }
    }, true);

    powersForm.addEventListener("submit", async event => {
        event.preventDefault();
        if (button.disabled) return;

        button.disabled = true;
        errorBox.textContent = "";
        resultSection.hidden = true;
        lastPowersResult = null;

        try {
            if (typeof editor.getValue !== "function") {
                throw new Error(t("mathEditorLoading"));
            }
            const originalLatex = editor.value;
            const expression = latexToEquation(originalLatex)
                .replace(/(\d)(?=[a-zA-Z])/g, "$1*");
            if (!expression.trim()) {
                throw new Error(t("invalidMathExpression"));
            }
            const result = await requestSolution(
                "powers",
                expression
            );
            await renderPowers(result, originalLatex);
            lastPowersResult = result;
            lastPowersLatex = originalLatex;
        } catch (error) {
            resultSection.hidden = true;
            errorBox.textContent = t(
                error.message || "calculationFailed"
            );
        } finally {
            button.disabled = false;
        }
    });
    document.querySelectorAll(".powers-example").forEach(
        example => {
            example.addEventListener("click", () => {
                editor.value = example.dataset.latex;
                editor.focus();
            });
        }
    );
}
document.addEventListener("languagechange", () => {
    if (lastPowersResult) {
        renderPowers(
            lastPowersResult,
            lastPowersLatex
        ).catch(error => {
            document.getElementById(
                "powers-error"
            ).textContent = error.message;
        });
    }
});
document.addEventListener("calculatorcleared", () => {
    lastPowersResult = null;
})