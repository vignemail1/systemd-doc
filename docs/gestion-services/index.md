# Gestion des services

La gestion des services systemd couvre la création, modification, débogage et optimisation des unit files. Cette section explique comment créer des services robustes et maintenables.

## Cycle de vie d'un service

Un service systemd passe par plusieurs étapes :

1. **Création** : Écriture du unit file
2. **Installation** : Placement et activation
3. **Démarrage** : Lancement du service
4. **Surveillance** : Monitoring et logs
5. **Modification** : Mise à jour de la configuration
6. **Débogage** : Résolution de problèmes

## Création d'un service

### Anatomie d'un service complet

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application Service
Documentation=https://myapp.example.com/docs
After=network-online.target
Wants=network-online.target
Requires=postgresql.service

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
EnvironmentFile=/etc/myapp/environment
ExecStartPre=/usr/local/bin/myapp-prestart.sh
ExecStart=/usr/local/bin/myapp --config /etc/myapp/config.yaml
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/usr/local/bin/myapp-stop.sh
Restart=on-failure
RestartSec=5s
TimeoutStartSec=30s
TimeoutStopSec=10s

# Sécurité
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/myapp /var/log/myapp

# Limites ressources
MemoryMax=2G
CPUQuota=200%
TasksMax=500

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

[Install]
WantedBy=multi-user.target
Also=myapp-worker.service
```

### Étapes de création

#### 1. Créer l'utilisateur système

```bash
# Créer un utilisateur dédié sans shell
sudo useradd -r -s /usr/sbin/nologin -d /opt/myapp myapp

# Créer les répertoires
sudo mkdir -p /opt/myapp /var/lib/myapp /var/log/myapp
sudo chown -R myapp:myapp /opt/myapp /var/lib/myapp /var/log/myapp
```

#### 2. Écrire le unit file

```bash
sudo nano /etc/systemd/system/myapp.service
```

#### 3. Valider la syntaxe

```bash
# Vérifier la syntaxe
systemd-analyze verify /etc/systemd/system/myapp.service

# Voir le fichier tel que systemd le comprend
systemctl cat myapp.service
```

#### 4. Recharger systemd

```bash
sudo systemctl daemon-reload
```

#### 5. Activer et démarrer

```bash
# Activer au boot
sudo systemctl enable myapp.service

# Démarrer
sudo systemctl start myapp.service

# Vérifier
sudo systemctl status myapp.service
```

## Modification de services

### Drop-in files (méthode recommandée)

Plutôt que de modifier directement un unit file système, utilisez des drop-ins :

```bash
# Créer un override
sudo systemctl edit nginx.service
```

Cela crée `/etc/systemd/system/nginx.service.d/override.conf` :

```ini
[Service]
Environment="NGINX_OPTS=-g 'daemon off;'"
MemoryMax=4G
Restart=always
```

Avantages :

- Ne modifie pas le fichier original
- Survit aux mises à jour du paquet
- Plusieurs drop-ins peuvent coexister
- Facile à versionner

### Modification complète

Pour remplacer complètement un unit :

```bash
# Copier le unit système
sudo cp /usr/lib/systemd/system/nginx.service /etc/systemd/system/

# Éditer
sudo nano /etc/systemd/system/nginx.service

# Recharger
sudo systemctl daemon-reload
sudo systemctl restart nginx.service
```

### Voir les modifications

```bash
# Voir tous les overrides
systemd-delta

# Voir la configuration effective
systemctl cat nginx.service

# Voir seulement les drop-ins
systemctl show nginx.service -p FragmentPath -p DropInPaths
```

## Débogage

### Service ne démarre pas

```bash
# Voir l'état détaillé
systemctl status myapp.service

# Logs récents
journalctl -u myapp.service -n 50

# Logs depuis le dernier boot
journalctl -u myapp.service -b

# Suivre en temps réel
journalctl -u myapp.service -f

# Niveau de détail maximum
SystemdLogLevel=debug
systemctl daemon-reload
systemctl restart myapp.service
journalctl -u myapp.service -n 100
```

### Vérifier les dépendances

```bash
# Voir les dépendances
systemctl list-dependencies myapp.service

# Voir les dépendances inverses
systemctl list-dependencies --reverse myapp.service

# Voir les services requis non démarrés
systemctl list-dependencies myapp.service | grep -E '●|×'
```

### Analyser les temps de démarrage

```bash
# Temps de démarrage du service
systemd-analyze blame | grep myapp

# Chaîne critique
systemd-analyze critical-chain myapp.service
```

### Tester manuellement

```bash
# Exécuter comme systemd le ferait
sudo -u myapp /usr/local/bin/myapp --config /etc/myapp/config.yaml

# Avec l'environnement systemd
sudo systemd-run --unit=myapp-test \
  --working-directory=/opt/myapp \
  --setenv=ENV_VAR=value \
  /usr/local/bin/myapp
```

## Reload vs Restart

### Reload (rechargement à chaud)

```bash
systemctl reload nginx.service
```

Envoie un signal (généralement SIGHUP) pour recharger la configuration sans interrompre le service.

Configuration :

```ini
[Service]
ExecReload=/bin/kill -HUP $MAINPID
# ou
ExecReload=/usr/sbin/nginx -s reload
```

### Restart (redémarrage complet)

```bash
systemctl restart nginx.service
```

Arrête puis redémarre le service. Provoque une interruption.

### Try-restart

```bash
systemctl try-restart nginx.service
```

Redémarre seulement si le service est déjà actif.

### Reload-or-restart

```bash
systemctl reload-or-restart nginx.service
```

Tente un reload, sinon fait un restart.

## Templates de services

Les templates permettent de créer plusieurs instances d'un service :

```ini
# /etc/systemd/system/myapp@.service
[Unit]
Description=My App Instance %i
After=network.target

[Service]
Type=simple
User=myapp
ExecStart=/usr/local/bin/myapp --instance %i --port 808%i
Environment="INSTANCE=%i"
WorkingDirectory=/var/lib/myapp/%i

[Install]
WantedBy=multi-user.target
```

Utilisation :

```bash
# Démarrer plusieurs instances
systemctl start myapp@1.service
systemctl start myapp@2.service
systemctl start myapp@prod.service

# Activer au boot
systemctl enable myapp@1.service myapp@2.service

# Voir toutes les instances
systemctl list-units 'myapp@*'
```

Variables disponibles :

- `%i` : Identifiant de l'instance (après @)
- `%I` : Identifiant échappé
- `%n` : Nom complet de l'unit
- `%N` : Nom sans le suffixe
- `%p` : Prefix (nom sans @)
- `%H` : Hostname
- `%u` : Username

## Bonnes pratiques

### 1. Toujours documenter

```ini
[Unit]
Description=Clear and concise description
Documentation=https://docs.example.com/myapp
Documentation=man:myapp(8)
```

### 2. Utiliser des utilisateurs dédiés

```ini
[Service]
User=myapp
Group=myapp
DynamicUser=yes  # Crée automatiquement l'utilisateur
```

### 3. Définir des timeouts

```ini
[Service]
TimeoutStartSec=30s
TimeoutStopSec=10s
TimeoutSec=40s  # Définit les deux
```

### 4. Gérer les échecs

```ini
[Service]
Restart=on-failure
RestartSec=5s
StartLimitBurst=3
StartLimitIntervalSec=60s
```

### 5. Limiter les ressources

```ini
[Service]
MemoryMax=2G
CPUQuota=200%
TasksMax=500
IOWeight=500
```

### 6. Sécuriser le service

```ini
[Service]
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadOnlyPaths=/
ReadWritePaths=/var/lib/myapp
```

### 7. Logger correctement

```ini
[Service]
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp
SyslogLevel=info
```

### 8. Tester avant production

```bash
# Vérifier la syntaxe
systemd-analyze verify myapp.service

# Tester le démarrage
systemctl start myapp.service
systemctl status myapp.service

# Tester le reload
systemctl reload myapp.service

# Tester le restart
systemctl restart myapp.service

# Tester l'arrêt
systemctl stop myapp.service
```

## Automatisation

### Générer un service avec un script

```bash
#!/bin/bash
# generate-service.sh

NAME=$1
USER=$2
EXEC=$3

cat > /etc/systemd/system/${NAME}.service <<EOF
[Unit]
Description=${NAME} Service
After=network.target

[Service]
Type=simple
User=${USER}
ExecStart=${EXEC}
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ${NAME}.service
```

### Utiliser systemd-run pour tests

```bash
# Créer un service temporaire
systemd-run --unit=test-app \
  --property=User=myapp \
  --property=WorkingDirectory=/opt/myapp \
  /usr/local/bin/myapp

# Service qui s'autodétruit après exécution
systemd-run --scope /usr/bin/mycommand
```

La maîtrise de la gestion des services systemd permet de créer des services robustes, sécurisés et facilement maintenables.
