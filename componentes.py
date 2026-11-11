"""
Módulo pedagógico de niveles de explicación sin emojis.
"""

def obtener_explicacion_nivel(nivel: str) -> dict:
    guias = {
        "sencillo": {
            "titulo": "Nivel Sencillo: Aprendizaje Paso a Paso Desglosado",
            "descripcion": "Explicación detallada con glosarios, justificación de operaciones y fórmulas sustituidas en formato matemático."
        },
        "normal": {
            "titulo": "Nivel Normal: Estándar Académico Completo",
            "descripcion": "Desarrollo completo en formato de tabla académica formal con todas las iteraciones para auditar la práctica."
        },
        "avanzado": {
            "titulo": "Nivel Avanzado: Resumen Ejecutivo y Tabla Sintética de Hitos",
            "descripcion": "Panel de indicadores clave (KPIs) y tabla sintética de hitos (Inicio, Intermedio y Convergencia Final) sin sobrecarga visual."
        }
    }
    return guias.get(nivel, guias["normal"])