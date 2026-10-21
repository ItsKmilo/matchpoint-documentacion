# Guía rápida de publicación y entrega — MatchPoint

## Qué estamos entregando

1. **Canvas de equipo:** documento visual en SVG editable + acuerdos escritos.
2. **Visión del producto:** documento accesible en la web y en Markdown.
3. **Mapa de historias de usuario:** SVG completo y 4 secciones detalladas, 20 historias organizadas en 6 épicas y 2 sprints.
4. **Product Backlog:** Excel, CSV y Markdown + buscador interactivo en la web. Cada HU tiene paso a paso (formato Identificador · Nombre · Descripción · Criterios de aceptación) y mockup.
5. **Plan de 2 sprints / 2 entregas:** sección «Sprints» de la web y hoja `03_Plan_Sprints`.
6. **URL del sitio:** se obtiene **después de publicarlo** en GitHub Pages.

## Estado de la revisión

- [x] Sitio web elaborado y archivos incorporados.
- [x] 20 historias contrastadas con la tabla del Product Backlog, el mapa y los mockups.
- [x] Comprobado que no faltan los enlaces a archivos locales.
- [x] Comprobado el funcionamiento del buscador, filtros y detalle de historias.
- [ ] El equipo confirma las metas personales y los acuerdos propuestos.
- [ ] Se socializan prioridades y entregas con la profesora para sus ajustes.
- [ ] Se publica la web en GitHub Pages y se comprueba la URL.
- [ ] Se entrega el enlace público en Canvas.

## Opción recomendada: Git desde Windows (PowerShell)

1. Crea el repositorio **público** `matchpoint-documentacion` en tu cuenta GitHub, sin README inicial.
2. Descomprime el ZIP en tu equipo.
3. Abre PowerShell **dentro de la carpeta que contiene `index.html`**.
4. Ejecuta los siguientes comandos, cambiando `TU_USUARIO` por tu usuario real:

```powershell
git init
git add .
git commit -m "Documentacion inicial MatchPoint"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/matchpoint-documentacion.git
git push -u origin main
```

5. Abre el repositorio en GitHub y entra a **Settings → Pages → Build and deployment**.
6. Elige **Deploy from a branch**, `main`, `/(root)` y guarda.
7. Espera a que aparezca la dirección del sitio. Verifica que puedes acceder sin iniciar sesión.

**Atención:** `https://TU_USUARIO.github.io/matchpoint-documentacion/` es solo una forma típica de la URL, no una dirección activa hasta que la hayas publicado. Si `git remote add origin` indica que ya existe un remoto, revisa la configuración con `git remote -v` antes de cambiarla.

## Comprobaciones antes de enviar

- [ ] La página inicial carga sin error.
- [ ] Se muestra el Team Canvas completo.
- [ ] Se lee la visión del producto y los usuarios previstos.
- [ ] Se pueden cambiar las cinco vistas del mapa de historias.
- [ ] El Product Backlog muestra 20 historias sin filtros.
- [ ] Al buscar `HU005`, se muestra su historia y el detalle abre la tabla paso a paso con su mockup.
- [ ] La sección «HU y mockups» muestra las 20 tarjetas y filtra por Sprint 1 / Sprint 2.
- [ ] Los botones para descargar SVG y Excel abren los archivos correctos.
- [ ] La URL se abre también desde un celular.
- [x] Los cuatro nombres están correctos: Santiago Solano, Maicol Rubiano, Diego Romero y Camilo Bastidas.

### Nota académica

Las metas individuales, acuerdos propuestos y priorización del backlog necesitan revisión y aprobación; el sitio no declara que ya se ha implementado la plataforma MatchPoint.


## Identidad académica y logo

La página incorpora el logo de la UMB suministrado por el estudiante en `assets/img/umb-logo-original.png`. El aviso «Trabajo académico» aclara que no es un sitio institucional oficial ni representa un sistema MatchPoint implementado.

## Evidencia de construcción del mapa

La guía solicita trabajo individual previo al consenso. El mapa de esta página es la propuesta **consolidada**, sin afirmar que se hayan elaborado o mostrado mapas individuales. Antes de presentar, documentar la participación de los integrantes y, si aplica, enlazar las propuestas individuales.

## Punto de revisión importante del backlog

El backlog tiene 20 historias en 2 sprints. Los controles críticos no se aplazan: permisos por rol (HU001), privacidad de la información propia (HU010) y descuento de créditos sin saldo negativo ni duplicados (HU008) están en el Sprint 1. Confirmar con la profesora la duración de los sprints y si las historias Could (HU019, HU020) se mantienen.
