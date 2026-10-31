const quadraticForm = document.getElementById("quadratic-form");
if (quadraticForm) {
    quadraticForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const equation = document.getElementById("equation").value;
        const steps = document.getElementById("solution-steps");
        const answer = document.getElementById("final-answer");
        const button = quadraticForm.querySelector(
            'button[type="submit"]'
        );
        button.disabled = true;
        steps.textContent = t("calculating");
        answer.textContent = "";

        try {
            const result = await requestSolution(
                "quadratic",
                equation
            );
            await renderSolution(result, equation);
        } catch (error) {
            steps.textContent =
                error.message || t("calculationFailed");
        } finally {
            button.disabled = false;
        }
    });
}
