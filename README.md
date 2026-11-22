# Math Calculators

**Learn the process, not just the answer.**

Math Calculators is a free, student-focused website that helps students understand mathematics through detailed, step-by-step solutions.

Instead of simply providing an answer, it explains the calculations using clear mathematical notation and notebook-style workings.

Developed by **[Vėjas Kašėta](https://github.com/v4jas2020)** as a Hack Club project.

### Development progress — Week 5 archive

**8 of 18 planned calculators available (44%)** — 6 functional, 2 in beta, 10 planned.

![Calculator progress: 44%](https://img.shields.io/badge/Calculator%20progress-44%25-555555?style=flat-square)

`████████░░░░░░░░░░` **8 / 18**

*Progress measures calculator availability, not overall project completion. Week 5 is archived at this README update; further improvements can continue in future weeks.*

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)

---

## Preview

![Math Calculators Website](frontend/assets/images/Screenshot_2026-11-08_20-07-52.png)

*Interactive mathematical input and step-by-step solutions.*

## Weekly versions for reviewers

[**Open the version selection**](https://math-calculator-gold.vercel.app/) — Week 2, Week 3, and the [Week 4 archived website](https://math-calculator-rmv2enz3a-v4jas2020s-projects.vercel.app/) are preserved. **Week 5 is archived at the commit titled “Updated readme a bit :3 final commit. -Archiving week 5 from this commit.”** The main website may continue to change after this snapshot.

## Features

- **Step-by-step solutions** — Understand every stage of a calculation.
- **Visual maths editor** — Enter mathematical expressions using properly formatted symbols.
- **Exact calculations** — Fractions, square roots and symbolic answers.
- **Notebook-style workings** — Clear and readable mathematical explanations.
- **Two languages** — 🇬🇧 English and 🇱🇹 Lithuanian.
- **Responsive design** — Support for desktop and mobile devices.

## Calculator progress

| Calculator | Status |
|---|---|
| Quadratic Equations | Functional |
| Linear Equations | Functional |
| Fractions | Functional |
| Expand Brackets | Functional |
| Combine Like Terms | Functional |
| Add & Subtract Expressions | Functional |
| Simplifying Square Roots | Beta |
| Powers & Exponents | Beta |
| Percentages | Planned |
| Radical Fractions | Planned |
| Inequalities | Planned |
| Systems of Equations | Planned |
| Geometry Formulas | Planned |
| Polynomial Division | Planned |
| Functions & Graphing | Planned |
| Trigonometry | Planned |
| Logarithms | Planned |
| Universal Math Solver | Planned |

*Statuses match the [calculator catalog](https://math-calculator-gold.vercel.app/calculators.html) at the end of Week 5.*

## Technologies

| Frontend | Backend |
|---|---|
| HTML5 | Python |
| CSS3 | FastAPI |
| JavaScript | SymPy |
| MathLive | |
| MathJax | |

**Hosting:** Vercel

## Getting Started

Clone the repository:

```bash
git clone https://github.com/v4jas2020/math-calculator.git
cd math-calculator
```

Install dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

Start the development server:

```bash
python -m uvicorn backend.main:app --reload
```

Visit **http://127.0.0.1:8000**.

## Roadmap

- [x] Quadratic equation solver
- [x] Fractions calculator
- [x] Linear equation solver
- [x] Visual mathematical editor
- [x] English and Lithuanian support
- [x] Finish testing Expand Brackets
- [ ] Improve advanced mathematical explanations
- [x] Launch 8 calculator pages (6 functional, 2 beta)
- [ ] Add more calculators
- [ ] Add educational guides
- [ ] Improve mobile support

## Contributing

Suggestions, bug reports and improvements are welcome.

[Open an issue](https://github.com/v4jas2020/math-calculator/issues) to report a problem or suggest a feature.

## Support the Project

If Math Calculators is useful to you, consider [starring the repository](https://github.com/v4jas2020/math-calculator).

---

**Developed and maintained by Vėjas Kašėta.**

*Created as a Hack Club project.*

**Development began during Hack Club Terra Weeks 2 and 3. Week 5 is now archived; more calculators, explanations, and mobile improvements remain planned.**