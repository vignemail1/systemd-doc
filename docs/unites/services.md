# Services (.service)

Les unités de type `.service` sont le type le plus courant dans systemd. Elles représentent des processus ou daemons qui s'exécutent en arrière-plan.

## Structure d'un fichier service

Un fichier `.service` typique contient trois sections principales :

```ini
[Unit]
Description=Mon Application Web
Documentation=https://example.com/docs
After=network.target
Requires=network.target

[Service]
Type=simple
User=webapp
Group=webapp
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/myapp --config /etc/myapp/config.yaml
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```text

## Section [Unit]

La section `[Unit]` contient les métadonnées et dépendances.

### Options courantes

**Description**

: Description lisible du service (affichée par `systemctl status`)

```ini
Description=Nginx HTTP Server
```text

**Documentation**

: URLs vers la documentation (man pages, sites web)

```ini
Documentation=man:nginx(8)
Documentation=https://nginx.org/en/docs/
```text

**After** / **Before**

: Ordre de démarrage (n'implique pas de dépendance forte)

```ini
After=network.target syslog.target
Before=nginx.service
```text

**Requires**

: Dépendance stricte (si la dépendance échoue, ce service échoue aussi)

```ini
Requires=postgresql.service
```text

**Wants**

: Dépendance faible (recommandée mais pas obligatoire)

```ini
Wants=redis.service
```text

**Conflicts**

: Unités incompatibles (ne peuvent pas tourner simultanément)

```ini
Conflicts=apache2.service
```text

**Condition** / **Assert**

: Conditions de démarrage

```ini
ConditionPathExists=/etc/myapp/config.yaml
ConditionFileNotEmpty=/etc/myapp/config.yaml
AssertPathExists=/usr/bin/myapp
```text

## Section [Service]

La section `[Service]` définit comment exécuter et gérer le processus.

### Type de service

Le paramètre `Type=` définit comment systemd doit gérer le processus :

#### Type=simple (défaut)

Le processus démarré par `ExecStart` est le processus principal.

```ini
[Service]
Type=simple
ExecStart=/usr/bin/myapp
```text

**Utilisation** : Pour les applications qui restent au premier plan.

#### Type=forking

Le processus fork() et le parent se termine, l'enfant continue.

```ini
[Service]
Type=forking
PIDFile=/var/run/nginx.pid
ExecStart=/usr/sbin/nginx
```text

**Utilisation** : Daemons traditionnels qui se mettent en arrière-plan.

#### Type=oneshot

Le processus s'exécute puis se termine (pas de daemon persistant).

```ini
[Service]
Type=oneshot
ExecStart=/usr/bin/backup.sh
RemainAfterExit=yes
```text

**Utilisation** : Scripts de configuration, tâches ponctuelles.

#### Type=notify

Le service notifie systemd quand il est prêt via `sd_notify()`.

```ini
[Service]
Type=notify
ExecStart=/usr/bin/myapp
```text

**Utilisation** : Applications qui supportent la notification systemd (nginx, PostgreSQL...).

#### Type=dbus

Le service est considéré prêt quand il acquiert un nom D-Bus.

```ini
[Service]
Type=dbus
BusName=org.example.MyApp
ExecStart=/usr/bin/myapp
```text

**Utilisation** : Services D-Bus.

#### Type=idle

Retarde le démarrage jusqu'à ce que tous les autres services soient lancés.

```ini
[Service]
Type=idle
ExecStart=/usr/bin/late-service
```text

**Utilisation** : Rare, pour des services qui doivent démarrer en dernier.

### Commandes d'exécution

**ExecStart**

: Commande principale de démarrage (obligatoire sauf pour Type=oneshot)

```ini
ExecStart=/usr/bin/myapp --port 8080
```text

**ExecStartPre** / **ExecStartPost**

: Commandes à exécuter avant/après le démarrage

```ini
ExecStartPre=/usr/bin/setup.sh
ExecStart=/usr/bin/myapp
ExecStartPost=/usr/bin/notify-started.sh
```text

**ExecReload**

: Commande pour recharger la configuration sans redémarrer

```ini
ExecReload=/bin/kill -HUP $MAINPID
```text

**ExecStop**

: Commande pour arrêter proprement le service

```ini
ExecStop=/usr/bin/myapp-stop.sh
```text

**ExecStopPost**

: Commandes après l'arrêt (nettoyage)

```ini
ExecStopPost=/usr/bin/cleanup.sh
```text

### Redémarrage automatique

**Restart**

: Politique de redémarrage automatique

```ini
Restart=on-failure  # Redémarre uniquement en cas d'échec
```text

Valeurs possibles :

- `no` : Jamais redémarrer (défaut)
- `always` : Toujours redémarrer
- `on-success` : Redémarrer si terminé avec succès
- `on-failure` : Redémarrer en cas d'échec
- `on-abnormal` : Redémarrer si terminé anormalement
- `on-abort` : Redémarrer si terminé par signal
- `on-watchdog` : Redémarrer si watchdog timeout

**RestartSec**

: Délai avant redémarrage

```ini
RestartSec=5s
```text

**StartLimitBurst** / **StartLimitIntervalSec**

: Protection contre les boucles de redémarrage

```ini
StartLimitBurst=3          # Max 3 redémarrages
StartLimitIntervalSec=60s  # Dans une fenêtre de 60 secondes
```text

### Identité et permissions

**User** / **Group**

: Utilisateur et groupe sous lesquels exécuter le service

```ini
User=webapp
Group=webapp
```text

**DynamicUser**

: Crée automatiquement un utilisateur temporaire

```ini
DynamicUser=yes
```text

### Répertoires de travail

**WorkingDirectory**

: Répertoire de travail du processus

```ini
WorkingDirectory=/opt/myapp
```text

**RootDirectory** / **RootImage**

: Changement de racine (chroot)

```ini
RootDirectory=/srv/chroot/myapp
```text

### Variables d'environnement

**Environment**

: Définir des variables

```ini
Environment="VAR1=value1" "VAR2=value2"
Environment="PATH=/usr/local/bin:/usr/bin"
```text

**EnvironmentFile**

: Charger des variables depuis un fichier

```ini
EnvironmentFile=/etc/myapp/env
```text

Contenu de `/etc/myapp/env` :

```bash
PORT=8080
DATABASE_URL=postgresql://localhost/mydb
```text

### Limites de ressources

**LimitNOFILE** / **LimitNPROC**

: Limites de descripteurs de fichiers et processus

```ini
LimitNOFILE=65536
LimitNPROC=4096
```text

**MemoryLimit** / **CPUQuota**

: Limites mémoire et CPU

```ini
MemoryLimit=2G
CPUQuota=200%  # 2 cores
```text

### Timeouts

**TimeoutStartSec**

: Timeout pour le démarrage

```ini
TimeoutStartSec=30s
```text

**TimeoutStopSec**

: Timeout pour l'arrêt

```ini
TimeoutStopSec=10s
```text

## Section [Install]

Définit les liens de dépendances lors de l'activation.

**WantedBy**

: Target qui "veut" ce service

```ini
WantedBy=multi-user.target
```text

**RequiredBy**

: Target qui "requiert" ce service (dépendance forte)

```ini
RequiredBy=graphical.target
```text

**Alias**

: Noms alternatifs pour le service

```ini
Alias=webserver.service
```text

## Exemples complets

### Service simple

```ini
# /etc/systemd/system/simple-webapp.service
[Unit]
Description=Simple Web Application
After=network.target

[Service]
Type=simple
User=webapp
WorkingDirectory=/opt/webapp
ExecStart=/usr/bin/python3 /opt/webapp/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```text

### Service avec préparation

```ini
# /etc/systemd/system/advanced-service.service
[Unit]
Description=Advanced Service with Setup
After=network-online.target
Wants=network-online.target
Requires=postgresql.service
After=postgresql.service

[Service]
Type=notify
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp

# Préparation
ExecStartPre=/usr/bin/mkdir -p /var/run/myapp
ExecStartPre=/usr/bin/chown myapp:myapp /var/run/myapp

# Démarrage
ExecStart=/usr/bin/myapp --config /etc/myapp/config.yaml

# Rechargement
ExecReload=/bin/kill -HUP $MAINPID

# Arrêt propre
ExecStop=/usr/bin/myapp-shutdown
ExecStopPost=/usr/bin/rm -rf /var/run/myapp

# Redémarrage automatique
Restart=on-failure
RestartSec=10s
StartLimitBurst=5
StartLimitIntervalSec=120s

# Environnement
EnvironmentFile=/etc/myapp/environment
Environment="LOG_LEVEL=info"

# Ressources
LimitNOFILE=32768
MemoryLimit=4G

# Timeouts
TimeoutStartSec=60s
TimeoutStopSec=30s

[Install]
WantedBy=multi-user.target
```text

### Service avec isolation de sécurité

```ini
# /etc/systemd/system/secure-service.service
[Unit]
Description=Secure Isolated Service
After=network.target

[Service]
Type=simple

# Utilisateur dynamique
DynamicUser=yes

# Commande
ExecStart=/usr/bin/secure-app

# Isolation
PrivateTmp=yes
PrivateDevices=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/secure-app

# Sécurité
NoNewPrivileges=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictRealtime=yes
RestrictNamespaces=yes

# Syscalls
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM

# Capacités
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
```text

### Service oneshot

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Daily Backup Service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
User=backup
StandardOutput=journal
StandardError=journal
```text

Utilisé avec un timer :

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily Backup Timer

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```text

## Bonnes pratiques

### 1. Toujours spécifier User/Group

Éviter de lancer des services en root sauf nécessaire :

```ini
User=myapp
Group=myapp
```text

### 2. Utiliser Restart=on-failure

Pour la résilience :

```ini
Restart=on-failure
RestartSec=5s
```text

### 3. Définir des timeouts raisonnables

```ini
TimeoutStartSec=30s
TimeoutStopSec=15s
```text

### 4. Utiliser Type=notify quand possible

Pour une détection précise de l'état "ready" :

```ini
Type=notify
```text

### 5. Documenter le service

```ini
[Unit]
Description=Description claire et concise
Documentation=man:myapp(8)
Documentation=https://docs.example.com
```text

### 6. Appliquer des restrictions de sécurité

```ini
PrivateTmp=yes
ProtectSystem=strict
NoNewPrivileges=yes
```text

### 7. Utiliser des fichiers d'environnement

Plutôt que d'encoder les secrets dans le fichier unité :

```ini
EnvironmentFile=/etc/myapp/secrets.env
```text

## Débogage

### Voir l'état détaillé

```bash
systemctl status myapp.service
```text

### Voir les logs

```bash
journalctl -u myapp.service
journalctl -u myapp.service -f  # Suivi temps réel
journalctl -u myapp.service --since "1 hour ago"
```text

### Vérifier la configuration

```bash
systemd-analyze verify myapp.service
```text

### Voir la configuration effective

```bash
systemctl show myapp.service
```text

### Recharger après modification

```bash
systemctl daemon-reload
systemctl restart myapp.service
```text

## Variables spéciales

systemd fournit des variables utilisables dans les commandes :

- `%n` : Nom complet de l'unité
- `%N` : Nom sans le suffixe de type
- `%p` : Nom préfixe (avant @)
- `%i` : Instance (après @)
- `%I` : Instance unescaped
- `%u` : Nom d'utilisateur
- `%U` : UID
- `%h` : Home directory
- `%s` : Shell de l'utilisateur
- `%t` : Runtime directory (`/run`)
- `%S` : State directory (`/var/lib`)

Exemple :

```ini
ExecStart=/usr/bin/myapp --instance %i --user %u
```text

Les services sont le cœur de systemd. Maîtriser leur configuration est essentiel pour administrer efficacement un système Linux moderne.

