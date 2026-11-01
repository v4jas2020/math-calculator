const fractionForm = document.getElementById("fraction-form");
let lastFractionResult = null;

async function renderFractionSolution(result) {
    const container = document.getElementById("fraction-steps");
    const finalAnswer = document.getElementById("fraction-answer");
    const resultSection = document.getElementById("fraction-result");

    await waitForMathJax();

    if (window.MathJax.typesetClear) {
        window.MathJax.typesetClear([container, finalAnswer]);
    }

    container.replaceChildren();
    finalAnswer.replaceChildren();

    result.steps.forEach((step, index) => {
        const section = document.createElement("section");
        section.className = "fraction-solution-step";

        const title = document.createElement("h3");
        title.textContent = `${index + 1}) ${t(step.title)}`;

        const maths = document.createElement("div");
        maths.className = "fraction-maths";
        maths.textContent = "\\[" + step.latex + "\\]";

        section.appendChild(title);
        section.appendChild(maths);
        container.appendChild(section);
    });

    finalAnswer.textContent =
        "\\[\\boxed{" + result.final_answer_latex + "}\\]";

    resultSection.hidden = false;

    await window.MathJax.typesetPromise([
        container,
        finalAnswer
    ]);
}
if (fractionForm) {
    document.getElementById("equation").addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.isComposing) {
            event.preventDefault();
            fractionForm.requestSubmit();
        }
    });
    fractionForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = fractionForm.querySelector(
            'button[type="submit"]'
        );
        const errorBox = document.getElementById("fraction-error");

        button.disabled = true;
        errorBox.textContent = "";

        try {
            if (typeof document.getElementById("equation").getValue !== "function") {
                throw new Error(t("mathEditorLoading"));
            }
            const equation = latexToEquation(document.getElementById("equation").value, true);
            const result = await requestSolution(
                "fractions",
                equation
            );
            if (!result.steps.length) {
                result.steps.push({
                    title: "fractionStepOriginal",
                    latex: document.getElementById("equation").value
                });
            }
            lastFractionResult = result;
            await renderFractionSolution(result);
        } catch (error) {
            errorBox.textContent =
                t(error.message || "Calculation failed.");
        } finally {
            button.disabled = false;
        }
    });

    document.querySelectorAll(".fraction-example").forEach(
        button => {
            button.addEventListener("click", () => {
                const operation = { "+": "+", "-": "-", "*": "\\cdot", "/": "\\div" }[button.dataset.op];
                document.getElementById("equation").value =
                    `\\frac{${button.dataset.a}}{${button.dataset.b}}${operation}\\frac{${button.dataset.c}}{${button.dataset.d}}`;
            });
        }
    );
}
document.addEventListener("languagechange", () => {
    if (lastFractionResult) {
        renderFractionSolution(lastFractionResult).catch(error => {
            document.getElementById("fraction-error").textContent =
                error.message;
        });
    }
});
