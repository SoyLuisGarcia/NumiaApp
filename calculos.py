import math
import re
import sympy as sp

def parse_input_math(expr_str):
    """Limpia y sanitiza notaciones comunes pegadas por el usuario (e.g. 3x^2 -> 3*x**2)."""
    if not expr_str:
        return ""
    s = str(expr_str).strip()
    s = s.replace('^', '**')
    s = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', s)
    s = re.sub(r'(\))([a-zA-Z\d\(])', r'\1*\2', s)
    s = re.sub(r'([xXyYzZ])([a-zA-Z])', r'\1*\2', s)
    return s

def parse_matrix_input(raw_text):
    """
    Parsea matrices en múltiples formatos:
    - Renglones con comas o espacios: 3 1 5 / 1 2 5
    - Corchetes simples o anidados: [[3, 1, 5], [1, 2, 5]]
    - Ecuaciones lineales: 3x + y = 5; x + 2y = 5
    """
    raw_text = str(raw_text).strip()
    import json

    if raw_text.startswith('{') and raw_text.endswith('}'):
        try:
            data = json.loads(raw_text)
            if 'A' in data and 'b' in data:
                return data['A'], data['b']
        except Exception:
            pass

    try:
        possible_json = raw_text.replace("'", '"')
        parsed = json.loads(possible_json)
        if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], list):
            A = [row[:-1] for row in parsed]
            b = [row[-1] for row in parsed]
            return A, b
    except Exception:
        pass

    if '=' in raw_text:
        try:
            lines = [l.strip() for l in re.split(r'[\n;]', raw_text) if l.strip()]
            eqs = []
            syms = set()
            for l in lines:
                if '=' in l:
                    left, right = l.split('=')
                    eq_expr = sp.sympify(parse_input_math(left)) - sp.sympify(parse_input_math(right))
                    eqs.append(eq_expr)
                    syms.update(eq_expr.free_symbols)
            if eqs and syms:
                sorted_syms = sorted(list(syms), key=lambda s: s.name)
                A_mat, b_vec = sp.linear_eq_to_matrix(eqs, sorted_syms)
                A = [[float(val) for val in row] for row in A_mat.tolist()]
                b = [float(val[0]) for val in b_vec.tolist()]
                return A, b
        except Exception:
            pass

    rows = []
    lines = [line.strip() for line in re.split(r'[\n;]', raw_text) if line.strip()]
    for line in lines:
        cleaned = line.replace('[', '').replace(']', '').replace('{', '').replace('}', '').strip()
        if not cleaned:
            continue
        parts = [float(p) for p in re.split(r'[\s,]+', cleaned) if p.strip()]
        if len(parts) >= 2:
            rows.append(parts)
            
    if rows:
        A = [r[:-1] for r in rows]
        b = [r[-1] for r in rows]
        return A, b
        
    raise ValueError("No se pudo interpretar el formato de la matriz. Revisa los datos ingresados.")

def fmt(val, dec=4):
    """Formateador numérico limpio."""
    if isinstance(val, (int, float)):
        if abs(val - round(val)) < 1e-7:
            return str(int(round(val)))
        return f"{val:.{dec}f}".rstrip('0').rstrip('.')
    return str(val)

def evaluar_fx(expr_str, valor_x):
    x = sp.Symbol('x')
    clean_expr = parse_input_math(expr_str)
    expr = sp.sympify(clean_expr)
    return float(expr.subs(x, valor_x))

def evaluar_fxy(expr_str, valor_x, valor_y):
    x, y = sp.symbols('x y')
    clean_expr = parse_input_math(expr_str)
    expr = sp.sympify(clean_expr)
    return float(expr.subs({x: valor_x, y: valor_y}))

def mat_to_latex(M):
    cols = len(M[0])
    col_spec = "c" * (cols - 1) + "|c"
    rows_str = " \\\\ ".join([" & ".join([fmt(val) for val in row[:-1]]) + " & " + fmt(row[-1]) for row in M])
    return f"\\left[\\begin{{array}}{{{col_spec}}} {rows_str} \\end{{array}}\\right]"

# ------------------------------------------------------------------
# 1. BISECCIÓN
# ------------------------------------------------------------------
def biseccion(f_str, a, b, tol=0.0001, max_iter=50, nivel='sencillo'):
    clean_f = parse_input_math(f_str)
    x_sym = sp.Symbol('x')
    expr = sp.sympify(clean_f)
    f_latex = sp.latex(expr)

    fa = evaluar_fx(clean_f, a)
    fb = evaluar_fx(clean_f, b)
    
    if fa * fb >= 0:
        return {"error": "El intervalo [a, b] no encierra una raíz (f(a) y f(b) tienen el mismo signo)."}

    pasos = []
    c_viejo = a
    c = a
    
    for i in range(1, max_iter + 1):
        c = (a + b) / 2.0
        fc = evaluar_fx(clean_f, c)
        error = abs((c - c_viejo) / c) * 100 if i > 1 else 100.0
        
        signo_fa = "+" if fa > 0 else "-"
        signo_fc = "+" if fc > 0 else "-"
        siguiente_int = f"[{fmt(c)}, {fmt(b)}]" if fa * fc > 0 else f"[{fmt(a)}, {fmt(c)}]"
        
        formula_c_latex = f"c_{{{i}}} = \\frac{{{fmt(a)} + {fmt(b)}}}{{2}} = {fmt(c)}"
        formula_fc_latex = f"f({fmt(c)}) = {fmt(fc)}"
        
        explicacion_manzanitas = (
            f"Paso {i}: Calculamos el punto medio $c_{{{i}}} = \\frac{{{fmt(a)} + {fmt(b)}}}{{2}} = {fmt(c)}$. "
            f"Evaluando la función se obtiene $f({fmt(c)}) = {fmt(fc)}$. "
            f"El nuevo intervalo de búsqueda se ajusta a ${siguiente_int}$."
        )

        pasos.append({
            "iteracion": i,
            "a": fmt(a),
            "b": fmt(b),
            "c": fmt(c),
            "fa": fmt(fa),
            "fb": fmt(fb),
            "fc": fmt(fc),
            "signo_fa": signo_fa,
            "signo_fc": signo_fc,
            "error": fmt(error, 2) + "%",
            "formula_c_latex": formula_c_latex,
            "formula_fc_latex": formula_fc_latex,
            "siguiente_intervalo": siguiente_int,
            "explicacion_manzanitas": explicacion_manzanitas
        })
        
        if abs(fc) < tol or error < tol:
            break
            
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
        c_viejo = c

    n_pasos = len(pasos)
    hitos = [pasos[0]]
    if n_pasos > 2:
        hitos.append(pasos[n_pasos // 2])
    if n_pasos > 1:
        hitos.append(pasos[-1])

    return {
        "metodo": "Bisección",
        "funcion_latex": f"f(x) = {f_latex}",
        "formula_general_latex": "c_k = \\frac{a_k + b_k}{2}",
        "raiz": fmt(c, 6),
        "iteraciones": len(pasos),
        "error_final": pasos[-1]["error"],
        "pasos": pasos,
        "hitos": hitos,
        "explicacion_manzanitas": f"Convergencia alcanzada en {len(pasos)} iteraciones. Raíz en $c = {fmt(c, 6)}$ con error del {pasos[-1]['error']}.",
        "nivel": nivel
    }

# ------------------------------------------------------------------
# 2. NEWTON-RAPHSON
# ------------------------------------------------------------------
def newton_raphson(f_str, x0, tol=0.0001, max_iter=50, nivel='sencillo'):
    clean_f = parse_input_math(f_str)
    x_sym = sp.Symbol('x')
    expr = sp.sympify(clean_f)
    df_expr = sp.diff(expr, x_sym)
    
    f_latex = sp.latex(expr)
    df_latex = sp.latex(df_expr)
    
    pasos = []
    xi = float(x0)
    xi_next = xi
    
    for i in range(1, max_iter + 1):
        f_val = float(expr.subs(x_sym, xi))
        df_val = float(df_expr.subs(x_sym, xi))
        
        if abs(df_val) < 1e-12:
            return {"error": f"La derivada se anula en x = {fmt(xi)} (división por cero)."}
            
        xi_next = xi - (f_val / df_val)
        error = abs((xi_next - xi) / xi_next) * 100 if xi_next != 0 else 0.0
        
        formula_paso_latex = f"x_{{{i}}} = {fmt(xi)} - \\frac{{{fmt(f_val)}}}{{{fmt(df_val)}}} = {fmt(xi_next)}"
        explicacion_manzanitas = (
            f"Paso {i}: Evaluamos $f({fmt(xi)}) = {fmt(f_val)}$ y la derivada $f'({fmt(xi)}) = {fmt(df_val)}$. "
            f"La nueva aproximación tangente es $x_{{{i}}} = {fmt(xi_next)}$."
        )
        
        pasos.append({
            "iteracion": i,
            "xi": fmt(xi),
            "f_xi": fmt(f_val),
            "df_xi": fmt(df_val),
            "xi_siguiente": fmt(xi_next),
            "error": fmt(error, 2) + "%",
            "formula_paso_latex": formula_paso_latex,
            "explicacion_manzanitas": explicacion_manzanitas
        })
        
        if abs(xi_next - xi) < tol or error < tol:
            break
        xi = xi_next

    n_pasos = len(pasos)
    hitos = [pasos[0]]
    if n_pasos > 2:
        hitos.append(pasos[n_pasos // 2])
    if n_pasos > 1:
        hitos.append(pasos[-1])

    return {
        "metodo": "Newton-Raphson",
        "funcion_latex": f"f(x) = {f_latex}",
        "derivada_latex": f"f'(x) = {df_latex}",
        "formula_general_latex": "x_{k+1} = x_k - \\frac{f(x_k)}{f'(x_k)}",
        "raiz": fmt(xi_next, 6),
        "iteraciones": len(pasos),
        "error_final": pasos[-1]["error"],
        "pasos": pasos,
        "hitos": hitos,
        "explicacion_manzanitas": f"Convergencia alcanzada en {len(pasos)} pasos. Raíz aproximada en $x = {fmt(xi_next, 6)}$.",
        "nivel": nivel
    }

# ------------------------------------------------------------------
# 3. INTERPOLACIÓN POLINOMIAL
# ------------------------------------------------------------------
def interpolacion_polinomial(x_pts, y_pts, x_eval, nivel='sencillo'):
    x_sym = sp.Symbol('x')
    puntos = list(zip(x_pts, y_pts))
    
    polinomio = sp.interpolate(puntos, x_sym)
    polinomio_exp = sp.expand(polinomio)
    resultado = float(polinomio_exp.subs(x_sym, x_eval))
    pol_latex = sp.latex(polinomio_exp)

    pasos = []
    for k, (xp, yp) in enumerate(puntos):
        pasos.append({
            "punto": f"P_{{{k+1}}}",
            "x": fmt(xp),
            "y": fmt(yp),
            "explicacion_manzanitas": f"Nodo $P_{{{k+1}}} = ({fmt(xp)}, {fmt(yp)})$: Punto de paso obligatorio para el polinomio interpolador."
        })

    eval_latex = f"P({fmt(x_eval)}) = {fmt(resultado, 4)}"
    explicacion_manzanitas = (
        f"Polinomio interpolador obtenido: $P(x) = {pol_latex}$. "
        f"Evaluando en $x = {fmt(x_eval)}$ se obtiene $P({fmt(x_eval)}) = {fmt(resultado, 4)}$."
    )

    return {
        "metodo": "Interpolación Polinomial",
        "polinomio_str": str(polinomio_exp),
        "polinomio_latex": f"P(x) = {pol_latex}",
        "evaluacion_latex": eval_latex,
        "x_eval": fmt(x_eval),
        "resultado": fmt(resultado, 4),
        "pasos": pasos,
        "explicacion_manzanitas": explicacion_manzanitas,
        "nivel": nivel
    }

# ------------------------------------------------------------------
# 4. DERIVACIÓN NUMÉRICA
# ------------------------------------------------------------------
def derivacion_numerica(f_str, x_val, h=0.001, tipo='centrada', nivel='sencillo'):
    clean_f = parse_input_math(f_str)
    x_sym = sp.Symbol('x')
    expr = sp.sympify(clean_f)
    f_latex = sp.latex(expr)

    fx = evaluar_fx(clean_f, x_val)
    fx_mas_h = evaluar_fx(clean_f, x_val + h)
    fx_menos_h = evaluar_fx(clean_f, x_val - h)

    if tipo == 'adelante':
        derivada = (fx_mas_h - fx) / h
        formula_gen_latex = "f'(x) \\approx \\frac{f(x+h) - f(x)}{h}"
        formula_paso_latex = f"f'({fmt(x_val)}) \\approx \\frac{{f({fmt(x_val + h)}) - f({fmt(x_val)})}}{{{fmt(h)}}} = {fmt(derivada, 4)}"
        explicacion_manzanitas = f"Diferencia hacia adelante entre $x = {fmt(x_val)}$ y $x + h = {fmt(x_val + h)}$."
    elif tipo == 'atras':
        derivada = (fx - fx_menos_h) / h
        formula_gen_latex = "f'(x) \\approx \\frac{f(x) - f(x-h)}{h}"
        formula_paso_latex = f"f'({fmt(x_val)}) \\approx \\frac{{f({fmt(x_val)}) - f({fmt(x_val - h)})}}{{{fmt(h)}}} = {fmt(derivada, 4)}"
        explicacion_manzanitas = f"Diferencia hacia atrás entre $x = {fmt(x_val)}$ y $x - h = {fmt(x_val - h)}$."
    else:
        derivada = (fx_mas_h - fx_menos_h) / (2 * h)
        formula_gen_latex = "f'(x) \\approx \\frac{f(x+h) - f(x-h)}{2h}"
        formula_paso_latex = f"f'({fmt(x_val)}) \\approx \\frac{{f({fmt(x_val + h)}) - f({fmt(x_val - h)})}}{{2 \\cdot {fmt(h)}}} = {fmt(derivada, 4)}"
        explicacion_manzanitas = f"Diferencia centrada promedio entre $x - h = {fmt(x_val - h)}$ y $x + h = {fmt(x_val + h)}$."

    pasos = [
        {
            "paso": 1,
            "x": fmt(x_val),
            "h": fmt(h),
            "esquema": tipo.capitalize(),
            "formula_paso_latex": formula_paso_latex,
            "derivada": fmt(derivada, 4),
            "explicacion_manzanitas": explicacion_manzanitas
        }
    ]

    return {
        "metodo": "Derivación Numérica",
        "funcion_latex": f"f(x) = {f_latex}",
        "tipo": tipo,
        "x": fmt(x_val),
        "h": fmt(h),
        "derivada": fmt(derivada, 4),
        "formula_general_latex": formula_gen_latex,
        "formula_paso_latex": formula_paso_latex,
        "pasos": pasos,
        "explicacion_manzanitas": explicacion_manzanitas,
        "nivel": nivel
    }

# ------------------------------------------------------------------
# 5. TRAPECIO COMPUESTO
# ------------------------------------------------------------------
def trapecio_compuesto(f_str, a, b, n=10, nivel='sencillo'):
    clean_f = parse_input_math(f_str)
    x_sym = sp.Symbol('x')
    expr = sp.sympify(clean_f)
    f_latex = sp.latex(expr)

    h = (b - a) / n
    x_vals = [a + i * h for i in range(n + 1)]
    y_vals = [evaluar_fx(clean_f, x) for x in x_vals]

    suma_intermedios = sum(y_vals[1:-1])
    area = (h / 2.0) * (y_vals[0] + 2 * suma_intermedios + y_vals[-1])

    formula_gen_latex = "I \\approx \\frac{h}{2} \\left[ f(x_0) + 2 \\sum_{i=1}^{n-1} f(x_i) + f(x_n) \\right]"
    formula_paso_latex = f"I \\approx \\frac{{{fmt(h)}}}{{2}} \\left[ {fmt(y_vals[0])} + 2({fmt(suma_intermedios)}) + {fmt(y_vals[-1])} \\right] = {fmt(area, 4)}"

    pasos = []
    for i in range(n + 1):
        peso = 1 if (i == 0 or i == n) else 2
        prod = peso * y_vals[i]
        pasos.append({
            "i": i,
            "xi": fmt(x_vals[i]),
            "f_xi": fmt(y_vals[i]),
            "peso": peso,
            "producto": fmt(prod),
            "explicacion_manzanitas": f"Nodo $i = {i}$: $x_{{{i}}} = {fmt(x_vals[i])}$, $f(x) = {fmt(y_vals[i])}$. Peso = {peso}."
        })

    explicacion_manzanitas = (
        f"Dividiendo en $n = {n}$ trapecios con ancho $h = {fmt(h)}$, "
        f"se obtiene un área integrada de $I \\approx {fmt(area, 4)}$."
    )

    return {
        "metodo": "Trapecio Compuesto",
        "funcion_latex": f"f(x) = {f_latex}",
        "formula_general_latex": formula_gen_latex,
        "formula_paso_latex": formula_paso_latex,
        "a": fmt(a),
        "b": fmt(b),
        "n": n,
        "h": fmt(h),
        "area_aproximada": fmt(area, 4),
        "suma_intermedios": fmt(suma_intermedios, 4),
        "pasos": pasos,
        "explicacion_manzanitas": explicacion_manzanitas,
        "nivel": nivel
    }

# ------------------------------------------------------------------
# 6. SIMPSON 1/3 COMPUESTO
# ------------------------------------------------------------------
def simpson_13(f_str, a, b, n=10, nivel='sencillo'):
    if n % 2 != 0:
        n += 1

    clean_f = parse_input_math(f_str)
    x_sym = sp.Symbol('x')
    expr = sp.sympify(clean_f)
    f_latex = sp.latex(expr)

    h = (b - a) / n
    x_vals = [a + i * h for i in range(n + 1)]
    y_vals = [evaluar_fx(clean_f, x) for x in x_vals]

    suma_impares = sum(y_vals[i] for i in range(1, n, 2))
    suma_pares = sum(y_vals[i] for i in range(2, n, 2))

    area = (h / 3.0) * (y_vals[0] + 4 * suma_impares + 2 * suma_pares + y_vals[-1])

    formula_gen_latex = "I \\approx \\frac{h}{3} \\left[ f(x_0) + 4 \\sum_{impares} f(x_i) + 2 \\sum_{pares} f(x_i) + f(x_n) \\right]"
    formula_paso_latex = f"I \\approx \\frac{{{fmt(h)}}}{{3}} \\left[ {fmt(y_vals[0])} + 4({fmt(suma_impares)}) + 2({fmt(suma_pares)}) + {fmt(y_vals[-1])} \\right] = {fmt(area, 4)}"

    pasos = []
    for i in range(n + 1):
        peso = 1 if (i == 0 or i == n) else (4 if i % 2 != 0 else 2)
        prod = peso * y_vals[i]
        pasos.append({
            "i": i,
            "xi": fmt(x_vals[i]),
            "f_xi": fmt(y_vals[i]),
            "peso": peso,
            "producto": fmt(prod),
            "explicacion_manzanitas": f"Nodo $i = {i}$: $x_{{{i}}} = {fmt(x_vals[i])}$, $f(x) = {fmt(y_vals[i])}$. Peso = {peso}."
        })

    explicacion_manzanitas = (
        f"Ajustando parábolas sobre $n = {n}$ subintervalos ($h = {fmt(h)}$), "
        f"el área integrada resulta $I \\approx {fmt(area, 4)}$."
    )

    return {
        "metodo": "Simpson 1/3 Compuesto",
        "funcion_latex": f"f(x) = {f_latex}",
        "formula_general_latex": formula_gen_latex,
        "formula_paso_latex": formula_paso_latex,
        "a": fmt(a),
        "b": fmt(b),
        "n": n,
        "h": fmt(h),
        "area_aproximada": fmt(area, 4),
        "suma_impares": fmt(suma_impares, 4),
        "suma_pares": fmt(suma_pares, 4),
        "pasos": pasos,
        "explicacion_manzanitas": explicacion_manzanitas,
        "nivel": nivel
    }

# ------------------------------------------------------------------
# 7. MÉTODO DE EULER
# ------------------------------------------------------------------
def euler(f_str, x0, y0, h, n, nivel='sencillo'):
    clean_f = parse_input_math(f_str)
    x_sym, y_sym = sp.symbols('x y')
    expr = sp.sympify(clean_f)
    f_latex = sp.latex(expr)

    pasos = []
    xi, yi = float(x0), float(y0)

    for i in range(n + 1):
        dydx = evaluar_fxy(clean_f, xi, yi)
        yi_next = yi + h * dydx
        formula_paso_latex = f"y_{{{i+1}}} = {fmt(yi)} + {fmt(h)} \\cdot ({fmt(dydx)}) = {fmt(yi_next)}"
        explicacion_manzanitas = (
            f"Paso {i}: En $(x = {fmt(xi)}, y = {fmt(yi)})$, la pendiente $\\frac{{dy}}{{dx}} = {fmt(dydx)}$. "
            f"Avanzando paso $h = {fmt(h)}$ resulta $y_{{{i+1}}} = {fmt(yi_next)}$."
        )
        pasos.append({
            "paso": i,
            "xi": fmt(xi),
            "yi": fmt(yi),
            "dydx": fmt(dydx),
            "yi_next": fmt(yi_next),
            "formula_paso_latex": formula_paso_latex,
            "explicacion_manzanitas": explicacion_manzanitas
        })
        yi = yi_next
        xi = xi + h

    n_pasos = len(pasos)
    hitos = [pasos[0]]
    if n_pasos > 2:
        hitos.append(pasos[n_pasos // 2])
    if n_pasos > 1:
        hitos.append(pasos[-1])

    return {
        "metodo": "Método de Euler",
        "funcion_latex": f"\\frac{{dy}}{{dx}} = {f_latex}",
        "formula_general_latex": "y_{k+1} = y_k + h \\cdot f(x_k, y_k)",
        "x0": fmt(x0),
        "y0": fmt(y0),
        "h": fmt(h),
        "n": n,
        "pasos": pasos,
        "hitos": hitos,
        "y_final": fmt(pasos[-2]["yi_next"] if len(pasos) > 1 else y0, 4),
        "explicacion_manzanitas": f"Solución aproximada para $n = {n}$ pasos: $y({fmt(xi)}) = {fmt(pasos[-2]['yi_next'] if len(pasos)>1 else y0, 4)}$.",
        "nivel": nivel
    }

# ------------------------------------------------------------------
# 8. GAUSS-JORDAN
# ------------------------------------------------------------------
def gauss_jordan(A_mat, b_vec, nivel='sencillo'):
    n = len(A_mat)
    M = [A_mat[i][:] + [b_vec[i]] for i in range(n)]
    mat_inicial_latex = mat_to_latex(M)
    
    pasos = []
    pasos.append({
        "paso": 0,
        "operacion": "Matriz Inicial [ A | b ]",
        "por_que": "Matriz aumentada del sistema original.",
        "explicacion_manzanitas": "Inicio del sistema: Matriz aumentada $[A | b]$.",
        "matriz": [[fmt(x) for x in row] for row in M],
        "matriz_latex": mat_to_latex(M),
        "pivote": None
    })
    
    paso_cnt = 1
    for i in range(n):
        if abs(M[i][i]) < 1e-12:
            max_row = i
            for k in range(i + 1, n):
                if abs(M[k][i]) > abs(M[max_row][i]):
                    max_row = k
            if max_row != i:
                M[i], M[max_row] = M[max_row], M[i]
                pasos.append({
                    "paso": paso_cnt,
                    "operacion": f"Intercambiar Fila {i+1} con Fila {max_row+1}",
                    "por_que": "Pivoteo para evitar división por cero.",
                    "explicacion_manzanitas": f"Paso {paso_cnt}: Intercambiamos Fila {i+1} con Fila {max_row+1}.",
                    "matriz": [[fmt(x) for x in row] for row in M],
                    "matriz_latex": mat_to_latex(M),
                    "pivote": (i, i)
                })
                paso_cnt += 1

        pivote = M[i][i]
        if abs(pivote) < 1e-12:
            return {"error": "El sistema no tiene solución única (pivote nulo)."}

        if abs(pivote - 1.0) > 1e-12:
            val_piv_str = fmt(pivote)
            for j in range(n + 1):
                M[i][j] /= pivote
            pasos.append({
                "paso": paso_cnt,
                "operacion": f"Fila {i+1} = Fila {i+1} / {val_piv_str}",
                "por_que": "Convertir pivote diagonal en 1.",
                "explicacion_manzanitas": f"Paso {paso_cnt}: Normalizamos la Fila {i+1} dividiendo todos sus elementos entre {val_piv_str}.",
                "matriz": [[fmt(x) for x in row] for row in M],
                "matriz_latex": mat_to_latex(M),
                "pivote": (i, i)
            })
            paso_cnt += 1

        for k in range(n):
            if k != i:
                factor = M[k][i]
                if abs(factor) > 1e-12:
                    val_fac_str = fmt(factor)
                    for j in range(n + 1):
                        M[k][j] -= factor * M[i][j]
                    pasos.append({
                        "paso": paso_cnt,
                        "operacion": f"Fila {k+1} = Fila {k+1} - ({val_fac_str}) * Fila {i+1}",
                        "por_que": "Hacer 0 los elementos fuera de la diagonal.",
                        "explicacion_manzanitas": f"Paso {paso_cnt}: Anulamos la columna {i+1} en la Fila {k+1} restando ({val_fac_str}) * Fila {i+1}.",
                        "matriz": [[fmt(x) for x in row] for row in M],
                        "matriz_latex": mat_to_latex(M),
                        "pivote": (i, i)
                    })
                    paso_cnt += 1

    soluciones = [fmt(M[i][n], 4) for i in range(n)]
    mat_final_latex = mat_to_latex(M)

    return {
        "metodo": "Gauss-Jordan",
        "matriz_inicial_latex": mat_inicial_latex,
        "matriz_final_latex": mat_final_latex,
        "soluciones": soluciones,
        "soluciones_latex": "X = \\begin{bmatrix} " + " \\\\ ".join(soluciones) + " \\end{bmatrix}",
        "pasos": pasos,
        "explicacion_manzanitas": "Transformación matricial Gauss-Jordan completada con éxito.",
        "nivel": nivel
    }

# ------------------------------------------------------------------
# 9. GAUSS-SEIDEL
# ------------------------------------------------------------------
def gauss_seidel(A_mat, b_vec, x0=None, tol=0.0001, max_iter=50, nivel='sencillo'):
    n = len(A_mat)
    if x0 is None:
        x0 = [0.0] * n
    
    es_dominante = True
    detalles_dom = []
    for i in range(n):
        diag = abs(A_mat[i][i])
        suma_otros = sum(abs(A_mat[i][j]) for j in range(n) if j != i)
        if diag <= suma_otros:
            es_dominante = False
            detalles_dom.append(f"Fila {i+1}: |{fmt(A_mat[i][i])}| <= {fmt(suma_otros)} (No estrictamente dominante)")
        else:
            detalles_dom.append(f"Fila {i+1}: |{fmt(A_mat[i][i])}| > {fmt(suma_otros)} (Dominante)")

    x = list(x0)
    historial = []

    for iter_num in range(1, max_iter + 1):
        x_viejo = list(x)
        desglose = []
        pasos_desglosados = []
        
        for i in range(n):
            suma = sum(A_mat[i][j] * x[j] for j in range(n) if j != i)
            x[i] = (b_vec[i] - suma) / A_mat[i][i]
            
            expr_tex = f"x_{{{i+1}}} = \\frac{{{fmt(b_vec[i])} - ({fmt(suma, 4)})}}{{{fmt(A_mat[i][i])}}} = {fmt(x[i], 4)}"
            desglose.append(expr_tex)
            pasos_desglosados.append({
                "variable": f"x_{{{i+1}}}",
                "formula_latex": expr_tex,
                "resultado": fmt(x[i], 4)
            })
        
        errores = [abs((x[i] - x_viejo[i]) / x[i]) * 100 if x[i] != 0 else 0.0 for i in range(n)]
        error_max = max(errores)

        historial.append({
            "iteracion": iter_num,
            "vector_x": [fmt(val, 4) for val in x],
            "error_max": fmt(error_max, 2) + "%",
            "desglose": desglose,
            "pasos_variables": pasos_desglosados,
            "explicacion_manzanitas": f"Iteración {iter_num}: Se despejan y actualizan las variables secuencialmente en tiempo real."
        })

        if error_max < tol:
            break

    n_pasos = len(historial)
    hitos = [historial[0]]
    if n_pasos > 2:
        hitos.append(historial[n_pasos // 2])
    if n_pasos > 1:
        hitos.append(historial[-1])

    return {
        "metodo": "Gauss-Seidel",
        "soluciones": [fmt(val, 4) for val in x],
        "iteraciones": len(historial),
        "error_final": historial[-1]["error_max"],
        "diagonal_dominante": es_dominante,
        "detalles_dominancia": detalles_dom,
        "pasos": historial,
        "hitos": hitos,
        "explicacion_manzanitas": f"Convergencia alcanzada en {len(historial)} iteraciones (Error máximo final: {historial[-1]['error_max']}).",
        "nivel": nivel
    }