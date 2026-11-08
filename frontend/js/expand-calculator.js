const expandForm = document.getElementById("expand-form");
let lastExpandResult = null;

async function renderExpandSolution(result) {
    const container = document.getElementById("expand-steps");
    const answer = document.getElementById("expand-answer");
    const resultSection = document.getElementById("expand-result");
    await waitForMathJax();

    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, answer]);
    }
    container.replaceChildren();
    answer.replaceChildren();

    result.steps.forEach((step, index) => {
        const section = document.createElement("section");
        section.className = "expand-solution-step";
        const heading = document.createElement("h3");
        heading.textContent = (index + 1) + ") " + t(step.title);
        const maths = document.createElement("div");
        maths.className = "expand-maths";
        maths.textContent = "\\[" + step.latex + "\\]";
        section.append(heading, maths);
        container.appendChild(section);
    });

    answer.textContent = "\\[\\boxed{" + result.final_answer_latex + "}\\]";
    resultSection.hidden = false;
    await window.MathJax.typesetPromise([container, answer]);
}

if (expandForm) {
    const editor = document.getElementById("equation");
    const button = expandForm.querySelector('button[type="submit"]');
    const errorBox = document.getElementById("expand-error");
    const resultSection = document.getElementById("expand-result");

    editor.addEventListener("keydown", event => {
        if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
            event.preventDefault();
            event.stopPropagation();
            if (!button.disabled) expandForm.requestSubmit();
        }
    }, true);

    expandForm.addEventListener("submit", async event => {
        event.preventDefault();
        if (button.disabled) return;
        button.disabled = true;
        errorBox.textContent = "";
        resultSection.hidden = true;
        lastExpandResult = null;
        try {
            if (typeof editor.getValue !== "function") {
                throw new Error(t("mathEditorLoading"));
            }
            const expression = latexToEquation(editor.value);
            if (!expression.trim()) throw new Error(t("invalidMathExpression"));
            const result = await requestSolution("expand", expression);
            await renderExpandSolution(result);
            lastExpandResult = result;
        } catch (error) {
            resultSection.hidden = true;
            errorBox.textContent = t(error.message || "calculationFailed");
        } finally {
            button.disabled = false;
        }
    });

    document.querySelectorAll(".expand-example").forEach(example => {
        example.addEventListener("click", () => {
            editor.value = example.dataset.latex;
            editor.focus();
        });
    });
}

document.addEventListener("languagechange", () => {
    if (lastExpandResult) {
        renderExpandSolution(lastExpandResult).catch(error => {
            document.getElementById("expand-error").textContent = error.message;
        });
    }
});
