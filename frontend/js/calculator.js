const quadraticForm = document.getElementById("quadratic-form");
if (quadraticForm) {
    const mathEditor = document.getElementById("equation");
    mathEditor.addEventListener("keydown", (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {
            event.preventDefault();
            event.stopPropagation();
            const submitButton = quadraticForm.querySelector(
                'button[type="submit"]'
            );
            if (!submitButton.disabled) {
                quadraticForm.requestSubmit();
            }
        }
    }, true);
    quadraticForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const editor = document.getElementById("equation");
        const originalLatex = editor.value;
        let equation;
        const steps = document.getElementById("solution-steps");
        const answer = document.getElementById("final-answer");
        const button = quadraticForm.querySelector(
            'button[type="submit"]'
        );
        button.disabled = true;
        steps.textContent = t("calculating");
        answer.textContent = "";

        try {
            if (typeof editor.getValue !== "function") {
                throw new Error(t("mathEditorLoading"));
            }
            equation = latexToEquation(originalLatex);
            if (!equation.trim()) {
                throw new Error(t("invalidMathExpression"));
            }
            const result = await requestSolution(
                "quadratic",
                equation
            );
            await renderSolution(result, equation, originalLatex);
        } catch (error) {
            steps.textContent =
                error.message || t("calculationFailed");
        } finally {
            button.disabled = false;
        }
    });
}
