"""Peer service — business logic for peer management."""

import time
import logging
from models.peer import Peer, NewPeerDTO
from repositories.peer_repo import peer_repo
from services.wg_easy_client import wg_easy, WgEasyError
from services.yaml_service import yaml_service
from config import Config

log = logging.getLogger(__name__)


class PeerService:
    def get_all(self) -> list[Peer]:
        return peer_repo.get_all()

    def get_by_id(self, peer_id: str) -> Peer | None:
        return peer_repo.get_by_id(peer_id)

    def get_by_role(self, role_id: str) -> list[Peer]:
        return peer_repo.get_by_role(role_id)

    def count(self) -> int:
        return peer_repo.count()

    def count_online(self) -> int:
        return peer_repo.count_online()

    # ---------- create (reescrito) ----------
    def create(self, dto: NewPeerDTO) -> Peer:
        """
        Orquesta: WG-Easy primero (fuente de verdad de claves e IP),
        luego DB local con wg_easy_id linkeado, luego trigger YAML.
        Si WG-Easy falla, no creamos nada localmente.
        Si la DB falla después de crear en WG-Easy, intentamos rollback remoto.
        """
        # 1. Crear en WG-Easy — asigna keys + IP automáticamente
        try:
            remote = wg_easy.create_client(name=dto.username)
        except WgEasyError as e:
            log.exception("create_peer: WG-Easy unreachable")
            raise  # el controller lo traduce a HTTP 502

        remote_id = remote.get("id")
        address_raw = remote.get("address") or ""
        # WG-Easy devuelve "10.8.0.3/24" — normalizamos a "10.8.0.3"
        address = address_raw.split("/")[0].strip()

        if not remote_id or not address:
            # Respuesta corrupta — intentamos limpiar para no dejar huérfano
            try:
                if remote_id:
                    wg_easy.delete_client(remote_id)
            except WgEasyError:
                log.exception("Rollback remoto tras payload inválido falló")
            raise WgEasyError(
                f"WG-Easy devolvió payload sin id/address: {remote!r}"
            )

        # 2. Crear localmente
        peer = Peer(
            id=f"peer-{int(time.time() * 1000)}",
            display_name=dto.display_name or dto.username,
            username=dto.username,
            ip=address,                 # ← viene de WG-Easy, no del DTO
            role_id=dto.role_id,
            status="offline",
            last_seen="ahora",
            created_at=time.time(),
            user_id=dto.user_id,
            device_name=dto.device_name,
            wg_easy_id=remote_id,       # ← link hacia el peer real
        )
        try:
            peer_repo.add(peer)
        except Exception:
            log.exception("add() local falló tras crear en WG-Easy; rollback remoto")
            try:
                wg_easy.delete_client(remote_id)
            except WgEasyError:
                log.exception("Rollback remoto tras fallo de DB también falló")
            raise

        # 3. Trigger del YAML → watcher → iptables.
        # Si falla, el peer existe pero el ACL no se re-aplicó.
        # No lo tratamos como error fatal: el usuario puede pulsar Sincronizar.
        try:
            yaml_service.save_to_file()
        except Exception:
            log.exception("yaml_service.save_to_file() tras create falló")

        return peer

    # ---------- update (sin cambios funcionales) ----------
    def update(self, peer_id: str, data: dict) -> Peer | None:
        peer = peer_repo.get_by_id(peer_id)
        if not peer:
            return None
        field_map = {
            "displayName": "display_name",
            "username": "username",
            # "ip": NO SE PERMITE — la IP es responsabilidad de WG-Easy.
            # Si alguien la manda, se ignora silenciosamente.
            "roleId": "role_id",
            "deviceName": "device_name",
        }
        for camel, snake in field_map.items():
            if camel in data:
                setattr(peer, snake, data[camel])
        if "userId" in data:
            peer.user_id = data["userId"] or ""
        return peer_repo.update(peer_id, peer)

    def update_role(self, peer_id: str, role_id: str) -> Peer | None:
        peer = peer_repo.get_by_id(peer_id)
        if not peer:
            return None
        peer.role_id = role_id
        updated = peer_repo.update(peer_id, peer)
        # Cambiar rol SÍ requiere regenerar el YAML
        if updated:
            try:
                yaml_service.save_to_file()
            except Exception:
                log.exception("yaml_service.save_to_file() tras update_role falló")
        return updated

    # ---------- remove (reescrito) ----------
    def remove(self, peer_id: str) -> bool:
        peer = peer_repo.get_by_id(peer_id)
        if not peer:
            return False

        # Orden: WG-Easy primero. Si falla la red, abortamos — no queremos
        # borrar local y dejar el peer vivo en WG-Easy.
        if peer.wg_easy_id:
            try:
                wg_easy.delete_client(peer.wg_easy_id)
            except WgEasyError as e:
                log.exception("delete remoto falló, no borramos local")
                raise

        ok = peer_repo.delete(peer_id)

        try:
            yaml_service.save_to_file()
        except Exception:
            log.exception("yaml_service.save_to_file() tras delete falló")

        return ok

    def get_by_role(self, role_id: str) -> list[Peer]:
        return peer_repo.get_by_role(role_id)

    def count_online(self) -> int:
        return peer_repo.count_online()

    def count(self) -> int:
        return peer_repo.count()

    # ---------- generate_config (reescrito de cero) ----------
    def generate_config(self, peer_id: str) -> str | None:
        """
        Devuelve el .conf real tal como lo provee WG-Easy. Si el peer no
        está linkeado (wg_easy_id vacío, legado), devuelve None y el
        controller responde 409 con un mensaje explicativo.

        Este método ya NO construye el .conf sintéticamente — eso producía
        archivos con PrivateKey placeholder y PublicKey del servidor, que
        aparentaban ser válidos pero fallaban el handshake (Bug #9).
        """
        peer = peer_repo.get_by_id(peer_id)
        if not peer:
            return None
        if not peer.wg_easy_id:
            log.warning("generate_config: peer %s sin wg_easy_id", peer_id)
            return None
        try:
            return wg_easy.get_configuration(peer.wg_easy_id)
        except WgEasyError:
            log.exception("generate_config: WG-Easy no respondió")
            raise

    # ---------- reconcile (nuevo) ----------
    def reconcile_with_wg_easy(self) -> dict:
        """
        Alinea la DB con el estado real de WG-Easy.

        - Peers locales con wg_easy_id válido pero IP desactualizada → update IP
        - Peers locales sin wg_easy_id pero con match por username → link
        - Peers remotos sin match local → reportados para adopción manual
          (no los creamos solos porque no sabemos qué role_id asignarles)
        - Peers locales con wg_easy_id que ya no existe remoto → 'orphaned'
          (el frontend los muestra con badge rojo y botón "Eliminar")

        Devuelve un dict con las cuatro listas. No lanza excepción salvo que
        WG-Easy sea directamente inalcanzable.
        """
        remote = wg_easy.list_clients()  # deja propagar WgEasyError
        local = peer_repo.get_all()

        by_wge_id = {p.wg_easy_id: p for p in local if p.wg_easy_id}
        by_username = {p.username: p for p in local}

        updated_ips, linked, adopted_pending, orphaned = [], [], [], []
        remote_ids = set()

        for rc in remote:
            rid = rc.get("id")
            rname = rc.get("name") or ""
            raddr = (rc.get("address") or "").split("/")[0].strip()
            if not rid:
                continue
            remote_ids.add(rid)

            match = by_wge_id.get(rid) or by_username.get(rname)

            if not match:
                adopted_pending.append({
                    "wg_easy_id": rid,
                    "name": rname,
                    "address": raddr,
                })
                continue

            dirty = False
            if not match.wg_easy_id:
                match.wg_easy_id = rid
                linked.append(match.username)
                dirty = True
            if raddr and match.ip != raddr:
                match.ip = raddr
                dirty = True
                if match.username not in linked:
                    updated_ips.append(match.username)
            if dirty:
                peer_repo.update(match.id, match)

        for p in local:
            if p.wg_easy_id and p.wg_easy_id not in remote_ids:
                orphaned.append(p.username)

        try:
            yaml_service.save_to_file()
        except Exception:
            log.exception("yaml_service tras reconcile falló")

        return {
            "remote_count": len(remote),
            "local_count": len(local),
            "linked": linked,
            "updated_ips": updated_ips,
            "orphaned": orphaned,
            "adopted_pending": adopted_pending,
        }


peer_service = PeerService()
