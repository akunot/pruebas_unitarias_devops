"""Pruebas unitarias del módulo calculadora (estructura AAA)."""
import math

import pytest

from src.calculadora import (
    calcular_area_rectangulo,
    calcular_perimetro_rectangulo,
    dividir,
    maximo,
    minimo,
    multiplicar,
    potencia,
    promedio,
    raiz_cuadrada,
    restar,
    sumar,
)


# ---------------------------------------------------------------- sumar
def test_sumar_positivos():
    # Arrange
    a, b = 7, 5
    # Act
    resultado = sumar(a, b)
    # Assert
    assert resultado == 12


def test_sumar_negativo_y_positivo_da_la_diferencia():
    # Arrange
    a, b = -10, 4
    # Act
    resultado = sumar(a, b)
    # Assert
    assert resultado == -6


def test_sumar_decimales_usa_aproximacion():
    # Arrange: 0.1 + 0.2 no es exactamente 0.3 en punto flotante
    a, b = 0.1, 0.2
    # Act
    resultado = sumar(a, b)
    # Assert
    assert resultado == pytest.approx(0.3)


# ---------------------------------------------------------------- restar / multiplicar
def test_restar_resultado_negativo():
    # Arrange
    a, b = 3, 10
    # Act
    resultado = restar(a, b)
    # Assert
    assert resultado == -7


@pytest.mark.parametrize(
    "a, b, esperado",
    [(4, 5, 20), (-3, 6, -18), (-2, -8, 16), (123, 0, 0)],
)
def test_multiplicar_signos_y_cero(a, b, esperado):
    # Arrange: valores dados por el parametrize
    # Act
    resultado = multiplicar(a, b)
    # Assert
    assert resultado == esperado


# ---------------------------------------------------------------- dividir
def test_dividir_exacta():
    # Arrange
    a, b = 10, 4
    # Act
    resultado = dividir(a, b)
    # Assert
    assert resultado == 2.5


def test_dividir_por_cero_lanza_error():
    # Arrange
    a, b = 10, 0
    # Act / Assert
    with pytest.raises(ValueError):
        dividir(a, b)


# ---------------------------------------------------------------- potencia
@pytest.mark.parametrize(
    "base, exponente, esperado",
    [(2, 10, 1024), (5, 0, 1), (0, 0, 1), (2, -1, 0.5), (-3, 3, -27)],
)
def test_potencia_casos_limite(base, exponente, esperado):
    # Arrange: valores dados por el parametrize
    # Act
    resultado = potencia(base, exponente)
    # Assert
    assert resultado == esperado


# ---------------------------------------------------------------- raiz_cuadrada
@pytest.mark.parametrize("numero, esperado", [(0, 0), (1, 1), (16, 4), (2, math.sqrt(2))])
def test_raiz_cuadrada_valores_validos(numero, esperado):
    # Arrange: valores dados por el parametrize
    # Act
    resultado = raiz_cuadrada(numero)
    # Assert
    assert resultado == pytest.approx(esperado)


def test_raiz_cuadrada_de_negativo_lanza_error():
    # Arrange
    numero = -9
    # Act / Assert: no debe devolver un número complejo en silencio
    with pytest.raises(ValueError):
        raiz_cuadrada(numero)


# ---------------------------------------------------------------- promedio
def test_promedio_lista_normal():
    # Arrange
    lista = [2, 4, 6, 8]
    # Act
    resultado = promedio(lista)
    # Assert
    assert resultado == 5


def test_promedio_lista_de_un_elemento():
    # Arrange
    lista = [7]
    # Act
    resultado = promedio(lista)
    # Assert
    assert resultado == 7


def test_promedio_lista_vacia_lanza_error():
    # Arrange
    lista = []
    # Act / Assert
    with pytest.raises(ValueError):
        promedio(lista)


# ---------------------------------------------------------------- maximo / minimo
@pytest.mark.parametrize(
    "lista, esperado",
    [([3, 9, 1], 9), ([-5, -2, -9], -2), ([4], 4), ([7, 7, 7], 7)],
)
def test_maximo_varias_listas(lista, esperado):
    # Arrange: valores dados por el parametrize
    # Act
    resultado = maximo(lista)
    # Assert
    assert resultado == esperado


def test_maximo_lista_vacia_lanza_error():
    # Arrange
    lista = []
    # Act / Assert
    with pytest.raises(ValueError):
        maximo(lista)


def test_minimo_con_todos_positivos():
    # Arrange: ningún elemento es 0 ni negativo
    lista = [3, 5, 7]
    # Act
    resultado = minimo(lista)
    # Assert
    assert resultado == 3


@pytest.mark.parametrize(
    "lista, esperado",
    [([4, -1, 8], -1), ([-5, -2, -9], -9), ([0, 10], 0), ([42], 42)],
)
def test_minimo_varias_listas(lista, esperado):
    # Arrange: valores dados por el parametrize
    # Act
    resultado = minimo(lista)
    # Assert
    assert resultado == esperado


def test_minimo_lista_vacia_lanza_error():
    # Arrange
    lista = []
    # Act / Assert
    with pytest.raises(ValueError):
        minimo(lista)


# ---------------------------------------------------------------- rectángulo
def test_area_rectangulo():
    # Arrange
    base, altura = 4, 2.5
    # Act
    resultado = calcular_area_rectangulo(base, altura)
    # Assert
    assert resultado == 10


def test_area_rectangulo_con_lado_cero_es_cero():
    # Arrange: el cero es el límite inferior permitido
    base, altura = 0, 8
    # Act
    resultado = calcular_area_rectangulo(base, altura)
    # Assert
    assert resultado == 0


def test_perimetro_rectangulo():
    # Arrange
    base, altura = 3, 5
    # Act
    resultado = calcular_perimetro_rectangulo(base, altura)
    # Assert
    assert resultado == 16


@pytest.mark.parametrize("funcion", [calcular_area_rectangulo, calcular_perimetro_rectangulo])
@pytest.mark.parametrize("base, altura", [(-1, 5), (5, -1)])
def test_rectangulo_con_lado_negativo_lanza_error(funcion, base, altura):
    # Arrange: valores dados por el parametrize
    # Act / Assert
    with pytest.raises(ValueError):
        funcion(base, altura)
