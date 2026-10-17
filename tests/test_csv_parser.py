"""Pruebas unitarias del módulo csv_parser (estructura AAA).

Ninguna prueba lee archivos reales: el contenido CSV se define en memoria y,
donde se simula la lectura de un archivo, se usa ``unittest.mock.mock_open``.
"""
from unittest.mock import call, mock_open, patch

import pytest

from src import csv_parser
from src.csv_parser import (
    contar_columnas,
    contar_filas,
    csv_a_diccionarios,
    extraer_columna,
    filtrar_por_columna,
    leer_csv_como_lista,
    parse_csv_line,
    validar_csv,
)

CSV_PRODUCTOS = "nombre,precio,categoria\ncafe,12000,bebida\npan,3000,panaderia\nte,8000,bebida"


# ---------------------------------------------------------------- mocking
def test_leer_csv_desde_archivo_simulado_con_mock_open():
    # Arrange: simulamos un archivo en disco sin crearlo
    archivo_falso = mock_open(read_data="id,nombre\n1,Ana\n2,Luis\n")
    # Act
    with patch("builtins.open", archivo_falso):
        with open("datos/clientes.csv", encoding="utf-8") as f:
            resultado = csv_a_diccionarios(f.read())
    # Assert
    archivo_falso.assert_called_once_with("datos/clientes.csv", encoding="utf-8")
    assert resultado == [{"id": "1", "nombre": "Ana"}, {"id": "2", "nombre": "Luis"}]


def test_leer_csv_como_lista_delega_cada_linea_en_parse_csv_line():
    # Arrange: reemplazamos el parser de línea para aislar leer_csv_como_lista
    contenido = "a,b\nc,d"
    with patch.object(csv_parser, "parse_csv_line", return_value=["X"]) as parser_falso:
        # Act
        resultado = leer_csv_como_lista(contenido)
    # Assert
    assert parser_falso.call_args_list == [call("a,b"), call("c,d")]
    assert resultado == [["X"], ["X"]]


def test_contar_columnas_usa_el_parser_solo_con_la_primera_linea():
    # Arrange
    with patch.object(csv_parser, "parse_csv_line", return_value=["a", "b", "c"]) as parser_falso:
        # Act
        resultado = contar_columnas("a,b,c\n1,2,3")
    # Assert
    parser_falso.assert_called_once_with("a,b,c")
    assert resultado == 3


# ---------------------------------------------------------------- parse_csv_line
def test_parse_linea_simple():
    # Arrange
    linea = "uno,dos,tres"
    # Act
    resultado = parse_csv_line(linea)
    # Assert
    assert resultado == ["uno", "dos", "tres"]


def test_parse_linea_vacia_devuelve_lista_vacia():
    # Arrange
    linea = ""
    # Act
    resultado = parse_csv_line(linea)
    # Assert
    assert resultado == []


def test_parse_linea_con_coma_dentro_de_comillas():
    # Arrange: la coma de "Manizales, Caldas" es parte del valor
    linea = 'Ana,"Manizales, Caldas",30'
    # Act
    resultado = parse_csv_line(linea)
    # Assert
    assert resultado == ["Ana", "Manizales, Caldas", "30"]


def test_parse_linea_con_comillas_escapadas():
    # Arrange: en CSV una comilla dentro de un campo se escribe doble ("")
    linea = '1,"Dijo ""hola""",ok'
    # Act
    resultado = parse_csv_line(linea)
    # Assert
    assert resultado == ["1", 'Dijo "hola"', "ok"]


def test_parse_linea_con_campos_vacios():
    # Arrange
    linea = "a,,c,"
    # Act
    resultado = parse_csv_line(linea)
    # Assert
    assert resultado == ["a", "", "c", ""]


# ---------------------------------------------------------------- leer / diccionarios
def test_leer_csv_vacio_devuelve_lista_vacia():
    # Arrange
    contenido = ""
    # Act
    resultado = leer_csv_como_lista(contenido)
    # Assert
    assert resultado == []


def test_csv_a_diccionarios_con_cabecera():
    # Arrange
    contenido = CSV_PRODUCTOS
    # Act
    resultado = csv_a_diccionarios(contenido)
    # Assert
    assert len(resultado) == 3
    assert resultado[0] == {"nombre": "cafe", "precio": "12000", "categoria": "bebida"}


def test_csv_a_diccionarios_fila_con_menos_columnas_completa_con_vacio():
    # Arrange: a la segunda fila le falta la columna "edad"
    contenido = "nombre,ciudad,edad\nAna,Manizales,30\nLuis,Pereira"
    # Act
    resultado = csv_a_diccionarios(contenido)
    # Assert: todas las filas deben tener las mismas claves
    assert resultado[1] == {"nombre": "Luis", "ciudad": "Pereira", "edad": ""}


def test_csv_a_diccionarios_fila_con_columnas_de_mas_lanza_error():
    # Arrange: la fila trae un valor que no corresponde a ninguna cabecera
    contenido = "nombre,edad\nAna,30,extra"
    # Act / Assert: perder datos en silencio es peor que avisar
    with pytest.raises(ValueError):
        csv_a_diccionarios(contenido)


@pytest.mark.parametrize(
    "contenido, tiene_cabecera",
    [("", True), ("solo,cabecera", True), (CSV_PRODUCTOS, False)],
)
def test_csv_a_diccionarios_casos_sin_datos_devuelven_lista_vacia(contenido, tiene_cabecera):
    # Arrange: valores dados por el parametrize
    # Act
    resultado = csv_a_diccionarios(contenido, tiene_cabecera=tiene_cabecera)
    # Assert
    assert resultado == []


# ---------------------------------------------------------------- validar_csv
@pytest.mark.parametrize(
    "contenido, esperado",
    [(CSV_PRODUCTOS, True), ("a,b\n1,2,3", False), ("", False), ("unica", True)],
)
def test_validar_csv(contenido, esperado):
    # Arrange: valores dados por el parametrize
    # Act
    resultado = validar_csv(contenido)
    # Assert
    assert resultado is esperado


# ---------------------------------------------------------------- columnas / filtros / conteos
def test_extraer_columna_rellena_con_vacio_si_la_fila_es_corta():
    # Arrange
    contenido = "a,b\n1\n2,3"
    # Act
    resultado = extraer_columna(contenido, 1)
    # Assert
    assert resultado == ["b", "", "3"]


def test_extraer_columna_de_csv_vacio():
    # Arrange
    contenido = ""
    # Act
    resultado = extraer_columna(contenido, 0)
    # Assert
    assert resultado == []


def test_filtrar_por_columna_devuelve_solo_coincidencias():
    # Arrange
    contenido = CSV_PRODUCTOS
    # Act
    resultado = filtrar_por_columna(contenido, 2, "bebida")
    # Assert
    assert resultado == [["cafe", "12000", "bebida"], ["te", "8000", "bebida"]]


@pytest.mark.parametrize("contenido, indice", [("", 0), (CSV_PRODUCTOS, 9)])
def test_filtrar_por_columna_sin_resultados(contenido, indice):
    # Arrange: CSV vacío o índice de columna inexistente
    # Act
    resultado = filtrar_por_columna(contenido, indice, "bebida")
    # Assert
    assert resultado == []


@pytest.mark.parametrize(
    "contenido, filas, columnas",
    [(CSV_PRODUCTOS, 4, 3), ("", 0, 0), ("x\n", 1, 1)],
)
def test_contar_filas_y_columnas(contenido, filas, columnas):
    # Arrange: valores dados por el parametrize
    # Act
    total_filas = contar_filas(contenido)
    total_columnas = contar_columnas(contenido)
    # Assert
    assert (total_filas, total_columnas) == (filas, columnas)
