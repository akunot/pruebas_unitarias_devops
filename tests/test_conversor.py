"""Pruebas unitarias del módulo conversor (estructura AAA)."""
import pytest

from src import conversor
from src.conversor import (
    celsius_a_fahrenheit,
    celsius_a_kelvin,
    fahrenheit_a_celsius,
    kelvin_a_celsius,
    kilometros_a_millas,
    millas_a_kilometros,
)


# ---------------------------------------------------------------- temperatura
@pytest.mark.parametrize(
    "celsius, fahrenheit",
    [(0, 32), (100, 212), (-40, -40), (37, 98.6)],
)
def test_celsius_a_fahrenheit_puntos_de_referencia(celsius, fahrenheit):
    # Arrange: congelación, ebullición, punto donde coinciden y temperatura corporal
    # Act
    resultado = celsius_a_fahrenheit(celsius)
    # Assert
    assert resultado == pytest.approx(fahrenheit)


@pytest.mark.parametrize("fahrenheit, celsius", [(32, 0), (212, 100), (-40, -40)])
def test_fahrenheit_a_celsius_puntos_de_referencia(fahrenheit, celsius):
    # Arrange: valores dados por el parametrize
    # Act
    resultado = fahrenheit_a_celsius(fahrenheit)
    # Assert
    assert resultado == pytest.approx(celsius)


def test_celsius_a_kelvin_cero_celsius():
    # Arrange
    celsius = 0
    # Act
    resultado = celsius_a_kelvin(celsius)
    # Assert
    assert resultado == pytest.approx(273.15)


@pytest.mark.parametrize("kelvin, celsius", [(273.15, 0), (373.15, 100), (0, -273.15)])
def test_kelvin_a_celsius_valores_validos_incluye_cero_absoluto(kelvin, celsius):
    # Arrange: 0 K es el límite físico y debe aceptarse
    # Act
    resultado = kelvin_a_celsius(kelvin)
    # Assert
    assert resultado == pytest.approx(celsius)


def test_kelvin_negativo_lanza_error():
    # Arrange: por debajo del cero absoluto no existe temperatura
    kelvin = -10
    # Act / Assert
    with pytest.raises(ValueError):
        kelvin_a_celsius(kelvin)


def test_ida_y_vuelta_celsius_kelvin_conserva_el_valor():
    # Arrange
    original = 25.5
    # Act
    resultado = kelvin_a_celsius(celsius_a_kelvin(original))
    # Assert
    assert resultado == pytest.approx(original)


# ---------------------------------------------------------------- millas / kilómetros
def test_millas_a_kilometros():
    # Arrange
    millas = 10
    # Act
    resultado = millas_a_kilometros(millas)
    # Assert
    assert resultado == pytest.approx(16.0934)


def test_kilometros_a_millas_maraton():
    # Arrange: una maratón mide 42.195 km ≈ 26.219 millas
    kilometros = 42.195
    # Act
    resultado = kilometros_a_millas(kilometros)
    # Assert
    assert resultado == pytest.approx(26.219, abs=0.001)


def test_kilometros_a_millas_es_inversa_de_millas_a_kilometros():
    # Arrange
    millas = 7
    # Act
    resultado = kilometros_a_millas(millas_a_kilometros(millas))
    # Assert
    assert resultado == pytest.approx(millas)


# ---------------------------------------------------------------- pares de conversión
# (ida, vuelta, valor, resultado esperado de la ida)
PARES = [
    ("metros_a_kilometros", "kilometros_a_metros", 1500, 1.5),
    ("libras_a_kilogramos", "kilogramos_a_libras", 10, 4.53592),
    ("galones_a_litros", "litros_a_galones", 2, 7.57082),
    ("millas_a_kilometros", "kilometros_a_millas", 3, 4.82802),
    ("pies_a_metros", "metros_a_pies", 10, 3.048),
    ("onzas_a_gramos", "gramos_a_onzas", 4, 113.398),
]


@pytest.mark.parametrize("ida, vuelta, valor, esperado", PARES)
def test_conversion_de_ida_da_el_valor_esperado(ida, vuelta, valor, esperado):
    # Arrange
    funcion = getattr(conversor, ida)
    # Act
    resultado = funcion(valor)
    # Assert
    assert resultado == pytest.approx(esperado)


@pytest.mark.parametrize("ida, vuelta, valor, esperado", PARES)
def test_conversion_ida_y_vuelta_recupera_el_valor(ida, vuelta, valor, esperado):
    # Arrange
    ir, volver = getattr(conversor, ida), getattr(conversor, vuelta)
    # Act
    resultado = volver(ir(valor))
    # Assert
    assert resultado == pytest.approx(valor)


@pytest.mark.parametrize("nombre", sorted({p[0] for p in PARES} | {p[1] for p in PARES}))
def test_conversion_de_cero_es_cero(nombre):
    # Arrange: el cero es el límite inferior válido
    funcion = getattr(conversor, nombre)
    # Act
    resultado = funcion(0)
    # Assert
    assert resultado == 0


@pytest.mark.parametrize("nombre", sorted({p[0] for p in PARES} | {p[1] for p in PARES}))
def test_conversion_de_negativo_lanza_error(nombre):
    # Arrange: distancias, pesos y volúmenes no pueden ser negativos
    funcion = getattr(conversor, nombre)
    # Act / Assert
    with pytest.raises(ValueError):
        funcion(-0.5)
