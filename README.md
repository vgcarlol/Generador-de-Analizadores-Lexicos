# Proyecto de Generador de Analizadores Léxicos

Este proyecto implementa una herramienta en Python capaz de generar un analizador léxico funcional a partir de un archivo de especificación escrito en el lenguaje YALex. Además, se genera un gráfico (en formato PNG) que muestra el árbol de expresión combinado, el cual representa la definición regular de los componentes léxicos (tokens).

## Características del Proyecto

- **Conversión de expresiones regulares:**  
  Conversión de expresiones regulares de notación infija a notación postfix.

- **Construcción directa de AFD:**  
  Generación directa de un Autómata Finito Determinista (AFD) a partir de la expresión regular en postfix.

- **Minimización del AFD:**  
  Reducción del número de estados mediante técnicas de minimización basadas en la teoría de autómatas finitos.

- **Visualización:**  
  - Visualización del AFD generado utilizando Graphviz.
  - Generación de un único gráfico que une los árboles sintácticos de cada regla (es decir, de la especificación completa de tokens).

- **Simulación:**  
  Simulación de cadenas de entrada para verificar si son aceptadas o rechazadas por el AFD.

- **Generación Automática del Analizador:**  
  A partir del archivo YALex se genera automáticamente un programa fuente (por ejemplo, `thelexer.py`) que implementa el analizador léxico.

## Flujo de Ejecución

El proyecto se utiliza en dos etapas principales:

1. **Generación del Analizador y del Árbol de Expresión**  
   Ejecuta el siguiente comando:
   ```bash
   python yalex_generator.py lexer.yal thelexer.py
   ```
   Esto realiza lo siguiente:
   - Procesa el archivo `lexer.yal` para extraer el header, definiciones y reglas.
   - Para cada regla, se realiza la conversión (sustitución de definiciones, infix a postfix), se construye y minimiza el AFD.
   - Se genera el archivo fuente `thelexer.py`, que implementa el analizador léxico.
   - Se combinan las expresiones finales (de las reglas no triviales) en una mega expresión, y se construye un único árbol de expresión que se grafica en `combined_syntax_tree.png`.

2. **Ejecución del Analizador Léxico**  
   Una vez generado `thelexer.py`, ejecuta:
   ```bash
   python thelexer.py archivo_entrada.txt
   ```
   Este comando procesa el archivo de entrada, muestra en consola los tokens identificados o los errores léxicos en caso de no haber coincidencias.

## Cuadro de Requerimientos y Cumplimiento

| **Requerimiento / Objetivo**                                                                                          | **Cumple** | **Comentarios**                                                                                                                    |
|-----------------------------------------------------------------------------------------------------------------------|:----------:|------------------------------------------------------------------------------------------------------------------------------------|
| **Objetivo General:** Implementar un Generador de Analizadores Léxicos                                                 |     ✓      | Se genera automáticamente el analizador léxico a partir de la especificación YALex.                                                |
| **Específico 1:** Aplicar la teoría de analizadores léxicos (postfix, AFD, minimización)                                |     ✓      | Se convierten expresiones regulares a postfix, se construye y minimiza el AFD usando técnicas de autómatas finitos.                   |
| **Específico 2:** Generar un programa fuente que implemente un analizador léxico basado en la especificación YALex       |     ✓      | Se genera el archivo `thelexer.py` que contiene el analizador léxico completo.                                                     |
| **Específico 3:** Visualización del árbol de expresión que representa la definición regular de tokens                  |     ✓      | Se genera un único gráfico, `combined_syntax_tree.png`, que agrupa los árboles sintácticos de las reglas definidas en el YALex.        |
| **Funcionamiento del Analizador (Entrada):** Archivo de texto plano con cadenas de caracteres                         |     ✓      | `thelexer.py` lee el archivo de entrada y simula el análisis léxico.                                                               |
| **Funcionamiento del Analizador (Salida):** Impresión en pantalla de tokens o mensajes de error léxico                  |     ✓      | Se muestran los tokens reconocidos o un mensaje de error en caso de que no se encuentre transición para algún carácter.              |

## Instalación

1. **Clona el repositorio:**
    ```sh
    git clone https://github.com/vgcarlol/Construccion-Directa-de-AFD
    ```
2. **Navega al directorio del proyecto:**
    ```sh
    cd Construccion-Directa-de-AFD/
    ```
3. **Instala las dependencias:**
    ```sh
    pip install -r requirements.txt
    ```
   > Nota: Si encuentras problemas con `graphviz`, revisa la configuración o consulta la documentación oficial: [Graphviz Downloads](https://graphviz.gitlab.io/download/).

## Uso

1. **Generación del Analizador y del Árbol de Expresión:**
   ```sh
   python yalex_generator.py lexer.yal thelexer.py
   ```
   Esto creará:
   - El archivo fuente `thelexer.py`.
   - El gráfico `combined_syntax_tree.png` que muestra el árbol combinado de las definiciones regulares.

2. **Ejecución del Analizador Léxico:**
   ```sh
   python thelexer.py archivo_entrada.txt
   ```
   Se mostrará en consola la impresión de los tokens o los mensajes de error.


## Videos de Ejecución y Explicación

- **Construcción Directa:**
  - [Video de Ejecución](https://youtu.be/gBHMyWfz9Ow)
  - [Video de Explicación](https://youtu.be/0_EHSKtklvI)


## Notas Adicionales

- La herramienta procesa el archivo YALex y extrae header, definiciones y reglas para generar el analizador y la visualización del árbol de expresión.
- El árbol de expresión combinado se genera a partir de la unión de las expresiones de cada regla (excluyendo las triviales, como espacios y saltos).
- Se recomienda revisar los logs y la salida gráfica para depurar en caso de errores inesperados.

## Desarrollador

- **Carlos Valladares**
