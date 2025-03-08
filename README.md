# Proyecto de Construcción Directa de AFD

Este proyecto implementa la construcción directa de un Autómata Finito Determinista (AFD) a partir de una expresión regular dada en notación postfix. Además, incluye la minimización del AFD y la simulación de cadenas de entrada para verificar su aceptación.

## Características del Proyecto

- Conversión de expresiones regulares en notación infija a postfix.
- Construcción directa de un AFD a partir de la expresión regular en postfix.
- Minimización del AFD para reducir el número de estados.
- Visualización del AFD utilizando `graphviz`.
- Simulación de cadenas de entrada para verificar su aceptación.
- Sistema de pruebas unitarias para validar la correcta construcción y funcionamiento del AFD.

## VIDEOS DE EXPLICACIÓN Y EJECUCIÓN:

Construcción Directa:
- [Video de Ejecución](https://youtu.be/gBHMyWfz9Ow)
- [Video de Explicación](https://youtu.be/0_EHSKtklvI)

Simulación de un AFN
- [Video de Ejecución](https://youtu.be/qiqhd0nq3HU)
- Video de explicación no sé si sea necesario al ser un proyecto ya explicado a Bidkar el semestre pasado (Proyecto 1 - Teoría de la Computación)

## Requisitos

- Python 3.x
- Las dependencias del proyecto se encuentran en el archivo `requirements.txt`. (Aunque, debido a errores en el computador, se dejó la dependencia de manera fija en la carpeta raíz de este proyecto).

## Instalación

1. Clona este repositorio:
    ```sh
    git clone https://github.com/vgcarlol/Construccion-Directa-de-AFD
    ```
2. Navega al directorio del proyecto:
    ```sh
    cd Construccion-Directa-de-AFD/
    ```
3. Instala las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

## Uso

1. Ejecuta el programa principal:
    ```sh
    python ./src/main.py
    ```
2. Ingresa la expresión regular y la cadena a evaluar cuando el programa lo solicite.
3. El programa generará y visualizará el AFD y mostrará si la cadena es aceptada o no.

## Dependencias

El proyecto utiliza `graphviz` para la generación de gráficos de los autómatas. Asegúrate de tenerlo instalado y configurado correctamente.

Para instalar `graphviz`, ejecuta:
```sh
pip install graphviz
```
Si tienes problemas con `graphviz`, revisa la documentación oficial: https://graphviz.gitlab.io/download/. Aunque predeterminadamente se encuentra dentro de la carpeta src/ debido a que en mi computador si causa problemas.

## Notas

- La expresión regular ingresada se convierte automáticamente a postfix antes de generar el AFD.
- La implementación de la minimización del AFD está basada en la división de estados en conjuntos equivalentes.
- El simulador del AFD maneja transiciones ε y evalúa correctamente si una cadena pertenece o no al lenguaje definido por la expresión regular.
- Se recomienda revisar los logs generados para depuración en caso de errores inesperados.

## Ejecución de Pruebas

Para ejecutar las pruebas unitarias y verificar el correcto funcionamiento del AFD, ejecuta:
```sh
python -m unittest discover -s ./tests
```

## Desarrolladores:
- Carlos Valladares

