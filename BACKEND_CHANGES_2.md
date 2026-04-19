# Cambios requeridos en el Backend — v2

## Resumen de endpoints necesarios

| Método | Ruta | Estado | Descripción |
|--------|------|--------|-------------|
| `PUT` | `/api/roles/:id` | **NUEVO** | Editar nombre, descripción y color de un rol |
| `DELETE` | `/api/roles/:id` | Verificar | Ya debe existir — confirmar que elimina entradas de access_matrix también |
| `POST` | `/api/access/toggle` | **NUEVO** | Activar/desactivar acceso de un rol a un servicio |
| `PUT` | `/api/peers/:id` | **NUEVO** | Editar campos del peer (deviceName, userId, roleId, ip, etc.) |
| `DELETE` | `/api/vpn-users/:id?cascade=true` | **NUEVO** | Eliminar usuario y opcionalmente todos sus peers |
| `PUT` | `/api/vpn-users/:id` | **NUEVO** | Editar displayName, email o roleId de un usuario |

---

## 1. PUT /api/roles/:id

### Request body
```json
{
  "displayName": "familia",
  "description": "Media, archivos y DNS",
  "color": "#3b82f6"
}
```
> Todos los campos son opcionales — solo se actualizan los que se envíen.

### Response `200`
```json
{
  "id": "familia",
  "displayName": "familia",
  "description": "Media, archivos y DNS",
  "color": "#3b82f6",
  "createdAt": 1713479280.0
}
```

### Errores
| Código | Situación |
|--------|-----------|
| `404` | Rol no encontrado |

---

## 2. DELETE /api/roles/:id

Debe eliminar el rol **y en cascada**:
- Todas las entradas de `access_matrix` donde `role_id == id`
- Los peers con ese rol deben quedar con `role_id = ""` o reasignarse al primer rol disponible

### Response `204` — sin body

---

## 3. POST /api/access/toggle

El frontend llama este endpoint cada vez que el usuario hace click en un servicio dentro de un rol expandido.

### Request body
```json
{
  "roleId": "familia",
  "serviceId": "jellyfin"
}
```

### Lógica esperada
- Si existe la entrada `(roleId, serviceId)` en `access_matrix` → **eliminarla**
- Si no existe → **crearla**
- Devolver la matriz completa actualizada

### Response `200`
```json
[
  { "roleId": "familia", "serviceId": "jellyfin" },
  { "roleId": "familia", "serviceId": "navidrome" }
]
```
> El frontend reemplaza toda la matriz local con esta respuesta — es importante devolver **todas** las entradas, no solo las del rol afectado.

---

## 4. GET /api/services — campo `url` nuevo

El modelo de servicio ahora tiene un campo `url` opcional (subdominio amigable).

### Response esperada
```json
[
  {
    "id": "aguaquim-crm",
    "name": "Aguaquim CRM",
    "endpoint": "100.75.203.14:5433",
    "url": "www.aguaquim.com",
    "category": "CRM"
  },
  {
    "id": "minecraft-java",
    "name": "Minecraft Java",
    "endpoint": "100.75.203.14:25565",
    "url": null,
    "category": "Gaming"
  }
]
```

### Migración SQL
```sql
ALTER TABLE services ADD COLUMN url VARCHAR(512) NULL;

UPDATE services SET url = 'jellyfin.home.local'  WHERE id = 'jellyfin';
UPDATE services SET url = 'navidrome.home.local' WHERE id = 'navidrome';
UPDATE services SET url = 'files.home.local'     WHERE id = 'filebrowser';
UPDATE services SET url = 'kavita.home.local'    WHERE id = 'kavita';
UPDATE services SET url = 'www.aguaquim.com'     WHERE id = 'aguaquim-crm';
UPDATE services SET url = 'portainer.home.local' WHERE id = 'portainer';
UPDATE services SET url = 'dns.home.local'       WHERE id = 'dns-pihole';
```

---

## 5. PUT /api/peers/:id

### Request body (todos opcionales)
```json
{
  "displayName": "Juan · MacBook Pro",
  "username": "apraghato_mac",
  "ip": "10.8.0.2",
  "roleId": "admin",
  "deviceName": "MacBook Pro",
  "userId": null
}
```
> `userId: null` desvincula el peer del usuario sin eliminarlo.

### Response `200` — peer actualizado completo

---

## 6. DELETE /api/vpn-users/:id

### Query param opcional
- `?cascade=true` → elimina el usuario **y** todos sus peers (`user_id == id`)
- Sin param → solo elimina el usuario; los peers quedan con `user_id = ""`

### Response `204` — sin body

---

## 7. PUT /api/vpn-users/:id

### Request body (todos opcionales)
```json
{
  "displayName": "Juan Camilo Cardona",
  "email": "cardonarealpe@gmail.com",
  "roleId": "admin"
}
```

### Response `200` — usuario actualizado completo

### Errores
| Código | Situación |
|--------|-----------|
| `404` | Usuario no encontrado |
| `409` | El email ya está en uso por otro usuario |

---

## 8. GET /api/vpn-users — respuesta esperada

El frontend usa este endpoint para el dropdown de "Usuario" al crear un peer.

```json
[
  {
    "id": "vpnuser-1",
    "displayName": "Juan Camilo Cardona",
    "email": "cardonarealpe@gmail.com",
    "roleId": "admin",
    "createdAt": 1713479280.0
  }
]
```
