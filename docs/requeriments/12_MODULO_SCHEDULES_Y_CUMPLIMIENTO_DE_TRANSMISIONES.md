# Módulo 12 — Schedules, Calendarios de Emisión y Control de Cumplimiento

## 1. Alcance y Modelos de Datos

Este módulo gestiona la planificación, calendarización, supervisión operativa y auditoría de cumplimiento de las pautas de transmisión en vivo de los creadores de contenido de la agencia. Resuelve la necesidad crítica de garantizar que los talentos cumplan los días estipulados de emisión, las franjas horarias acordadas y las horas mínimas pactadas en sus contratos, proporcionando trazabilidad formal entre lo programado (*planned schedule*) y lo efectivamente transmitido (*actual streaming sessions*).

Para dotar al sistema de máxima flexibilidad y apego a estándares de la industria, las pautas recurrentes utilizan **reglas de recurrencia RRULE bajo el estándar RFC 5545** (Internet Calendaring and Scheduling Core Object Specification), permitiendo definir frecuencias semanales con selección múltiple de días, frecuencias diarias, quincenales, mensuales e intervalos personalizados.

### Modelos de Base de Datos Involucrados:
- [`CreatorSchedulePattern`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/schedules/models/pattern.py) (`schedules_creator_schedule_pattern`): Pauta recurrente de horarios comprometida por el creador gobernada por reglas RFC 5545 (`rrule`). Contiene título, creador, plataforma/canal, regla RRULE (ej. `FREQ=WEEKLY;BYDAY=MO,WE,FR;INTERVAL=1`), franja horaria (`start_time`, `end_time`), temática planeada, duración requerida y vigencia temporal (`effective_from`, `effective_until`). Mantiene el alias `CreatorWeeklySchedule` para compatibilidad retroactiva.
- [`CreatorScheduleSlot`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/schedules/models/slot.py) (`schedules_creator_schedule_slot`): Instancia concreta fechada de transmisión en el calendario (cita programada). Registra las horas pactadas, horas efectivas transmitidas, estado de cumplimiento, desfase de inicio (*start delay*), porcentaje de cumplimiento y vínculo directo 1:1 opcional con la sesión real [`StreamingSession`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/streams/models.py).
- [`ScheduleException`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/schedules/models/exception.py) (`schedules_schedule_exception`): Justificaciones, licencias médicas, periodos vacacionales o contingencias técnicas aprobadas que exoneran formalmente al creador de transmitir en ciertas fechas sin penalizar sus indicadores.
- [`CreatorScheduleComplianceSummary`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/schedules/models/compliance.py) (`schedules_creator_compliance_summary`): Consolidado mensual y periódico de auditoría de cumplimiento. Totaliza días estipulados vs días cumplidos, horas pactadas vs horas realizadas, tasa de puntualidad e inasistencias injustificadas para alimentar el cierre de liquidaciones (*payouts*) y evaluación contractual.

---

## 2. Reglas de Negocio del Módulo (RN-SCH)

### RN-SCH-001: Ventana de Tolerancia para Puntualidad (Grace Period)
- La puntualidad del inicio de una transmisión se evalúa respecto a la hora pactada (`scheduled_start_time`).
- Se establece una **ventana de tolerancia estándar de 15 minutos** posterior a la hora programada.
- Si la sesión real inicia dentro del intervalo `[scheduled_start_time, scheduled_start_time + 15 min]`, se computa como **puntual** (`on_time = True`, `start_delay_minutes <= 15`).
- Si la sesión real inicia con más de 15 minutos de demora, se computa como **retraso** (`start_delay_minutes > 15`) y el slot se clasifica en estado `LATE` (salvo que no se alcance la duración mínima, caso en el que primará `PARTIAL`).

### RN-SCH-002: Criterios de Evaluación y Clasificación del Estado del Slot
El estado operativo de cada `CreatorScheduleSlot` se determina bajo las siguientes reglas formales de negocio:
1. **`SCHEDULED`**: Slot futuro o pendiente de ejecución sin sesión de stream vinculada aún.
2. **`COMPLETED`**: La transmisión real cumplió con al menos el **90.00%** de la duración pactada (`compliance_rate_pct >= 90.00`) y comenzó dentro del margen de tolerancia o sin penalización grave de horario.
3. **`PARTIAL`**: El creador transmitió pero no alcanzó el umbral del 90.00% estipulado (`0.00 < compliance_rate_pct < 90.00`).
4. **`LATE`**: El creador completó el tiempo mínimo de transmisión (`compliance_rate_pct >= 90.00`) pero inició con un desfase superior al margen de tolerancia (`start_delay_minutes > 15`).
5. **`MISSED`**: La fecha y hora límite del slot concluyeron y no se registró ninguna sesión de streaming vinculada o las horas efectivas fueron `0.00` sin existir justificación previa.
6. **`JUSTIFIED_ABSENCE`**: El slot coincidió con un periodo amparado por una `ScheduleException` debidamente aprobada por la agencia.
7. **`CANCELLED`**: El slot fue desconvocado con antelación por mutuo acuerdo entre la agencia y el talento.
8. **`RESCHEDULED`**: El slot fue movido formalmente a otra franja u otro día.

### RN-SCH-003: Validación Formal de Reglas RRULE y Detección de Superposiciones
- Toda pauta recurrente debe almacenar una cadena RRULE sintácticamente válida bajo la especificación RFC 5545 (evaluada mediante `python-dateutil.rrule`).
- Para un mismo creador, no pueden coexistir dos pautas recurrentes activas cuyas ocurrencias coincidan en fecha y se solapen en sus ventanas horarias `[start_time, end_time]` dentro de su período de vigencia compartido.

### RN-SCH-004: Generación Idempotente de Slots Calendario con Motor RRULE
- El motor de generación de slots proyecta las pautas recurrentes (`CreatorSchedulePattern`) utilizando `dateutil.rrule.rrulestr(pattern.rrule).between(start, end)` para obtener las fechas exactas de emisión.
- La generación debe ser estrictamente **idempotente**: si un slot ya existe para una fecha, creador y hora pactada, el sistema no duplica el registro, preservando cualquier estado o sesión real ya vinculada.

### RN-SCH-005: Conciliación Inteligente con Sesiones Reales (Reconciliation Engine)
- El proceso de conciliación asocia automáticamente las emisiones reales de [`StreamingSession`](file:///home/diego/Proyectos/rrss-creators-analyzer/rrss_creatos_analyzer/apps/streams/models.py) con el `CreatorScheduleSlot` más coherente según los siguientes criterios:
  1. Coincidencia exacta de `creator_id`.
  2. Coincidencia de fecha calendario (`scheduled_date == streamed_at.date()`).
  3. Coincidencia opcional de canal/plataforma (`channel_id` o `platform`).
  4. Cercanía temporal: La hora de inicio real `streamed_at` debe encontrarse dentro de una ventana de captura de `scheduled_start_time ± 120 minutos`.
- Si se concilia la sesión:
  - `actual_streaming_session = session`
  - `actual_start_datetime = session.streamed_at`
  - `actual_end_datetime = session.ended_at`
  - `actual_duration_minutes = session.duration_seconds // 60`
  - `actual_hours = session.hours_streamed`
  - `compliance_rate_pct = min(100.00, (actual_hours / planned_hours) * 100.00)`

### RN-SCH-006: Tratamiento y Exclusión de Ausencias Justificadas
- Todo slot cuya `scheduled_date` coincida con una `ScheduleException` aprobada (`is_approved = True`) pasa automáticamente a estado `JUSTIFIED_ABSENCE`.
- En el cálculo del consolidado mensual de cumplimiento (`CreatorScheduleComplianceSummary`):
  - Los días y horas en `JUSTIFIED_ABSENCE` **no se contabilizan como faltas** (`missed_days_count`).
  - La base para el cálculo de la tasa de cumplimiento de días considera los días estipulados netos:
    $$\text{days\_compliance\_rate\_pct} = \frac{\text{completed\_days\_count} + \text{late\_days\_count}}{\text{stipulated\_days\_count} - \text{justified\_days\_count}} \times 100$$
  - De igual forma, las horas justificadas se deducen para formar la cuota horaria neta exigible.

### RN-SCH-007: Consistencia Temporal y Duración Estipulada
- En todo patrón u horario, `planned_duration_minutes` debe ser estrictamente mayor a 0 (`planned_duration_minutes > 0`).
- La hora de fin estipulada (`end_time`) debe ser posterior a la hora de inicio (`start_time`), y la fecha de vigencia final (`effective_until`) debe ser igual o superior a la fecha inicial (`effective_from`).

### RN-SCH-008: Métricas Consolidadas de Auditoría Mensual
- Cada registro de `CreatorScheduleComplianceSummary` computa:
  - **Tasa de Cumplimiento de Horas**: $\min(100.00, (\text{actual\_hours} / \text{stipulated\_hours}) \times 100)$
  - **Tasa de Puntualidad**: $(\text{on\_time\_starts\_count} / (\text{completed\_days\_count} + \text{late\_days\_count})) \times 100$
  - **Estatus de Conformidad Global (`is_compliant`)**: `True` si `hours_compliance_rate_pct >= 90.00` y `days_compliance_rate_pct >= 85.00`.

### RN-SCH-009: Interfaz de Usuario Intuitiva y Entrada Directa de RRULE
- La UI no obliga al usuario a escribir código sintáctico RRULE, sino que dispone de un **Constructor Visual Intuitivo**:
  - Selector por botones de frecuencia: Semanal, Diaria, Mensual.
  - Intervalo de repetición numérico ("Repetir cada X semanas/días").
  - Botones toggle de selección rápida de días: "Lunes a Viernes", "Fin de semana", "Todos los días".
  - Resumen dinámico en lenguaje natural en tiempo real: *"Cada semana los Lunes, Miércoles y Viernes"*.
  - Modo Avanzado desplegable que permite **introducir o pegar directamente una cadena RFC 5545 RRULE**, sincronizando bidireccionalmente el constructor visual y validando en el cliente y servidor.

### RN-SCH-010: Visibilidad y Control de Acceso RBAC
- Los creadores únicamente tienen acceso a sus propias pautas, slots y excepciones.
- Los managers y administradores acceden al universo completo de creadores, disponiendo de permisos exclusivos para aprobar licencias médicas y contingencias.

---

## 3. Casos de Uso del Módulo

### CU-SCH-01: Configurar Pauta Recurrente mediante Constructor RRULE o Entrada Directa
- **Actor Primario**: Talent Manager (`ACT-MGR`) o Company Admin (`ACT-ADM`).
- **Precondiciones**: Creador existente con canal configurado.
- **Disparador**: Definición o ajuste de la pauta de transmisión habitual del talento.
- **Flujo Principal**:
  1. El actor accede a **Schedules > Pautas Recurrentes > Nueva Pauta**.
  2. Selecciona creador, título descriptivo, canal, plataforma, horario de inicio/fin y temática.
  3. En la sección de recurrencia, utiliza los controles visuales intuitivos:
     - Frecuencia (Semanal, Diaria, Mensual).
     - Días específicos de transmisión mediante botones toggle o atajos (L-V, Fin de semana).
     - Opcionalmente abre el Modo Avanzado para pegar directamente una cadena RRULE estándar.
  4. La interfaz muestra en tiempo real la interpretación en español de la agenda.
  5. Pulsa **Guardar Pauta**.
  6. El sistema valida la coherencia temporal, ausencia de traslapes y sintaxis RFC 5545, persistiendo el registro `CreatorSchedulePattern`.
- **Postcondiciones**: El patrón recurrente queda activo para la proyección automatizada de citas en el calendario.

---

### CU-SCH-02: Generar Lote de Slots en Calendario para un Periodo
- **Actor Primario**: Talent Manager (`ACT-MGR`) o Business Analyst (`ACT-ANA`).
- **Precondiciones**: Existencia de pautas recurrentes activas.
- **Disparador**: Planificación quincenal, mensual o bimestral.
- **Flujo Principal**:
  1. El actor accede a **Schedules > Generar Lote de Slots**.
  2. Define rango de fechas (`start_date` a `end_date`) y creador (o todos).
  3. El motor ejecuta `rule.between(...)` para cada pauta activa y genera de manera idempotente los registros `CreatorScheduleSlot`.
  4. Los slots coincidentes con excepciones aprobadas se marcan de inmediato como `JUSTIFIED_ABSENCE`.
- **Postcondiciones**: La agenda proyectada queda disponible en FullCalendar y en vistas de lista.

---

### CU-SCH-03: Crear Slot Extraordinario o Ad-hoc
- **Actor Primario**: Talent Manager (`ACT-MGR`).
- **Disparador**: Transmisión especial puntual no cubierta por la pauta habitual (ej. torneo, maratón, evento especial).
- **Flujo Principal**:
  1. El actor accede a **Nuevo Slot**.
  2. Ingresa creador, fecha fija, hora inicio/fin, título y duración.
  3. Guarda el slot con indicador de obligatoriedad según corresponda.
- **Postcondiciones**: El slot computa dentro del período mensual correspondiente.

---

### CU-SCH-04: Conciliar Sesiones Reales con Slots de Calendario
- **Actor Primario**: Proceso Asíncrono o Staff de Agencia.
- **Disparador**: Ingesta diaria de emisiones o pulsación de "Conciliar" en slot.
- **Flujo Principal**:
  1. El motor busca sesiones de streaming de ese creador dentro de $\pm 120$ minutos del inicio programado.
  2. Asocia la sesión, calcula retraso en minutos, horas reales y tasa de cumplimiento.
  3. Clasifica en `COMPLETED`, `LATE`, `PARTIAL` o `MISSED`.
- **Postcondiciones**: Métricas operativas registradas con auditoría de cambios.

---

### CU-SCH-05: Registrar y Aprobar Justificación de Ausencia
- **Actor Primario**: Creador (`ACT-TAL`) o Talent Manager (`ACT-MGR`).
- **Flujo Principal**:
  1. Se registra una excepción con rango de fechas, motivo y comprobante.
  2. El staff revisa y aprueba la excepción.
  3. Los slots comprendidos en el rango cambian automáticamente a `JUSTIFIED_ABSENCE`.
- **Postcondiciones**: La inasistencia queda exonerada en las tasas de cumplimiento.

---

### CU-SCH-06: Generar y Auditar Resumen Mensual de Cumplimiento
- **Actor Primario**: Business Analyst (`ACT-ANA`) o Financial Director (`ACT-FIN`).
- **Flujo Principal**:
  1. Se solicita el recálculo o cierre mensual para un creador, mes y año.
  2. El sistema calcula días estipulados netos, horas efectivas, puntualidad y condición contractual `is_compliant`.
  3. Guarda o actualiza el registro `CreatorScheduleComplianceSummary`.
- **Postcondiciones**: El informe consolidado queda disponible para el módulo de liquidaciones y contratos.
