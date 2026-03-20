#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=/opt/medroundtable
APP_USER=medroundtable

echo "[1/7] Install system packages"
dnf install -y git nginx python3 python3-pip python3-devel gcc openssl openssl-devel libffi-devel

echo "[2/7] Create app user and directories"
id -u "${APP_USER}" >/dev/null 2>&1 || useradd --system --create-home --shell /bin/bash "${APP_USER}"
mkdir -p "${PROJECT_DIR}" "${PROJECT_DIR}/data/uploads"
chown -R "${APP_USER}:${APP_USER}" "${PROJECT_DIR}"

echo "[3/7] Sync project files"
if [ ! -d "${PROJECT_DIR}/.git" ]; then
    git clone https://github.com/MoKangMedical/medroundtable.git "${PROJECT_DIR}"
fi
cd "${PROJECT_DIR}"
git fetch --all --prune
git checkout main
git pull --ff-only origin main

echo "[4/7] Create virtualenv and install Python dependencies"
sudo -u "${APP_USER}" python3 -m venv "${PROJECT_DIR}/.venv"
sudo -u "${APP_USER}" "${PROJECT_DIR}/.venv/bin/pip" install --upgrade pip setuptools wheel
sudo -u "${APP_USER}" "${PROJECT_DIR}/.venv/bin/pip" install -r "${PROJECT_DIR}/requirements.txt"

echo "[5/7] Install service files"
install -m 644 "${PROJECT_DIR}/ops/tencent/medroundtable-api.service" /etc/systemd/system/medroundtable-api.service
install -m 644 "${PROJECT_DIR}/ops/tencent/nginx-medroundtable-api.conf" /etc/nginx/conf.d/medroundtable-api.conf

echo "[6/7] Prepare environment file"
if [ ! -f "${PROJECT_DIR}/.env.production" ]; then
    cp "${PROJECT_DIR}/ops/tencent/.env.server.example" "${PROJECT_DIR}/.env.production"
    chown "${APP_USER}:${APP_USER}" "${PROJECT_DIR}/.env.production"
    chmod 600 "${PROJECT_DIR}/.env.production"
    echo "Created ${PROJECT_DIR}/.env.production"
    echo "Fill in secrets before starting the service."
fi

echo "[7/7] Enable services"
nginx -t
systemctl daemon-reload
systemctl enable nginx
systemctl enable medroundtable-api

echo
echo "Next steps:"
echo "1. Edit ${PROJECT_DIR}/.env.production"
echo "2. systemctl restart medroundtable-api"
echo "3. systemctl restart nginx"
echo "4. certbot --nginx -d api.medroundtable.vip"
echo "   or certbot --nginx -d 43-134-3-158.sslip.io"
