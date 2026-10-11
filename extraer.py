#!/usr/bin/env python3
"""Saca de tu instalación de AoE2 DE los escudos, nombres, especialidades,
unidades únicas y tecnologías únicas de cada civilización.

Uso:  python3 extraer.py [ruta/a/AoE2DE]
Vuelve a ejecutarlo cuando salga un DLC con civilizaciones nuevas.
"""
import json
import re
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
JUEGO = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".local/share/Steam/steamapps/common/AoE2DE"
DAT = JUEGO / "resources/_common/dat"
WPFG = JUEGO / "resources/_common/wpfg"

# civilizations.json no dice de qué expansión es cada civ, así que el reparto va a mano.
# La clave es la del nombre oficial del DLC en los textos del juego (IDS_DLC_NAME_<clave>).
EXPANSIONES = [
    ("The Age of Kings", None, "Britons Franks Goths Teutons Japanese Chinese Byzantines Persians Saracens Turks Vikings Mongols Celts"),
    ("The Conquerors", None, "Spanish Aztecs Mayans Huns Koreans"),
    ("The Forgotten", None, "Italians Indians Incas Magyars Slavs"),
    ("The African Kingdoms", None, "Portuguese Ethiopians Malians Berbers"),
    ("Rise of the Rajas", None, "Khmer Malay Burmese Vietnamese"),
    ("The Last Khans", None, "Bulgarians Tatars Cumans Lithuanians"),
    ("Lords of the West", "PALERMO", "Burgundians Sicilians"),
    ("Dawn of the Dukes", "PRAGUE", "Poles Bohemians"),
    ("Dynasties of India", "PORTO", "Dravidians Bengalis Gurjaras"),
    ("Return of Rome", "POMPEII", "Romans"),
    ("The Mountain Royals", "PLYMOUTH", "Armenians Georgians"),
    ("Chronicles: Battle for Greece", "PAPHOS", "Achaemenids Athenians Spartans"),
    ("The Three Kingdoms", "PERU", "Shu Wu Wei Jurchens Khitans"),
    ("Chronicles: Alexander the Great", "PROVIDENCE", "Macedonians Thracians Puru"),
    ("The Last Chieftains", "PARIS", "Muisca Mapuche Tupi"),
    ("The Viking Sagas", "PORTLAND", "Saxons Varangians Danes"),
]


def textos(idioma):
    """Todos los textos del juego en un idioma: {id: texto}."""
    out = {}
    for fichero in ("key-value-strings-utf8.txt", "key-value-paphos-strings-utf8.txt"):
        ruta = JUEGO / "resources" / idioma / "strings/key-value" / fichero
        if ruta.exists():
            for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
                m = re.match(r'\s*(\w+)\s+"(.*)"', linea)
                if m:
                    out.setdefault(m[1], m[2])
    return out


def slug(texto):
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")


def mayuscula(texto):
    return texto[:1].upper() + texto[1:]


def especialidad(desc, idioma):
    """Primera línea de la descripción: 'Foot Archer civilization' -> 'Foot Archer',
    'Civilización de arqueros a pie' -> 'Arqueros a pie'."""
    texto = desc.split(r"\n\n")[0].strip()
    if idioma == "en":
        texto = re.sub(r"\s*civilization$", "", texto, flags=re.I)
    else:
        texto = re.sub(r"^Civilización\s+(de\s+)?", "", texto)
    return mayuscula(texto)


def tecnologias(desc):
    """[(nombre, efecto)] de la lista de tecnologías únicas de la descripción de la civ."""
    for parte in desc.split(r"\n\n"):
        cabecera, *lineas = parte.split(r"\n")
        vinetas = [linea.strip().lstrip("•").strip() for linea in lineas if linea.strip().startswith("•")]
        if cabecera.startswith("<b>") and vinetas:  # la de bonificaciones no tiene cabecera
            lista = []
            for item in vinetas:
                m = re.match(r"(.+?)\s*\((.*)\)\s*\.?$", item)
                lista.append((m[1], mayuscula(m[2])) if m else (item, ""))
            return lista
    return []


en, es = textos("en"), textos("es")
expansion = {}
for nombre, clave, miembros in EXPANSIONES:
    nombres = {"en": nombre, "es": nombre}
    if clave:
        nombres = {"en": en.get(f"IDS_DLC_NAME_{clave}", nombre), "es": es.get(f"IDS_DLC_NAME_{clave}", nombre)}
    for civ in miembros.split():
        expansion[civ] = nombres

for carpeta in ("escudos", "unidades", "iconos"):
    (AQUI / carpeta).mkdir(exist_ok=True)

datos, avisos = [], []
for c in json.loads((DAT / "civilizations.json").read_text(encoding="utf-8"))["civilization_list"]:
    if not c.get("tech_tree_image_path"):  # Gaia
        continue
    nombre = c["internal_name"]
    civ_id = nombre.lower()
    shutil.copyfile(WPFG / c["tech_tree_image_path"].lstrip("/"), AQUI / "escudos" / f"{civ_id}.png")
    desc = {"en": en[str(c["tech_tree_description_string_id"])], "es": es[str(c["tech_tree_description_string_id"])]}

    unidades = []
    for ids, imagen in zip(c["unique_unit_string_ids"], c["unique_unit_image_paths"]):
        u_en = en[str(ids["name"])]
        unidad = {"id": slug(u_en), "en": u_en, "es": es.get(str(ids["name"]), u_en)}
        shutil.copyfile(WPFG / imagen.lstrip("/"), AQUI / "unidades" / f"{unidad['id']}.png")
        unidades.append(unidad)

    # La edad de cada tecnología única sale del árbol tecnológico (allí los nombres llevan saltos de línea)
    arbol = json.loads((DAT / "CivTechTrees" / f"{c['tech_tree_name']}.json").read_text(encoding="utf-8"))
    edades = {}
    for nodo in arbol["civ_techs_units"] + arbol["civ_techs_buildings"]:
        if nodo.get("Node Type") == "UniqueTech":
            limpio = re.sub(r"-\s+", "", en.get(str(nodo["Name String ID"]), "").replace(r"\n", " "))
            edades[limpio.lower()] = nodo["Age ID"]
    t_en, t_es = tecnologias(desc["en"]), tecnologias(desc["es"])
    if len(t_es) != len(t_en):
        avisos.append(f"{nombre}: las tecnologías en español no cuadran, uso las inglesas")
        t_es = t_en
    techs = []
    for i, ((n_en, fx_en), (n_es, fx_es)) in enumerate(zip(t_en, t_es)):
        edad = edades.get(n_en.lower(), (3, 4)[i] if len(t_en) == 2 else None)
        techs.append({"id": slug(n_en), "en": n_en, "es": n_es, "edad": edad, "fx": {"en": fx_en, "es": fx_es}})
    if len(techs) < 2:
        avisos.append(f"{nombre}: solo he encontrado {len(techs)} tecnologías únicas")

    if nombre not in expansion:
        avisos.append(f"{nombre}: no sé de qué expansión es, añádela a EXPANSIONES")
    spec_en = especialidad(desc["en"], "en")
    datos.append({
        "id": civ_id,
        "en": en[str(c["name_string_id"])],
        "es": es.get(str(c["name_string_id"]), nombre),
        "chronicles": c.get("era") != "base",  # Aqueménidas, Atenienses... solo existen en Chronicles
        "exp": expansion.get(nombre, {"en": "Other", "es": "Otras"}),
        # Las etiquetas sirven para que las opciones de especialidad no se pisen ("Infantry" vs "Infantry and Naval")
        "spec": {"en": spec_en, "es": especialidad(desc["es"], "es"), "tags": sorted(set(spec_en.lower().replace(" and ", " ").split()))},
        "units": unidades,
        "techs": techs,
    })

for edad in (1, 2, 3, 4):
    shutil.copyfile(JUEGO / f"widgetui/textures/ingame/icons/age-{edad}.png", AQUI / "iconos" / f"edad-{edad}.png")

filas = ",\n".join("  " + json.dumps(d, ensure_ascii=False) for d in datos)
(AQUI / "civs.js").write_text(
    f"// Generado por extraer.py a partir de los archivos del juego.\nwindow.CIVS = [\n{filas}\n];\n",
    encoding="utf-8",
)
print(f"{len(datos)} civilizaciones ({sum(d['chronicles'] for d in datos)} de Chronicles), "
      f"{sum(len(d['units']) for d in datos)} unidades únicas y {sum(len(d['techs']) for d in datos)} tecnologías únicas")
for aviso in avisos:
    print("  ¡Ojo!", aviso)
