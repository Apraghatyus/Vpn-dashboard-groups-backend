"""YAML service — generates WireGuard ACL config from current state."""

from config import Config
from repositories.role_repo import role_repo
from repositories.peer_repo import peer_repo
from repositories.service_repo import service_repo
from repositories.access_repo import access_repo


class YamlService:
    def generate(self) -> str:
        roles = role_repo.get_all()
        peers = peer_repo.get_all()
        all_services = service_repo.get_all()
        total = len(all_services)
        lines: list[str] = []

        lines.append("# WireGuard ACL — generado por WG-ACL Manager")
        lines.append("")
        lines.append("roles:")

        for role in roles:
            lines.append(f"  {role.id}:")
            lines.append(f'    description: "{role.description}"')
            lines.append("    rules:")

            entries = access_repo.get_for_role(role.id)
            service_ids = {e.service_id for e in entries}
            role_services = [s for s in all_services if s.id in service_ids]

            if len(role_services) == total:
                lines.append('      - "*"')
            else:
                for svc in role_services:
                    lines.append(f'      - "{svc.endpoint}"')
            lines.append("")

        lines.append("clients:")

        for peer in peers:
            lines.append(f"  {peer.username}:")
            lines.append(f'    ip: "{peer.ip}"')
            lines.append(f"    role: {peer.role_id}")
            lines.append(f'    description: "{peer.display_name}"')
            lines.append("")

        return "\n".join(lines)

    def save_to_file(self) -> str:
        """Generate, save internally and to ACL output path."""
        content = self.generate()
        with open(Config.YAML_OUTPUT, "w", encoding="utf-8") as f:
            f.write(content)
        acl_output = getattr(Config, "ACL_OUTPUT", None)
        if acl_output and acl_output != Config.YAML_OUTPUT:
            with open(acl_output, "w", encoding="utf-8") as f:
                f.write(content)
        return content

yaml_service = YamlService()
