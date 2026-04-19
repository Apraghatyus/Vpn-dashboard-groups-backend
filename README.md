# Composes archivados — 19 Abr 2026

Estos composes vivían antes en `backend/docker-compose.yml` y `frontend/docker-compose.yml`.
Fueron consolidados en el `docker-compose.yml` raíz como fuente única de verdad.

Motivo de la consolidación:
- Redundancia de definiciones (wg-acl-backend definido 2 veces con configs distintas).
- backend/docker-compose.yml re-introducía el Bug #5 (DEFAULT_ADMIN_USER/PASS con default 'admin').
- Inconsistencia de network: uno external: true, otro driver: bridge.

Si necesitás levantar solo un servicio:
  docker compose up -d mariadb backend    # desde la raíz
  docker compose up -d frontend           # desde la raíz
