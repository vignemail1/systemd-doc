# Device Units (.device)

Les unités `.device` représentent des périphériques matériels exposés par le noyau Linux via udev. Elles sont générées automatiquement par systemd et permettent de déclencher des services lors de la connexion/déconnexion de matériel.

## Principe

Les device units sont **générées automatiquement** par systemd-udevd à partir des événements udev. Vous ne créez généralement **pas** de fichiers `.device` manuellement.

### Fonctionnement

1. Un périphérique est connecté/déconnecté
2. Le noyau génère un événement udev
3. systemd-udevd crée/supprime un device unit
4. Les services qui dépendent du périphérique sont activés/désactivés

## Nommage des device units

Les device units sont nommés d'après le chemin sysfs du périphérique :

```
/sys/devices/... → sys-devices-....device
/dev/sda → dev-sda.device
/dev/disk/by-uuid/... → dev-disk-by\x2duuid-....device
```

Les caractères spéciaux sont échappés avec `\xNN` (code hexadécimal).

## Lister les device units

```bash
# Tous les devices actifs
systemctl list-units --type=device

# Tous les devices (actifs et inactifs)
systemctl list-units --type=device --all

# Rechercher un device spécifique
systemctl list-units --type=device | grep sda
```

Exemple de sortie :
```
dev-sda.device           loaded active plugged Samsung_SSD
dev-sda1.device          loaded active plugged Samsung_SSD 1
dev-disk-by\x2duuid-...  loaded active plugged Samsung_SSD
```

## Inspecter un device unit

```bash
# Voir les propriétés
systemctl status dev-sda.device
systemctl show dev-sda.device

# Voir les dépendances
systemctl list-dependencies dev-sda.device
systemctl list-dependencies --reverse dev-sda.device
```

Propriétés intéressantes :
- `SysFSPath` : Chemin dans /sys
- `DeviceNode` : Chemin dans /dev (si applicable)
- `Following` : Liens vers d'autres noms du même device

## Dépendances sur des devices

Les services peuvent dépendre de périphériques spécifiques :

### Par chemin /dev

```ini
# myapp.service
[Unit]
Description=Application requiring USB device
BindsTo=dev-ttyUSB0.device
After=dev-ttyUSB0.device

[Service]
ExecStart=/usr/bin/myapp --device /dev/ttyUSB0

[Install]
WantedBy=multi-user.target
```

**BindsTo** : Le service s'arrête automatiquement si le device disparaît.

### Par UUID

```ini
[Unit]
Description=Service requiring specific disk
Requires=dev-disk-by\x2duuid-12345678.device
After=dev-disk-by\x2duuid-12345678.device
```

### Par label

```ini
[Unit]
Requires=dev-disk-by\x2dlabel-BACKUP.device
After=dev-disk-by\x2dlabel-BACKUP.device
```

## Obtenir le nom d'un device unit

### Avec systemd-escape

```bash
# Convertir un chemin en nom d'unité
systemd-escape -p --suffix=device /dev/sda
# Output: dev-sda.device

systemd-escape -p --suffix=device /dev/disk/by-uuid/abc-123
# Output: dev-disk-by\x2duuid-abc\x2d123.device
```

### Depuis udevadm

```bash
# Informations udev complètes
udevadm info /dev/sda

# Voir le SYSTEMD_WANTS (services à démarrer)
udevadm info /dev/sda | grep SYSTEMD
```

## Règles udev personnalisées

Bien que les device units soient automatiques, vous pouvez influencer leur comportement via les règles udev.

### Démarrer un service à la connexion

```udev
# /etc/udev/rules.d/99-usb-backup.rules
# Démarrer backup.service quand le disque USB est connecté
SUBSYSTEM=="block", ENV{ID_SERIAL}="My_USB_Drive", \
  ENV{SYSTEMD_WANTS}+="usb-backup.service"
```

```ini
# /etc/systemd/system/usb-backup.service
[Unit]
Description=Backup to USB Drive

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup-to-usb.sh
```

Recharger les règles :
```bash
udevadm control --reload-rules
udevadm trigger
```

### Taguer des devices

```udev
# /etc/udev/rules.d/99-camera.rules
# Taguer les caméras
SUBSYSTEM=="video4linux", TAG+="systemd", \
  ENV{SYSTEMD_ALIAS}+="/dev/camera"
```

Crée un alias `/dev/camera` utilisable dans les services.

### Définir des propriétés

```udev
# Marquer un device comme amovible
SUBSYSTEM=="block", ENV{ID_SERIAL}="External_Disk", \
  ENV{SYSTEMD_READY}="1"
```

## Cas d'usage pratiques

### Service pour disque externe

```ini
# /etc/systemd/system/backup-drive-mount.service
[Unit]
Description=Mount Backup Drive
BindsTo=dev-disk-by\x2dlabel-BACKUP.device
After=dev-disk-by\x2dlabel-BACKUP.device

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/mount /dev/disk/by-label/BACKUP /mnt/backup
ExecStop=/usr/bin/umount /mnt/backup

[Install]
WantedBy=dev-disk-by\x2dlabel-BACKUP.device
```

Le service se lance automatiquement quand le disque est connecté.

### Application USB série

```ini
# /etc/systemd/system/serial-app.service
[Unit]
Description=Serial Port Application
BindsTo=dev-ttyUSB0.device
After=dev-ttyUSB0.device

[Service]
Type=simple
ExecStart=/usr/bin/serial-app /dev/ttyUSB0
Restart=on-failure

[Install]
WantedBy=dev-ttyUSB0.device
```

### Surveillance de périphériques multiples

```ini
# /etc/systemd/system/multi-device.service
[Unit]
Description=Service requiring multiple devices
Requires=dev-ttyUSB0.device dev-ttyUSB1.device
After=dev-ttyUSB0.device dev-ttyUSB1.device

[Service]
Type=simple
ExecStart=/usr/bin/myapp
```

Le service ne démarre que si **tous** les devices sont présents.

### Script de notification

Via règle udev :

```udev
# /etc/udev/rules.d/99-usb-notify.rules
SUBSYSTEM=="usb", ACTION=="add", \
  RUN+="/usr/local/bin/usb-notify.sh 'USB device connected'"

SUBSYSTEM=="usb", ACTION=="remove", \
  RUN+="/usr/local/bin/usb-notify.sh 'USB device removed'"
```

## Débogage

### Trouver le device unit d'un périphérique

```bash
# Lister les devices
lsblk

# Informations udev
udevadm info /dev/sda

# Trouver l'unité systemd
systemctl list-units --type=device | grep sda

# Ou avec systemd-escape
systemd-escape -p --suffix=device /dev/sda
```

### Vérifier les dépendances

```bash
# Services qui dépendent d'un device
systemctl list-dependencies --reverse dev-sda.device

# Services démarrés par un device
systemctl show dev-sda.device -p Wants
```

### Surveiller les événements

```bash
# Événements udev en temps réel
udevadm monitor

# Logs systemd
journalctl -f -u systemd-udevd

# Logs d'un device spécifique
journalctl -f /dev/sda
```

### Tester une règle udev

```bash
# Simuler un événement
udevadm test /sys/block/sda

# Recharger les règles
udevadm control --reload-rules
udevadm trigger

# Vérifier les propriétés
udevadm info --query=property /dev/sda
```

## Limitations

### Devices volatiles

Les device units existent uniquement quand le matériel est connecté. Pour des services persistants, utilisez des dépendances souples :

```ini
[Unit]
# Plutôt que Requires=
Wants=dev-ttyUSB0.device
```

### Identification instable

`/dev/ttyUSB0` peut changer entre redémarrages. Utilisez des identifiants stables :

```bash
# Préférer
dev-serial-by\x2did-usb\x2dFTDI_....device

# Plutôt que
dev-ttyUSB0.device
```

### Droits d'accès

Les règles udev doivent définir les permissions :

```udev
SUBSYSTEM=="usb", ATTR{idVendor}=="1234", \
  OWNER="myuser", GROUP="mygroup", MODE="0660"
```

## Bonnes pratiques

1. **Utiliser des identifiants stables**
   ```bash
   # Préférer by-uuid, by-id, by-path
   /dev/disk/by-uuid/...
   /dev/serial/by-id/...
   ```

2. **BindsTo pour dépendances strictes**
   ```ini
   BindsTo=dev-ttyUSB0.device
   ```
   Arrête le service si le device disparaît.

3. **Wants pour dépendances souples**
   ```ini
   Wants=dev-sda.device
   ```
   Le service peut démarrer sans le device.

4. **Documenter les devices requis**
   ```ini
   [Unit]
   Description=App requiring /dev/ttyUSB0 (FTDI USB-Serial)
   ```

5. **Utiliser udev pour la logique complexe**
   - Règles udev pour la détection
   - Device units pour les dépendances

6. **Tester avec udevadm**
   ```bash
   udevadm test /sys/class/.../.../
   ```

Les device units offrent une intégration transparente entre le matériel et les services systemd, permettant une gestion automatique et élégante des périphériques.
