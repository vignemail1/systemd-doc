# udevadm

`udevadm` est l'outil d'administration de `systemd-udevd`, le gestionnaire de périphériques Linux. Il permet d'interroger la base de données udev, de surveiller les événements périphériques, de déclencher des règles manuellement et de tester la configuration avant déploiement.

## Syntaxe générale

```bash
udevadm COMMANDE [OPTIONS]
```

## Informations sur un périphérique

### `udevadm info`

```bash
# Informations complètes sur un périphérique (par nœud de périphérique)
udevadm info /dev/sda
udevadm info /dev/nvme0n1
udevadm info /dev/ttyUSB0

# Par chemin sysfs
udevadm info /sys/class/net/eth0
udevadm info /sys/block/sda

# Par nom de périphérique udev
udevadm info --name=/dev/sda

# Arbre de la hiérarchie complète (périphérique + parents)
udevadm info --attribute-walk /dev/sda
udevadm info -a /dev/ttyUSB0

# Exporter toutes les propriétés
udevadm info --export /dev/sda

# Propriété spécifique
udevadm info --query=property --name=/dev/sda
udevadm info --query=symlink --name=/dev/disk/by-id/...
udevadm info --query=path --name=/dev/sda
```

La sortie de `udevadm info` liste :

- `P:` — chemin sysfs
- `N:` — nœud de périphérique (`/dev/...`)
- `L:` — priorité de lien symbolique
- `S:` — liens symboliques créés par udev
- `E:` — propriétés (variables d'environnement udev)

### Trouver un périphérique par attribut

```bash
# Lister tous les disques avec leurs attributs
udevadm info --attribute-walk /dev/sda | grep -E 'ATTR|ATTRS'

# Identifier le fabricant et le modèle
udevadm info /dev/sda | grep -E 'ID_VENDOR|ID_MODEL'

# Identifier le bus de connexion
udevadm info /dev/sda | grep ID_BUS

# Identifier les périphériques USB
udevadm info /dev/ttyUSB0 | grep -E 'ID_VENDOR_ID|ID_MODEL_ID|ID_SERIAL'
```

## Surveillance des événements

### `udevadm monitor`

```bash
# Surveiller tous les événements udev (brancher/débrancher un périphérique)
udevadm monitor

# Événements du noyau uniquement (avant traitement udev)
udevadm monitor --kernel

# Événements udev uniquement (après traitement des règles)
udevadm monitor --udev

# Filtrer par sous-système
udevadm monitor --subsystem-match=usb
udevadm monitor --subsystem-match=net
udevadm monitor --subsystem-match=block

# Filtrer par type de périphérique
udevadm monitor --udev --subsystem-match=usb --property
```

Très utile pour déboguer la détection de périphériques ou écrire des règles udev : brancher le périphérique et observer les événements et propriétés en temps réel.

## Déclenchement de règles

### `udevadm trigger`

```bash
# Rejouer les événements pour tous les périphériques (recharge les règles)
sudo udevadm trigger

# Rejouer pour un périphérique spécifique
sudo udevadm trigger /sys/block/sda
sudo udevadm trigger --sysname-match=sda

# Rejouer uniquement les événements de type add
sudo udevadm trigger --action=add

# Filtrer par sous-système
sudo udevadm trigger --subsystem-match=net
sudo udevadm trigger --subsystem-match=block

# Attendre la fin du traitement avant de rendre la main
sudo udevadm trigger --settle
```

## Rechargement des règles

```bash
# Recharger les fichiers de règles udev depuis le disque
sudo udevadm control --reload-rules

# Recharger ET rejouer les événements (combo fréquent après modification de règles)
sudo udevadm control --reload-rules && sudo udevadm trigger

# Changer le niveau de log de udevd
sudo udevadm control --log-priority=debug
sudo udevadm control --log-priority=info
```

## Test de règles

### `udevadm test`

```bash
# Simuler le traitement udev d'un périphérique (sans appliquer les changements)
sudo udevadm test /sys/block/sda
sudo udevadm test /sys/class/net/eth0
sudo udevadm test $(udevadm info -q path /dev/ttyUSB0)
```

Affiche les règles qui s'appliquent, dans l'ordre, et les valeurs attribuées. Indispensable pour déboguer une règle udev sans redémarrer.

### `udevadm test-builtin`

```bash
# Tester un builtin spécifique (ex: net_id pour les noms d'interfaces)
sudo udevadm test-builtin net_id /sys/class/net/eth0
sudo udevadm test-builtin path_id /sys/block/sda
```

## Écrire des règles udev

Les règles personnalisées se placent dans `/etc/udev/rules.d/` avec un nom numéroté (ex: `99-local.rules`). Les règles fournies par les paquets sont dans `/usr/lib/udev/rules.d/`.

```bash
# Emplacement des règles
ls /usr/lib/udev/rules.d/
ls /etc/udev/rules.d/
```

### Syntaxe d'une règle

```ini
CLÉ=="VALEUR", CLEF2=="VALEUR2", ACTION="valeur"
```

Exemple — donner un nom stable à une clé USB série :

```ini
# /etc/udev/rules.d/99-usb-serial.rules
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", \
  ATTRS{serial}=="A1B2C3D4", SYMLINK+="ttyArduino"
```

Exemple — appliquer des permissions sur un périphérique :

```ini
# /etc/udev/rules.d/99-gpio.rules
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0660"
```

Exemple — exécuter un script au branchement d'une clé USB :

```ini
# /etc/udev/rules.d/99-usb-mount.rules
ACTION=="add", KERNEL=="sd[b-z][0-9]", SUBSYSTEM=="block", \
  RUN+="/usr/local/bin/usb-mount.sh %k"
```

```bash
# Après modification des règles, toujours recharger
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Diagnostics courants

### Trouver les attributs pour écrire une règle

```bash
# Brancher le périphérique, identifier son nœud
ls /dev/ttyUSB*

# Inspecter la hiérarchie complète
udevadm info --attribute-walk /dev/ttyUSB0
# Les lignes ATTRS{...} du parent USB sont utilisables dans les règles
```

### Règle qui ne s'applique pas

```bash
# Simuler le traitement complet
sudo udevadm test $(udevadm info -q path /dev/ttyUSB0) 2>&1 | less

# Vérifier l'ordre des règles (la première correspondance gagne pour SYMLINK, NAME)
ls -la /etc/udev/rules.d/ /usr/lib/udev/rules.d/

# Vérifier les logs udevd
journalctl -u systemd-udevd -f
sudo udevadm control --log-priority=debug
journalctl -u systemd-udevd | grep -i error
```

### Attendre la fin de l'initialisation au boot

```bash
# Attendre que udev ait traité tous les événements en attente
sudo udevadm settle

# Avec timeout
sudo udevadm settle --timeout=30
```

Utilisé dans les scripts de démarrage pour s'assurer que tous les périphériques sont prêts avant de continuer.

## Récapitulatif des sous-commandes

| Sous-commande | Description |
| ------------- | ----------- |
| `info` | Informations sur un périphérique |
| `monitor` | Surveiller les événements udev/kernel |
| `trigger` | Rejouer les événements udev |
| `control` | Contrôler le démon udevd |
| `test` | Tester les règles sans les appliquer |
| `test-builtin` | Tester un builtin udev |
| `settle` | Attendre la fin du traitement des événements |
| `verify` | Vérifier la syntaxe des fichiers de règles |

## Voir aussi

- `man udevadm`
- `man udev(7)` — documentation des règles udev
- `man systemd-udevd.service`
