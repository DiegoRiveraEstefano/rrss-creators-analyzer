# Política de Seguridad (SECURITY)

Este documento describe la arquitectura de seguridad, el control de acceso basado en el **sistema nativo de Permisos y Grupos de Django**, la protección de datos en **SQLite** y **DiskCache**, y el protocolo para reportar vulnerabilidades en **RRSS Creators Analyzer**.

---

## 1. Modelo de Autenticación e Identidad

1. **Autenticación Robusta (`django-allauth[mfa]`)**:
   - Soporte nativo para Autenticación Multifactor (MFA / TOTP) recomendado y exigible para usuarios pertenecientes a los grupos `Company Admin`, `Manager` y `Finance`.
   - Verificación obligatoria de correo electrónico (`ACCOUNT_EMAIL_VERIFICATION = "mandatory"`).
2. **Almacenamiento de Contraseñas**:
   - Uso prioritario de **Argon2** (`Argon2PasswordHasher` mediante `argon2-cffi`) como algoritmo principal de hashing de contraseñas, seguido de validadores estrictos de longitud y complejidad.
3. **Protección de Sesiones y Cookies**:
   - `SESSION_COOKIE_HTTPONLY = True` y `CSRF_COOKIE_HTTPONLY = True`.
   - En producción: `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`, `SECURE_SSL_REDIRECT = True` y cabeceras HSTS activas.
   - `X_FRAME_OPTIONS = "DENY"` para prevenir ataques de Clickjacking.

---

## 2. Autorización Basada en Grupos y Permisos de Django (`django.contrib.auth`)

En el sistema anterior (ver [`old-migrations/20260904000004_rls_security_policies.sql`](file:///home/diego/Proyectos/rrss-creators-analyzer/old-migrations/20260904000004_rls_security_policies.sql)), el control de acceso se realizaba mediante políticas RLS en PostgreSQL. Al ser ahora una aplicación **single-tenant** en Django sobre SQLite, toda la autorización se gestiona mediante el **sistema nativo de Grupos (`Group`) y Permisos (`Permission`) de Django** (ver [`docs/schema.sql`](file:///home/diego/Proyectos/rrss-creators-analyzer/docs/schema.sql)).

- **Sin campos `role` harcodeados en `User`**: Un usuario puede pertenecer a uno o más grupos (`users_user_groups`) y recibir permisos granulares (`auth_group_permissions` y `users_user_user_permissions`).
- **Verificación mediante `user.has_perm(...)` y `PermissionRequiredMixin`**: Las vistas y servicios validan permisos explícitos (`<app_label>.<codename>`) en lugar de comparar strings de roles.

### Matriz de Grupos Base y Permisos de Dominio

| Recurso / Permiso de Django | Grupo `Company Admin` | Grupo `Manager` | Grupo `Analyst` | Grupo `Finance` | Grupo `Creator` |
|---|---|---|---|---|---|
| **Usuarios y Grupos (`auth.*`, `users.*`)** | CRUD Completo | `view_user` | Sin acceso | Sin acceso | Solo su propio perfil |
| **Creadores (`creators.*`)** | CRUD + `view_all_creators` | `add`, `change`, `view` + `view_all_creators` | `view_creator` + `view_all_creators` | `view_creator` + `view_all_creators` | `view_creator` (solo el suyo) |
| **Contratos (`creators.manage_contracts`)** | Sí | Lectura | Sin acceso | CRUD Completo | Solo ver su contrato |
| **Sesiones (`streams.*`)** | CRUD + `view_all_sessions` + `export_sessions` | `add`, `change`, `view` + `view_all_sessions` | `view` + `view_all_sessions` + `export_sessions` | `view` + `view_all_sessions` | `view_streamingsession` (solo las suyas) |
| **Videos y Publicaciones (`videos.*`)** | CRUD + `view_all_videos` + `view_production_costs` | `add`, `change`, `view` + `view_all_videos` + `view_production_costs` | `view` + `view_all_videos` + `view_production_costs` | `view` + `view_all_videos` + `view_production_costs` | `view_video`, `view_videopublication` (solo los suyos) |
| **Alertas y Strikes (`alerts.*`)** | CRUD + `view_all_alerts` + `resolve_channel_alert` | `add`, `change`, `view` + `view_all_alerts` + `resolve_channel_alert` | `view_channelalert` + `view_all_alerts` | Sin acceso | `view_channelalert` (solo las suyas) |
| **Lotes de Importación (`imports.*`)** | CRUD Completo | `add`, `view` | `add`, `view` | Sin acceso | Sin acceso |
| **Liquidaciones (`payouts.*`)** | CRUD Completo | Solo lectura | Sin acceso | CRUD Completo | Ver sus propias liquidaciones |
| **Dashboard Global (`analytics.view_company_dashboard`)** | Sí | Sí | Sí | Sí | Solo dashboard personal |

### Reglas de Prevención de IDOR (Insecure Direct Object Reference)
- Ninguna vista de detalle (`CreatorDetailView`, `StreamingSessionDetailView`, `VideoDetailView`, `ChannelAlertDetailView`) debe consultar `Model.objects.get(pk=pk)` directamente.
- Todas las consultas pasan por el `Selector` recibiendo `user: User`:
  - Si `user.has_perm("<app>.view_all_<models>")` es `True`, retorna el queryset global de la compañía.
  - Si es `False`, filtra estrictamente por `creator__user=user` (o asignaciones en `creators_team_assignment`).

---

## 3. Seguridad en Base de Datos (SQLite) y Caché (DiskCache)

Dado que el despliegue utiliza **SQLite** y **DiskCache** en el sistema de archivos local:

1. **Permisos de Sistema de Archivos**:
   - El archivo de base de datos (`db.sqlite3`, junto con `db.sqlite3-wal` y `db.sqlite3-shm`) y el directorio de caché (`.cache/diskcache/`) deben residir **fuera** de los directorios servidos públicamente (`STATIC_ROOT` y `MEDIA_ROOT`).
   - Los permisos en el servidor deben restringirse a `0600` (archivos) y `0700` (directorios), perteneciendo exclusivamente al usuario de sistema que ejecuta el proceso WSGI/ASGI.
2. **Prevención de Inyección SQL**:
   - Queda **estrictamente prohibido** interpolar cadenas en consultas SQL (`raw()`, `extra()` o cursores directos).
   - Toda consulta analítica o de filtrado debe construirse utilizando el ORM de Django (`QuerySet`, `F`, `Q`, `Value`, `Window`) y `django-filter`.
3. **Seguridad en Importación de Archivos (`django-import-export`)**:
   - Validar el tamaño máximo de archivo subido (`DATA_UPLOAD_MAX_MEMORY_SIZE`) y permitir únicamente extensiones explícitas (`.csv`, `.xlsx`).
   - Sanitizar fórmulas en exportaciones/importaciones CSV/Excel para prevenir ataques de **CSV Formula Injection** (prefijar celdas que comiencen con `=`, `+`, `-`, `@`).
4. **Auditoría Inmutable (`django-simple-history`)**:
   - Todas las modificaciones sobre creadores, contratos, canales, costos de producción de videos, ingresos estimados y resoluciones de alertas/strikes quedan registradas con fecha, hora y usuario autor (`history_user`).

---

## 4. Gestión de Secretos y Variables de Entorno

- **Prohibido** almacenar claves secretas (`DJANGO_SECRET_KEY`, credenciales SMTP, tokens de APIs de Twitch/YouTube/Kick/TikTok) en el código fuente o en commits de Git.
- Utilizar siempre `django-environ` leyendo desde variables de entorno del sistema o archivos `.env` excluidos en [`.gitignore`](file:///home/diego/Proyectos/rrss-creators-analyzer/.gitignore).

---

## 5. Reporte de Vulnerabilidades

Si descubres una vulnerabilidad de seguridad en este proyecto:
1. **No abras un Issue público** en el repositorio.
2. Envía un reporte detallado al administrador del proyecto (`diego-rivera@example.com`) incluyendo:
   - Descripción de la vulnerabilidad y componente afectado.
   - Pasos para reproducir el problema (Proof of Concept).
   - Impacto potencial sobre los datos de los creadores o métricas financieras de la compañía.
3. El equipo acusará recibo en un plazo máximo de **48 horas** y coordinará la corrección antes de cualquier divulgación.
