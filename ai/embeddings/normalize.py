import re
from typing import List

_STOPWORDS = {
	"de",
	"la",
	"el",
	"los",
	"las",
	"y",
	"con",
	"sin",
	"para",
	"por",
}

_DESCRIPTORS = {
	"grande",
	"grandes",
	"pequeño",
	"pequeños",
	"largo",
	"largos",
	"corto",
	"cortos",
	"fino",
	"finos",
	"extra",
	"natural",
	"fresco",
	"frescos",
	"seco",
	"seca",
	"light",
	"sin",
	"integral",
	"enteros",
	"entero",
}


def _tokenize(text: str) -> List[str]:
	text = text.lower()
	text = re.sub(r"[^a-záéíóúñ0-9\s]", " ", text)
	tokens = [t.strip() for t in text.split() if t.strip()]
	return tokens


def normalize(text: str) -> str:
	"""Normaliza una string con un producto a una version sin descriptores.

	Ejemplo: 'Fideos largos' -> 'fideos'

	Estrategia:
	- lowercase, remover acentos/puntuaciones
	- dividir en tokens
	- tirar descriptores
	- devolver el primer token restante o el token original
	"""
	if not text:
		return ""

	tokens = _tokenize(text)
	if not tokens:
		return ""

	filtered = [t for t in tokens if t not in _STOPWORDS and t not in _DESCRIPTORS]

	# Si hay algun token restante despues de filtrar entonces devuelve el primero.
	if filtered:
		return filtered[0]

	return tokens[0]


def normalize_list(items: List[str]) -> List[str]:
	"""Normaliza una lista de productos."""
	return [normalize(i) for i in items]


if __name__ == "__main__":
    # Test rapido
	examples = [
		"Fideos largos",
		"Arroz integral 1kg",
		"Queso fresco",
		"Galletitas light",
		"",
		"Pan de molde",
	]
	for e in examples:
		print(e, "->", normalize(e))

