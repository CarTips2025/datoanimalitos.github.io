#!/usr/bin/env python3
# scripts/update_revistas.py
# Workflow que actualiza data/revistas.json automaticamente

import json
import os
import requests
from datetime import datetime
from typing import Dict, List

# Configuracion de hipodromos con IMAGENES LOCALES
# Ajusta las rutas de imagenes y URLs de PDFs segun tus necesidades

HIPODROMOS_CONFIG = [
    {
        "id": "gulfstream-park",
        "nombre": "Gulfstream Park",
        "logo": "img/winner/gulfstream.webp",
        "revistas": {
            "espanol": "https://pollamacaco.com/Revistas/GulfstreamPark.pdf",
            "winnersChoice": "https://pollamacaco.com/Revistas/WinGulfstreamPark.pdf"
        }
    },
    {
        "id": "santa-anita",
        "nombre": "Santa Anita Park",
        "logo": "img/winner/santa-anita.webp",
        "revistas": {
            "espanol": "https://pollamacaco.com/Revistas/SantaAnitaPark.pdf",
            "winnersChoice": "https://pollamacaco.com/Revistas/WinSantaAnitaPark.pdf"
        }
    },
    {
        "id": "aqueduct",
        "nombre": "Aqueduct",
        "logo": "img/winner/aqueduct.webp",
        "revistas": {
            "espanol": "https://pollamacaco.com/Revistas/Aqueduct.pdf",
            "winnersChoice": "https://pollamacaco.com/Revistas/WinAqueduct.pdf"
        }
    },
    {
        "id": "churchill-downs",
        "nombre": "Churchill Downs",
        "logo": "img/winner/churchill.webp",
        "revistas": {
            "espanol": "https://pollamacaco.com/Revistas/ChurchillDowns.pdf",
            "winnersChoice": "https://pollamacaco.com/Revistas/WinChurchillDowns.pdf"
        }
    },
    {
        "id": "belmont-park",
        "nombre": "Belmont Park",
        "logo": "img/winner/belmont.webp",
        "revistas": {
            "espanol": "https://pollamacaco.com/Revistas/BelmontPark.pdf",
            "winnersChoice": "https://pollamacaco.com/Revistas/WinBelmontPark.pdf"
        }
    },
    {
        "id": "monmouth-park",
        "nombre": "Monmouth Park",
        "logo": "img/winner/monmouth.webp",
        "revistas": {
            "espanol": "https://pollamacaco.com/Revistas/MonmouthPark.pdf",
            "winnersChoice": "https://pollamacaco.com/Revistas/WinMonmouthPark.pdf"
        }
    },
    {
        "id": "woodbine",
        "nombre": "Woodbine",
        "logo": "img/winner/woodbine.webp",
        "revistas": {
            "espanol": "https://pollamacaco.com/Revistas/Woodbine.pdf",
            "winnersChoice": "https://pollamacaco.com/Revistas/WinWoodbine.pdf"
        }
    },
    {
        "id": "parx-racing",
        "nombre": "Parx Racing",
        "logo": "img/winner/parx.webp",
        "revistas": {
            "espanol": "https://pollamacaco.com/Revistas/ParxRacing.pdf",
            "winnersChoice": "https://pollamacaco.com/Revistas/WinParxRacing.pdf"
        }
    }
]

def verificar_imagen_local(ruta_imagen: str) -> bool:
    """Verifica si la imagen local existe"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    ruta_completa = os.path.join(project_root, ruta_imagen)
    existe = os.path.exists(ruta_completa)
    if not existe:
        print(f"  ADVERTENCIA: Imagen no encontrada - {ruta_imagen}")
    return existe

def verificar_url_pdf(url: str) -> bool:
    """Verifica si un PDF existe y esta accesible"""
    try:
        response = requests.head(url, timeout=15, allow_redirects=True)
        content_type = response.headers.get('content-type', '')
        return response.status_code == 200 and ('pdf' in content_type.lower() or url.endswith('.pdf'))
    except requests.exceptions.RequestException as e:
        print(f"  Error verificando URL: {str(e)[:60]}")
        return False
    except Exception as e:
        print(f"  Error inesperado: {str(e)[:60]}")
        return False

def actualizar_revistas() -> Dict:
    """Actualiza la informacion de todas las revistas"""
    hipodromos_activos = []
    hipodromos_inactivos = []
    
    print(f"Iniciando verificacion de {len(HIPODROMOS_CONFIG)} hipodromos...")
    
    for config in HIPODROMOS_CONFIG:
        print(f"\nVerificando {config['nombre']}...")
        
        # Verificar imagen local
        verificar_imagen_local(config['logo'])
        
        # Verificar PDFs
        espanol_valida = verificar_url_pdf(config['revistas']['espanol'])
        winners_valida = verificar_url_pdf(config['revistas']['winnersChoice'])
        
        if espanol_valida and winners_valida:
            hipodromos_activos.append({
                "id": config["id"],
                "nombre": config["nombre"],
                "logo": config["logo"],
                "revistas": {
                    "espanol": config["revistas"]["espanol"],
                    "winnersChoice": config["revistas"]["winnersChoice"]
                },
                "activo": True,
                "ultimaActualizacion": datetime.now().strftime("%Y-%m-%d")
            })
            print(f"  OK - {config['nombre']} activo")
        else:
            hipodromos_inactivos.append({
                "id": config["id"],
                "nombre": config["nombre"],
                "razon": "Revistas no disponibles"
            })
            print(f"  ERROR - {config['nombre']} no disponible")
    
    return {
        "metadata": {
            "lastUpdate": datetime.now().isoformat(),
            "totalHipodromos": len(hipodromos_activos),
            "totalConfigurados": len(HIPODROMOS_CONFIG),
            "version": "1.0.0"
        },
        "hipodromos": hipodromos_activos,
        "errores": hipodromos_inactivos if hipodromos_inactivos else None
    }

def guardar_json(data: Dict, ruta: str = "data/revistas.json"):
    """Guarda el JSON en la ruta especificada"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    ruta_completa = os.path.join(project_root, ruta)
    
    os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
    
    with open(ruta_completa, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nJSON guardado en {ruta}")
    print(f"Hipodromos activos: {data['metadata']['totalHipodromos']} de {data['metadata']['totalConfigurados']}")

def main():
    print("=" * 60)
    print(f"ACTUALIZACION DE REVISTAS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        datos = actualizar_revistas()
        guardar_json(datos)
        print("\n" + "=" * 60)
        print("ACTUALIZACION COMPLETADA EXITOSAMENTE")
        print("=" * 60)
    except Exception as e:
        print(f"\nERROR FATAL: {str(e)}")
        raise

if __name__ == "__main__":
    main()