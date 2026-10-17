"""Pruebas unitarias del módulo descuentos (estructura AAA)."""
import pytest

from src.descuentos import (
    aplicar_descuento,
    calcular_descuento,
    calcular_precio_final,
    descuento_apilado,
    descuento_cumulativo,
    descuento_por_volumen,
)


# ---------------------------------------------------------------- aplicar_descuento
@pytest.mark.parametrize(
    "precio, porcentaje, esperado",
    [(100, 20, 80), (100, 0, 100), (100, 100, 0), (0, 50, 0), (59.99, 10, 53.991)],
)
def test_aplicar_descuento_casos_validos_y_limites(precio, porcentaje, esperado):
    # Arrange: valores dados por el parametrize (incluye 0 % y 100 %)
    # Act
    resultado = aplicar_descuento(precio, porcentaje)
    # Assert
    assert resultado == pytest.approx(esperado)


@pytest.mark.parametrize("precio, porcentaje", [(-1, 10), (100, -0.01), (100, 100.01)])
def test_aplicar_descuento_fuera_de_rango_lanza_error(precio, porcentaje):
    # Arrange: precio negativo o porcentaje justo por fuera de [0, 100]
    # Act / Assert
    with pytest.raises(ValueError):
        aplicar_descuento(precio, porcentaje)


# ---------------------------------------------------------------- calcular_descuento
def test_calcular_descuento_devuelve_el_monto_descontado():
    # Arrange
    precio, porcentaje = 250, 12
    # Act
    resultado = calcular_descuento(precio, porcentaje)
    # Assert
    assert resultado == pytest.approx(30)


@pytest.mark.parametrize("precio, porcentaje", [(-5, 10), (100, -1), (100, 101)])
def test_calcular_descuento_invalido_lanza_error(precio, porcentaje):
    # Arrange: valores dados por el parametrize
    # Act / Assert
    with pytest.raises(ValueError):
        calcular_descuento(precio, porcentaje)


# ---------------------------------------------------------------- calcular_precio_final
def test_precio_final_impuesto_se_aplica_sobre_precio_con_descuento():
    # Arrange: 100 con 20 % de descuento = 80; 19 % de IVA sobre 80 = 15.2
    precio, impuesto, descuento = 100, 19, 20
    # Act
    resultado = calcular_precio_final(precio, impuesto, descuento)
    # Assert
    assert resultado == pytest.approx(95.2)


def test_precio_final_sin_descuento_solo_suma_impuesto():
    # Arrange
    precio, impuesto, descuento = 200, 19, 0
    # Act
    resultado = calcular_precio_final(precio, impuesto, descuento)
    # Assert
    assert resultado == pytest.approx(238)


def test_precio_final_con_descuento_total_es_cero():
    # Arrange: si el producto es gratis no se debe cobrar impuesto
    precio, impuesto, descuento = 100, 19, 100
    # Act
    resultado = calcular_precio_final(precio, impuesto, descuento)
    # Assert
    assert resultado == pytest.approx(0)


@pytest.mark.parametrize(
    "precio, impuesto, descuento",
    [(-1, 19, 10), (100, -1, 10), (100, 19, -1), (100, 19, 101)],
)
def test_precio_final_parametros_invalidos_lanzan_error(precio, impuesto, descuento):
    # Arrange: valores dados por el parametrize
    # Act / Assert
    with pytest.raises(ValueError):
        calcular_precio_final(precio, impuesto, descuento)


# ---------------------------------------------------------------- descuento_por_volumen
@pytest.mark.parametrize(
    "cantidad, esperado",
    [
        (0, 0),
        (9, 90),      # justo antes del primer tramo: sin descuento
        (10, 95),     # 5 %
        (19, 180.5),
        (20, 180),    # 10 %
        (49, 441),
        (50, 425),    # 15 %
        (99, 841.5),
        (100, 800),   # 20 %
    ],
)
def test_descuento_por_volumen_fronteras_de_cada_tramo(cantidad, esperado):
    # Arrange: precio unitario de 10 para leer fácil los resultados
    precio_unitario = 10
    # Act
    resultado = descuento_por_volumen(cantidad, precio_unitario)
    # Assert
    assert resultado == pytest.approx(esperado)


@pytest.mark.parametrize("cantidad, precio_unitario", [(-1, 10), (5, -10)])
def test_descuento_por_volumen_valores_negativos_lanzan_error(cantidad, precio_unitario):
    # Arrange: valores dados por el parametrize
    # Act / Assert
    with pytest.raises(ValueError):
        descuento_por_volumen(cantidad, precio_unitario)


# ---------------------------------------------------------------- descuento_cumulativo
def test_descuento_cumulativo_aplica_descuentos_en_cadena():
    # Arrange: 100 -> 90 (10 %) -> 72 (20 %)
    precio, descuentos = 100, [10, 20]
    # Act
    resultado = descuento_cumulativo(precio, descuentos)
    # Assert
    assert resultado == pytest.approx(72)


def test_descuento_cumulativo_sin_descuentos_devuelve_precio():
    # Arrange
    precio, descuentos = 100, []
    # Act
    resultado = descuento_cumulativo(precio, descuentos)
    # Assert
    assert resultado == 100


@pytest.mark.parametrize("precio, descuentos", [(-1, [10]), (100, [10, 120]), (100, [-5])])
def test_descuento_cumulativo_invalido_lanza_error(precio, descuentos):
    # Arrange: valores dados por el parametrize
    # Act / Assert
    with pytest.raises(ValueError):
        descuento_cumulativo(precio, descuentos)


# ---------------------------------------------------------------- descuento_apilado
def test_descuento_apilado_suma_los_porcentajes():
    # Arrange: 10 % + 20 % = 30 % sobre 100
    precio, descuentos = 100, [10, 20]
    # Act
    resultado = descuento_apilado(precio, descuentos)
    # Assert
    assert resultado == pytest.approx(70)


def test_descuento_apilado_sin_descuentos_devuelve_precio():
    # Arrange
    precio, descuentos = 100, []
    # Act
    resultado = descuento_apilado(precio, descuentos)
    # Assert
    assert resultado == 100


def test_descuento_apilado_que_supera_100_se_limita_a_precio_cero():
    # Arrange: 60 % + 50 % = 110 %; el producto queda gratis, nunca negativo
    precio, descuentos = 100, [60, 50]
    # Act
    resultado = descuento_apilado(precio, descuentos)
    # Assert
    assert resultado == 0


def test_descuento_apilado_con_un_descuento_negativo_lanza_error():
    # Arrange: un -10 % escondido en la lista encarecería el producto
    precio, descuentos = 100, [-10, 20]
    # Act / Assert
    with pytest.raises(ValueError):
        descuento_apilado(precio, descuentos)


def test_descuento_apilado_precio_negativo_lanza_error():
    # Arrange
    precio, descuentos = -50, [10]
    # Act / Assert
    with pytest.raises(ValueError):
        descuento_apilado(precio, descuentos)   