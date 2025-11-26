#!/usr/bin/env python3
import os
import sys
from pathlib import Path

INDEX_PATH = Path(__file__).parent / 'embeddings' / 'faiss_index' / 'index.faiss'
CSV_PATH = Path(__file__).parent / 'dataset_10000_productos_arg_5_super.csv'

def main():
    print('Python:', sys.executable)
    print('CSV path:', CSV_PATH)
    print('Index path:', INDEX_PATH)

    if not CSV_PATH.exists():
        print('ERROR: no se encontró el CSV en', CSV_PATH)
        sys.exit(2)

    if INDEX_PATH.exists():
        print('Eliminando índice viejo:', INDEX_PATH)
        try:
            INDEX_PATH.unlink()
        except Exception as e:
            print('No pude borrar el índice:', e)
            print('Por favor borrá manualmente y volvé a intentar')
            sys.exit(3)

    try:
        from embeddings.embeddingModel import ProductEmbedder
    except ModuleNotFoundError as e:
        print('\nFALTA DEPENDENCIA:', e)
        print('Instalá las dependencias y volvé a ejecutar:')
        print('\nPipa sugerida:')
        print('  python -m pip install --upgrade pip')
        print('  python -m pip install faiss-cpu sentence-transformers')
        print('\nO si usás conda:')
        print('  conda install -c conda-forge faiss-cpu sentence-transformers')
        sys.exit(4)

    print('Construyendo índice... esto puede tardar varios minutos según tu CPU')
    e = ProductEmbedder()
    try:
        e.build_index(csv_path=str(CSV_PATH))
    except Exception as ex:
        print('Error durante build_index:', ex)
        raise

    print('\nResultado:')
    print('Index loaded:', e.index is not None)
    print('Index ntotal:', getattr(e.index, 'ntotal', 'N/A'))
    print('Productos en products_df:', None if e.products_df is None else len(e.products_df))

if __name__ == '__main__':
    main()
