# Cambios requeridos en el Backend

## Resumen

| Módulo | Cambio |
|--------|--------|
| **Services** | Agregar columna `url` — subdominio amigable para mostrar en la UI |
| **VPN Users** | `DELETE` con cascade — eliminar usuario y todos sus dispositivos |
| **Peers** | `PUT /api/peers/:id` — editar campos incluyendo desvincular usuario (`userId: null`) |

---

## 1. Services — agregar campo `url`

### Cambio en la tabla

```sql
ALTER TABLE services ADD COLUMN url VARCHAR(512) NULL;
```

### Cambio en el modelo (`db/tables.py`)

```python
class ServiceRow(Base):
    __tablename__ = "services"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    endpoint: Mapped[str] = mapped_column(String(256))
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    category: Mapped[str] = mapped_column(String(64))
```

### Cambio en el modelo de dominio (`models/service.py`)

```python
@dataclass
class Service:
    id: str
    name: str
    endpoint: str
    category: str
    url: str | None = None
```

### Actualizar seed (`data/seed.py`)

```python
services = [
    Service(id='jellyfin',       name='Jellyfin',       endpoint='100.75.203.14:8096',  category='Media',           url='jellyfin.home.local'),
    Service(id='navidrome',      name='Navidrome',      endpoint='100.75.203.14:4533',  category='Media',           url='navidrome.home.local'),
    Service(id='filebrowser',    name='FileBrowser',    endpoint='100.75.203.14:8080',  category='Herramientas',    url='files.home.local'),
    Service(id='kavita',         name='Kavita',         endpoint='100.75.203.14:5000',  category='Media',           url='kavita.home.local'),
    Service(id='minecraft-java', name='Minecraft Java', endpoint='100.75.203.14:25565', category='Gaming',          url=None),
    Service(id='mc-bedrock',     name='MC Bedrock',     endpoint='100.75.203.14:19132', category='Gaming',          url=None),
    Service(id='terraria',       name='Terraria',       endpoint='100.75.203.14:7777',  category='Gaming',          url=None),
    Service(id='aguaquim-crm',   name='Aguaquim CRM',   endpoint='100.75.203.14:5433',  category='CRM',             url='www.aguaquim.com'),
    Service(id='portainer',      name='Portainer',      endpoint='100.75.203.14:9443',  category='Infraestructura', url='portainer.home.local'),
    Service(id='dns-pihole',     name='DNS (Pi-hole)',  endpoint='100.114.140.34:53',   category='Red',             url='dns.home.local'),
]
```

### Respuesta GET /api/services (añadir `url`)

```json
[
  {
    "id": "aguaquim-crm",
    "name": "Aguaquim CRM",
    "endpoint": "100.75.203.14:5433",
    "url": "www.aguaquim.com",
    "category": "CRM"
  }
]
```

---

## 2. VPN Users — DELETE con cascade

### Comportamiento esperado

`DELETE /api/vpn-users/:id` debe aceptar un query param `?cascade=true`.

- `?cascade=true` → elimina el usuario **y todos sus peers** (`userId == id`)
- Sin `?cascade` (default) → solo elimina el usuario; los peers quedan con `userId = ""`

### Implementación en `controllers/vpn_user_routes.py`

```python
@vpn_users_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
def delete_vpn_user(user_id):
    cascade = request.args.get("cascade", "false").lower() == "true"
    vpn_user_service.delete(user_id, cascade=cascade)
    return "", 204
```

### Implementación en `services/vpn_user_service.py`

```python
def delete(self, user_id: str, cascade: bool = False) -> None:
    if cascade:
        peer_repo.delete_by_user_id(user_id)   # elimina todos los peers del usuario
    vpn_user_repo.delete(user_id)
```

### Nuevo método en `repositories/peer_repo.py`

```python
def delete_by_user_id(self, user_id: str) -> None:
    with get_session() as session:
        session.query(PeerRow).filter(PeerRow.user_id == user_id).delete()
        session.commit()
```

---

## 3. Peers — PUT /api/peers/:id (editar + desvincular usuario)

Endpoint nuevo (o existente que se expanda): `PUT /api/peers/:id`

### Body esperado (todos los campos opcionales)

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
> `userId: "vpnuser-2"` lo reasigna a otro usuario.

### Implementación en `controllers/peer_routes.py`

```python
@peers_bp.route("/<peer_id>", methods=["PUT"])
@jwt_required()
def update_peer(peer_id):
    data = request.get_json()
    peer = peer_service.update(peer_id, data)
    return jsonify(peer.to_dict()), 200
```

### Implementación en `services/peer_service.py`

```python
def update(self, peer_id: str, data: dict) -> Peer:
    peer = peer_repo.get_by_id(peer_id)
    if not peer:
        abort(404)
    # Actualizar solo los campos enviados
    for field in ("displayName", "username", "ip", "roleId", "deviceName"):
        if field in data:
            setattr(peer, snake(field), data[field])
    if "userId" in data:
        peer.user_id = data["userId"] or ""   # None → string vacío en DB
    peer_repo.update(peer)
    return peer
```

### Nuevo método en `repositories/peer_repo.py`

```python
def update(self, peer: Peer) -> None:
    with get_session() as session:
        row = session.get(PeerRow, peer.id)
        if row:
            row.display_name = peer.display_name
            row.username     = peer.username
            row.ip           = peer.ip
            row.role_id      = peer.role_id
            row.device_name  = peer.device_name
            row.user_id      = peer.user_id
            session.commit()
```

---

## 4. Resumen de endpoints nuevos/modificados

| Método | Ruta | Cambio |
|--------|------|--------|
| `GET` | `/api/services` | Incluye campo `url` en respuesta |
| `PUT` | `/api/peers/:id` | **NUEVO** — edita campos del peer, soporta `userId: null` |
| `DELETE` | `/api/vpn-users/:id?cascade=true` | Elimina usuario + todos sus dispositivos |

---

## 5. Migración SQL (base de datos existente)

```sql
-- 1. Agregar columna url a services
ALTER TABLE services ADD COLUMN url VARCHAR(512) NULL;

-- 2. Actualizar urls conocidas
UPDATE services SET url = 'jellyfin.home.local'  WHERE id = 'jellyfin';
UPDATE services SET url = 'navidrome.home.local' WHERE id = 'navidrome';
UPDATE services SET url = 'files.home.local'     WHERE id = 'filebrowser';
UPDATE services SET url = 'kavita.home.local'    WHERE id = 'kavita';
UPDATE services SET url = 'www.aguaquim.com'     WHERE id = 'aguaquim-crm';
UPDATE services SET url = 'portainer.home.local' WHERE id = 'portainer';
UPDATE services SET url = 'dns.home.local'       WHERE id = 'dns-pihole';
```
