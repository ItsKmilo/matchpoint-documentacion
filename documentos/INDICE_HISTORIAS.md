# MatchPoint · Índice de historias de usuario

**Empresa:** Nexo Digital Labs
**Equipo:** Santiago Solano · Maicol Rubiano · Diego Romero · Camilo Bastias
**Estado:** Propuesta a revisar con el equipo y la docente.

## Organización en sprints

- **Sprint 1 · Entrega 1 (Configurar y participar):** 10 historias · 39 SP.
- **Sprint 2 · Entrega 2 (Resolver y controlar):** 10 historias · 43 SP.

El Product Backlog (`PRODUCT_BACKLOG.md`) contiene el paso a paso completo y el mockup de cada historia; este documento es un índice complementario al mapa visual.

## Épica 01. Acceso y usuarios
**Etapa:** 01 · Administración de competencias. **Actividades:** Ingresar a la plataforma, Gestionar participantes.

### HU001 — Iniciar sesión
- **Sprint 1** · **MoSCoW:** Must · **Actor:** Usuario (participante o administrador) · **Actividad:** Ingresar a la plataforma
- **Necesidad:** Quiero iniciar sesión con mi usuario y contraseña para acceder únicamente a las funciones autorizadas para mi rol.
- **Paso 1:** Al ingresar a MatchPoint sin una sesión activa, el sistema deberá mostrar la pantalla de inicio de sesión con los campos usuario y contraseña.
- **Mockup:** Pantalla de inicio de sesión con validación de campos y mensaje de error genérico.

### HU002 — Registrar participante
- **Sprint 1** · **MoSCoW:** Must · **Actor:** Administrador · **Actividad:** Gestionar participantes
- **Necesidad:** Quiero registrar participantes para que puedan ingresar a MatchPoint y participar en los torneos.
- **Paso 1:** Al seleccionar la opción «Nuevo participante» desde la lista de participantes, el sistema deberá mostrar el formulario de registro.
- **Mockup:** Lista de participantes con el diálogo «Nuevo participante» y validación de correo duplicado.

## Épica 02. Torneos y eventos
**Etapa:** 01 · Administración de competencias. **Actividades:** Gestionar torneos, Programar eventos.

### HU003 — Crear torneo
- **Sprint 1** · **MoSCoW:** Must · **Actor:** Administrador · **Actividad:** Gestionar torneos
- **Necesidad:** Quiero crear un torneo deportivo para organizar sus eventos y habilitar la participación.
- **Paso 1:** Al seleccionar la opción «Crear torneo» desde la lista de torneos, el sistema deberá mostrar el formulario con nombre, deporte, fecha de inicio, fecha de fin y descripción.
- **Mockup:** Formulario de creación de torneo con validación de fechas y vista previa.

### HU004 — Editar torneo
- **Sprint 1** · **MoSCoW:** Should · **Actor:** Administrador · **Actividad:** Gestionar torneos
- **Necesidad:** Quiero editar los datos de un torneo para corregir o actualizar su información sin afectar los pronósticos registrados.
- **Paso 1:** Al seleccionar la opción «Editar» en un torneo de la lista, el sistema deberá mostrar el formulario con los datos actuales cargados.
- **Mockup:** Formulario de edición con datos cargados, aviso de eventos asociados e historial de cambios.

### HU005 — Eliminar torneo
- **Sprint 1** · **MoSCoW:** Should · **Actor:** Administrador · **Actividad:** Gestionar torneos
- **Necesidad:** Quiero eliminar un torneo para retirarlo de la plataforma en caso de que ya no se necesite, siempre y cuando no tenga eventos asociados.
- **Paso 1:** Al seleccionar la opción «Eliminar torneo» desde la lista de torneos, el sistema deberá validar si el torneo tiene eventos asociados.
- **Mockup:** Lista de torneos con diálogo de confirmación y mensaje cuando el torneo tiene eventos.

### HU006 — Programar evento
- **Sprint 1** · **MoSCoW:** Must · **Actor:** Administrador · **Actividad:** Programar eventos
- **Necesidad:** Quiero programar un evento dentro de un torneo para definir los contendientes, la fecha límite para pronosticar, el costo y el premio en créditos.
- **Paso 1:** Al seleccionar la opción «Agregar evento» dentro del detalle de un torneo, el sistema deberá mostrar el formulario del encuentro.
- **Mockup:** Formulario de evento con opciones de pronóstico, validación de fecha límite y calendario del torneo.

## Épica 03. Pronósticos
**Etapa:** 02 · Pronósticos. **Actividades:** Explorar eventos, Pronosticar y seguir.

### HU007 — Consultar torneos y eventos
- **Sprint 1** · **MoSCoW:** Must · **Actor:** Participante · **Actividad:** Explorar eventos
- **Necesidad:** Quiero consultar los torneos activos y sus eventos para conocer en qué puedo pronosticar, hasta cuándo y con qué costo.
- **Paso 1:** Al ingresar al panel de participante, el sistema deberá mostrar la lista de torneos activos con nombre, deporte y fechas.
- **Mockup:** Panel del participante con torneos activos, eventos, estados y filtro.

### HU008 — Registrar pronóstico
- **Sprint 1** · **MoSCoW:** Must · **Actor:** Participante · **Actividad:** Pronosticar y seguir
- **Necesidad:** Quiero registrar un pronóstico en un evento abierto para participar usando mis créditos virtuales.
- **Paso 1:** Al seleccionar la opción «Pronosticar» en un evento abierto, el sistema deberá mostrar las opciones válidas, el costo en créditos y el saldo disponible.
- **Mockup:** Detalle del evento con opciones, diálogo de confirmación y estado de saldo insuficiente.

### HU011 — Consultar mis pronósticos
- **Sprint 2** · **MoSCoW:** Must · **Actor:** Participante · **Actividad:** Pronosticar y seguir
- **Necesidad:** Quiero consultar mis pronósticos y su estado para saber cuáles están pendientes, cuáles acerté y qué premio recibí.
- **Paso 1:** Al seleccionar la opción «Mis pronósticos», el sistema deberá mostrar la lista de pronósticos del participante con torneo, evento, opción elegida, créditos y estado.
- **Mockup:** Lista «Mis pronósticos» con estados y panel de detalle con resultado y premio.

### HU012 — Anular pronóstico
- **Sprint 2** · **MoSCoW:** Should · **Actor:** Participante · **Actividad:** Pronosticar y seguir
- **Necesidad:** Quiero anular un pronóstico antes de la fecha límite para recuperar mis créditos si cambio de decisión, siempre y cuando el evento siga abierto.
- **Paso 1:** Al seleccionar la opción «Anular» en un pronóstico pendiente, el sistema deberá validar si el evento sigue abierto.
- **Mockup:** Mis pronósticos con diálogo de anulación y mensaje de evento cerrado.

## Épica 04. Créditos virtuales
**Etapa:** 03 · Créditos virtuales. **Actividades:** Asignar créditos, Consultar y ajustar saldo.

### HU009 — Asignar créditos iniciales
- **Sprint 1** · **MoSCoW:** Must · **Actor:** Administrador / sistema · **Actividad:** Asignar créditos
- **Necesidad:** Quiero que cada participante reciba automáticamente su saldo inicial de créditos virtuales para que pueda participar desde su registro.
- **Paso 1:** Al registrar un nuevo participante (HU002), el sistema deberá asignarle automáticamente el saldo inicial configurado (por ejemplo, 1.000 créditos).
- **Mockup:** Detalle del participante con saldo inicial, movimiento de asignación y bloqueo de doble asignación.

### HU010 — Consultar saldo y movimientos
- **Sprint 1** · **MoSCoW:** Must · **Actor:** Participante · **Actividad:** Consultar y ajustar saldo
- **Necesidad:** Quiero consultar mi saldo y mis movimientos de créditos para verificar cada descuento y cada premio.
- **Paso 1:** Al seleccionar la opción «Mis créditos», el sistema deberá mostrar el saldo disponible actualizado.
- **Mockup:** Pantalla «Mis créditos» con saldo, movimientos coloreados y verificación de suma.

### HU017 — Ajustar créditos autorizados
- **Sprint 2** · **MoSCoW:** Should · **Actor:** Responsable de control · **Actividad:** Consultar y ajustar saldo
- **Necesidad:** Quiero registrar ajustes de créditos justificados para corregir saldos de forma trazable.
- **Paso 1:** Al seleccionar la opción «Ajustar créditos» en el detalle de un participante, el sistema deberá mostrar el formulario con tipo (abono o cargo), cantidad y motivo obligatorio.
- **Mockup:** Diálogo de ajuste con tipo, cantidad, motivo y saldo resultante.

## Épica 05. Resultados y liquidación
**Etapa:** 04 · Resultados y control. **Actividades:** Cerrar y publicar, Liquidar y corregir.

### HU013 — Cerrar recepción de pronósticos
- **Sprint 2** · **MoSCoW:** Must · **Actor:** Administrador / sistema · **Actividad:** Cerrar y publicar
- **Necesidad:** Quiero que la recepción de pronósticos se cierre en la fecha límite para que nadie pronostique cuando el evento ya comenzó.
- **Paso 1:** Al llegar la fecha límite de un evento, el sistema deberá cambiar automáticamente su estado a «Cerrado».
- **Mockup:** Lista de eventos con cierre automático, diálogo de cierre manual y distribución de pronósticos.

### HU014 — Publicar resultado oficial
- **Sprint 2** · **MoSCoW:** Must · **Actor:** Administrador · **Actividad:** Cerrar y publicar
- **Necesidad:** Quiero publicar el resultado oficial de un evento cerrado para que los pronósticos puedan liquidarse.
- **Paso 1:** Al seleccionar la opción «Registrar resultado» en un evento cerrado, el sistema deberá mostrar el formulario con el marcador y la opción ganadora.
- **Mockup:** Formulario de resultado con opción ganadora, diálogo de publicación y bloqueo de evento abierto.

### HU015 — Liquidar evento y acreditar premios
- **Sprint 2** · **MoSCoW:** Must · **Actor:** Administrador · **Actividad:** Liquidar y corregir
- **Necesidad:** Quiero liquidar un evento finalizado para acreditar los premios de los pronósticos acertados una sola vez.
- **Paso 1:** Al seleccionar la opción «Liquidar» en un evento finalizado, el sistema deberá identificar los pronósticos acertados según el resultado oficial.
- **Mockup:** Resumen de liquidación con indicadores, ganadores y aviso de evento ya liquidado.

### HU016 — Corregir resultado publicado
- **Sprint 2** · **MoSCoW:** Should · **Actor:** Administrador · **Actividad:** Liquidar y corregir
- **Necesidad:** Quiero corregir un resultado publicado por error para recalcular los premios sin borrar el historial de lo ocurrido.
- **Paso 1:** Al seleccionar la opción «Corregir resultado» en un evento finalizado, el sistema deberá solicitar el nuevo resultado y un motivo obligatorio.
- **Mockup:** Formulario de corrección con motivo, diálogo de impacto e historial de correcciones.

## Épica 06. Auditoría y reportes
**Etapa:** 04 · Resultados y control. **Actividades:** Auditar movimientos, Consolidar información.

### HU018 — Consultar transacciones
- **Sprint 2** · **MoSCoW:** Must · **Actor:** Responsable de control · **Actividad:** Auditar movimientos
- **Necesidad:** Quiero consultar todas las transacciones de créditos para verificar su origen y detectar errores.
- **Paso 1:** Al seleccionar la opción «Transacciones» en el panel de control, el sistema deberá listar los movimientos con identificador, fecha, usuario, tipo, valor y origen.
- **Mockup:** Tabla de transacciones con filtros y panel de detalle de solo lectura.

### HU019 — Conciliar saldos
- **Sprint 2** · **MoSCoW:** Could · **Actor:** Responsable de control · **Actividad:** Auditar movimientos
- **Necesidad:** Quiero comparar cada saldo con la suma de sus movimientos para detectar inconsistencias.
- **Paso 1:** Al seleccionar la opción «Ejecutar conciliación», el sistema deberá recalcular el saldo de cada participante a partir de sus movimientos.
- **Mockup:** Tabla de conciliación con diferencias resaltadas y descarga CSV.

### HU020 — Generar reporte del torneo
- **Sprint 2** · **MoSCoW:** Could · **Actor:** Administrador · **Actividad:** Consolidar información
- **Necesidad:** Quiero generar un reporte del torneo para conocer la participación, los aciertos y los créditos utilizados y entregados.
- **Paso 1:** Al seleccionar la opción «Reporte» en un torneo, el sistema deberá mostrar el resumen de eventos, pronósticos, aciertos, créditos usados y créditos entregados como premio.
- **Mockup:** Reporte del torneo con indicadores, gráfico por evento y descargas.
