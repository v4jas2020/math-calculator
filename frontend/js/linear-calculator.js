const linearForm = document.getElementById("linear-form");
let lastLinearResult = null;

async function renderLinearSolution(result) {
    const container = document.getElementById("linear-steps");
    const answer = document.getElementById("linear-answer");
    const resultSection = document.getElementById("linear-result");

    await waitForMathJax();

    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, answer]);
    }
    container.replaceChildren();
    answer.replaceChildren();

    result.steps.forEach((step, index) => {
        const section = document.createElement("section");
        section.className = "linear-solution-step";
        const heading = document.createElement("h3");
        heading.textContent = `${index + 1}) ${t(step.title)}`;
        const maths = document.createElement("div");
        maths.className = "linear-maths";
        maths.textContent = `\\[${step.latex}\\]`;

        section.appendChild(heading);
        section.appendChild(maths);
        container.appendChild(section);
    });
    let finalLatex = result.final_answer_latex;
    if (result.solution_type === "none") {
        finalLatex = `\\text{${t("linearNoSolution")}}`;
    } else if (result.solution_type === "infinite") {
        finalLatex = `\\text{${t("linearInfinite")}}`
    }
    answer.textContent = `\\[\\boxed{${finalLatex}}\\]`;

    resultSection.hidden = false;

    await window.MathJax.typesetPromise([
        container,
        answer
    ]);
}

if (linearForm) {
    const editor = document.getElementById("equation");
    const submitButton = linearForm.querySelector(
        'button[type="submit"]'
    );
    const errorBox = document.getElementById("linear-error");
    const resultSection = document.getElementById("linear-result");
    editor.addEventListener("keydown", (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();
            event.stopPropagation();
            if (!submitButton.disabled) {
                linearForm.requestSubmit();
            }
        }
    }, true);
    linearForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (submitButton.disabled) return;
        submitButton.disabled = true;
        errorBox.textContent = "";
        resultSection.hidden = true;
        lastLinearResult = null;
        try {
            if (typeof editor.getValue !== "function") {
                throw new Error(t("mathEditorLoading"));
            }
            const equation = latexToEquation(editor.value);

            if (!equation.trim()) {
                throw new Error(t("invalidMathExpression"));
            }
            const result = await requestSolution(
                "linear",
                equation
            );
            await renderLinearSolution(result);
            lastLinearResult = result;
        } catch (error) {
            resultSection.hidden = true;
            errorBox.textContent = t(
                error.message || "calculationFailed"
            );
        } finally {
            submitButton.disabled = false;
        }
    });
    document.querySelectorAll(".linear-example").forEach(
        button => {
            button.addEventListener("click", () => {
                editor.value = button.dataset.expression;
                editor.focus();
            });
        }
    );
}
document.addEventListener("languagechange", () => {
    if (lastLinearResult) {
        renderLinearSolution(lastLinearResult).catch(error => {
            document.getElementById("linear-error").textContent =
                error.message;
        });
    }
});