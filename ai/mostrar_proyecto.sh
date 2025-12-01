#!/bin/bash

echo "========================================"
echo "📁 Árbol de la carpeta (filtrado)"
echo "========================================"
echo

find . \
  -path "./venv" -prune -o \
  -path "./__pycache__" -prune -o \
  -path "./embeddings/faiss_index" -prune -o \
  -print

echo
echo "========================================"
echo "📄 Lista de archivos con tamaño (filtrado)"
echo "========================================"
echo

ls -lh | grep -v "venv" | grep -v "__pycache__"

echo
echo "========================================"
echo "📜 Contenido de archivos .py (filtrado)"
echo "========================================"
echo

find . \
  -path "./venv" -prune -o \
  -path "./__pycache__" -prune -o \
  -path "./embeddings/faiss_index" -prune -o \
  -name "*.py" -print | while read f; do
    echo "---------- $f ----------"
    cat "$f"
    echo
done

echo
echo "========================================"
echo "📜 Contenido de archivos .txt, .md, .json (filtrado)"
echo "========================================"
echo

find . \
  -path "./venv" -prune -o \
  -path "./__pycache__" -prune -o \
  -path "./embeddings/faiss_index" -prune -o \
  -type f \( -name "*.txt" -o -name "*.md" -o -name "*.json" \) -print | while read f; do
    echo "---------- $f ----------"
    cat "$f"
    echo
done

echo
echo "✅ Listo. Copiá la salida y pegala acá."
