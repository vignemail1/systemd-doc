# Device (.device)

Les unités `.device` représentent des périphériques matériels exposés par le système via udev. Contrairement aux autres types d'unités, elles sont **générées automatiquement** par systemd et ne sont généralement pas créées manuellement.

## Concept

Les device units permettent à systemd de :

- **Suivre** l'état des périphériques matériels
- **Créer des dépendances** entre services et matériel
- **Activer des services** quand un périphérique apparaît
- **Détecter** le branchement/débranchement de matériel

## Génération automatique

systemd-udevd génère automatiquement des unités `.device` pour chaque périphérique détecté :

```bash
# Lister les device units
systemctl list-units --type=device

# Exemples de devices
dev-sda.device
dev-sda1.device
dev-disk-by\x2duuid-xxx.device
dev-ttyS0.device
sys-devices-pci0000:00-xxx.device
```

## Nommage

Les noms suivent le chemin du périphérique dans `/dev` ou `/sys` :

```
/dev/sda → dev-sda.device
/dev/sda1 → dev-sda1.device
/dev/ttyUSB0 → dev-ttyUSB0.device
/dev/disk/by-uuid/xxx → dev-disk-by\x2duuid-xxx.device
```

Les `/` sont remplacés par `-` et les caractères spéciaux par `\xNN`.

## Voir les informations d'un device

```bash
# Statut d'un device
systemctl status dev-sda.device

# Propriétés complètes
systemctl show dev-sda.device

# Dépendances
systemctl list-dependencies dev-sda1.device
systemctl list-dependencies --reverse dev-sda1.device
```

## Utilisation avec d'autres unités

### Service dépendant d'un device

```ini
# /etc/systemd/system/usb-backup.service
[Unit]
Description=USB Backup Service
BindsTo=dev-disk-by\x2dlabel-BACKUP.device
After=dev-disk-by\x2dlabel-BACKUP.device

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup-to-usb.sh

[Install]
WantedBy=multi-user.target
```

**BindsTo** : Le service s'arrête si le device disparaît.

### Mount dépendant d'un device

```ini
# /etc/systemd/system/mnt-external.mount
[Unit]
Description=External Drive
BindsTo=dev-disk-by\x2duuid-xxx.device
After=dev-disk-by\x2duuid-xxx.device

[Mount]
What=/dev/disk/by-uuid/xxx
Where=/mnt/external
Type=ext4
Options=defaults

[Install]
WantedBy=multi-user.target
```

### Service activé par device (udev rule)

Plutôt que de référencer directement un device unit, utiliser une règle udev :

```bash
# /etc/udev/rules.d/99-usb-backup.rules
ACTION=="add", SUBSYSTEM=="block", ENV{ID_FS_LABEL}=="BACKUP", \
    TAG+="systemd", ENV{SYSTEMD_WANTS}="usb-backup.service"
```

Le service démarre automatiquement quand le device avec le label "BACKUP" est branché.

Recharger udev :
```bash
udevadm control --reload-rules
udevadm trigger
```

## Propriétés udev

Les device units héritent des propriétés udev :

```bash
# Voir les propriétés udev d'un device
udevadm info /dev/sda
udevadm info --query=property /dev/sda

# Exemples de propriétés
ID_SERIAL=XXXXX
ID_MODEL=Samsung_SSD
ID_FS_TYPE=ext4
ID_FS_UUID=xxx
ID_FS_LABEL=DATA
```

Ces propriétés peuvent être utilisées dans les règles udev.

## Cas d'usage

### Backup automatique sur branchement USB

**Règle udev** :
```bash
# /etc/udev/rules.d/99-backup-usb.rules
ACTION=="add", SUBSYSTEM=="block", ENV{ID_FS_LABEL}=="BACKUP_DISK", \
    TAG+="systemd", ENV{SYSTEMD_WANTS}="usb-backup@%k.service"
```

**Service template** :
```ini
# /etc/systemd/system/usb-backup@.service
[Unit]
Description=Backup to USB device %I
BindsTo=dev-%i.device
After=dev-%i.device

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh /dev/%I
ExecStartPost=/usr/bin/systemctl poweroff
```

### Surveillance de périphérique série

```ini
# /etc/systemd/system/serial-monitor.service
[Unit]
Description=Monitor Serial Port
BindsTo=dev-ttyUSB0.device
After=dev-ttyUSB0.device

[Service]
Type=simple
ExecStart=/usr/bin/screen /dev/ttyUSB0 115200
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Service pour imprimante

```ini
# /etc/systemd/system/printer-daemon.service
[Unit]
Description=Printer Daemon
BindsTo=dev-usb-lp0.device
After=dev-usb-lp0.device

[Service]
Type=simple
ExecStart=/usr/bin/printer-daemon
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Udev et systemd ensemble

### Tags systemd dans udev

Pour qu'udev communique avec systemd, utiliser le tag `systemd` :

```bash
TAG+="systemd"
```

### Variables d'environnement systemd

**SYSTEMD_WANTS** : Services à démarrer
```bash
ENV{SYSTEMD_WANTS}="myservice.service"
```

**SYSTEMD_USER_WANTS** : Services utilisateur
```bash
ENV{SYSTEMD_USER_WANTS}="user-service.service"
```

**SYSTEMD_ALIAS** : Alias pour le device
```bash
ENV{SYSTEMD_ALIAS}="/dev/mydevice"
```

**SYSTEMD_READY** : Marquer le device comme prêt
```bash
ENV{SYSTEMD_READY}="1"
```

### Exemple complet

```bash
# /etc/udev/rules.d/99-camera.rules
# Détecte une caméra USB et démarre un service
ACTION=="add", SUBSYSTEM=="video4linux", ATTRS{idVendor}=="046d", \
    TAG+="systemd", ENV{SYSTEMD_WANTS}="camera-manager.service"

ACTION=="remove", SUBSYSTEM=="video4linux", ATTRS{idVendor}=="046d", \
    TAG+="systemd"
```

```ini
# /etc/systemd/system/camera-manager.service
[Unit]
Description=Camera Manager
BindsTo=dev-video0.device
After=dev-video0.device

[Service]
Type=simple
ExecStart=/usr/local/bin/camera-manager
Restart=no
```

## Debugging

### Voir les événements udev

```bash
# Monitorer les événements udev en temps réel
udevadm monitor

# Avec propriétés
udevadm monitor --property

# Filtrer par subsystem
udevadm monitor --subsystem-match=block
```

### Tester une règle udev

```bash
# Tester sans appliquer
udevadm test /sys/class/block/sda

# Forcer le déclenchement
udevadm trigger --action=add /dev/sda

# Recharger les règles
udevadm control --reload-rules
```

### Vérifier le lien device-service

```bash
# Voir quel service dépend du device
systemctl list-dependencies --reverse dev-sda.device

# Logs du device
journalctl -u dev-sda.device
```

## Limitations

### Pas de configuration directe

On ne peut pas créer de fichiers `.device` manuellement. Ils sont générés par systemd-udevd.

### Noms volatiles

Les noms comme `sda`, `ttyUSB0` peuvent changer au reboot. Préférer :

- UUID : `/dev/disk/by-uuid/xxx`
- Label : `/dev/disk/by-label/BACKUP`
- Path : `/dev/disk/by-path/xxx`
- ID : `/dev/disk/by-id/xxx`

### Dépendances BindsTo

Utiliser `BindsTo=` plutôt que `Requires=` pour les devices :

```ini
# Bon
BindsTo=dev-sda.device

# Moins bon
Requires=dev-sda.device
```

`BindsTo` arrête le service si le device disparaît.

## Bonnes pratiques

1. **Utiliser udev rules** : Pour activer des services sur détection de device
2. **BindsTo pour matériel** : Toujours utiliser avec les devices
3. **Identifiants stables** : UUID, label plutôt que noms volatiles
4. **Tester les règles** : Avec `udevadm test` avant déploiement
5. **Documenter** : Expliquer quelle règle udev active quel service
6. **Logs** : Vérifier les logs systemd et udev ensemble

## Ressources

```bash
# Documentation udev
man udev
man systemd.device

# Exemples de règles
ls /lib/udev/rules.d/

# Informations device
lsblk
lsusb
lspci
```

Les device units permettent une intégration étroite entre la détection matérielle (udev) et la gestion des services (systemd), offrant des possibilités d'automatisation puissantes.
