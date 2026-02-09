# Path Units (.path)

Les unités `.path` surveillent des fichiers ou répertoires et déclenchent des services lorsque des modifications sont détectées. Elles utilisent les APIs inotify du noyau Linux pour une surveillance efficace.

## Principe de fonctionnement

1. systemd surveille un chemin spécifié
2. Une condition se produit (fichier créé, modifié, supprimé...)
3. systemd active automatiquement le service associé
4. Le service traite l'événement

## Structure d'un path unit

```ini
[Unit]
Description=Watch for configuration changes

[Path]
PathModified=/etc/myapp/config.yaml
Unit=myapp-reload.service

[Install]
WantedBy=multi-user.target
```

## Section [Path]

### Types de surveillance

**PathExists**

: Déclenche quand le fichier ou répertoire existe

```ini
[Path]
PathExists=/tmp/trigger-file
```

Utilisé pour : déclenchement manuel, fichiers de verrouillage.

**PathExistsGlob**

: Comme PathExists mais supporte les wildcards

```ini
[Path]
PathExistsGlob=/var/spool/mail/*
```

**PathChanged**

: Déclenche quand le fichier ou répertoire change (création, modification, suppression)

```ini
[Path]
PathChanged=/etc/myapp/
```

Détecte les changements de métadonnées (permissions, propriétaire) mais pas le contenu.

**PathModified**

: Déclenche quand le contenu change (plus précis que PathChanged)

```ini
[Path]
PathModified=/etc/myapp/config.yaml
```

Détecte les modifications réelles du contenu du fichier.

**DirectoryNotEmpty**

: Déclenche quand le répertoire contient au moins un fichier

```ini
[Path]
DirectoryNotEmpty=/var/spool/myapp
```

Utilisé pour : traitement de files d'attente, spool directories.

### Options

**Unit**

: Service à activer (par défaut : même nom avec .service)

```ini
Unit=my-handler.service
```

**MakeDirectory**

: Créer le répertoire s'il n'existe pas

```ini
MakeDirectory=yes
DirectoryMode=0755
```

**TriggerLimitBurst** / **TriggerLimitIntervalSec**

: Limite le nombre de déclenchements

```ini
TriggerLimitBurst=5
TriggerLimitIntervalSec=60s
```

Protège contre les boucles infinies.

## Exemples pratiques

### Rechargement automatique de configuration

```ini
# /etc/systemd/system/nginx-config-watch.path
[Unit]
Description=Watch Nginx Configuration

[Path]
PathModified=/etc/nginx/nginx.conf
PathModified=/etc/nginx/conf.d/
Unit=nginx-reload.service

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/nginx-reload.service
[Unit]
Description=Reload Nginx Configuration

[Service]
Type=oneshot
ExecStart=/usr/sbin/nginx -t
ExecStart=/usr/sbin/nginx -s reload
```

Activation :

```bash
systemctl enable nginx-config-watch.path
systemctl start nginx-config-watch.path

# Nginx se recharge automatiquement quand la config change
```

### Traitement de files d'attente

```ini
# /etc/systemd/system/process-queue.path
[Unit]
Description=Watch Upload Queue

[Path]
DirectoryNotEmpty=/var/spool/uploads
MakeDirectory=yes

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/process-queue.service
[Unit]
Description=Process Upload Queue

[Service]
Type=oneshot
ExecStart=/usr/local/bin/process-uploads.sh
User=processor
```

### Déclenchement manuel

```ini
# /etc/systemd/system/backup-trigger.path
[Unit]
Description=Manual Backup Trigger

[Path]
PathExists=/tmp/trigger-backup
Unit=backup.service

[Install]
WantedBy=multi-user.target
```

Utilisation :

```bash
# Déclencher la sauvegarde
touch /tmp/trigger-backup

# Le service backup.service se lance automatiquement
```

### Surveillance de certificats

```ini
# /etc/systemd/system/ssl-cert-watch.path
[Unit]
Description=Watch SSL Certificates

[Path]
PathChanged=/etc/ssl/certs/mysite.crt
PathChanged=/etc/ssl/private/mysite.key
Unit=ssl-cert-reload.service

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/ssl-cert-reload.service
[Unit]
Description=Reload Services After Cert Change

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl reload nginx.service
ExecStart=/usr/bin/systemctl reload postfix.service
```

### Surveillance de logs

```ini
# /etc/systemd/system/error-log-watch.path
[Unit]
Description=Watch Error Logs

[Path]
PathModified=/var/log/myapp/error.log
Unit=error-alert.service
TriggerLimitBurst=10
TriggerLimitIntervalSec=300s

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/error-alert.service
[Unit]
Description=Send Error Alert

[Service]
Type=oneshot
ExecStart=/usr/local/bin/send-alert.sh "Errors detected in log"
```

### Hot-reload d'application

```ini
# /etc/systemd/system/app-reload.path
[Unit]
Description=Watch Application Files

[Path]
PathModified=/opt/myapp/app.py
PathModified=/opt/myapp/config.py
Unit=myapp-reload.service

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/myapp-reload.service
[Unit]
Description=Reload My Application

[Service]
Type=oneshot
ExecStart=/usr/bin/systemctl reload myapp.service
```

### Traitement batch de fichiers

```ini
# /etc/systemd/system/file-processor.path
[Unit]
Description=Watch for Files to Process

[Path]
PathExistsGlob=/var/spool/input/*.csv
Unit=file-processor.service

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/file-processor.service
[Unit]
Description=Process CSV Files

[Service]
Type=oneshot
ExecStart=/usr/local/bin/process-csv-files.sh
User=processor
```

## Gestion des path units

### Commandes de base

```bash
# Lister les path units
systemctl list-units --type=path
systemctl list-units --type=path --all

# Activer
systemctl enable mywatch.path
systemctl start mywatch.path

# Désactiver
systemctl stop mywatch.path
systemctl disable mywatch.path

# Voir l'état
systemctl status mywatch.path

# Voir les chemins surveillés
systemctl show mywatch.path -p Paths
```

### Tester un path unit

```bash
# Démarrer la surveillance
systemctl start mywatch.path

# Dans un autre terminal, surveiller les logs
journalctl -u mywatch.path -f
journalctl -u mywatch.service -f

# Modifier le fichier surveillé
echo "test" >> /path/to/watched/file

# Observer l'activation du service
```

## Cas d'usage avancés

### Multiple chemins, un seul service

```ini
[Path]
PathModified=/etc/app/config1.yaml
PathModified=/etc/app/config2.yaml
PathModified=/etc/app/includes/
Unit=app-reload.service
```

Tout changement déclenche le même service.

### Chaînes de traitement

```ini
# Stage 1: Détection de fichiers
# process-stage1.path
[Path]
DirectoryNotEmpty=/var/spool/stage1
Unit=process-stage1.service
```

```ini
# process-stage1.service déplace vers stage2
[Service]
Type=oneshot
ExecStart=/usr/local/bin/stage1-to-stage2.sh
```

```ini
# Stage 2: Traitement
# process-stage2.path
[Path]
DirectoryNotEmpty=/var/spool/stage2
Unit=process-stage2.service
```

### Avec dépendances

```ini
# config-watch.path
[Unit]
Description=Configuration Watcher
After=myapp.service

[Path]
PathModified=/etc/myapp/config.yaml
Unit=myapp-reload.service

[Install]
WantedBy=multi-user.target
```

Le path unit ne démarre qu'après le service principal.

## Limitations et considérations

### Limitations inotify

Linux limite le nombre de watches inotify :

```bash
# Voir la limite actuelle
cat /proc/sys/fs/inotify/max_user_watches

# Augmenter temporairement
echo 524288 | sudo tee /proc/sys/fs/inotify/max_user_watches

# Permanent (/etc/sysctl.conf)
fs.inotify.max_user_watches=524288
```

### Performance

La surveillance de nombreux fichiers peut consommer des ressources :

- Privilégier DirectoryNotEmpty plutôt que PathExistsGlob
- Éviter de surveiller des répertoires avec des milliers de fichiers
- Utiliser des patterns spécifiques plutôt que génériques

### Systèmes de fichiers réseau

inotify ne fonctionne pas sur tous les systèmes de fichiers réseau (NFS, CIFS).

Alternative : utiliser des timers avec polling.

### Boucles infinies

Attention aux services qui modifient les fichiers surveillés :

```ini
# Protection
[Path]
TriggerLimitBurst=3
TriggerLimitIntervalSec=60s
```

## Débogage

### Path unit ne déclenche pas

```bash
# Vérifier l'état
systemctl status mywatch.path

# Le path est-il correct ?
systemctl show mywatch.path -p Paths

# Le fichier existe ?
ls -l /path/to/watched/file

# Logs
journalctl -u mywatch.path

# Tester manuellement le service
systemctl start mywatch.service
```

### Déclenchements trop fréquents

```bash
# Voir l'historique des déclenchements
journalctl -u mywatch.path
journalctl -u mywatch.service

# Ajuster les limites
[Path]
TriggerLimitBurst=5
TriggerLimitIntervalSec=120s
```

### Service ne s'exécute pas

```bash
# Vérifier que le service existe
systemctl cat mywatch.service

# Tester le service indépendamment
systemctl start mywatch.service
systemctl status mywatch.service

# Logs du service
journalctl -u mywatch.service -n 50
```

## Comparaison avec d'autres approches

### Path units vs inotifywait

**inotifywait** :

```bash
#!/bin/bash
while inotifywait -e modify /etc/myapp/config.yaml; do
    systemctl reload myapp.service
done
```

**Path units** :

- Intégration systemd native
- Logs dans journald
- Gestion automatique du cycle de vie
- Redémarrage automatique en cas d'échec

### Path units vs Timers

**Timers** : Vérification périodique (polling)

```ini
[Timer]
OnUnitActiveSec=5min
```

**Path units** : Réaction immédiate (inotify)

- Plus réactif
- Moins de charge système
- Mais ne fonctionne pas sur tous les FS

## Bonnes pratiques

1. **Utiliser Type=oneshot** pour les services déclenchés

   ```ini
   [Service]
   Type=oneshot
   ```

2. **Toujours définir des limites**

   ```ini
   TriggerLimitBurst=5
   TriggerLimitIntervalSec=60s
   ```

3. **Créer les répertoires si nécessaire**

   ```ini
   MakeDirectory=yes
   DirectoryMode=0755
   ```

4. **Surveiller les répertoires plutôt que les fichiers individuels**

   ```ini
   PathModified=/etc/myapp/
   ```

5. **Documenter clairement**

   ```ini
   [Unit]
   Description=Clear description of what triggers this
   ```

6. **Tester les limites inotify**

   ```bash
   cat /proc/sys/fs/inotify/max_user_watches
   ```

7. **Logger les déclenchements**

   ```ini
   [Service]
   Type=oneshot
   ExecStartPre=/usr/bin/logger "Path triggered: processing"
   ```

Les path units sont un outil puissant pour réagir aux changements du système de fichiers, permettant une automatisation élégante de nombreuses tâches administratives.
