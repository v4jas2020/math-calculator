const quadraticForm = document.getElementById("quadratic-form");
if (quadraticForm) {
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
