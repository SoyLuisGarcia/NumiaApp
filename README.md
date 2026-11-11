#  NumiaApp — Calculadora Didáctica de Métodos Numéricos

Es una aplicación web interactiva diseñada para la enseñanza y resolución de Métodos Numéricos aplicados a la ciencia y la ingeniería. Integra visión computacional (OCR) para escanear ejercicios directamente desde la cámara del celular y ofrece desgloses pedagógicos adaptativos.

---

##  Características Principales

- **3 Niveles Didácticos:**
  - **Sencillo:** Tarjetas interactivas con explicaciones aritméticas paso a paso (ideal para aprender).
  - **Normal:** Tablas académicas tradicionales completas para auditar tareas.
  - **Avanzado:** Resumen ejecutivo con indicadores clave (KPIs) y tablas sintéticas de hitos.
- **Escáner OCR con Cámara en Tiempo Real:** Reconocimiento automático de ecuaciones y variables desde cuadernos o libros utilizando `Tesseract.js`.
- **Formato Matemático Profesional:** Renderizado en tiempo real de notación LaTeX mediante `MathJax`.
- **9 Métodos Numéricos Integrados:**
  * Bisección
  * Newton-Raphson
  * Interpolación Polinomial
  *  Derivación Numérica (Centrada, Adelante, Atrás)
  *  Trapecio Compuesto
  * Simpson 1/3 Compuesto
  * Método de Euler (EDOs)
  * Gauss-Jordan (Sistemas de Ecuaciones / Matrices)
  * Gauss-Seidel (Método Iterativo)

---

##  Tecnologías Utilizadas

- **Backend:** Python 3.x, Flask, SymPy, NumPy
- **Frontend:** HTML5, CSS3 (Custom Responsive Properties), JavaScript (ES6+)
- **Librerías Clave:** MathJax v3, Tesseract.js v5

---

## Dependencias
pip install flask sympy numpy
