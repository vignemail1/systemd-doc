# Mount et Automount

Les unités `.mount` et `.automount` permettent à systemd de gérer les systèmes de fichiers montés, remplaçant ou complétant `/etc/fstab`.

## Mount (.mount)

Les unités `.mount` définissent des points de montage gérés par systemd.

### Pourquoi utiliser .mount ?

- **Intégration systemd** : Dépendances explicites avec d'autres services
- **Supervision** : Détection automatique des problèmes de montage
- **Flexibilité** : Conditions, timeouts, retry
- **Logs structurés** : Dans journald
- **Activation à la demande** : Avec automount

### Convention de nommage

Le nom du fichier `.mount` **doit** correspondre au chemin de montage :

```
/data/backup → data-backup.mount
/mnt/nfs/share → mnt-nfs-share.mount
/home → home.mount
```

Les `/` deviennent des `-`, sauf le premier `/` qui est omis.

### Structure d'un fichier .mount

```ini
[Unit]
Description=Data Backup Mount
After=network-online.target
Wants=network-online.target

[Mount]
What=/dev/sdb1
Where=/data/backup
Type=ext4
Options=defaults,noatime

[Install]
WantedBy=multi-user.target
```

## Section [Mount]

### Options principales

**What**
: Device, UUID, ou chemin source (obligatoire)

```ini
# Device
What=/dev/sdb1

# UUID
What=UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Label
What=LABEL=backup

# NFS
What=server.example.com:/export/data

# CIFS/SMB
What=//server/share
```

**Where**
: Point de montage (obligatoire)

```ini
Where=/mnt/data
```

**Type**
: Type de système de fichiers

```ini
Type=ext4
Type=xfs
Type=nfs
Type=cifs
Type=tmpfs
Type=btrfs
```

**Options**
: Options de montage (comme dans fstab)

```ini
Options=defaults,noatime,nodiratime
Options=ro,noexec,nosuid
Options=rw,user,auto
```

### Options avancées

**DirectoryMode**
: Permissions du point de montage s'il doit être créé

```ini
DirectoryMode=0755
```

**TimeoutSec**
: Timeout pour le montage

```ini
TimeoutSec=30s
```

**SloppyOptions**
: Ignorer les options non reconnues

```ini
SloppyOptions=yes
```

**LazyUnmount**
: Démontage lazy (détache immédiatement, libère à la fermeture)

```ini
LazyUnmount=yes
```

**ForceUnmount**
: Force le démontage même si occupé

```ini
ForceUnmount=yes
```

## Exemples de .mount

### Montage disque local

```ini
# /etc/systemd/system/data-backup.mount
[Unit]
Description=Backup Data Partition

[Mount]
What=UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
Where=/data/backup
Type=ext4
Options=defaults,noatime

[Install]
WantedBy=multi-user.target
```

Activation :
```bash
systemctl enable data-backup.mount
systemctl start data-backup.mount
```

### Montage NFS

```ini
# /etc/systemd/system/mnt-nfs-share.mount
[Unit]
Description=NFS Share from File Server
After=network-online.target
Wants=network-online.target

[Mount]
What=fileserver.lan:/export/shared
Where=/mnt/nfs/share
Type=nfs
Options=_netdev,nfsvers=4,rw
TimeoutSec=30

[Install]
WantedBy=multi-user.target
```

!!! note "Option _netdev"
    L'option `_netdev` indique que le montage nécessite le réseau.

### Montage CIFS/SMB

```ini
# /etc/systemd/system/mnt-smb-documents.mount
[Unit]
Description=Windows Share - Documents
After=network-online.target
Wants=network-online.target

[Mount]
What=//windowsserver/documents
Where=/mnt/smb/documents
Type=cifs
Options=credentials=/etc/smb-credentials,uid=1000,gid=1000,_netdev

[Install]
WantedBy=multi-user.target
```

Fichier credentials (`/etc/smb-credentials`) :
```
username=monuser
password=monpass
domain=DOMAIN
```

Permissions :
```bash
chmod 600 /etc/smb-credentials
```

### Montage tmpfs

```ini
# /etc/systemd/system/tmp-app-cache.mount
[Unit]
Description=Application Cache in RAM

[Mount]
What=tmpfs
Where=/tmp/app-cache
Type=tmpfs
Options=size=1G,mode=1777

[Install]
WantedBy=multi-user.target
```

### Montage avec dépendances

```ini
# /etc/systemd/system/var-lib-postgresql.mount
[Unit]
Description=PostgreSQL Data Directory
Before=postgresql.service

[Mount]
What=/dev/mapper/vg0-postgres
Where=/var/lib/postgresql
Type=ext4
Options=defaults,noatime

[Install]
RequiredBy=postgresql.service
```

PostgreSQL ne démarrera que si le montage réussit.

## Automount (.automount)

Les unités `.automount` permettent le montage automatique à la demande lors du premier accès.

### Avantages

- **Boot plus rapide** : Les filesystems ne sont pas montés au démarrage
- **Ressources** : Économise les ressources pour les montages rarement utilisés
- **Réseau** : Évite les timeouts au boot pour les montages réseau
- **Transparence** : Le montage se fait automatiquement à l'accès

### Convention de nommage

Même règle que `.mount` :

```
/data/backup → data-backup.automount
```

### Structure d'un .automount

```ini
[Unit]
Description=Automount for Backup Data

[Automount]
Where=/data/backup
TimeoutIdleSec=300

[Install]
WantedBy=multi-user.target
```

## Section [Automount]

**Where**
: Point de montage (doit correspondre au .mount associé)

```ini
Where=/data/backup
```

**DirectoryMode**
: Permissions du point de montage

```ini
DirectoryMode=0755
```

**TimeoutIdleSec**
: Délai avant démontage automatique si inactif

```ini
TimeoutIdleSec=300  # 5 minutes
TimeoutIdleSec=0    # Ne jamais démonter auto
```

## Exemples d'automount

### Automount NFS

```ini
# /etc/systemd/system/mnt-nfs-share.automount
[Unit]
Description=Automount NFS Share

[Automount]
Where=/mnt/nfs/share
TimeoutIdleSec=600

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/mnt-nfs-share.mount
[Unit]
Description=NFS Share
After=network-online.target

[Mount]
What=fileserver:/export/shared
Where=/mnt/nfs/share
Type=nfs
Options=_netdev,nfsvers=4
```

Activation :
```bash
# Activer l'automount (pas le mount)
systemctl enable mnt-nfs-share.automount
systemctl start mnt-nfs-share.automount

# Le montage se fera au premier accès
ls /mnt/nfs/share  # Déclenche le montage
```

### Automount avec timeout court

```ini
# /etc/systemd/system/mnt-usb-backup.automount
[Unit]
Description=USB Backup Automount

[Automount]
Where=/mnt/usb/backup
TimeoutIdleSec=60  # Démonte après 1 minute d'inactivité

[Install]
WantedBy=multi-user.target
```

Idéal pour des périphériques USB ou disques externes.

## Gestion des montages

### Commandes de base

```bash
# Lister les montages systemd
systemctl list-units --type=mount

# Lister les automounts
systemctl list-units --type=automount

# Démarrer un montage
systemctl start data-backup.mount

# Arrêter (démonter)
systemctl stop data-backup.mount

# Statut
systemctl status data-backup.mount

# Recharger après modification
systemctl daemon-reload
systemctl restart data-backup.mount
```

### Forcer un démontage

```bash
# Démontage normal
systemctl stop data-backup.mount

# Si occupé, tuer les processus
fuser -km /data/backup
systemctl stop data-backup.mount
```

## Migration depuis /etc/fstab

### Entrée fstab

```
UUID=xxx  /data/backup  ext4  defaults,noatime  0  2
```

### Équivalent systemd

```ini
# /etc/systemd/system/data-backup.mount
[Unit]
Description=Backup Data

[Mount]
What=UUID=xxx
Where=/data/backup
Type=ext4
Options=defaults,noatime

[Install]
WantedBy=multi-user.target
```

On peut conserver les deux : systemd lit aussi `/etc/fstab`.

## Cas d'usage avancés

### Montage conditionnel

```ini
# /etc/systemd/system/mnt-external.mount
[Unit]
Description=External Drive
ConditionPathExists=/dev/disk/by-label/EXTERNAL

[Mount]
What=LABEL=EXTERNAL
Where=/mnt/external
Type=ext4
Options=defaults

[Install]
WantedBy=multi-user.target
```

Ne monte que si le disque est présent.

### Montage avec retry

```ini
# /etc/systemd/system/mnt-nfs-data.mount
[Unit]
Description=NFS Data Mount
After=network-online.target

[Mount]
What=server:/data
Where=/mnt/nfs/data
Type=nfs
Options=_netdev,soft,timeo=30,retrans=3

[Service]
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### Montage readonly en cas d'erreur

```ini
[Mount]
What=/dev/sdb1
Where=/data/critical
Type=ext4
Options=errors=remount-ro
```

## Debugging

### Voir les logs de montage

```bash
journalctl -u data-backup.mount
journalctl -u data-backup.mount -f
journalctl -b -u '*.mount'
```

### Vérifier la configuration

```bash
systemd-analyze verify data-backup.mount
```

### Tester manuellement

```bash
# Vérifier que le montage fonctionne
mount -t ext4 /dev/sdb1 /data/backup

# Puis convertir en unit systemd
```

### Problèmes courants

**Timeout au boot** :
```ini
[Mount]
TimeoutSec=30s

[Unit]
# Pour NFS/CIFS
After=network-online.target
```

**Démontage impossible** :
```bash
# Trouver qui utilise
lsof +D /data/backup
fuser -v /data/backup

# Tuer les processus
fuser -km /data/backup
```

**Automount ne fonctionne pas** :
```bash
# Vérifier que l'automount est actif
systemctl status data-backup.automount

# Pas le .mount
systemctl status data-backup.mount  # Doit être inactif
```

## Bonnes pratiques

1. **Utiliser UUID** : Plus fiable que les noms de devices
2. **_netdev pour réseau** : Toujours utiliser pour NFS/CIFS
3. **Timeout raisonnable** : Éviter que le boot se bloque
4. **Documenter** : Description claire de ce qui est monté
5. **Tester** : Valider le montage avant d'activer au boot
6. **Automount pour réseau** : Préférer automount pour les montages réseau
7. **Credentials sécurisés** : Protéger les fichiers de credentials (chmod 600)

Les unités mount et automount offrent une gestion moderne et flexible des systèmes de fichiers, bien intégrée avec le reste de systemd.
