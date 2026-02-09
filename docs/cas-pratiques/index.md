# Cas pratiques

Cette section présente des exemples concrets et complets d'utilisation de systemd dans des situations réelles. Chaque cas pratique est prêt à l'emploi et documenté.

## Application web Python avec Gunicorn

### Contexte

Déployer une application Flask/Django avec Gunicorn derrière Nginx.

### Structure

```text
/opt/webapp/
├── app.py
├── requirements.txt
├── venv/
└── config/
    └── gunicorn.py
```

### Service systemd

```ini
# /etc/systemd/system/webapp.service
[Unit]
Description=Web Application with Gunicorn
After=network.target

[Service]
Type=notify
User=webapp
Group=webapp
WorkingDirectory=/opt/webapp
Environment="PATH=/opt/webapp/venv/bin"
EnvironmentFile=/etc/webapp/environment
ExecStart=/opt/webapp/venv/bin/gunicorn \

    --config /opt/webapp/config/gunicorn.py \
    --bind unix:/run/webapp/webapp.sock \

    app:application
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s

# Sécurité
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/webapp /var/log/webapp /run/webapp

# Répertoires
RuntimeDirectory=webapp
RuntimeDirectoryMode=0755
StateDirectory=webapp
LogsDirectory=webapp

# Ressources
MemoryMax=1G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

### Configuration Gunicorn

```python
# /opt/webapp/config/gunicorn.py
import multiprocessing

bind = 'unix:/run/webapp/webapp.sock'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/webapp/access.log'
errorlog = '/var/log/webapp/error.log'
loglevel = 'info'
```

### Nginx

```nginx
# /etc/nginx/sites-available/webapp
upstream webapp {
    server unix:/run/webapp/webapp.sock fail_timeout=0;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://webapp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /opt/webapp/static;
    }
}
```

### Déploiement

```bash
# Créer l'utilisateur
sudo useradd -r -s /usr/sbin/nologin -d /opt/webapp webapp

# Installer l'application
sudo mkdir -p /opt/webapp
sudo chown webapp:webapp /opt/webapp
sudo -u webapp python3 -m venv /opt/webapp/venv
sudo -u webapp /opt/webapp/venv/bin/pip install -r requirements.txt

# Activer le service
sudo systemctl daemon-reload
sudo systemctl enable webapp.service
sudo systemctl start webapp.service

# Vérifier
sudo systemctl status webapp.service
curl -I http://localhost
```

## Base de données PostgreSQL personnalisée

### Contexte

Instance PostgreSQL dédiée pour une application avec configuration personnalisée.

### Template service

```ini
# /etc/systemd/system/postgresql@.service
[Unit]
Description=PostgreSQL database server - %i
After=network.target

[Service]
Type=notify
User=postgres
Group=postgres
Environment=PGDATA=/var/lib/postgresql/%i
Environment=PGPORT=54%i
ExecStartPre=/usr/bin/postgresql-check-db-dir %i
ExecStart=/usr/bin/postgres -D /var/lib/postgresql/%i
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
KillSignal=SIGINT
TimeoutSec=0

# Sécurité
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ReadWritePaths=/var/lib/postgresql/%i /var/log/postgresql

# Ressources
MemoryMax=4G
CPUQuota=400%

[Install]
WantedBy=multi-user.target
```

### Initialisation

```bash
# Créer l'instance
sudo -u postgres /usr/bin/initdb -D /var/lib/postgresql/prod

# Configuration
sudo -u postgres tee /var/lib/postgresql/prod/postgresql.conf <<EOF
port = 5433
max_connections = 100
shared_buffers = 1GB
effective_cache_size = 3GB
EOF

# Démarrer
sudo systemctl enable postgresql@prod.service
sudo systemctl start postgresql@prod.service
```

## Service avec sauvegarde automatique

### Service principal

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=myapp
ExecStart=/usr/local/bin/myapp
Restart=on-failure

StateDirectory=myapp
LogsDirectory=myapp

[Install]
WantedBy=multi-user.target
```

### Service de sauvegarde

```ini
# /etc/systemd/system/myapp-backup.service
[Unit]
Description=Backup My Application Data
After=myapp.service
Requires=myapp.service

[Service]
Type=oneshot
User=myapp
ExecStart=/usr/local/bin/myapp-backup.sh

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp-backup
```

### Timer de sauvegarde

```ini
# /etc/systemd/system/myapp-backup.timer
[Unit]
Description=Backup My Application Daily

[Timer]
# Tous les jours à 2h du matin
OnCalendar=daily
OnCalendar=*-*-* 02:00:00

# Si le système était éteint, rattraper
Persistent=yes

# Randomiser légèrement l'heure
RandomizedDelaySec=30min

[Install]
WantedBy=timers.target
```

### Script de sauvegarde

```bash
#!/bin/bash
# /usr/local/bin/myapp-backup.sh

BACKUP_DIR="/var/backups/myapp"
DATE=$(date +%Y%m%d-%H%M%S)
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

# Sauvegarde
tar -czf "$BACKUP_DIR/myapp-${DATE}.tar.gz" /var/lib/myapp/

# Nettoyage ancien
find "$BACKUP_DIR" -name "myapp-*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: myapp-${DATE}.tar.gz"
```

### Activation

```bash
sudo chmod +x /usr/local/bin/myapp-backup.sh
sudo systemctl enable myapp-backup.timer
sudo systemctl start myapp-backup.timer

# Vérifier
systemctl list-timers --all
```

## Surveillance et restart automatique

### Service surveillé

```ini
# /etc/systemd/system/monitored-app.service
[Unit]
Description=Application with Health Check
After=network.target

[Service]
Type=simple
User=myapp
ExecStart=/usr/local/bin/myapp
Restart=on-failure
RestartSec=5s

# Health check toutes les 30s
ExecStartPost=/usr/local/bin/register-health-check.sh

[Install]
WantedBy=multi-user.target
```

### Service de health check

```ini
# /etc/systemd/system/health-check@.service
[Unit]
Description=Health Check for %i

[Service]
Type=oneshot
ExecStart=/usr/local/bin/health-check.sh %i

# Si échec, logger et redémarrer
ExecStartPost=/bin/sh -c 'if [ $EXIT_STATUS -ne 0 ]; then systemctl restart %i; fi'
```

### Timer de health check

```ini
# /etc/systemd/system/health-check@.timer
[Unit]
Description=Periodic Health Check for %i

[Timer]
OnBootSec=1min
OnUnitActiveSec=30s

[Install]
WantedBy=timers.target
```

### Script health check

```bash
#!/bin/bash
# /usr/local/bin/health-check.sh

SERVICE="$1"
ENDPOINT="http://localhost:8080/health"

if curl -f -s -o /dev/null "$ENDPOINT"; then
    echo "$SERVICE: Health check OK"
    exit 0
else
    echo "$SERVICE: Health check FAILED"
    exit 1
fi
```

## Stack Docker avec systemd

### Service Docker Compose

```ini
# /etc/systemd/system/docker-app.service
[Unit]
Description=Docker Compose Application
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/docker-app
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
ExecReload=/usr/bin/docker compose up -d --force-recreate
TimeoutStartSec=0

# Restart containers si nécessaire
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### Mise à jour automatique des images

```ini
# /etc/systemd/system/docker-app-update.service
[Unit]
Description=Update Docker Images
After=docker-app.service

[Service]
Type=oneshot
WorkingDirectory=/opt/docker-app
ExecStart=/usr/bin/docker compose pull
ExecStartPost=/usr/bin/systemctl restart docker-app.service
```

```ini
# /etc/systemd/system/docker-app-update.timer
[Unit]
Description=Update Docker Images Weekly

[Timer]
OnCalendar=weekly
Persistent=yes

[Install]
WantedBy=timers.target
```

## Service multi-instances

### Template

```ini
# /etc/systemd/system/worker@.service
[Unit]
Description=Worker Process %i
After=network.target redis.service

[Service]
Type=simple
User=worker
WorkingDirectory=/opt/worker
Environment="WORKER_ID=%i"
Environment="REDIS_URL=redis://localhost:6379/%i"
ExecStart=/opt/worker/venv/bin/python worker.py --id %i
Restart=on-failure

# Chaque instance a son propre répertoire
StateDirectory=worker/%i
LogsDirectory=worker/%i

# Limites par instance
MemoryMax=512M
CPUQuota=100%

[Install]
WantedBy=multi-user.target
```

### Target pour toutes les instances

```ini
# /etc/systemd/system/workers.target
[Unit]
Description=All Worker Instances
Wants=worker@1.service worker@2.service worker@3.service worker@4.service

[Install]
WantedBy=multi-user.target
```

### Gestion

```bash
# Démarrer toutes les instances
sudo systemctl start workers.target

# Démarrer une instance spécifique
sudo systemctl start worker@1.service

# Voir toutes les instances
systemctl list-units 'worker@*'

# Ajouter une nouvelle instance
sudo systemctl enable worker@5.service
sudo systemctl start worker@5.service
```

## Service avec notifications

### Service avec alertes

```ini
# /etc/systemd/system/critical-app.service
[Unit]
Description=Critical Application
After=network.target

[Service]
Type=simple
User=myapp
ExecStart=/usr/local/bin/myapp

# Notifications
ExecStartPost=/usr/local/bin/notify.sh "Critical App started"
ExecStopPost=/usr/local/bin/notify.sh "Critical App stopped"

# Restart avec notification
Restart=on-failure
RestartSec=10s
ExecStartPre=/usr/local/bin/notify.sh "Critical App restarting after failure"

[Install]
WantedBy=multi-user.target
```

### Script de notification

```bash
#!/bin/bash
# /usr/local/bin/notify.sh

MESSAGE="$1"
WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Slack
curl -X POST "$WEBHOOK_URL" \

  -H 'Content-Type: application/json' \
  -d '{"text": "'"$MESSAGE"'"}'

# Email
echo "$MESSAGE" | mail -s "System Alert" admin@example.com

# Syslog
logger -t systemd-notify "$MESSAGE"
```

## Bonnes pratiques récapitulatives

### Checklist pour chaque service

- [ ] Utilisateur dédié ou DynamicUser
- [ ] NoNewPrivileges=yes
- [ ] ProtectSystem=strict
- [ ] PrivateTmp=yes
- [ ] Limites mémoire et CPU
- [ ] ExecReload pour rechargement à chaud
- [ ] Restart=on-failure
- [ ] Documentation claire
- [ ] Logs vers journal
- [ ] Health checks si applicable

### Template de base

```ini
[Unit]
Description=
Documentation=
After=network.target

[Service]
Type=simple
User=
Group=
WorkingDirectory=
ExecStart=
ExecReload=
Restart=on-failure
RestartSec=5s

# Sécurité
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes

# Répertoires
StateDirectory=
LogsDirectory=

# Ressources
MemoryMax=
CPUQuota=

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Ces cas pratiques couvrent les scénarios les plus courants et servent de base pour créer vos propres services systemd robustes et maintenables.
