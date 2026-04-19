-- WG-ACL Manager — Seed data
-- Run after schema.sql on a fresh database.
-- The password hash below corresponds to 'admin' hashed with bcrypt.

-- Roles
INSERT INTO roles (id, display_name, description, color, created_at) VALUES
    ('admin',           'admin',           'Acceso total a toda la infraestructura', '#ef4444', UNIX_TIMESTAMP() - 86400 * 30),
    ('familia',         'familia',         'Media, archivos y DNS',                 '#3b82f6', UNIX_TIMESTAMP() - 86400 * 25),
    ('gaming',          'gaming',          'Servidores de juegos',                  '#f59e0b', UNIX_TIMESTAMP() - 86400 * 20),
    ('cliente_aguaquim','cliente_aguaquim','Solo acceso al CRM corporativo',        '#14b8a6', UNIX_TIMESTAMP() - 86400 * 10);

-- VPN Users
INSERT INTO vpn_users (id, display_name, email, role_id, created_at) VALUES
    ('vpnuser-1', 'Juan Camilo Cardona', 'cardonarealpe@gmail.com', 'admin',            UNIX_TIMESTAMP() - 86400 * 30),
    ('vpnuser-2', 'Camila',              'camila@home.local',       'familia',          UNIX_TIMESTAMP() - 86400 * 25),
    ('vpnuser-3', 'Papá',               'papa@home.local',         'familia',          UNIX_TIMESTAMP() - 86400 * 20),
    ('vpnuser-4', 'Santi',              'santi@home.local',        'gaming',           UNIX_TIMESTAMP() - 86400 * 15),
    ('vpnuser-5', 'Operador Aguaquim',  'operador@aguaquim.com',   'cliente_aguaquim', UNIX_TIMESTAMP() - 86400 *  5);

-- Peers
INSERT INTO peers (id, display_name, username, ip, role_id, status, last_seen, created_at, user_id, device_name) VALUES
    ('peer-1', 'Juan Camilo · MacBook Pro', 'apraghato_mac',    '10.8.0.2', 'admin',            'online',  'ahora', UNIX_TIMESTAMP() - 86400 * 30, 'vpnuser-1', 'MacBook Pro'),
    ('peer-2', 'Juan Camilo · iPhone',      'apraghato_iphone', '10.8.0.3', 'admin',            'offline', '1h',    UNIX_TIMESTAMP() - 86400 * 28, 'vpnuser-1', 'iPhone 15 Pro'),
    ('peer-3', 'Camila · iPhone',           'camila_phone',     '10.8.0.4', 'familia',          'online',  '2 min', UNIX_TIMESTAMP() - 86400 * 25, 'vpnuser-2', 'iPhone 14'),
    ('peer-4', 'Camila · iPad',             'camila_ipad',      '10.8.0.5', 'familia',          'offline', '5h',    UNIX_TIMESTAMP() - 86400 * 24, 'vpnuser-2', 'iPad Air'),
    ('peer-5', 'Papá · Smart TV',          'papa_tv',          '10.8.0.6', 'familia',          'offline', '3h',    UNIX_TIMESTAMP() - 86400 * 20, 'vpnuser-3', 'Smart TV'),
    ('peer-6', 'Santi · Gaming rig',        'santi_pc',         '10.8.0.7', 'gaming',           'online',  'ahora', UNIX_TIMESTAMP() - 86400 * 15, 'vpnuser-4', 'Gaming PC'),
    ('peer-7', 'Operador 1 · Aguaquim',     'aguaquim_op1',     '10.8.0.8', 'cliente_aguaquim', 'offline', '1d',    UNIX_TIMESTAMP() - 86400 *  5, 'vpnuser-5', 'Laptop Oficina');

-- Services
INSERT INTO services (id, name, endpoint, url, category) VALUES
    ('jellyfin',       'Jellyfin',       '100.75.203.14:8096',  'jellyfin.home.local',  'Media'),
    ('navidrome',      'Navidrome',      '100.75.203.14:4533',  'navidrome.home.local', 'Media'),
    ('filebrowser',    'FileBrowser',    '100.75.203.14:8080',  'files.home.local',     'Herramientas'),
    ('kavita',         'Kavita',         '100.75.203.14:5000',  'kavita.home.local',    'Media'),
    ('minecraft-java', 'Minecraft Java', '100.75.203.14:25565', NULL,                   'Gaming'),
    ('mc-bedrock',     'MC Bedrock',     '100.75.203.14:19132', NULL,                   'Gaming'),
    ('terraria',       'Terraria',       '100.75.203.14:7777',  NULL,                   'Gaming'),
    ('aguaquim-crm',   'Aguaquim CRM',   '100.75.203.14:5433',  'www.aguaquim.com',     'CRM'),
    ('portainer',      'Portainer',      '100.75.203.14:9443',  'portainer.home.local', 'Infraestructura'),
    ('dns-pihole',     'DNS (Pi-hole)',  '100.114.140.34:53',   'dns.home.local',       'Red');

-- Access matrix
INSERT INTO access_matrix (role_id, service_id) VALUES
    -- admin: todo
    ('admin', 'jellyfin'), ('admin', 'navidrome'), ('admin', 'filebrowser'), ('admin', 'kavita'),
    ('admin', 'minecraft-java'), ('admin', 'mc-bedrock'), ('admin', 'terraria'),
    ('admin', 'aguaquim-crm'), ('admin', 'portainer'), ('admin', 'dns-pihole'),
    -- familia
    ('familia', 'jellyfin'), ('familia', 'navidrome'), ('familia', 'filebrowser'),
    ('familia', 'kavita'), ('familia', 'dns-pihole'), ('familia', 'minecraft-java'),
    -- gaming
    ('gaming', 'minecraft-java'), ('gaming', 'mc-bedrock'), ('gaming', 'terraria'), ('gaming', 'jellyfin'),
    -- cliente_aguaquim
    ('cliente_aguaquim', 'aguaquim-crm'), ('cliente_aguaquim', 'portainer');

-- Admin user (password: admin — cambiar en producción)
-- Generar un hash nuevo con: python -c "import bcrypt; print(bcrypt.hashpw(b'admin', bcrypt.gensalt()).decode())"
INSERT INTO users (id, username, password_hash, display_name, role, created_at) VALUES
    ('user-admin', 'admin', '$2b$12$PLACEHOLDER_REPLACE_WITH_REAL_HASH', 'Administrador', 'admin', UNIX_TIMESTAMP());

-- DNS records
INSERT INTO dns_records (id, domain, answer, type, description, service_id, created_at) VALUES
    ('dns-1', 'jellyfin.home.local',  '100.75.203.14',  'A', 'Servidor de media Jellyfin',          'jellyfin',    UNIX_TIMESTAMP()),
    ('dns-2', 'navidrome.home.local', '100.75.203.14',  'A', 'Servidor de música Navidrome',        'navidrome',   UNIX_TIMESTAMP()),
    ('dns-3', 'kavita.home.local',    '100.75.203.14',  'A', 'Biblioteca de libros Kavita',         'kavita',      UNIX_TIMESTAMP()),
    ('dns-4', 'files.home.local',     '100.75.203.14',  'A', 'FileBrowser — gestión de archivos',   'filebrowser', UNIX_TIMESTAMP()),
    ('dns-5', 'portainer.home.local', '100.75.203.14',  'A', 'Portainer — gestión de contenedores', 'portainer',   UNIX_TIMESTAMP()),
    ('dns-6', 'crm.home.local',       '100.75.203.14',  'A', 'Aguaquim CRM',                        'aguaquim-crm',UNIX_TIMESTAMP()),
    ('dns-7', 'dns.home.local',       '100.114.140.34', 'A', 'AdGuard Home — DNS',                  '',            UNIX_TIMESTAMP()),
    ('dns-8', '*.home.local',         '100.75.203.14',  'A', 'Wildcard — fallback para *.home.local','',           UNIX_TIMESTAMP());
