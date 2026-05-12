# Guia Localio (localize): instalacion, uso y comparativa

## 1. Que es Localio y que hace localize

Localio es una herramienta CLI (linea de comandos) para transformar un archivo fuente de traducciones (normalmente XLSX) en archivos de salida para la app (en este proyecto, JSON).

El comando que se ejecuta es `localize` (normalmente via `bundle exec localize`).

Flujo general:
1. Lee la configuracion en `localio.yml`.
2. Toma la fuente de textos (archivo local o URL XLSX).
3. Interpreta claves, idiomas, plurales y placeholders.
4. Genera los JSON en la carpeta de salida.

En este repo, la salida va a `src/assets/i18n`.

## 2. Instalacion en un proyecto nuevo

### Requisitos
- Ruby instalado.
- Bundler instalado.
- Proyecto con Node/npm (si quieres integrarlo al flujo npm).

### Paso a paso
1. Crear `Gemfile` en la raiz del frontend e incluir Localio:

   source "https://rubygems.org"

   gem 'localio',
       git: 'https://bitbucket.org/mobivery-public/localio',
       branch: 'main'

2. Instalar dependencias Ruby:
- Ejecutar `bundle install`.

3. Crear `localio.yml`:

   job:
     format: json
     output_path: ./src/assets/i18n
     source:
       path: translations.xlsx
       sheet: 0
     key_format: none
     default_language: es

4. (Opcional pero recomendado) Crear un script Node para ejecutar localize sin romper el arranque si falta Bundler.
- En este repo se usa `scripts/run-i18n.mjs`.

5. Conectar scripts npm:
- Ejemplo:
  - `i18n`: node ./scripts/run-i18n.mjs
  - `start`: npm run i18n && ng serve

6. Ejecutar localizacion:
- `npm run i18n`

7. Verificar salida:
- Revisar JSON generados en `src/assets/i18n`.

## 3. Como se usa en el dia a dia

Uso tipico:
1. Actualizas traducciones en tu fuente (XLSX, Google Drive o Lokalise exportado a XLSX).
2. Ejecutas `npm run i18n`.
3. Se regeneran archivos JSON.
4. Levantas la app con `npm run start`.

## 4. Por que [key] y no key

En esta version de Localio, el parser XLSX no toma "key" como un encabezado normal.
Busca marcadores literales para delimitar un bloque:
- Inicio del bloque: `[key]`
- Fin del bloque: `[end]`

Si escribes `key` sin corchetes, el parser no lo reconoce como marcador de estructura.
Resultado: falla con error de formato porque "no encuentra [key]".

### Estructura minima esperada en XLSX
1. Fila inicial: `[key] | en | es`
2. Filas de contenido: `mi.clave | texto EN | texto ES`
3. Fila final: `[end]`

## 5. Diferencias entre Google Drive y Lokalise

| Tema | Google Drive | Lokalise |
|---|---|---|
| Objetivo principal | Hoja compartida simple para editar textos | Plataforma especializada de localizacion |
| Curva de entrada | Muy baja | Media |
| Flujo colaborativo | Manual, basado en hoja | Gestion avanzada con roles, historial, QA |
| Control de calidad | Basico (manual) | Avanzado (checks y validaciones) |
| Integraciones | Limitadas y mas manuales | Amplias (CI/CD, API, TMS) |
| Coste | Puede ser gratis en uso basico | Normalmente de pago segun plan |
| Fuente para Localio | URL de export XLSX (`pub?output=xlsx`) | Export XLSX (manual o API) |
| Escenario ideal | Equipos pequenos, setup rapido | Equipos medianos/grandes, flujo profesional |

## 6. Como conectarlo con cada opcion

### Opcion A: Google Drive
1. Publicar la hoja.
2. Usar URL directa de export XLSX (no la URL de vista HTML).
3. Ponerla en `localio.yml` en `job.source.url`.
4. Ejecutar `npm run i18n`.

Ejemplo de URL valida:
- `https://docs.google.com/spreadsheets/d/e/.../pub?output=xlsx`

### Opcion B: Lokalise
1. Mantener claves y estructuras en Lokalise.
2. Exportar a XLSX (manual o via API/CLI).
3. Guardar como `translations.xlsx` (o ajustar `source.path`).
4. Ejecutar `npm run i18n`.

## 7. Recomendacion practica

- Si quieres empezar rapido: Google Drive + Localio.
- Si necesitas control, QA y escalado: Lokalise + Localio.

Localio se mantiene como capa de transformacion final para generar los JSON de la app.
