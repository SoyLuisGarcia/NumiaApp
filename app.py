from flask import Flask, render_template, request, jsonify
import calculos
import componentes

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    datos = request.get_json()
    metodo = datos.get('metodo')
    nivel = datos.get('nivel', 'sencillo')

    try:
        if metodo == 'biseccion':
            res = calculos.biseccion(
                datos['funcion'], float(datos['a']), float(datos['b']),
                float(datos.get('tol', 0.0001)), int(datos.get('max_iter', 50)), nivel
            )
        elif metodo == 'newton':
            res = calculos.newton_raphson(
                datos['funcion'], float(datos['x0']),
                float(datos.get('tol', 0.0001)), int(datos.get('max_iter', 50)), nivel
            )
        elif metodo == 'polinomial':
            x_pts = [float(v.strip()) for v in datos['x_pts'].split(',') if v.strip()]
            y_pts = [float(v.strip()) for v in datos['y_pts'].split(',') if v.strip()]
            res = calculos.interpolacion_polinomial(x_pts, y_pts, float(datos['x_eval']), nivel)
        elif metodo == 'derivacion':
            res = calculos.derivacion_numerica(
                datos['funcion'], float(datos['x']), float(datos.get('h', 0.001)),
                datos.get('tipo', 'centrada'), nivel
            )
        elif metodo == 'trapecio':
            res = calculos.trapecio_compuesto(
                datos['funcion'], float(datos['a']), float(datos['b']),
                int(datos.get('n', 10)), nivel
            )
        elif metodo == 'simpson':
            res = calculos.simpson_13(
                datos['funcion'], float(datos['a']), float(datos['b']),
                int(datos.get('n', 10)), nivel
            )
        elif metodo == 'euler':
            res = calculos.euler(
                datos['funcion'], float(datos['x0']), float(datos['y0']),
                float(datos['h']), int(datos['n']), nivel
            )
        elif metodo in ['gauss_jordan', 'gauss_seidel']:
            raw_matrix = datos.get('matriz_raw', '')
            A, b = calculos.parse_matrix_input(raw_matrix)
            if metodo == 'gauss_jordan':
                res = calculos.gauss_jordan(A, b, nivel)
            else:
                res = calculos.gauss_seidel(
                    A, b, None,
                    float(datos.get('tol', 0.0001)), int(datos.get('max_iter', 50)), nivel
                )
        else:
            res = {"error": "Método numérico no reconocido."}
            
        res["meta_didactica"] = componentes.obtener_explicacion_nivel(nivel)
        return jsonify(res)

    except Exception as e:
        return jsonify({"error": f"Error de cómputo: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)