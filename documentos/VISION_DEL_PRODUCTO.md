# MatchPoint — Visión del producto

**Empresa solicitante:** Nexo Digital Labs  
**Producto:** MatchPoint  
**Fase:** Inicio del proyecto  
**Equipo:** Santiago Solano, Maicol Rubiano, Diego Romero y Camilo Bastidas

> **Visión:** Desarrollar MatchPoint como una plataforma deportiva confiable y fácil de utilizar, donde los usuarios puedan participar en torneos, realizar pronósticos y administrar sus créditos virtuales, mientras los administradores mantienen un control organizado sobre los eventos, resultados y transacciones.

## 1. Descripción

MatchPoint es una plataforma digital diseñada para facilitar la administración de torneos deportivos, permitir que los usuarios consulten eventos, registren sus pronósticos y participen utilizando créditos virtuales. Reúne estas actividades en un solo sistema y busca conservar un historial verificable de las operaciones.

## 2. Problema que resuelve

Las herramientas independientes, las hojas de cálculo y los procesos manuales dificultan el seguimiento de participantes, resultados y créditos. Además, los fallos de conexión y las solicitudes repetidas pueden ocasionar descuentos duplicados o movimientos inconsistentes. MatchPoint busca centralizar el proceso y mantener la trazabilidad.

## 3. Objetivo general

Desarrollar una plataforma que permita gestionar torneos deportivos, registrar pronósticos, administrar créditos virtuales y procesar resultados de forma confiable, garantizando seguimiento y consistencia de las operaciones realizadas.

## 4. Objetivos específicos

1. Crear y administrar torneos y eventos deportivos.
2. Permitir la consulta de encuentros y el registro de pronósticos válidos.
3. Gestionar créditos virtuales verificando saldos antes de cada participación.
4. Conservar el historial de movimientos y transacciones.
5. Publicar resultados oficiales e identificar pronósticos acertados.
6. Evitar descuentos y premios duplicados, incluso ante operaciones simultáneas.
7. Diseñar una solución organizada, mantenible y preparada para extensiones.

## 5. Usuarios

- **Participante:** consulta torneos, participa en pronósticos, revisa saldo, movimientos y resultados.
- **Administrador:** crea torneos, programa eventos, administra participantes y publica resultados.
- **Responsable de control (función autorizada):** audita operaciones, revisa liquidaciones, ajustes e inconsistencias. No se exige una cuenta separada: puede tratarse de un conjunto de permisos administrativos.

## 6. Módulos principales

1. Identidad y permisos.
2. Torneos y eventos.
3. Catálogo y consulta de encuentros.
4. Registro de pronósticos.
5. Créditos y movimientos.
6. Transacciones confiables e idempotencia.
7. Resultados y liquidaciones.
8. Historial, auditoría y reportes.

## 7. Propuesta de valor

Los participantes dispondrán de una experiencia centralizada para consultar eventos y seguir sus participaciones. Los administradores podrán gestionar torneos y verificar resultados y créditos desde una misma solución, con registro de movimientos y posibilidad de investigar errores.

## 8. Reglas del producto

- Los créditos son virtuales: no representan dinero, no pueden retirarse ni convertirse en dinero real.
- Las participaciones se aceptan únicamente dentro del plazo habilitado.
- Ninguna operación puede dejar saldo negativo.
- Solo usuarios autorizados pueden administrar torneos o resultados.
- Las solicitudes repetidas o simultáneas no generan descuentos ni premios duplicados.
- Las correcciones y reversiones conservan el historial de las operaciones previas.
- Los participantes acceden únicamente a su información autorizada.

## 9. Alcance propuesto en dos sprints

El backlog se concentró en **20 historias de usuario** (HU001 a HU020) organizadas en **6 épicas** y planificadas en **2 sprints, cada uno con su entrega**:

- **Sprint 1 · Entrega 1 — Configurar y participar:** inicio de sesión por rol, registro de participantes con créditos iniciales, creación, edición y eliminación de torneos, programación de eventos, consulta de eventos, registro de pronósticos con descuento seguro y consulta de saldo y movimientos.
- **Sprint 2 · Entrega 2 — Resolver y controlar:** consulta y anulación de pronósticos, cierre de la recepción, publicación y corrección de resultados, liquidación sin premios duplicados, ajustes autorizados de créditos, consulta de transacciones, conciliación de saldos y reporte del torneo.

La integridad transaccional, la autorización y la trazabilidad forman parte del Sprint 1, no son mejoras opcionales. Cada historia cuenta con un paso a paso de criterios de aceptación y un mockup de su pantalla. Las fechas de los sprints se acuerdan con la profesora.

## 10. Resultado esperado

Contar con una solución funcional en la que sea posible verificar registros de pronósticos, movimientos de crédito, resultados y liquidaciones. Deberá facilitar la detección de inconsistencias y el seguimiento de cada transacción.

---

**Estado:** Documento académico de visión inicial. Los acuerdos, prioridades, estimaciones y alcance por entrega están sujetos a revisión del equipo y la docente.
