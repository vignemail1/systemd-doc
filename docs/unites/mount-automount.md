# Mount et Automount

Les unités `.mount` et `.automount` gèrent le montage des systèmes de fichiers dans systemd. Elles offrent une alternative moderne au fichier `/etc/fstab` avec plus de contrôle et d'intégration.

## Mount Units (.mount)

Les unités `.mount` représentent un point de montage d'un système de fichiers.

### Nommage des unités mount

Le nom du fichier `.mount` **doit** correspondre exactement au chemin de montage, avec les `/` remplacés par des `-`.

**Exemples** :

| Point de montage | Nom du fichier |
| ------------------ | ---------------- |
| `/mnt/data` | `mnt-data.mount` |
| `/home` | `home.mount` |
| `/var/www` | `var-www.mount` |
| `/media/usb` | `media-usb.mount` |

### Structure d'un fichier .mount

```ini
[Unit]
Description=Data Storage Mount
Before=local-fs.target

[Mount]
What=/dev/sdb1
Where=/mnt/data
Type=ext4
Options=defaults,noatime

[Install]
WantedBy=local-fs.target
```text

## Section [Mount]

### Options obligatoires

**What**

: Périphérique, partition ou ressource à monter

```ini
# Périphérique
What=/dev/sdb1

# UUID (recommandé)
What=/dev/disk/by-uuid/12345678-1234-1234-1234-123456789012

# Label
What=/dev/disk/by-label/DATA

# Partage réseau
What=//server/share
What=server:/export/nfs
```text

**Where**

: Point de montage (doit correspondre au nom du fichier)

```ini
Where=/mnt/data
```text

**Type**

: Type de système de fichiers

```ini
Type=ext4
Type=xfs
Type=btrfs
Type=vfat
Type=ntfs
Type=cifs
Type=nfs
Type=tmpfs
```text

### Options facultatives

**Options**

: Options de montage (comme dans fstab)

```ini
Options=defaults,noatime,nodiratime
Options=ro,noexec,nosuid
Options=uid=1000,gid=1000,umask=022
```text

**SloppyOptions**

: Ignorer les options inconnues

```ini
SloppyOptions=yes
```text

**DirectoryMode**

: Permissions du point de montage s'il doit être créé

```ini
DirectoryMode=0755
```text

**TimeoutSec**

: Timeout pour le montage

```ini
TimeoutSec=30s
```text

## Exemples de mount units

### Partition de données

```ini
# /etc/systemd/system/mnt-data.mount
[Unit]
Description=Data Partition
Before=local-fs.target

[Mount]
What=/dev/disk/by-uuid/abcd1234-5678-90ef-ghij-klmnopqrstuv
Where=/mnt/data
Type=ext4
Options=defaults,noatime

[Install]
WantedBy=local-fs.target
```text

Activation :

```bash
systemctl enable mnt-data.mount
systemctl start mnt-data.mount
```text

### Partage NFS

```ini
# /etc/systemd/system/mnt-nfs.mount
[Unit]
Description=NFS Share
After=network-online.target
Wants=network-online.target

[Mount]
What=192.168.1.100:/export/share
Where=/mnt/nfs
Type=nfs
Options=defaults,_netdev,noatime

[Install]
WantedBy=remote-fs.target
```text

**Option importante** : `_netdev` indique que c'est un système de fichiers réseau.

### Partage CIFS/SMB

```ini
# /etc/systemd/system/mnt-samba.mount
[Unit]
Description=Samba Share
After=network-online.target
Wants=network-online.target

[Mount]
What=//server.example.com/share
Where=/mnt/samba
Type=cifs
Options=credentials=/etc/samba/credentials,uid=1000,gid=1000,_netdev

[Install]
WantedBy=remote-fs.target
```text

Fichier de credentials (`/etc/samba/credentials`) :

```text
username=myuser
password=mypassword
domain=WORKGROUP
```text

```bash
chmod 600 /etc/samba/credentials
```text

### tmpfs (RAM disk)

```ini
# /etc/systemd/system/tmp-cache.mount
[Unit]
Description=Temporary Cache in RAM

[Mount]
What=tmpfs
Where=/tmp/cache
Type=tmpfs
Options=size=1G,mode=1777

[Install]
WantedBy=local-fs.target
```text

### Bind mount

```ini
# /etc/systemd/system/var-www-logs.mount
[Unit]
Description=Bind mount for web logs
After=var-www.mount
Requires=var-www.mount

[Mount]
What=/mnt/data/logs
Where=/var/www/logs
Type=none
Options=bind

[Install]
WantedBy=local-fs.target
```text

## Automount Units (.automount)

Les unités `.automount` montent automatiquement un système de fichiers lors du premier accès.

### Principe

1. systemd crée un point de montage vide
2. L'utilisateur accède au répertoire
3. systemd monte automatiquement le système de fichiers
4. Optionnel : démontage après inactivité

### Avantages

- **Boot plus rapide** : Pas de montage au démarrage
- **Économie de ressources** : Montage à la demande
- **Systèmes lents** : NFS, partages réseau ne ralentissent pas le boot

### Structure d'un automount

```ini
# /etc/systemd/system/mnt-data.automount
[Unit]
Description=Automount Data Partition

[Automount]
Where=/mnt/data
TimeoutIdleSec=300

[Install]
WantedBy=local-fs.target
```text

**Important** : Doit être accompagné d'une unité `.mount` correspondante.

### Options [Automount]

**Where**

: Point de montage (identique au .mount)

```ini
Where=/mnt/data
```text

**DirectoryMode**

: Permissions du point de montage

```ini
DirectoryMode=0755
```text

**TimeoutIdleSec**

: Démonte après inactivité (optionnel)

```ini
TimeoutIdleSec=300   # 5 minutes
TimeoutIdleSec=0     # Jamais démonter (défaut)
```text

## Exemple complet automount

### NFS avec automount

```ini
# /etc/systemd/system/mnt-nfs.mount
[Unit]
Description=NFS Share
After=network-online.target

[Mount]
What=server:/export/data
Where=/mnt/nfs
Type=nfs
Options=defaults,_netdev,noatime
```text

```ini
# /etc/systemd/system/mnt-nfs.automount
[Unit]
Description=Automount NFS Share

[Automount]
Where=/mnt/nfs
TimeoutIdleSec=600

[Install]
WantedBy=remote-fs.target
```text

Activation :

```bash
# N'activer QUE l'automount
systemctl enable mnt-nfs.automount
systemctl start mnt-nfs.automount

# Le .mount sera activé automatiquement à l'accès
```text

### Données externes avec automount

```ini
# /etc/systemd/system/mnt-backup.mount
[Unit]
Description=External Backup Drive

[Mount]
What=/dev/disk/by-uuid/external-backup-uuid
Where=/mnt/backup
Type=ext4
Options=defaults,noatime
```text

```ini
# /etc/systemd/system/mnt-backup.automount
[Unit]
Description=Automount Backup Drive

[Automount]
Where=/mnt/backup
TimeoutIdleSec=600

[Install]
WantedBy=local-fs.target
```text

## Gestion des mounts

### Commandes de base

```bash
# Lister tous les mounts
systemctl list-units --type=mount

# Monter
systemctl start mnt-data.mount

# Démonter
systemctl stop mnt-data.mount

# Activer au boot
systemctl enable mnt-data.mount

# Voir l'état
systemctl status mnt-data.mount

# Recharger si modification
systemctl daemon-reload
systemctl restart mnt-data.mount
```text

### Commandes automount

```bash
# Lister les automounts
systemctl list-units --type=automount

# Activer un automount
systemctl enable mnt-data.automount
systemctl start mnt-data.automount

# Désactiver
systemctl stop mnt-data.automount
systemctl disable mnt-data.automount
```text

## Conversion depuis fstab

### fstab traditionnel

```text
# /etc/fstab
UUID=abc-123 /mnt/data ext4 defaults,noatime 0 2
//server/share /mnt/smb cifs credentials=/etc/creds 0 0
```text

### Équivalent systemd

```ini
# /etc/systemd/system/mnt-data.mount
[Unit]
Description=Data Partition

[Mount]
What=/dev/disk/by-uuid/abc-123
Where=/mnt/data
Type=ext4
Options=defaults,noatime

[Install]
WantedBy=local-fs.target
```text

```ini
# /etc/systemd/system/mnt-smb.mount
[Unit]
Description=SMB Share
After=network-online.target

[Mount]
What=//server/share
Where=/mnt/smb
Type=cifs
Options=credentials=/etc/creds,_netdev

[Install]
WantedBy=remote-fs.target
```text

### Outil de conversion

systemd peut générer des units depuis fstab :

```bash
# systemd génère automatiquement des .mount depuis /etc/fstab
# Visible avec:
systemctl list-units --type=mount --all
```text

## Dépendances

### Monter avant un service

```ini
# myapp.service
[Unit]
Description=My Application
After=mnt-data.mount
Requires=mnt-data.mount

[Service]
ExecStart=/usr/bin/myapp
```text

### Cascade de montages

```ini
# /etc/systemd/system/mnt-data.mount
[Unit]
Description=Data Partition

[Mount]
What=/dev/sdb1
Where=/mnt/data
Type=ext4
```text

```ini
# /etc/systemd/system/mnt-data-www.mount
[Unit]
Description=WWW Bind Mount
After=mnt-data.mount
Requires=mnt-data.mount

[Mount]
What=/mnt/data/www
Where=/var/www
Type=none
Options=bind
```text

## Sécurité

### Options de montage sécurisées

```ini
[Mount]
Options=nodev,nosuid,noexec
```text

**nodev**

: Pas de fichiers spéciaux de périphériques

**nosuid**

: Ignorer les bits SUID/SGID

**noexec**

: Pas d'exécution de binaires

### Montage en lecture seule

```ini
[Mount]
Options=ro
```text

### Restrictions d'accès

```ini
[Mount]
Options=uid=1000,gid=1000,umask=077
```text

## Dépannage

### Mount échoue

```bash
# Voir les logs
journalctl -u mnt-data.mount

# Tester le montage manuellement
mount -t ext4 /dev/sdb1 /mnt/data

# Vérifier le périphérique
lsblk
blkid

# Vérifier les permissions
ls -ld /mnt/data
```text

### Automount ne fonctionne pas

```bash
# L'automount est-il actif ?
systemctl status mnt-data.automount

# Le .mount existe ?
systemctl cat mnt-data.mount

# Tester l'accès
ls /mnt/data

# Logs
journalctl -u mnt-data.automount
journalctl -u mnt-data.mount
```text

### Démontage impossible

```bash
# Voir ce qui utilise le mount
lsof /mnt/data
fuser -vm /mnt/data

# Tuer les processus
fuser -km /mnt/data

# Forcer le démontage
umount -l /mnt/data  # Lazy unmount
```text

## Bonnes pratiques

1. **Utiliser UUID** plutôt que /dev/sdX

   ```ini
   What=/dev/disk/by-uuid/...
```text

2. **Option _netdev** pour montages réseau

   ```ini
   Options=_netdev
```text

3. **Automount pour ressources lentes**
   - NFS, CIFS
   - Disques externes
   - Ressources rarement utilisées

4. **Dépendances explicites**

   ```ini
   After=network-online.target
   Wants=network-online.target
```text

5. **Timeout raisonnable**

   ```ini
   TimeoutSec=30s
```text

6. **Documenter**

   ```ini
   [Unit]
   Description=Clear description of what is mounted
```text

Les mount et automount units offrent une gestion moderne et flexible des systèmes de fichiers, avec une meilleure intégration dans systemd que le traditionnel /etc/fstab.
