# Matriz de Trazabilidad Total y Compendio Maestro de Reglas de Negocio

## 1. Matriz de Trazabilidad de Requerimientos

La siguiente matriz consolida la relación bidireccional entre los Casos de Uso, Módulos, Modelos del ORM de Django, Actores involucrados y las Reglas de Negocio que gobiernan su comportamiento:

| Código CU | Título del Caso de Uso | Módulo / App | Modelos Django Involucrados | Actores Primarios | Reglas de Negocio Asociadas |
|---|---|---|---|---|---|
| **CU-USR-01** | Invitar Nuevo Miembro a la Plataforma | `members`, `users` | `MemberInvitation`, `User`, `RoleGroupProfile` | Company Admin | RN-SEC-001, RN-SEC-002, RN-SEC-007 |
| **CU-USR-02** | Aceptar Invitación y Completar Registro | `members`, `users` | `MemberInvitation`, `User`, `Group` | Invitado | RN-SEC-001, RN-SEC-002, RN-SEC-003 |
| **CU-USR-03** | Asignar y Revocar Roles a Usuarios | `permissions`, `users` | `RoleGroupProfile`, `User`, `Group` | Company Admin | RN-SEC-003, RN-SEC-006, RN-SEC-007 |
| **CU-USR-04** | Conformar Equipo de Trabajo para un Creador | `members`, `creators` | `CreatorTeamAssignment`, `Creator`, `User` | Company Admin, Manager | RN-SEC-005, RN-CRE-001 |
| **CU-USR-05** | Modificar Perfil y Zona Horaria | `users` | `User` | Todos los Usuarios | RN-SEC-001 |
| **CU-USR-06** | Desactivar o Suspender Acceso de Usuario | `users`, `audit` | `User`, `AuditEvent` | Company Admin | RN-SEC-006, RN-SYS-002 |
| **CU-CRE-01** | Alta de Creador en el Roster (Onboarding) | `creators` | `Creator` | Talent Manager, Admin | RN-CRE-001, RN-CRE-002 |
| **CU-CRE-02** | Registrar Información Confidencial KYC y Bancaria | `creators`, `audit` | `CreatorPersonalInfo`, `Creator`, `AuditEvent` | Finance Director, Admin | RN-CRE-003, RN-SEC-004 |
| **CU-CRE-03** | Vincular y Configurar Canales de Redes Sociales | `creators` | `Channel`, `Creator` | Talent Manager, Analyst | RN-CRE-004, RN-CRE-005 |
| **CU-CRE-04** | Registrar Snapshot Diario de Audiencia | `creators` | `ChannelSnapshot`, `Channel` | Worker Celery, Analyst | RN-CRE-005, RN-DAT-006 |
| **CU-CRE-05** | Redactar Borrador de Contrato de Representación | `contracts`, `creators` | `Contract`, `Creator` | Company Admin, Manager | RN-CRE-006, RN-CRE-007, RN-CRE-008 |
| **CU-CRE-06** | Formalizar y Activar Contrato | `contracts`, `creators` | `Contract`, `Creator`, `AuditEvent` | Finance Director, Admin | RN-CRE-006, RN-CRE-008, RN-CRE-009 |
| **CU-CRE-07** | Rescindir Contrato Anticipadamente | `contracts`, `creators` | `Contract`, `Creator` | Company Admin | RN-CRE-006, RN-PAY-003 |
| **CU-CRE-08** | Consultar Ficha Integral 360° del Creador | `creators`, `analytics` | `Creator`, `Channel`, `Contract`, `StreamingSession` | Manager, Analyst, Admin | RN-SEC-004, RN-DAT-005 |
| **CU-STR-01** | Registrar Manualmente una Sesión de Streaming | `streams` | `StreamingSession`, `Creator`, `Channel` | Talent Manager, Creador | RN-STR-001, RN-STR-002, RN-STR-003, RN-STR-004 |
| **CU-STR-02** | Importar Sesiones Masivas desde Exportaciones | `streams`, `imports` | `StreamingSession`, `ImportBatch` | Business Analyst | RN-STR-001, RN-DAT-001, RN-DAT-002 |
| **CU-STR-03** | Desglosar Sesión en Segmentos por Categoría | `streams` | `SessionSegment`, `StreamingSession` | Manager, Analyst | RN-STR-006 |
| **CU-STR-04** | Marcar y Conciliar Stream Patrocinado | `streams`, `campaigns` | `StreamingSession`, `CampaignDeliverable` | Talent Manager, Finance | RN-STR-007, RN-CAM-006 |
| **CU-STR-05** | Analizar Rendimiento Comparativo por Categoría | `streams`, `analytics` | `StreamingSession`, `SessionSegment` | Analyst, Manager | RN-STR-004, RN-DAT-005 |
| **CU-STR-06** | Vincular Stream con Videos/Clips Derivados | `streams`, `videos` | `StreamingSession`, `VideoRelation`, `Video` | Video Editor, Manager | RN-STR-001, RN-VID-008 |
| **CU-SCH-01** | Configurar Pauta Semanal Recurrente del Creador | `schedules` | `CreatorWeeklySchedule`, `Creator` | Talent Manager, Admin | RN-SCH-003, RN-SCH-008 |
| **CU-SCH-02** | Generar Lote de Slots en Calendario para un Periodo | `schedules` | `CreatorScheduleSlot`, `CreatorWeeklySchedule` | Talent Manager, Analyst | RN-SCH-004, RN-SCH-006 |
| **CU-SCH-03** | Crear Slot Extraordinario o Ad-hoc | `schedules` | `CreatorScheduleSlot`, `Creator` | Talent Manager | RN-SCH-008, RN-SCH-007 |
| **CU-SCH-04** | Conciliar Sesiones Reales con Slots de Calendario | `schedules`, `streams` | `CreatorScheduleSlot`, `StreamingSession` | Celery Beat, Analyst | RN-SCH-001, RN-SCH-002, RN-SCH-005, RN-SCH-010 |
| **CU-SCH-05** | Registrar y Aprobar Justificación de Ausencia | `schedules` | `ScheduleException`, `CreatorScheduleSlot` | Creador, Talent Manager | RN-SCH-006 |
| **CU-SCH-06** | Generar y Auditar Resumen Mensual de Cumplimiento | `schedules`, `contracts` | `CreatorScheduleComplianceSummary`, `Contract` | Analyst, Finance Director | RN-SCH-006, RN-SCH-007, RN-SCH-009 |
| **CU-VID-01** | Dar de Alta una Idea o Proyecto de Video | `videos` | `Video`, `Creator` | Manager, Creador, Editor | RN-VID-001, RN-VID-002 |
| **CU-VID-02** | Registrar y Controlar Costes de Producción | `videos` | `Video` | Finance Director, Manager | RN-VID-003, RN-VID-005 |
| **CU-VID-03** | Avanzar Etapas en el Pipeline (Kanban) | `videos` | `Video` | Manager, Editor, Creador | RN-VID-002 |
| **CU-VID-04** | Registrar Publicación Multicanal de un Video | `videos` | `VideoPublication`, `Video`, `Channel` | Talent Manager, Creador | RN-VID-001, RN-VID-004 |
| **CU-VID-05** | Actualizar Métricas de Rendimiento de Publicación | `videos` | `VideoPublication`, `Video` | Worker Celery, Analyst | RN-VID-006, RN-VID-007, RN-DAT-006 |
| **CU-VID-06** | Establecer Relaciones Genealógicas de Contenido | `videos` | `VideoRelation`, `Video` | Video Editor, Manager | RN-VID-008 |
| **CU-VID-07** | Evaluar ROI y Rentabilidad por Categoría | `videos`, `analytics` | `Video`, `VideoPublication` | Finance Director, Analyst | RN-VID-004, RN-VID-005, RN-VID-006 |
| **CU-EDT-01** | Alta de Editor o Estudio en el Directorio | `editors` | `Editor`, `User` | Talent Manager, Admin | RN-EDT-001, RN-EDT-002 |
| **CU-EDT-02** | Formalizar Asignación de Editor a Creador | `editors`, `creators` | `EditorAssignment`, `Editor`, `Creator` | Talent Manager | RN-EDT-002, RN-EDT-003 |
| **CU-EDT-03** | Crear y Asignar Tarea de Edición a Video | `editors`, `videos` | `EditingTask`, `Video`, `Editor` | Talent Manager, Creador | RN-EDT-002, RN-EDT-004, RN-EDT-008 |
| **CU-EDT-04** | Iniciar Trabajo y Subir Corte de Edición | `editors` | `TaskRevision`, `EditingTask` | Video Editor | RN-EDT-004, RN-EDT-005 |
| **CU-EDT-05** | Solicitar Cambios en el Corte con Marcas | `editors` | `TaskRevision`, `EditingTask` | Talent Manager, Creador | RN-EDT-005 |
| **CU-EDT-06** | Aprobar Tarea de Edición e Imputar Coste | `editors`, `videos` | `EditingTask`, `TaskRevision`, `Video` | Talent Manager, Creador | RN-EDT-006, RN-VID-003 |
| **CU-EDT-07** | Liquidar y Pagar Honorarios a Editores | `editors` | `EditingTask`, `Editor` | Financial Director | RN-EDT-007 |
| **CU-CAM-01** | Registrar Campaña Publicitaria con una Marca | `campaigns` | `SponsorCampaign` | Talent Manager, Finance | RN-CAM-001, RN-CAM-002 |
| **CU-CAM-02** | Asignar Entregables a Creadores del Roster | `campaigns`, `creators` | `CampaignDeliverable`, `SponsorCampaign` | Talent Manager | RN-CAM-001, RN-CAM-002, RN-CAM-003 |
| **CU-CAM-03** | Enviar Avance Publicitario a Revisión de Marca | `campaigns` | `CampaignDeliverable` | Talent Manager, Creador | RN-CAM-004 |
| **CU-CAM-04** | Registrar Veredicto de la Marca | `campaigns` | `CampaignDeliverable` | Talent Manager | RN-CAM-004 |
| **CU-CAM-05** | Publicar Entregable y Registrar Enlace de Prueba | `campaigns`, `streams`, `videos` | `CampaignDeliverable`, `VideoPublication` | Creador, Talent Manager | RN-CAM-004, RN-CAM-005, RN-CAM-006 |
| **CU-CAM-06** | Auditar Cumplimiento de Métricas y Cerrar | `campaigns` | `SponsorCampaign`, `CampaignDeliverable` | Analyst, Financial Director | RN-CAM-002, RN-CAM-005 |
| **CU-ALT-01** | Detección y Emisión de Alerta de Canal | `alerts`, `creators` | `ChannelAlert`, `Channel`, `Creator` | Worker Celery, Manager | RN-ALT-001, RN-ALT-002, RN-ALT-005 |
| **CU-ALT-02** | Asignar Responsable e Iniciar Investigación | `alerts` | `ChannelAlert`, `User` | Talent Manager, Admin | RN-ALT-002, RN-ALT-004 |
| **CU-ALT-03** | Presentar Contra-Notificación o Apelación | `alerts` | `ChannelAlert` | Talent Manager, Legal | RN-ALT-004 |
| **CU-ALT-04** | Resolver o Cerrar Incidente | `alerts`, `creators` | `ChannelAlert`, `Channel` | Talent Manager, Admin | RN-ALT-003, RN-ALT-004, RN-ALT-005 |
| **CU-ALT-05** | Detección Proactiva de Caída Anómala de Audiencia | `alerts`, `streams` | `ChannelAlert`, `StreamingSession` | Worker Celery, Analyst | RN-ALT-001, RN-ALT-002 |
| **CU-PAY-01** | Generar Precierre Automatizado Mensual | `payouts`, `contracts` | `CreatorPayout`, `Contract`, `Creator` | Financial Director, Celery | RN-PAY-001, RN-PAY-002, RN-CRE-008 |
| **CU-PAY-02** | Registrar Ajustes Manuales (Bonos y Deducciones) | `payouts` | `CreatorPayout` | Talent Manager, Finance | RN-PAY-002, RN-PAY-003 |
| **CU-PAY-03** | Enviar Liquidación a Aprobación Directiva | `payouts` | `CreatorPayout` | Talent Manager | RN-PAY-004 |
| **CU-PAY-04** | Aprobar Liquidación y Autorizar Desembolso | `payouts`, `creators` | `CreatorPayout`, `CreatorPersonalInfo` | Financial Director, Admin | RN-PAY-004, RN-PAY-005, RN-PAY-006 |
| **CU-PAY-05** | Consultar Estado de Cuenta por el Creador | `payouts` | `CreatorPayout` | Creador | RN-PAY-004, RN-SEC-004 |
| **CU-PAY-06** | Ejecutar Pago y Adjuntar Comprobante | `payouts` | `CreatorPayout` | Financial Director | RN-PAY-005, RN-PAY-006 |
| **CU-DAT-01** | Cargar Lote Masivo de Métricas (CSV/XLSX/JSON) | `imports` | `ImportBatch` | Business Analyst | RN-DAT-001, RN-DAT-002 |
| **CU-DAT-02** | Procesamiento y Mapeo Asíncrono del Lote | `imports`, `streams`, `videos` | `ImportBatch`, `StreamingSession` | Worker Celery | RN-DAT-002, RN-DAT-003, RN-DAT-006 |
| **CU-DAT-03** | Revertir un Lote de Importación (Rollback) | `imports`, `audit` | `ImportBatch`, `AuditEvent` | Company Admin, Analyst | RN-DAT-003, RN-SYS-002 |
| **CU-DAT-04** | Solicitar Exportación Personalizada de Datos | `exports` | `ExportJob`, `User` | Analyst, Finance, Manager | RN-DAT-002, RN-DAT-004 |
| **CU-DAT-05** | Descarga Segura de Archivos Exportados | `exports`, `audit` | `ExportJob`, `AuditEvent` | Usuario Solicitante | RN-DAT-004, RN-SYS-002 |
| **CU-DAT-06** | Visualizar Dashboard Ejecutivo y Ranking | `analytics` | Vistas SQL (`v_creator_overall_rankings`) | Company Admin, Manager | RN-DAT-005, RN-SEC-004 |
| **CU-DAT-07** | Forzar Recálculo e Invalidación de Caché | `analytics` | `DiskCache` | Company Admin | RN-DAT-005, RN-DAT-006 |
| **CU-SYS-01** | Configurar Parámetros Corporativos de la Agencia | `core` | `CompanySettings` | Company Admin | RN-SYS-001, RN-SYS-002 |
| **CU-SYS-02** | Consultar Bitácora de Auditoría Forense | `audit` | `AuditEvent` | System Auditor, Admin | RN-SYS-002, RN-SYS-007 |
| **CU-SYS-03** | Monitorear Registros de Error de Aplicación | `logs` | `ApplicationLogEntry` | SysAdmin, Company Admin | RN-SYS-007 |
| **CU-SYS-04** | Diagnóstico de Salud de Infraestructura y WAL | `monitor` | `InstanceHealthCheck` | Celery Beat, SysAdmin | RN-SYS-003, RN-SYS-004 |
| **CU-SYS-05** | Ejecutar Respaldo de la Base de Datos SQLite | `backups` | `DatabaseBackup` | Celery Beat, Admin | RN-SYS-005, RN-SYS-006, RN-SYS-007 |
| **CU-SYS-06** | Descarga y Verificación de Integridad de Backup | `backups`, `audit` | `DatabaseBackup`, `AuditEvent` | Company Admin | RN-SYS-005, RN-SYS-006, RN-SYS-007 |

---

## 2. Directrices Técnicas de Persistencia y Concurrencia en SQLite

El sistema opera sobre **SQLite en producción**, aprovechando al máximo su velocidad local y simplicidad operativa. Para garantizar la integridad referencial y alta concurrencia multi-hilo entre la aplicación web Django y los workers de Celery, deben cumplirse obligatoriamente los siguientes lineamientos de base de datos:

### 2.1 Pragmas Obligatorios de Conexión
Toda conexión a la base de datos debe inicializarse ejecutando:
```sql
PRAGMA journal_mode = WAL;            -- Write-Ahead Logging para lectura/escritura concurrente sin bloqueos
PRAGMA busy_timeout = 5000;           -- Espera activa de hasta 5 segundos ante contención de escritura
PRAGMA synchronous = NORMAL;          -- Máximo balance entre durabilidad y rendimiento I/O en SSD
PRAGMA foreign_keys = ON;             -- Activación forzada de integridad referencial de claves foráneas
PRAGMA cache_size = -64000;           -- 64 MB de memoria caché por conexión
```

### 2.2 Transacciones Cortas y Atómicas
- Las operaciones de escritura masiva en workers de Celery deben agruparse en bloques `transaction.atomic()` pequeños (lotes de 200 a 500 registros) para liberar el cerrojo de escritura rápidamente y evitar que las peticiones web experimenten `sqlite3.OperationalError: database is locked`.

### 2.3 Respaldo y Compactación Segura
- Nunca copiar directamente el archivo `db.sqlite3` en caliente mediante comandos shell planos (`cp`, `rsync`). Utilizar siempre `VACUUM INTO` con previo checkpoint pasivo (`RN-SYS-005`).

---

## 3. Criterios de Aceptación y Verificación de la Suite de Requerimientos

1. **Aislamiento Multitenant Lógico**:
   - Todo selector de consulta debe verificar la pertenencia de los datos respecto al usuario logueado, garantizando que creadores y editores no puedan acceder a métricas de terceros ni por URL directa ni por API.
2. **Coherencia Matemática Financiera**:
   - La suma de las comisiones retenidas por la agencia y el monto líquido a pagar al creador debe equivaler exactamente al 100% de los ingresos brutos generados (con tolerancia de 0.01 por redondeo monetario decimal).
3. **Resiliencia ante Caídas de Proceso**:
   - Ninguna importación o exportación debe bloquear el servidor web; ante un corte del worker de Celery, los estados deben marcarse en `failed` o `partial` sin dejar transacciones huérfanas en la base de datos.
4. **Trazabilidad Forense Completa**:
   - Toda alteración sobre contratos, información bancaria, estados de alertas y pagos aprobados debe tener su correspondiente registro indeleble en la bitácora de auditoría.
