# MatchPoint · Sitio de documentación (fase inicial)

Sitio estático listo para GitHub Pages con los entregables del proyecto **MatchPoint**, solicitado por **Nexo Digital Labs** como caso de estudio académico.

## Qué incluye

| Entregable | En la página | Archivo editable |
|---|---|---|
| Team Canvas | Sección «Equipo» | `descargas/Team_Canvas_MatchPoint_Editable.svg` (Adobe Illustrator) |
| Visión del producto | Sección «Visión» | `documentos/VISION_DEL_PRODUCTO.md` |
| Mapa de historias | Sección «Mapa» | `descargas/Mapa_Historias_MatchPoint_Editable.svg` y cuatro vistas parciales (6 épicas, 20 HU, 2 sprints) |
| Product Backlog | Sección «Backlog» con buscador y filtros por sprint | `descargas/Product_Backlog_MatchPoint.xlsx`, `.csv` y `documentos/PRODUCT_BACKLOG.md` |
| Historias paso a paso y mockups | Sección «HU y mockups» y detalle de cada historia | `assets/img/mockups/HU001.png`… y `descargas/mockups/*.svg` (ZIP: `descargas/MatchPoint_Mockups_HU_SVG.zip`) |
| Plan de 2 sprints | Sección «Sprints» | Hoja `03_Plan_Sprints` del Excel |

## Publicar en GitHub Pages paso a paso

1. Inicia sesión en **https://github.com** y crea un repositorio **público**, por ejemplo `matchpoint-documentacion`.
2. En la página del repositorio, usa **Add file → Upload files** y sube **todo el contenido de esta carpeta**, manteniendo la estructura de carpetas. Es imprescindible que `index.html` quede en la raíz del repositorio, no dentro de otra subcarpeta.
3. Confirma la carga (commit).
4. Abre **Settings → Pages**.
5. En **Build and deployment**, elige **Deploy from a branch**; selecciona `main` y la carpeta `/(root)`; guarda con **Save**.
6. Espera a que GitHub muestre la dirección del sitio y ábrela. Su estructura habitual es `https://TU_USUARIO.github.io/matchpoint-documentacion/`; reemplaza el usuario y el nombre por los reales. Esta dirección es ilustrativa, **no es una URL publicada todavía**.
7. Comprueba la portada, el buscador del backlog, las pestañas del mapa y los enlaces de descarga antes de enviar la URL a la docente.

**Nota:** no subas únicamente este README o el archivo ZIP. GitHub Pages necesita los archivos extraídos. También puedes cargar toda la carpeta usando Git desde tu equipo.

## Revisar localmente

Abre `index.html` en cualquier navegador. La lista de historias funciona sin internet porque está incluida como `assets/js/backlog-data.js` y no depende de solicitudes externas. La web es responsive y no usa frameworks o librerías de terceros.

## Estructura

```text
index.html                  Página principal
.nojekyll                   Hace que GitHub Pages sirva todos los archivos estáticos
assets/css/styles.css       Diseño responsive
assets/js/app.js            Filtros, buscador, diálogo y mapa
assets/js/backlog-data.js   20 historias con paso a paso y ruta de su mockup
assets/img/                 Recursos gráficos y mockups PNG (assets/img/mockups)
descargas/                  SVG vectoriales, mockups SVG, CSV y Excel
documentos/                Visión, acuerdos, índice y backlog en Markdown
```

## Estado académico

Los **cuatro roles** son la distribución propuesta para el equipo, pero las metas personales y las reglas del Team Canvas deben ratificarse por los integrantes. Las 20 historias (HU001 a HU020), su prioridad, responsables técnicos, los 2 sprints y las estimaciones son **propuestas**. La guía solicita socializar y ajustar el Product Backlog con la docente.

Los créditos MatchPoint son **virtuales** y no tienen valor monetario ni retiro o conversión a dinero. El diseño documenta una solución propuesta; **el sitio no es la plataforma MatchPoint operativa**.

## Equipo

- Santiago Solano — Scrum Master
- Maicol Rubiano — Backend Developer
- Diego Romero — Frontend Developer
- Camilo Bastidas — Database Administrator (DBA)

---

**Trabajo académico · Universidad Manuela Beltrán (UMB)**  
Logo de la UMB aportado por los estudiantes. El uso del logo identifica el contexto académico; esta web **no es un sitio oficial de la universidad**, de Nexo Digital Labs ni un producto MatchPoint en funcionamiento.  
Universidad Manuela Beltrán · Fase de inicio · MatchPoint


## Referencias utilizadas

- Guía «FASE DE INICIO» entregada en el aula. Indica Team Canvas, visión, mapa de historias (propuesta individual y consolidación grupal) y Product Backlog revisado con la docente.
- Giovanny Cifuentes, «Técnica Team Canvas (Lienzo de equipo) para crear cultura de equipo»: https://www.giovannycifuentes.com/tecnica-team-canvas-lienzo-de-equipo-para-crear-cultura-de-equipo/
- Ejemplo de mapa de historias compartido en clase: https://miro.com/app/board/o9J_lQKbLXc=/
- Enunciado académico «MatchPoint — Plataforma de gestión de torneos, pronósticos y créditos virtuales» (caso de Nexo Digital Labs).

## Por completar antes de entrega

- Confirmar en grupo las metas personales y reglas documentadas.
- La guía solicita un mapa individual previo por integrante y una consolidación grupal; este paquete incluye el **mapa colectivo**, no evidencia de cuatro trabajos individuales. Registrar dichas evidencias si la docente las solicita.
- Socializar el backlog con la profesora y aplicar correcciones que indique.
- Publicar el sitio en GitHub Pages y verificar el enlace sin iniciar sesión.


## Actualización: expedientes PDF y propuestas de mapa

El apartado **PDF y evidencias** (`#evidencias`) incorpora cuatro borradores de propuestas individuales y archivos PDF de respaldo, incluido el expediente completo de 44 páginas. Todas las rutas son relativas y funcionan en GitHub Pages.

**Nota:** los borradores individuales fueron preparados para revisión y no acreditan elaboración, socialización ni aprobación personal por cada estudiante. La docente debe revisar el mapa consolidado y el Product Backlog.

Si el repositorio ya está publicado en GitHub Pages, basta copiar estos archivos en la carpeta local, ejecutar `git add .`, `git commit -m "Agregar evidencias individuales y documentos PDF"` y `git push origin main`. No hace falta volver a activar Pages.
