"""
Cliente HTTP delgado para WG-Easy v14.

Auth: POST /api/session con {"password": "..."} → cookie wg-easy-session
Resto: GET/POST/DELETE /api/wireguard/client[/:id] con la cookie

Diseñado para fallar ruidoso. Errores de WG-Easy se propagan como WgEasyError
con status y body originales, no se silencian ni se traducen.
"""
import logging
import threading
import requests
from config import Config

log = logging.getLogger(__name__)


class WgEasyError(Exception):
    def __init__(self, message, status=None, body=None):
        super().__init__(message)
        self.status = status
        self.body = body

    def to_dict(self):
        return {
            "error": "wg_easy_error",
            "message": str(self),
            "upstream_status": self.status,
            "upstream_body": (self.body[:500] if self.body else None),
        }


class WgEasyClient:
    def __init__(self, base_url=None, password=None, timeout=None):
        self.base_url = (base_url or Config.WG_EASY_URL).rstrip("/")
        self._password = password or Config.WG_EASY_PASSWORD
        self._timeout = timeout or Config.WG_EASY_TIMEOUT
        self._session = requests.Session()
        self._lock = threading.Lock()
        self._logged_in = False

    # ---------- auth ----------

    def _login(self):
        url = f"{self.base_url}/api/session"
        try:
            r = self._session.post(
                url,
                json={"password": self._password},
                timeout=self._timeout,
            )
        except requests.RequestException as e:
            raise WgEasyError(f"No se puede contactar WG-Easy: {e}")
        if r.status_code not in (200, 204):
            raise WgEasyError(
                f"Login WG-Easy falló: HTTP {r.status_code}",
                status=r.status_code, body=r.text,
            )
        self._logged_in = True
        log.info("WG-Easy login OK")

    def _ensure(self):
        if not self._logged_in:
            with self._lock:
                if not self._logged_in:
                    self._login()

    def _req(self, method, path, **kw):
        self._ensure()
        kw.setdefault("timeout", self._timeout)
        url = f"{self.base_url}{path}"
        r = self._session.request(method, url, **kw)
        if r.status_code == 401:
            log.warning("Sesión WG-Easy expirada, re-login")
            self._logged_in = False
            self._ensure()
            r = self._session.request(method, url, **kw)
        return r

    # ---------- operaciones ----------

    def list_clients(self) -> list[dict]:
        r = self._req("GET", "/api/wireguard/client")
        if r.status_code != 200:
            raise WgEasyError(f"list_clients HTTP {r.status_code}",
                              status=r.status_code, body=r.text)
        return r.json()

    def create_client(self, name: str) -> dict:
        """
        Crea un cliente en WG-Easy. WG-Easy asigna IP automáticamente.
        Devuelve el cliente creado con {id, address, publicKey, ...}.
        """
        r = self._req("POST", "/api/wireguard/client", json={"name": name})
        if r.status_code not in (200, 201, 204):
            raise WgEasyError(f"create_client({name!r}) HTTP {r.status_code}",
                              status=r.status_code, body=r.text)

        # Algunos builds de v14 devuelven el objeto, otros 204 vacío.
        # Si no hay body, re-listamos y matchemos por nombre.
        if r.status_code == 200 and r.text:
            try:
                return r.json()
            except ValueError:
                pass

        clients = self.list_clients()
        matches = [c for c in clients if c.get("name") == name]
        if not matches:
            raise WgEasyError(
                f"create_client() OK pero {name!r} no aparece en la lista"
            )
        # El más reciente (mayor createdAt) gana ante duplicados
        return max(matches, key=lambda c: c.get("createdAt", ""))

    def delete_client(self, client_id: str) -> None:
        r = self._req("DELETE", f"/api/wireguard/client/{client_id}")
        if r.status_code == 404:
            log.warning("delete_client: %s ya no existe en WG-Easy", client_id)
            return
        if r.status_code not in (200, 204):
            raise WgEasyError(
                f"delete_client({client_id}) HTTP {r.status_code}",
                status=r.status_code, body=r.text,
            )

    def get_configuration(self, client_id: str) -> str:
        """Devuelve el texto del .conf ya formateado por WG-Easy."""
        r = self._req("GET", f"/api/wireguard/client/{client_id}/configuration")
        if r.status_code != 200:
            raise WgEasyError(
                f"get_configuration({client_id}) HTTP {r.status_code}",
                status=r.status_code, body=r.text,
            )
        return r.text


# Singleton de módulo
wg_easy = WgEasyClient()
