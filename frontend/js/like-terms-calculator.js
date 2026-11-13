const likeTermsCalculator = document.getElementById("like-terms-form");

let lastLikeTermsResult = null;
let lastLikeTermsLatex = "";

async function renderLikeTerms(result, originalLatex) {
    const stepsContainer = document.getElementById("like-terms-steps");
    const answer = document.getElementById("like-terms-answer");
    const resultSection = document.getElementById("like-terms-result");

    await waitForMathJax();
    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([stepsContainer, answer]);
    }
    stepsContainer.replaceChildren();
    answer.replaceChildren();
    result.steps.forEach((step, index) => {
        const section = document.createElement("section");
        section.className = "like-terms-solution-step";
        const heading = document.createElement("h3");
        heading.textContent = `${index + 1}) ${t(step.title)}`;
        const maths = document.createElement("div");
        maths.className = "like-terms-maths";
        const latex = index === 0
            ? originalLatex
            : step.latex;
        maths.textContent = `\\[${latex}]`;
        section.append(heading, maths);
        stepsContainer.appendChild(section);
    });
    answer.textContent =
        `\\[\\boxed{${result.final_answer_latex}}\\]`;
    resultSection.hidden = false;
    await window.MathJax.typesetPromise({
        stepsContainer,
        answer
    });
}
if (likeTermsForm) {
    const editor = document.getElementById("equation");
    const button = likeTermsForm.querySelector('button[type="submit"]');
    const errorBox = document.getElementById("like-terms-error");
    const resultSection = document.getElementById("like-terms-result");

    editor.addEventListener("keydown", event => {
        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();
            event.stepPropagation();
            if (!button.disabled) {
                likeTermsForm.requestSubmit();
            }
        }
    }, true);
    likeTermsFormForm.addEventListener("submit", async event => {
        event.preventDefault();
        if (button.disabled) return;
        button.disabled = true;
        errorBox.textContent = "";
        resultSection.hidden = true;
        lastLikeTermsResult = null;

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
                "like_terms",
                expression
            );
            await renderLikeTerms(result, originalLatex);
            lastLikeTermsResult = result;
            lastLikeTermsLatex = originalLatex;
        } catch (error) {
            resultSection.hidden = true;
            errorBox.textContent = t(
                error.message || "calculationFailed"
            );
        } finally {
            button.disabled = false;
        }
    });
    document.querySelectorAll(".like-terms-example").forEach(example => {
        example.addEventListener("click", () => {
            editor.value = example.dataset.latex;
            editor.focus();
        });
    });
}
document.addEventListener("languagechange", () => {
    if (lastLikeTermsResult) {
        renderLikeTerms(
            lastLikeTermsResult,
            lastLikeTermsLatex
        ).catch(error => {
            document.getElementById("like-terms-error").textContent =
                error.message;
        });
    }
});