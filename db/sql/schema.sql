-- WG-ACL Manager — Schema
-- Run once on a fresh database before starting the backend.

CREATE TABLE IF NOT EXISTS roles (
    id           VARCHAR(64)  NOT NULL PRIMARY KEY,
    display_name VARCHAR(256) NOT NULL,
    description  TEXT         NOT NULL,
    color        VARCHAR(16)  NOT NULL,
    created_at   DOUBLE       NOT NULL
);

CREATE TABLE IF NOT EXISTS vpn_users (
    id           VARCHAR(64)  NOT NULL PRIMARY KEY,
    display_name VARCHAR(256) NOT NULL,
    email        VARCHAR(256) NOT NULL UNIQUE,
    role_id      VARCHAR(64)  NOT NULL,
    created_at   DOUBLE       NOT NULL
);

CREATE TABLE IF NOT EXISTS peers (
    id           VARCHAR(64)  NOT NULL PRIMARY KEY,
    display_name VARCHAR(256) NOT NULL,
    username     VARCHAR(128) NOT NULL UNIQUE,
    ip           VARCHAR(45)  NOT NULL,
    role_id      VARCHAR(64)  NOT NULL,
    status       VARCHAR(16)  NOT NULL DEFAULT 'offline',
    last_seen    VARCHAR(64)  NOT NULL DEFAULT '',
    created_at   DOUBLE       NOT NULL,
    user_id      VARCHAR(64)  NOT NULL DEFAULT '',
    device_name  VARCHAR(256) NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS services (
    id       VARCHAR(64)  NOT NULL PRIMARY KEY,
    name     VARCHAR(256) NOT NULL,
    endpoint VARCHAR(256) NOT NULL,
    url      VARCHAR(512)          DEFAULT NULL,
    category VARCHAR(64)  NOT NULL
);

CREATE TABLE IF NOT EXISTS access_matrix (
    role_id    VARCHAR(64) NOT NULL,
    service_id VARCHAR(64) NOT NULL,
    PRIMARY KEY (role_id, service_id)
);

CREATE TABLE IF NOT EXISTS users (
    id            VARCHAR(64)  NOT NULL PRIMARY KEY,
    username      VARCHAR(128) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    display_name  VARCHAR(256) NOT NULL,
    role          VARCHAR(64)  NOT NULL,
    created_at    DOUBLE       NOT NULL
);

CREATE TABLE IF NOT EXISTS dns_records (
    id          VARCHAR(64)  NOT NULL PRIMARY KEY,
    domain      VARCHAR(256) NOT NULL,
    answer      VARCHAR(256) NOT NULL,
    type        VARCHAR(8)   NOT NULL,
    description TEXT         NOT NULL,
    service_id  VARCHAR(64)  NOT NULL DEFAULT '',
    created_at  DOUBLE       NOT NULL
);
