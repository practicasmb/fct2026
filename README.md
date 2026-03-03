# Arquitectura Base para Nuevos Proyectos Angular + Tailwind

Documento de referencia para arrancar proyectos frontend con Angular moderno y Tailwind. El objetivo es mantener una base escalable, testeable y consistente desde el día 1.

## 1. Arquitectura

### 1.1 Enfoque general

Se usa una arquitectura híbrida:

- **Feature-First:** el código de negocio se organiza por dominio funcional (`users`, `items`, `dashboard`, etc.).
- **Capas internas:** cada feature consume casos de uso y contratos de repositorio, sin acoplarse a detalles técnicos.

Resultado:

- Alta cohesión por feature.
- Bajo acoplamiento con API, framework UI o librerías concretas.
- Sustitución simple de mocks por implementación real.

### 1.2 Principios de diseño

- **Regla de dependencia:** las dependencias apuntan hacia el dominio.
- **Separación de responsabilidades:** UI, reglas de negocio y acceso a datos viven en capas distintas.
- **Arquitectura explícita:** cada archivo refleja su rol (`*.usecase.ts`, `*.repository.ts`, `*.store.ts`).
- **Escalabilidad incremental:** una feature nueva no debe obligar a modificar código de otras features.

### 1.3 Flujo estándar de datos

```text
UI (Page/Component)
  -> Store/Facade de la feature
  -> Use Case (dominio)
  -> Repository (puerto)
  -> Repository Implementation (infraestructura)
  -> API REST
```

Para lectura y escritura se sigue el mismo flujo; solo cambia la operación (query/command).

## 2. Módulos

En Angular moderno, los módulos funcionales se modelan con **standalone components** y rutas lazy, no con `NgModule`.

### 2.1 Estructura recomendada

```text
src/app/
  core/
  domain/
  infrastructure/
  features/
    <feature-name>/
      pages/
      components/
      state/
      resolvers/
      <feature-name>.routes.ts
  shared/
  theme/
```

### 2.2 Rol de cada módulo lógico

- `core`: autenticación, interceptores, guards, errores globales, configuración transversal.
- `domain`: entidades, value objects, contratos de repositorio y casos de uso.
- `infrastructure`: implementación de repositorios, mapeadores, cliente HTTP y DTOs.
- `features`: casos de uso de producto, pantallas y estado por feature.
- `shared`: piezas reutilizables sin lógica de negocio específica.
- `theme`: tokens visuales, variables y reglas globales de estilo.

### 2.3 Estructura mínima por feature

```text
features/cms-users/
  pages/
    user-list/
    user-detail/
  components/
  state/
    cms-users.store.ts
  resolvers/
  cms-users.routes.ts
```

## 3. Capas

| Capa | Responsabilidad | Depende de | No debe depender de |
| --- | --- | --- | --- |
| `domain` | Reglas de negocio y contratos | Tipos propios | `features`, `infrastructure` |
| `infrastructure` | Adaptadores externos (API, DTO, mappers) | `domain` | `features` |
| `core` | Servicios transversales de app | `shared` (utilidades), Angular | lógica específica de una feature |
| `features` | Casos de uso de UI y estado local por feature | `domain`, `core`, `shared` | implementación técnica de otra feature |
| `shared` | Componentes y utilidades reutilizables | Angular/Tailwind | reglas de negocio de una feature |
| `theme` | Tokens y estilos globales | Tailwind/CSS | lógica de negocio |

### 3.1 Reglas obligatorias

- `domain` no hace llamadas HTTP.
- `features` nunca accede a API directa; siempre vía use cases/repositorios.
- Los repositorios concretos se resuelven por DI en `app.config.ts`.
- Mientras no exista backend real, mantener repositorios mock y dejar `TODO` puntual para migración.

Ejemplo de TODO esperado:

```ts
// TODO add base url for API REST
```

## 4. Coding Style

### 4.1 Angular moderno (obligatorio)

- Componentes, directivas y pipes en modo `standalone`.
- Estado local y de feature con `signal`, `computed` y `effect`.
- Inyección con `inject()`.
- Inputs/outputs con `input()` y `output()`.
- Plantillas con control flow nativo: `@if`, `@for`, `@switch`.
- `ChangeDetectionStrategy.OnPush` por defecto.

### 4.2 Convenciones de nombres

- Archivos en `kebab-case`.
- Clases y tipos en `PascalCase`.
- Sufijos consistentes:
  - `*.component.ts`
  - `*.service.ts`
  - `*.store.ts`
  - `*.usecase.ts`
  - `*.repository.ts`
  - `*.mapper.ts`

### 4.3 Reglas de implementación

- Lógica de negocio en use cases, no en componentes.
- Componentes de página: orquestación y navegación.
- Componentes presentacionales: sin acceso a servicios de negocio.
- Formularios tipados y validaciones explícitas.
- Imports por alias (`@core/*`, `@domain/*`, `@features/*`, etc.) para evitar rutas relativas profundas.
- Mantener `strict` en TypeScript y cubrir casos límite con tests unitarios.

## 5. Design System

### 5.1 Principio rector

El sistema visual se basa en **tokens semánticos** y utilidades Tailwind. No se usan colores, tipografías o espaciados hardcodeados en componentes de negocio.

### 5.2 Jerarquía de tokens

- **Foundation tokens:** paleta, tipografías, escala de spacing, radios, sombras.
- **Semantic tokens:** intención (`--color-bg-surface`, `--color-text-muted`, `--color-border-default`).
- **Component tokens:** necesidades concretas (`--btn-primary-bg`, `--input-border-focus`).

### 5.3 Reglas de uso

- Definir tokens en el entrypoint de Tailwind (`@theme`).
- Centralizar estilos compartidos en `@layer components`.
- Usar utilidades de Tailwind en templates; evitar CSS ad-hoc por componente salvo excepciones justificadas.
- Mantener layout mobile-first y puntos de ruptura consistentes.
- Garantizar contraste, foco visible y estados `hover`/`active`/`disabled`.

### 5.4 Checklist de calidad visual

- No hay hex directos en páginas de feature.
- Todo color/tipo/espaciado viene de tokens.
- Los estados de error/éxito/información están tokenizados.
- La UI es usable en desktop y móvil sin overrides puntuales.

---

## Checklist de arranque de una feature nueva

1. Crear entidad, contrato de repositorio y use cases en `domain`.
2. Implementar repositorio mock en `infrastructure`.
3. Registrar provider en `app.config.ts`.
4. Crear rutas lazy + páginas standalone en `features/<feature>`.
5. Implementar store de feature con signals.
6. Aplicar tokens y utilidades de diseño desde `theme`/Tailwind.
7. Añadir tests unitarios de use cases, store y componentes clave.