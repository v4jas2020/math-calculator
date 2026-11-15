(() => {
    const form = document.querySelector('form[id$="-form"]');

    if (!form) return;

    const prefix = form.id.slice(0, -5);
    const editor = document.getElementById("equation")
    const submitButton = form.querySelector('button[type=submit]');
    const resultSection = document.getElementById(`${prefix}-result`);
    const steps = document.getElementById(`${prefix}-answer`);
    const answer = document.getElementById(`${prefix}-error`);

    if (
        !editor ||
        !submitButton ||
        !resultSection ||
        !steps ||
        !answer ||
        !errorBox
    ) {
        console.warn("Calculator actions: required elements missing");
        return;
    }
    let currentAnswer = "";

    const actions = document.createElement("div");
    actions.className = "calculator-actions";
    submitButton.parentNode.insertBefore(
        actions,
        submitButton
    );
    actions.appendChild(submitButton);

    const clearButton = document.createElement("button");
    clearButton.type = "button";
    clearButton.className = "calculator-clear";

    actions.appendChild(clearButton);
    const syncClearState = () => {
        clearButton.disabled = submitButton.disabled;
    };
    new MutationObserver(syncClearState).observe(
        submitButton,
        {
            attributes: true,
            attributeFilter: ["disabled"]
        }
    );
    syncClearState();
    clearButton.addEventListener("click", () => {
        if (submitButton.disabled) return;

        editor.value = "";
        errorBox.textContent = "";
        resultSection.hidden = true;
        currentAnswer = "";
        copyStatus.textContent = "";
        if (window.MathJax?.typesetClear) {
            window.MathJax.typesetClear([steps, answer]);
        }
        steps.replaceChildren();
        answer.replaceChildren();

        document.dispatchEvent(
            new Event("calculatorcleared")
        );
        editor.focus();
    });
    const copyButton = document.createElement("button");
    copyButton.type = "button";
    copyButton.className = "calculator-copy";
    const copyStatus = document.createElement("span");
    copyStatus.className = "calculator-copy-status";
    copyStatus.setAttribute("role", "status");
    copyStatus.setAttribute("aria-live", "polite");
    answer.insertAdjacentElement("afterend", copyButton);
    copyButton.insertAdjacentElement("afterend", copyStatus);

    function formatAnswer(data) {
        if (data.topic === "quadratic") {
            const roots = data.roots;
            if (Array.isArray(roots)) {
                if (roots.length === 0) {
                    return t("noRealRoots");
                }
                const match = String(
                    data.final_answer_latex || ""
                ).match(/^([a-zA-Z])_1/);
                const variable = match ? match[1] : "x";
                if (roots.length === 1) {
                    return `${variable}1 = ${variable}2 = ${roots[0]}`;
                }
                return (
                    `${variable}1 = ${roots[0]}, ` +
                    `${variable}2 = ${roots[1]}`
                );
            }
        }
        if (data.topic === "linear") {
            if (data.solution_type === "none") {
                return t("linearNoSolution");
            }
            if (data.solution_type === "infinite") {
                return t("linearInfinite")
            }
            if (data.solution != null) {
                return `${data.variable} = ${data.solution}`;
            }
        }
        if (data.answer != null) {
            return String(data.answer);
        }
        return String(data.final_answer_latex || "");
    }
    document.addEventListener("calculatoranswer", event => {
        currentAnswer = formatAnswer(event.detail);
        copyStatus.textContent = "";
    });
    form.addEventListener("submit", () => {
        currentAnswer = "";
        copyStatus.textContent = "";
    }, true);
    copyButton.addEventListener("click", async () => {
        if (!currentAnswer || resultSection.hidden) return;
        try {
            await navigator.clipboard.writeText(currentAnswer);
            copyStatus.textContent = t("copied");
        } catch (error) {
            copyStatus.textContent = t("copyFailed");
        }
    });
    function updateLabels() {
        clearButton.textContent = t("clearEquation");
        copyButton.textContent = t("copyAnswer");
    }
    document.addEventListener(
        "languagechange",
        updateLabels
    );
    updateLabels();
})();