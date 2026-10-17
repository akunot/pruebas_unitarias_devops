# Informe — Taller de Análisis y Mejora de Pruebas Unitarias

## 1. Datos

| Campo | Valor |
|---|---|
| Estudiante | Sergio Alejandro Castro Botero |
| Usuario de GitHub | [akunot](https://github.com/akunot) |
| Curso | Introducción a DevOps — Universidad Nacional de Colombia, Sede Manizales |
| Profesor | Cesar Augusto Palacios Alarcón |
| Fecha | 17 de octubre de 2026 |
| Repositorio | <https://github.com/akunot/pruebas_unitarias_devops> |

**Resumen.** Se escribieron **72 funciones de prueba** (que al parametrizarse generan **160 casos**) para cuatro módulos: `calculadora`, `descuentos` (obligatorios), `conversor` (tercer módulo elegido) y `csv_parser` (extra, con *mocking*). Las pruebas revelaron y permitieron corregir **8 bugs**. Todos los casos pasan y la cobertura de los módulos trabajados es del 100 % (97 % en `csv_parser`, ver sección 4). Además, el repositorio ejecuta las pruebas automáticamente en cada `push` con GitHub Actions.

### Cómo ejecutar

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Metodología

Cada prueba sigue la estructura **AAA** (*Arrange–Act–Assert*), marcada con comentarios, y tiene un nombre que describe el comportamiento esperado (`test_minimo_con_todos_positivos`, `test_kelvin_negativo_lanza_error`). Para cada función me pregunté *“¿qué entrada la rompería?”* y probé tres familias de casos:

1. **Caso típico**: el uso normal de la función.
2. **Casos límite**: el cero, los extremos de un rango (0 % y 100 %), las fronteras exactas entre tramos (9 → 10 unidades) y las listas de un solo elemento.
3. **Entradas inválidas**: negativos, valores fuera de rango y listas vacías, verificando con `pytest.raises` que se lance `ValueError`.

Usé `pytest.mark.parametrize` para cubrir muchas entradas sin duplicar código, y `pytest.approx` para comparar números de punto flotante (porque `0.1 + 0.2 != 0.3` en binario). El flujo de trabajo quedó registrado en el historial de commits: primero el commit con las pruebas que fallan (la evidencia del bug) y después un commit `fix:` por cada corrección.

## 2. Análisis por módulo

### 2.1 `calculadora.py` (obligatorio) — 22 pruebas, 41 casos

**Qué hace.** Operaciones aritméticas (`sumar`, `restar`, `multiplicar`, `dividir`, `potencia`, `raiz_cuadrada`), estadísticas sobre listas (`promedio`, `maximo`, `minimo`) y área y perímetro de un rectángulo.

**Casos probados y por qué.**
- **Signos combinados** en suma y multiplicación (positivo × negativo, negativo × negativo, × 0), porque los errores de signo son los más comunes en aritmética.
- **Decimales** con `approx`, para no confundir el error de redondeo propio del punto flotante con un bug.
- **División por cero** y **potencias límite** (`0**0`, exponente 0, exponente negativo, base negativa con exponente impar).
- **Raíz cuadrada** de 0, 1, un cuadrado perfecto, un irracional y **un negativo**: el negativo es el caso que “rompe” la función.
- **Mínimo y máximo** con listas solo positivas, solo negativas, con repetidos y de un elemento. La lista solo de positivos fue clave: un algoritmo de mínimo que arranca en un valor fijo solo falla cuando todos los elementos son mayores que ese valor.
- **Listas vacías** en `promedio`, `maximo` y `minimo`, y **lados negativos o en cero** en el rectángulo (el 0 es el límite permitido).

### 2.2 `descuentos.py` (obligatorio) — 18 pruebas, 40 casos

**Qué hace.** Aplica porcentajes de descuento a precios: un descuento simple, el monto descontado, el precio final con impuesto, descuentos por volumen en tramos y la combinación de varios descuentos (encadenados o apilados).

**Casos probados y por qué.**
- **Límites del porcentaje**: 0 %, 100 % y valores justo por fuera (−0.01 % y 100.01 %), porque el validador usa `<` y `>` y un error de `<=` se escondería ahí.
- **Precio final** con un caso calculado a mano (100 − 20 % = 80; 80 + 19 % de IVA = 95.2). Es un caso realista para Colombia, y comparar contra un valor calculado a mano es lo que expuso el bug del impuesto.
- **Las 9 fronteras de `descuento_por_volumen`** (0, 9, 10, 19, 20, 49, 50, 99, 100 unidades). En funciones por tramos los errores aparecen justo en el valor donde cambia el tramo.
- **Diferencia entre acumulativo y apilado**: 10 % + 20 % encadenados dan 72 y apilados dan 70. Verificar ambos asegura que cada función implementa su propia regla de negocio.
- **Descuentos apilados que suman más de 100 %** y **descuentos negativos escondidos en la lista**: son las entradas con las que un usuario podría pagar menos de cero o más del precio original.

### 2.3 `conversor.py` (tercer módulo elegido) — 13 pruebas, 52 casos

**Por qué lo elegí.** Las conversiones de unidades tienen una propiedad fácil de verificar: **ir y volver debe devolver el valor original**. Esa propiedad permite probar 12 funciones con pocas pruebas bien diseñadas y es justo el tipo de error que se cuela en producción sin que nadie lo note.

**Casos probados y por qué.**
- **Puntos de referencia físicos**: 0 °C = 32 °F, 100 °C = 212 °F, −40 °C = −40 °F (el punto donde ambas escalas coinciden) y 0 K = −273.15 °C.
- **Cero absoluto**: 0 K debe aceptarse y cualquier valor por debajo debe rechazarse.
- **Ida y vuelta** para los 6 pares de conversión (metros–km, libras–kg, galones–litros, millas–km, pies–metros, onzas–gramos), parametrizado. Esta prueba fue la que delató a `kilometros_a_millas`.
- **Un dato real**: una maratón mide 42.195 km ≈ 26.219 millas.
- **Cero y negativos** en las 12 funciones de distancia, peso y volumen, verificando que todas validen igual.

### 2.4 `csv_parser.py` (extra, con *mocking*) — 19 pruebas, 27 casos

**Qué hace.** Convierte texto CSV en listas o diccionarios, valida su forma, extrae y filtra columnas y cuenta filas y columnas.

**Uso de mocking (sin leer archivos reales).**
- `mock_open` simula un archivo `datos/clientes.csv`: la prueba “abre” y lee el archivo, verifica con qué ruta se llamó `open` y procesa el contenido sin que exista nada en disco.
- `patch.object(csv_parser, "parse_csv_line")` reemplaza el parser de una línea para probar **en aislamiento** que `leer_csv_como_lista` llama al parser una vez por línea, en orden, y que `contar_columnas` solo analiza la cabecera. Así, si falla la lectura del documento, la prueba apunta a esa función y no al parser.

**Casos probados y por qué.** Comas dentro de campos entre comillas (`"Manizales, Caldas"`), comillas escapadas (`""`), campos vacíos, filas con menos y con más columnas que la cabecera, CSV vacío, CSV con solo la cabecera e índices de columna inexistentes. Son los formatos que realmente aparecen en archivos exportados desde Excel.

## 3. Tabla de bugs

Se encontraron y corrigieron **8 bugs**: 6 en los módulos obligatorios y en el elegido, y 2 en `csv_parser` (módulo no obligatorio).

| # | Función | Entrada que lo revela | Resultado erróneo | Resultado esperado | Corrección aplicada |
|---|---|---|---|---|---|
| 1 | `calculadora.raiz_cuadrada` | `raiz_cuadrada(-9)` | Devuelve el complejo `(1.8e-16+3j)` sin avisar | `ValueError` | Validar `numero < 0` y lanzar `ValueError` antes de calcular |
| 2 | `calculadora.minimo` | `minimo([3, 5, 7])` | `0` (un valor que ni siquiera está en la lista) | `3` | Inicializar `min_val = lista[0]` en lugar de `0` |
| 3 | `descuentos.calcular_precio_final` | `(100, impuesto=19, descuento=20)` | `99.0` (IVA de 19 calculado sobre 100) | `95.2` (IVA de 15.2 calculado sobre 80) | Calcular el impuesto sobre `precio_con_descuento`, no sobre `precio` |
| 4 | `descuentos.descuento_apilado` | `(100, [60, 50])` y `(100, [-10, 20])` | El primero lanza un error confuso (“el porcentaje debe estar entre 0 y 100”) aunque cada descuento es válido; el segundo acepta el −10 % y devuelve 90 | `0` (el total se limita al 100 %) y `ValueError` | Validar cada descuento en [0, 100] y limitar la suma con `min(sum(...), 100)` |
| 5 | `conversor.kelvin_a_celsius` | `kelvin_a_celsius(-10)` | `-283.15` (temperatura físicamente imposible) | `ValueError` | Validar `kelvin < 0` (por debajo del cero absoluto) |
| 6 | `conversor.kilometros_a_millas` | `kilometros_a_millas(42.195)` | `67.906` | `≈ 26.219` | Dividir por 1.60934 en vez de multiplicar |
| 7 | `csv_parser.parse_csv_line` | `'Ana,"Manizales, Caldas",30'` | `['Ana', '"Manizales', ' Caldas"', '30']` (4 campos) | `['Ana', 'Manizales, Caldas', '30']` | Usar `csv.reader` de la librería estándar cuando la línea contiene comillas |
| 8 | `csv_parser.csv_a_diccionarios` | Fila `Luis,Pereira` con cabecera `nombre,ciudad,edad`; fila `Ana,30,extra` con cabecera `nombre,edad` | Diccionario sin la clave `edad` (`KeyError` más adelante); el valor `extra` se pierde en silencio | `{"edad": ""}` y `ValueError` | Completar columnas faltantes con `""` y lanzar `ValueError` si sobran columnas |

**Decisiones de diseño en las correcciones.** En los bugs 4 y 8 el comportamiento “correcto” no era obvio y tuve que decidirlo. Para el descuento apilado elegí **limitar al 100 %** (el producto queda gratis) en vez de lanzar un error, porque sumar promociones válidas no es un error del usuario. Para el CSV elegí **rellenar con vacío** cuando faltan columnas (igual que ya hacía `extraer_columna`) y **fallar** cuando sobran, porque descartar datos sin avisar es peor que detener el proceso. Las pruebas dejan escritas estas decisiones como especificación.

**Commits de cada corrección** (`git log --oneline`):

```
fix: raiz_cuadrada con negativos lanza ValueError
fix: minimo inicia con el primer elemento de la lista y no con 0
fix: calcular_precio_final aplica el impuesto sobre el precio con descuento
fix: descuento_apilado valida cada descuento y limita el total al 100%
fix: kelvin_a_celsius rechaza valores por debajo del cero absoluto
fix: kilometros_a_millas divide por 1.60934 en lugar de multiplicar
fix: parse_csv_line respeta comas y comillas escapadas dentro de campos entre comillas
fix: csv_a_diccionarios completa columnas faltantes y rechaza filas con columnas de mas
```

## 4. Cobertura

Salida de `pytest tests/ -v --cov=src --cov-report=term-missing` (al final de la ejecución):

```
---------- coverage: platform linux, python 3.13.16-final-0 ----------
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
src/__init__.py                0      0   100%
src/autenticacion.py          42     42     0%   6-77
src/calculadora.py            44      0   100%
src/conversor.py              58      0   100%
src/csv_parser.py             75      2    97%   66, 124
src/descuentos.py             61      0   100%
src/fibonacci.py              42     42     0%   6-73
src/manipulador_texto.py      93     93     0%   6-156
src/procesador_texto.py       49     49     0%   6-84
src/utils.py                  53     53     0%   6-92
src/validador.py              64     64     0%   6-117
--------------------------------------------------------
TOTAL                        581    345    41%

============================= 160 passed in 0.43s ==============================
```

**Lectura de los resultados.**
- **La meta de ≥ 85 % se cumple en los cuatro módulos trabajados**: 100 % en `calculadora`, `descuentos` y `conversor`, y 97 % en `csv_parser`.
- **El 41 % total no es una falla**: es el promedio ponderado de todo `src/`, que incluye seis módulos que no estaban dentro del alcance del taller (por eso aparecen en 0 %). Si se mide solo lo trabajado (238 sentencias, 2 sin ejecutar), la cobertura es del **99,2 %**.
- **Las 2 líneas sin cubrir de `csv_parser` (66 y 124) son código inalcanzable.** Ambas son `if len(lineas) == 0`, pero `str.split('\n')` siempre devuelve al menos un elemento, y el contenido vacío ya se descartó antes con `if not contenido_csv`. Ninguna entrada puede ejecutar esas líneas. Escribir una prueba “trampa” para llegar al 100 % no aportaría nada; lo correcto sería eliminarlas en un refactor.

## 5. Integración continua (extra)

El archivo `.github/workflows/pruebas.yml` ejecuta la batería completa con cobertura **en cada `push` y cada *pull request***, con Python 3.10 (la versión mínima que pide el taller) y 3.12. Así ningún cambio que rompa una prueba puede pasar inadvertido. El resultado se ve en la pestaña **Actions** del repositorio.

## 6. Reflexión final

**¿Qué no mide la cobertura?** La cobertura dice qué líneas se *ejecutaron*, no si el resultado fue *correcto*. El caso de `calcular_precio_final` lo muestra bien: una prueba que solo llamara a la función con descuento 0 habría ejecutado todas sus líneas (100 % de cobertura) y aun así habría pasado, porque sin descuento el precio original y el precio descontado son iguales y el bug no se nota. El bug solo apareció cuando comparé contra un valor calculado a mano con un descuento distinto de cero. Tampoco mide si se probaron las **fronteras**: `descuento_por_volumen` tiene 100 % de cobertura con solo cinco entradas, pero un error de `>` por `>=` en un tramo solo se detecta probando exactamente 10, 20, 50 y 100 unidades. Y no mide los **requisitos que faltan**: `celsius_a_kelvin(-300)` está 100 % cubierta y devuelve una temperatura imposible (−26.85 K), porque ninguna línea del código valida ese caso. La cobertura solo puede medir el código que existe, no las validaciones que nadie escribió.

**¿Qué aprendí?** Lo más útil fue cambiar la forma de pensar al escribir una prueba: en lugar de confirmar que la función “funciona”, buscar activamente la entrada que la rompe. Casi todos los bugs aparecieron en un extremo (un negativo, una lista sin ceros, una coma dentro de comillas) y no en el caso típico. También entendí que una prueba en rojo es información valiosa y no un fracaso: el commit con la prueba que falla documenta el bug mejor que cualquier descripción, y el `fix:` siguiente demuestra que se resolvió. Por último, varias correcciones obligaron a tomar decisiones de negocio (qué hacer si los descuentos suman 110 %, o si a una fila le falta una columna). Las pruebas quedan como la especificación ejecutable de esas decisiones, y con GitHub Actions esa especificación se verifica sola en cada cambio. Ahí está la conexión con DevOps: el código, las pruebas y la documentación viven juntos y la verificación es automática.
