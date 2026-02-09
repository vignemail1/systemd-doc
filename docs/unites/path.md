# Path (.path)

Les unités `.path` permettent d'activer des services en réponse à des modifications du système de fichiers. Elles surveillent des fichiers ou répertoires et déclenchent des actions lorsque certains événements se produisent.

## Concept

Une unité `.path` surveille un ou plusieurs chemins et active automatiquement un service associé lorsqu'une condition est remplie (fichier créé, modifié, supprimé...).

## Cas d'usage

- **Traitement automatique** : Traiter des fichiers déposés dans un répertoire
- **Hot-reload** : Recharger une configuration quand elle change
- **Déclenchement de tâches** : Lancer une action sur création de fichier trigger
- **Monitoring** : Réagir à l'apparition de fichiers de log spécifiques
- **Build automatique** : Rebuilder quand des sources changent

## Structure d'un fichier .path

```ini
[Unit]
Description=Watch for configuration changes

[Path]
PathChanged=/etc/myapp/config.yaml
Unit=myapp-reload.service

[Install]
WantedBy=multi-user.target
```

## Section [Path]

### Types de surveillance

**PathExists**
: Déclenche quand le chemin existe

```ini
PathExists=/tmp/trigger-file
```

Vérifie périodiquement si le fichier/répertoire existe.

**PathExistsGlob**
: Déclenche quand au moins un fichier correspond au glob

```ini
PathExistsGlob=/var/spool/upload/*.csv
```

Supporte les wildcards.

**PathChanged**
: Déclenche quand le fichier ou répertoire change

```ini
PathChanged=/etc/myapp/config.yaml
```

Utilise inotify pour détecter les modifications.

**PathModified**
: Déclenche sur modification de contenu uniquement

```ini
PathModified=/var/log/app/important.log
```

Plus précis que `PathChanged` (ignore les changements de métadonnées).

**DirectoryNotEmpty**
: Déclenche quand le répertoire contient au moins un fichier

```ini
DirectoryNotEmpty=/var/spool/processing
```

### Options

**Unit**
: Service à activer (par défaut : même nom avec .service)

```ini
Unit=myapp-processor.service
```

**MakeDirectory**
: Créer le répertoire s'il n'existe pas

```ini
MakeDirectory=yes
```

**DirectoryMode**
: Permissions du répertoire créé

```ini
DirectoryMode=0755
```

**TriggerLimitIntervalSec** / **TriggerLimitBurst**
: Limite le taux de déclenchement

```ini
TriggerLimitIntervalSec=60s
TriggerLimitBurst=5  # Max 5 déclenchements par minute
```

## Exemples complets

### Traitement automatique de fichiers

```ini
# /etc/systemd/system/file-processor.path
[Unit]
Description=Watch for files to process

[Path]
DirectoryNotEmpty=/var/spool/inbox
Unit=file-processor.service

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/file-processor.service
[Unit]
Description=Process incoming files

[Service]
Type=oneshot
ExecStart=/usr/local/bin/process-files.sh
User=processor
```

Script de traitement :
```bash
#!/bin/bash
for file in /var/spool/inbox/*; do
    [ -f "$file" ] || continue
    process_file "$file"
    mv "$file" /var/spool/processed/
done
```

Activation :
```bash
systemctl enable file-processor.path
systemctl start file-processor.path

# Déposer un fichier pour tester
touch /var/spool/inbox/test.txt

# Vérifier
journalctl -u file-processor.service
```

### Rechargement automatique de configuration

```ini
# /etc/systemd/system/nginx-config-watcher.path
[Unit]
Description=Watch Nginx Configuration

[Path]
PathChanged=/etc/nginx/nginx.conf
PathChanged=/etc/nginx/sites-enabled
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
ExecStart=/usr/bin/nginx -t
ExecStart=/usr/bin/systemctl reload nginx.service
```

### Déclenchement par fichier trigger

```ini
# /etc/systemd/system/backup-trigger.path
[Unit]
Description=Trigger backup when requested

[Path]
PathExists=/tmp/backup.trigger
Unit=backup-now.service

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/backup-now.service
[Unit]
Description=Run backup now

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
ExecStartPost=/usr/bin/rm -f /tmp/backup.trigger
```

Utilisation :
```bash
# Déclencher le backup
touch /tmp/backup.trigger
```

### Surveillance de logs avec glob

```ini
# /etc/systemd/system/error-detector.path
[Unit]
Description=Detect error log files

[Path]
PathExistsGlob=/var/log/app/error-*.log
Unit=error-alert.service
TriggerLimitIntervalSec=300s
TriggerLimitBurst=1

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/error-alert.service
[Unit]
Description=Send error alert

[Service]
Type=oneshot
ExecStart=/usr/local/bin/send-alert.sh "Error logs detected"
```

### Build automatique

```ini
# /etc/systemd/system/auto-build.path
[Unit]
Description=Watch source files for changes

[Path]
PathModified=/home/dev/project/src
Unit=auto-build.service
TriggerLimitIntervalSec=10s
TriggerLimitBurst=1

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/auto-build.service
[Unit]
Description=Build project

[Service]
Type=oneshot
WorkingDirectory=/home/dev/project
ExecStart=/usr/bin/make build
User=dev
```

### Surveillance multiple de fichiers

```ini
# /etc/systemd/system/config-watcher.path
[Unit]
Description=Watch multiple config files

[Path]
PathChanged=/etc/app/main.conf
PathChanged=/etc/app/database.conf
PathChanged=/etc/app/cache.conf
Unit=app-restart.service

[Install]
WantedBy=multi-user.target
```

## Gestion des path units

### Commandes de base

```bash
# Lister les path units
systemctl list-units --type=path
systemctl list-unit-files --type=path

# Démarrer la surveillance
systemctl start file-processor.path

# Activer au boot
systemctl enable file-processor.path

# Voir l'état
systemctl status file-processor.path

# Arrêter la surveillance
systemctl stop file-processor.path
```

### Voir les logs

```bash
# Logs du path unit
journalctl -u file-processor.path

# Logs du service déclenché
journalctl -u file-processor.service

# Les deux ensemble
journalctl -u file-processor.path -u file-processor.service
```

### Tester manuellement

```bash
# Démarrer le path
systemctl start file-processor.path

# Déclencher manuellement
touch /var/spool/inbox/test.txt

# Vérifier que le service s'est déclenché
systemctl status file-processor.service
```

## Différences PathChanged vs PathModified

**PathChanged** détecte :
- Modification du contenu
- Changement de permissions
- Changement de propriétaire
- Changement de timestamps
- Ajout/suppression de fichiers (pour répertoires)

**PathModified** détecte :
- Modification du contenu uniquement (pour fichiers)
- Ajout/suppression de fichiers (pour répertoires)

Utiliser `PathModified` pour éviter les faux positifs.

## Limitations

### inotify

Les path units utilisent inotify, qui a des limitations :

```bash
# Voir les limites actuelles
cat /proc/sys/fs/inotify/max_user_watches

# Augmenter si nécessaire
echo "fs.inotify.max_user_watches=524288" >> /etc/sysctl.conf
sysctl -p
```

### Fichiers réseau

inotify ne fonctionne pas bien avec NFS/CIFS. Pour ces cas, utiliser des timers avec vérification périodique.

### Polling

Si inotify n'est pas disponible, systemd utilise le polling (moins efficace).

## Cas d'usage avancés

### Hot-reload d'application

```ini
# /etc/systemd/system/app-config-watcher.path
[Unit]
Description=Application Config Watcher
PartOf=myapp.service

[Path]
PathModified=/etc/myapp/config.yaml
Unit=myapp.service

[Install]
WantedBy=multi-user.target
```

Le service sera redémarré automatiquement.

### Pipeline de traitement

```ini
# Stage 1: Détection
# /etc/systemd/system/stage1-detect.path
[Path]
DirectoryNotEmpty=/data/stage1
Unit=stage1-process.service

# Stage 2: Traitement
# /etc/systemd/system/stage2-detect.path
[Path]
DirectoryNotEmpty=/data/stage2
Unit=stage2-process.service
```

Crée un pipeline avec plusieurs étapes.

### Déploiement automatique

```ini
# /etc/systemd/system/auto-deploy.path
[Unit]
Description=Watch for deployment packages

[Path]
PathExistsGlob=/var/deploy/*.tar.gz
Unit=deploy-app.service
TriggerLimitIntervalSec=60s
TriggerLimitBurst=1

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/deploy-app.service
[Unit]
Description=Deploy application

[Service]
Type=oneshot
ExecStart=/usr/local/bin/deploy.sh
ExecStartPost=/usr/bin/mv /var/deploy/*.tar.gz /var/deploy/deployed/
```

## Debugging

### Le service ne se déclenche pas

Vérifications :

```bash
# Le path est-il actif ?
systemctl status myapp.path

# Vérifier les permissions
ls -la /path/surveillé

# Tester inotify manuellement
inotifywait -m /path/surveillé

# Vérifier les limites
cat /proc/sys/fs/inotify/max_user_watches
```

### Trop de déclenchements

```ini
[Path]
# Limiter le taux
TriggerLimitIntervalSec=60s
TriggerLimitBurst=3
```

### Logs verbeux

```bash
# Activer le debug pour systemd
systemctl log-level debug

# Vérifier les événements
journalctl -u myapp.path -f

# Remettre le niveau normal
systemctl log-level info
```

## Bonnes pratiques

1. **Utiliser PathModified** quand possible pour éviter les faux positifs
2. **Limiter les déclenchements** avec TriggerLimit*
3. **Type=oneshot** pour les services déclenchés
4. **Nettoyer après traitement** : Supprimer/déplacer les fichiers traités
5. **Tester** : Vérifier que le déclenchement fonctionne
6. **Documenter** : Expliquer clairement ce qui est surveillé
7. **Permissions** : Vérifier que systemd peut accéder au chemin
8. **Éviter les répertoires massifs** : inotify peut être limité

## Alternative : Timers

Pour certains cas, un timer avec vérification périodique peut être plus adapté :

```ini
# Au lieu d'un path unit, utiliser un timer
[Timer]
OnCalendar=*:0/5  # Toutes les 5 minutes
Persistent=true
```

Avantages :
- Fonctionne avec NFS/CIFS
- Pas de limite inotify
- Contrôle précis de la fréquence

Les path units sont idéaux pour réagir rapidement aux changements du système de fichiers, permettant des workflows automatiques et réactifs.
