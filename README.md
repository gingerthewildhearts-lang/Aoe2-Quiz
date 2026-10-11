# Civilizaciones · quiz de fans de Age of Empires II

Un juego rápido, al estilo del de las banderas, para aprender las civilizaciones de **Age of Empires II: Definitive Edition**: sus escudos, en qué destaca cada una, sus unidades únicas y sus tecnologías únicas.

**[▶ Jugar](https://gingerthewildhearts-lang.github.io/Aoe2-Quiz/)**

## Modos

- **Escudos**: escudo → nombre, nombre → escudo o una mezcla de los dos.
- **Especialidad**: en qué destaca cada civ (caballería, arqueros, naval…).
- **Unidad → Civ** y **Civ → Unidades**: las unidades únicas de cada civilización.
- **Tecnología única**: lees qué hace y eliges de qué civ es.

Hay cuatro dificultades (de 4 opciones a todas), rondas de 10, 20, todas o infinitas, y los nombres pueden ir en inglés o en español. En *Estudiar* tienes la ficha de cada civ. Lo que más falles sale más a menudo; tu progreso se guarda solo en tu navegador.

Se juega con el ratón (o con las teclas 1-9, Enter y Esc).

## Jugar en local

Descarga el repo y abre `index.html` en el navegador. No hace falta instalar nada ni tener conexión.

## Actualizar los datos

Los escudos, los iconos y los textos salen de los archivos del juego. Si sale un DLC con civilizaciones nuevas, con el juego instalado:

```sh
python3 extraer.py [ruta/a/AoE2DE]
```

Sin ruta, busca la instalación de Steam en Linux (`~/.local/share/Steam/steamapps/common/AoE2DE`). El reparto de civs por expansión está escrito a mano en `extraer.py`: si avisa de una civ nueva, añádela a `EXPANSIONES`.

## Créditos

- Fuente [Cinzel](https://github.com/NDISCOVER/Cinzel), con licencia SIL Open Font License (`fuentes/OFL.txt`).
- Age of Empires II: Definitive Edition © Microsoft Corporation. Civilizaciones was created under Microsoft's "[Game Content Usage Rules](https://www.xbox.com/en-US/developers/rules)" using assets from Age of Empires II: Definitive Edition, and it is not endorsed by or affiliated with Microsoft.
