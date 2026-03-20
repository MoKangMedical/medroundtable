# Tencent Cloud Backend Deployment

This folder contains the minimum production assets to run the MedRoundTable
backend on a Tencent Cloud Lighthouse / CVM host running OpenCloudOS 9.

Recommended rollout:

1. Point a host to the server IP.
   Suggested long-term host: `api.medroundtable.vip`
   Temporary fallback: `43-134-3-158.sslip.io`
2. Open ports `80` and `443` in the Tencent Cloud firewall/security group.
3. SSH into the server after Tencent Cloud QR security login succeeds.
4. Run `deploy-opencloudos9.sh` as root.
5. Copy `.env.server.example` to `/opt/medroundtable/.env.production` and fill in secrets.
6. Enable the systemd service and nginx config.
7. Issue HTTPS with `certbot --nginx`.

Expected backend URL after deployment:

- `https://api.medroundtable.vip`
- or `https://43-134-3-158.sslip.io`

The FastAPI app listens on `127.0.0.1:8000`.
Nginx is the only public entrypoint.
