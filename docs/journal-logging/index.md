# Journal et logging

Le journal systemd (journald) est un système de logging centralisé qui collecte et stocke les logs de manière structurée. Il remplace ou complète syslog avec des fonctionnalités avancées.

## Architecture du journal

### Composants

- **systemd-journald** : Démon de collecte des logs
- **journalctl** : Outil de consultation
- **systemd-journal-remote** : Réception de logs distants
- **systemd-journal-upload** : Envoi de logs vers un serveur
- **systemd-journal-gatewayd** : API HTTP pour les logs

### Sources de logs

journald collecte les logs depuis :

- **stdout/stderr** des services systemd
- **syslog** (socket /dev/log)
- **Journal natif** (API sd_journal)
- **Messages noyau** (kmsg)
- **Audit** du noyau

### Stockage

Les logs sont stockés dans :

- `/run/journal/` : Volatile (RAM, perdu au reboot)
- `/var/log/journal/` : Persistant (disque)

Par défaut, si `/var/log/journal/` n'existe pas, les logs sont volatiles.

## Utilisation de journalctl

### Commandes de base

```bash
# Tous les logs
journalctl

# Logs depuis le dernier boot
journalctl -b

# Logs du boot précédent
journalctl -b -1

# Liste des boots
journalctl --list-boots

# Logs en temps réel (comme tail -f)
journalctl -f

# Dernières 50 lignes
journalctl -n 50
```text

### Filtrer par unité

```bash
# Logs d'un service spécifique
journalctl -u nginx.service

# Plusieurs services
journalctl -u nginx.service -u php-fpm.service

# Suivre un service
journalctl -u nginx.service -f

# Avec priorité
journalctl -u nginx.service -p err
```text

### Filtrer par temps

```bash
# Depuis une date
journalctl --since "2024-02-09 10:00:00"
journalctl --since "1 hour ago"
journalctl --since "yesterday"
journalctl --since "2 days ago"
journalctl --since "10 minutes ago"

# Jusqu'à une date
journalctl --until "2024-02-09 12:00:00"
journalctl --until "30 minutes ago"

# Période
journalctl --since "2024-02-09 08:00" --until "2024-02-09 18:00"
journalctl --since "1 hour ago" --until "30 minutes ago"
```text

### Filtrer par priorité

```bash
# Par niveau de sévérité
journalctl -p err        # Erreurs et plus grave
journalctl -p warning    # Warnings et plus grave
journalctl -p info       # Info et plus grave
journalctl -p debug      # Tous les messages

# Niveaux de priorité (syslog)
# 0: emerg (urgence)
# 1: alert (alerte)
# 2: crit (critique)
# 3: err (erreur)
# 4: warning (avertissement)
# 5: notice (notification)
# 6: info (information)
# 7: debug (débogage)
```text

### Filtrer par processus

```bash
# Par PID
journalctl _PID=1234

# Par nom de commande
journalctl _COMM=nginx

# Par UID
journalctl _UID=1000

# Par GID
journalctl _GID=1000
```text

### Filtrer par champs

```bash
# Identifier syslog
journalctl SYSLOG_IDENTIFIER=sshd

# Hostname
journalctl _HOSTNAME=server01

# Transport
journalctl _TRANSPORT=kernel
journalctl _TRANSPORT=syslog
journalctl _TRANSPORT=journal

# Combiner plusieurs filtres
journalctl _SYSTEMD_UNIT=nginx.service PRIORITY=3
```text

## Formats de sortie

### Format par défaut (short)

```bash
journalctl -o short
# Fév 09 14:30:25 server sshd[1234]: Accepted password for user
```text

### Format détaillé

```bash
# Verbose (tous les champs)
journalctl -o verbose

# JSON (une ligne)
journalctl -o json

# JSON (pretty print)
journalctl -o json-pretty

# Export binaire
journalctl -o export

# Format cat (juste le message)
journalctl -o cat
```text

### Exemples de formats

```bash
# Format court avec microsecondes
journalctl -o short-precise

# Format court ISO 8601
journalctl -o short-iso

# Format court ISO avec microsecondes
journalctl -o short-iso-precise

# Format court monotonic
journalctl -o short-monotonic
```text

## Recherche et filtrage avancé

### Grep dans les logs

```bash
# Recherche simple
journalctl | grep "error"

# Recherche insensible à la casse
journalctl | grep -i "error"

# Grep avec contexte
journalctl -u nginx.service | grep -C 5 "error"

# Utiliser --grep de journalctl (plus efficace)
journalctl --grep="error" --case-sensitive=false
```text

### Recherche par motif

```bash
# Expressions régulières
journalctl --grep="(error|fail|critical)"

# Inverser la recherche
journalctl --grep="error" --grep-invert
```text

### Lister les valeurs d'un champ

```bash
# Toutes les unités ayant logé
journalctl -F _SYSTEMD_UNIT

# Tous les PIDs
journalctl -F _PID

# Tous les identifiants syslog
journalctl -F SYSLOG_IDENTIFIER

# Tous les hostnames
journalctl -F _HOSTNAME
```text

## Configuration du journal

### Fichier de configuration

Fichier principal : `/etc/systemd/journald.conf`

```ini
[Journal]
# Stockage
Storage=persistent       # persistent, volatile, auto, none
Compress=yes            # Compresser les logs
Seal=yes                # Scellement cryptographique

# Limites de taille
SystemMaxUse=4G         # Utilisation max sur disque
SystemKeepFree=1G       # Espace libre min à garder
SystemMaxFileSize=128M  # Taille max par fichier journal
SystemMaxFiles=100      # Nombre max de fichiers

# Limites runtime (/run)
RuntimeMaxUse=256M
RuntimeKeepFree=512M
RuntimeMaxFileSize=64M
RuntimeMaxFiles=10

# Rotation
MaxRetentionSec=1month  # Garder 1 mois
MaxFileSec=1week        # Rotation hebdomadaire

# Forward vers syslog
ForwardToSyslog=no
ForwardToKMsg=no
ForwardToConsole=no
ForwardToWall=yes       # Messages critiques sur tous les terminaux

# Niveau maximum
MaxLevelStore=debug     # Tout stocker
MaxLevelSyslog=debug
MaxLevelKMsg=notice
MaxLevelConsole=info
MaxLevelWall=emerg

# Rate limiting
RateLimitIntervalSec=30s
RateLimitBurst=10000
```text

Appliquer les changements :

```bash
sudo systemctl restart systemd-journald
```text

### Activer la persistance

```bash
# Créer le répertoire
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal

# Redémarrer journald
sudo systemctl restart systemd-journald

# Vérifier
journalctl --disk-usage
```text

## Gestion de l'espace disque

### Voir l'utilisation

```bash
# Utilisation totale
journalctl --disk-usage

# Par fichier journal
ls -lh /var/log/journal/*/

# Statistiques détaillées
journalctl --header
```text

### Nettoyer les anciens logs

```bash
# Supprimer logs plus vieux que X
sudo journalctl --vacuum-time=2weeks
sudo journalctl --vacuum-time=30d
sudo journalctl --vacuum-time=1month

# Limiter la taille totale
sudo journalctl --vacuum-size=1G
sudo journalctl --vacuum-size=500M

# Limiter le nombre de fichiers
sudo journalctl --vacuum-files=10
```text

### Rotation manuelle

```bash
# Forcer une rotation
sudo systemctl kill --signal=SIGUSR2 systemd-journald

# Ou
sudo journalctl --rotate
```text

## Vérification et maintenance

### Vérifier l'intégrité

```bash
# Vérifier tous les fichiers
sudo journalctl --verify

# Vérifier un fichier spécifique
sudo journalctl --verify --file=/var/log/journal/xxx/system.journal
```text

### Diagnostics

```bash
# Statut du journal
systemctl status systemd-journald

# Configuration effective
journalctl --header

# Voir les warnings
journalctl -u systemd-journald -p warning
```text

## Export et sauvegarde

### Exporter vers un fichier

```bash
# Format texte
journalctl -u nginx.service > nginx.log

# Format JSON
journalctl -u nginx.service -o json > nginx.json

# Export binaire (pour import)
journalctl -o export > journal-export.bin
```text

### Sauvegarder les logs

```bash
# Copier les fichiers journal
sudo cp -r /var/log/journal/ /backup/journal-$(date +%Y%m%d)/

# Export pour archivage
sudo journalctl -o export | gzip > journal-backup-$(date +%Y%m%d).gz
```text

### Importer un journal

```bash
# Restaurer depuis export
sudo systemd-journal-remote -o /var/log/journal/remote/ \

  --split-mode=host < journal-export.bin

```text

## Logs centralisés

### Envoyer vers un serveur distant

Configuration `/etc/systemd/journal-upload.conf` :

```ini
[Upload]
URL=https://log-server.example.com:19532
ServerKeyFile=/etc/ssl/private/journal-upload.key
ServerCertificateFile=/etc/ssl/certs/journal-upload.pem
TrustedCertificateFile=/etc/ssl/certs/ca-bundle.crt
```text

```bash
sudo systemctl enable systemd-journal-upload
sudo systemctl start systemd-journal-upload
```text

### Recevoir des logs distants

Configuration `/etc/systemd/journal-remote.conf` :

```ini
[Remote]
Seal=yes
SplitMode=host
```text

```bash
sudo systemctl enable systemd-journal-remote.socket
sudo systemctl start systemd-journal-remote.socket
```text

## Logs structurés

### Écrire dans le journal (shell)

```bash
# Avec logger
logger -t myapp "Message de test"

# Avec systemd-cat
echo "Message" | systemd-cat -t myapp -p info

# Exécuter une commande et capturer sa sortie
systemd-cat -t backup /usr/local/bin/backup.sh
```text

### Écrire depuis un script

```bash
#!/bin/bash
# Script avec logging journal

log() {
    echo "<$1>$2" | systemd-cat -t myscript
}

log 6 "Script démarré"  # Info
log 3 "Erreur détectée"  # Error
log 6 "Script terminé"  # Info
```text

### API native (C, Python, etc.)

Python avec systemd :

```python
from systemd import journal

# Log simple
journal.send("Message de test")

# Log avec champs
journal.send(
    "Application démarrée",
    PRIORITY=journal.LOG_INFO,
    SYSLOG_IDENTIFIER="myapp",
    CUSTOM_FIELD="valeur"
)
```text

## Analyse et monitoring

### Statistiques

```bash
# Comptage de messages
journalctl --since today | wc -l

# Comptage par unité
journalctl -o json | jq -r '._SYSTEMD_UNIT' | sort | uniq -c | sort -rn

# Top 10 des services les plus verbeux
journalctl --since today -o json | \
  jq -r '._SYSTEMD_UNIT' | \
  sort | uniq -c | sort -rn | head -10
```text

### Détecter les erreurs

```bash
# Toutes les erreurs aujourd'hui
journalctl --since today -p err

# Erreurs par service
journalctl --since today -p err -o json | \
  jq -r '._SYSTEMD_UNIT' | sort | uniq -c | sort -rn

# Services en échec
systemctl --failed
```text

### Monitoring continu

```bash
# Surveiller les erreurs
journalctl -f -p err

# Surveiller plusieurs services
journalctl -f -u nginx -u mysql -u redis

# Alertes personnalisées
journalctl -f | grep -i --line-buffered "error" | \
  while read line; do
    notify-send "Erreur détectée" "$line"
  done
```text

## Bonnes pratiques

1. **Activer la persistance**

   ```bash
   sudo mkdir -p /var/log/journal
```text

2. **Définir des limites raisonnables**

   ```ini
   SystemMaxUse=2G
   MaxRetentionSec=1month
```text

3. **Utiliser des identifiants syslog clairs**

   ```ini
   [Service]
   SyslogIdentifier=myapp
```text

4. **Structurer les logs**

   ```python
   journal.send("User login", USER_ID=user_id, IP=ip_addr)
```text

5. **Nettoyer régulièrement**

   ```bash
   # Cron hebdomadaire
   0 2 * * 0 journalctl --vacuum-time=30d
```text

6. **Monitorer l'utilisation**

   ```bash
   journalctl --disk-usage
```text

7. **Sauvegarder les logs importants**

   ```bash
   journalctl -u production.service > backup.log
```text

Le journal systemd offre un système de logging puissant et flexible, essentiel pour le débogage et la surveillance des systèmes Linux modernes.
