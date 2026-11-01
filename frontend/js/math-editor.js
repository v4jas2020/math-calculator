const mathField = document.getElementById("equation");
if (mathField) {
    customElements.whenDefined("math-field").then(() => {
        document.querySelectorAll("[data-math]").forEach(button => {
            button.addEventListener("mousedown", event => {
                event.preventDefault();
            });
            button.addEventListener("click", () => {
                mathField.insert(button.dataset.math, {
                    selectionMode: "placeholder",
                    focus: true
                });
            });
        });
        document.querySelectorAll("[data-command]").forEach(button => {
            button.addEventListener("mousedown", event => {
                event.preventDefault();
            });
            button.addEventListener("click", () => {
                mathField.executeCommand(button.dataset.command);
                mathField.focus();
            });
        });
    });
}
function latexToEquation(latex) {
    const source = latex
        .replace(/\\left|\\right/g, "")
        .replace(/\\cdot|\\times/g, "*")
        .replace(/\\div/g, "/")
        .replace(/\\[.;!]/g, "")
        .replace(/\s/g, "");
    let position = 0;
    function parseUntil(closing = null) {
        let output = "";
        while (position < source.length) {
            if (closing && source[position] === closing) {
                position++;
                return output;
            }
            if (source.startsWith("\\frac", position)) {
                position +=5;
                const numerator = readGroup();
                const denominator = readGroup();

                output += `(${numerator})/(${denominator})`;
            } else if (source[position] === "{") {
                position++;
                output += `(${parseUntil("}")})`;
            } else if (/^[0-9.x()+\-*/^=]$/.test(source[position])) {
                output += source[position++];
            } else {
                throw new Error(t("invalidMathExpression"));
            }
        }
        if (closing) {
            throw new Error(t("invalidMathExpression"));
        }
        return output;
    }
    function readGroup() {
        if (source[position] !== "{") {
            throw new Error(t("invalidMathExpression"));
        }
        position++;
        const value = parseUntil("}");

        if (!value) {
            throw new Error(t("invalidMathExpression"));
        }
        return value
    }
    return parseUntil();
}