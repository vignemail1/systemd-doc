# Swap Units (.swap)

Les unités `.swap` gèrent les espaces de swap (mémoire virtuelle) dans systemd. Elles permettent d'activer et de contrôler les partitions ou fichiers de swap de manière intégrée.

## Qu'est-ce que le swap ?

Le **swap** est un espace disque utilisé comme extension de la RAM lorsque la mémoire physique est saturée. Le noyau Linux peut déplacer des pages mémoire rarement utilisées vers le swap pour libérer de la RAM.

### Types de swap

- **Partition swap** : Partition dédiée (type 82)
- **Fichier swap** : Fichier ordinaire utilisé comme swap
- **Swap sur zram** : Swap compressé en RAM

## Nommage des swap units

Le nom du fichier `.swap` correspond au chemin d'activation, avec `/` remplacés par `-` :

| Device/Fichier | Nom de l'unité |
| ---------------- | ---------------- |
| `/dev/sda2` | `dev-sda2.swap` |
| `/swapfile` | `swapfile.swap` |
| `/var/swap/file` | `var-swap-file.swap` |

## Structure d'un swap unit

```ini
[Unit]
Description=Swap Partition

[Swap]
What=/dev/disk/by-uuid/swap-uuid-here
Priority=100

[Install]
WantedBy=swap.target
```text

## Section [Swap]

### Options

**What**

: Périphérique ou fichier de swap

```ini
# Partition
What=/dev/sda2

# Par UUID (recommandé)
What=/dev/disk/by-uuid/12345678-1234-1234-1234-123456789012

# Par label
What=/dev/disk/by-label/swap

# Fichier
What=/swapfile
```text

**Priority**

: Priorité du swap (plus élevé = utilisé en premier)

```ini
Priority=100   # Priorité haute
Priority=10    # Priorité basse
Priority=-1    # Priorité par défaut du noyau
```text

Valeurs typiques : -1 à 32767 (plus haut = prioritaire)

**Options**

: Options de montage swap (rarement utilisé)

```ini
Options=discard  # Activer TRIM sur SSD
```text

**TimeoutSec**

: Timeout pour l'activation

```ini
TimeoutSec=30s
```text

## Création et configuration

### Partition swap

#### 1. Créer la partition

```bash
# Avec fdisk/gdisk/parted
fdisk /dev/sda
# Créer partition de type 82 (Linux swap)

# Formater
mkswap /dev/sda2

# Obtenir l'UUID
blkid /dev/sda2
```text

#### 2. Créer le swap unit

```ini
# /etc/systemd/system/dev-sda2.swap
[Unit]
Description=Swap Partition on SDA2

[Swap]
What=/dev/disk/by-uuid/abc-123-def-456
Priority=100

[Install]
WantedBy=swap.target
```text

#### 3. Activer

```bash
systemctl enable dev-sda2.swap
systemctl start dev-sda2.swap

# Vérifier
swapon --show
free -h
```text

### Fichier swap

#### 1. Créer le fichier

```bash
# Créer un fichier de 4 Go
dd if=/dev/zero of=/swapfile bs=1M count=4096

# Ou avec fallocate (plus rapide)
fallocate -l 4G /swapfile

# Permissions
chmod 600 /swapfile

# Formater
mkswap /swapfile
```text

#### 2. Créer le swap unit

```ini
# /etc/systemd/system/swapfile.swap
[Unit]
Description=Swap File

[Swap]
What=/swapfile
Priority=50

[Install]
WantedBy=swap.target
```text

#### 3. Activer

```bash
systemctl enable swapfile.swap
systemctl start swapfile.swap

# Vérifier
swapon --show
```text

### Swap multiple avec priorités

```ini
# Partition rapide (SSD) - priorité haute
# /etc/systemd/system/dev-nvme0n1p2.swap
[Unit]
Description=Fast Swap on NVMe

[Swap]
What=/dev/disk/by-uuid/nvme-swap-uuid
Priority=200
Options=discard

[Install]
WantedBy=swap.target
```text

```ini
# Partition lente (HDD) - priorité basse
# /etc/systemd/system/dev-sda2.swap
[Unit]
Description=Slow Swap on HDD

[Swap]
What=/dev/disk/by-uuid/hdd-swap-uuid
Priority=10

[Install]
WantedBy=swap.target
```text

Le noyau utilisera le swap NVMe en priorité.

### Swap sur zram

zram crée un swap compressé en RAM (utile pour les machines avec peu de mémoire).

```bash
# Installer zram-generator (Fedora/CentOS)
dnf install zram-generator

# Ou systemd-zram (Debian/Ubuntu)
apt install systemd-zram-generator
```text

Configuration `/etc/systemd/zram-generator.conf` :

```ini
[zram0]
zram-size = ram / 2
compression-algorithm = zstd
```text

Activation automatique au boot.

## Gestion du swap

### Commandes de base

```bash
# Lister les swap units
systemctl list-units --type=swap
systemctl list-units --type=swap --all

# Activer un swap
systemctl start dev-sda2.swap

# Désactiver un swap
systemctl stop dev-sda2.swap

# Activer au boot
systemctl enable dev-sda2.swap

# Désactiver au boot
systemctl disable dev-sda2.swap

# Voir l'état
systemctl status dev-sda2.swap
```text

### Commandes swapon/swapoff

```bash
# Voir le swap actif
swapon --show
free -h
cat /proc/swaps

# Activer manuellement
swapon /dev/sda2
swapon /swapfile

# Désactiver
swapoff /dev/sda2
swapoff /swapfile

# Désactiver tout le swap
swapoff -a

# Activer tout le swap
swapon -a
```text

### Informations détaillées

```bash
# Statistiques du swap
vmstat 1
cat /proc/meminfo | grep -i swap

# Priorités
swapon --show=NAME,SIZE,USED,PRIO

# Processus utilisant le swap
for pid in /proc/[0-9]*; do
  swap=$(grep VmSwap $pid/status 2>/dev/null | awk '{print $2}')
  if [ "$swap" != "" ] && [ "$swap" != "0" ]; then
    echo "$pid: $swap kB"
  fi
done
```text

## Configuration système

### Swappiness

Contrôle la tendance du noyau à utiliser le swap (0-100).

```bash
# Voir la valeur actuelle
cat /proc/sys/vm/swappiness

# Modifier temporairement
echo 10 | sudo tee /proc/sys/vm/swappiness

# Permanent (/etc/sysctl.conf)
vm.swappiness=10

# Appliquer
sysctl -p
```text

**Valeurs typiques** :
- `60` : Défaut (utilise le swap modérément)
- `10` : Serveurs (minimise l'utilisation du swap)
- `100` : Swap agressif
- `0` : Swap uniquement si nécessaire

### Vfs*cache*pressure

Contrôle la réclamation de mémoire cache.

```bash
# Permanent
vm.vfs_cache_pressure=50
```text

**Valeurs** :
- `100` : Défaut
- `50` : Conserve le cache plus longtemps
- `200` : Libère le cache agressivement

## Conversion depuis fstab

### fstab traditionnel

```text
# /etc/fstab
UUID=abc-123  none  swap  sw,pri=100  0 0
/swapfile     none  swap  sw,pri=50   0 0
```text

### Équivalent systemd

```ini
# /etc/systemd/system/dev-disk-by\x2duuid-abc\x2d123.swap
[Unit]
Description=Swap Partition

[Swap]
What=/dev/disk/by-uuid/abc-123
Priority=100

[Install]
WantedBy=swap.target
```text

```ini
# /etc/systemd/system/swapfile.swap
[Unit]
Description=Swap File

[Swap]
What=/swapfile
Priority=50

[Install]
WantedBy=swap.target
```text

**Note** : systemd peut générer automatiquement des swap units depuis fstab.

## Dimensionnement du swap

### Règles générales

| RAM | Swap recommandé | Swap avec hibernation |
| ----- | ------------------ | ------------------------ |
| < 2 Go | 2x RAM | 3x RAM |
| 2-8 Go | = RAM | 2x RAM |
| > 8 Go | 4-8 Go | 1.5x RAM |
| > 64 Go | 4 Go minimum | = RAM |

### Serveurs

```bash
# Serveurs avec beaucoup de RAM
# Swap minimal pour éviter l'OOM killer
Swap = 2-4 Go

# Workstations
# Swap pour hibernation
Swap = RAM + quelques Go
```text

## Monitoring et tuning

### Surveiller l'utilisation

```bash
# En temps réel
watch -n 1 free -h

# Historique
sar -S 1 10  # 10 mesures par seconde

# Voir si le swap est actif
vmstat 1 | awk '{print $7, $8}'
# si = swap in, so = swap out
```text

### Logs

```bash
# Logs swap
journalctl -u '*.swap'

# Événements OOM
journalctl -k | grep -i "out of memory"
```text

### Vider le swap

```bash
# Désactiver le swap (force le retour en RAM)
sudo swapoff -a

# Réactiver
sudo swapon -a
```text

⚠️ **Attention** : Nécessite suffisamment de RAM libre.

## Dépannage

### Swap ne s'active pas

```bash
# Vérifier l'unité
systemctl status dev-sda2.swap

# Le périphérique existe ?
lsblk
blkid /dev/sda2

# Est-ce bien formaté en swap ?
file -s /dev/sda2

# Logs
journalctl -u dev-sda2.swap

# Tester manuellement
sudo swapon /dev/sda2
```text

### Permissions fichier swap

```bash
# Vérifier
ls -l /swapfile

# Doit être 600
chmod 600 /swapfile
```text

### Performances dégradées

```bash
# Vérifier si swap sur SSD
lsblk -o NAME,ROTA
# ROTA=0 : SSD, ROTA=1 : HDD

# Activer TRIM si SSD
[Swap]
Options=discard

# Vérifier swappiness
cat /proc/sys/vm/swappiness
```text

## Sécurité

### Swap chiffré

Le swap peut contenir des données sensibles.

#### Avec LUKS

```bash
# Chiffrer la partition
cryptsetup luksFormat /dev/sda2
cryptsetup luksOpen /dev/sda2 swap_crypt

# Formater
mkswap /dev/mapper/swap_crypt
```text

```ini
# /etc/systemd/system/dev-mapper-swap_crypt.swap
[Unit]
Description=Encrypted Swap
After=systemd-cryptsetup@swap_crypt.service
Requires=systemd-cryptsetup@swap_crypt.service

[Swap]
What=/dev/mapper/swap_crypt

[Install]
WantedBy=swap.target
```text

#### Swap éphémère

Chiffrement avec clé aléatoire (perdue au reboot) :

```text
# /etc/crypttab
swap /dev/sda2 /dev/urandom swap,cipher=aes-xts-plain64,size=256
```text

## Bonnes pratiques

1. **Toujours utiliser UUID**

   ```ini
   What=/dev/disk/by-uuid/...
```text

2. **Définir des priorités**

   ```ini
   Priority=100  # SSD
   Priority=10   # HDD
```text

3. **TRIM sur SSD**

   ```ini
   Options=discard
```text

4. **Ajuster swappiness**

   ```bash
   # Serveur
   vm.swappiness=10
   
   # Desktop
   vm.swappiness=60
```text

5. **Monitorer l'utilisation**

   ```bash
   watch -n 1 'free -h && swapon --show'
```text

6. **Dimensionnement approprié**
   - Serveur : 2-4 Go minimum
   - Desktop : RAM pour hibernation

7. **Fichier swap sur Btrfs**

   ```bash
   # Désactiver COW
   chattr +C /swapfile
```text

8. **Sécuriser le swap**

   ```bash
   # Permissions strictes
   chmod 600 /swapfile
```text

Le swap reste important même sur des systèmes avec beaucoup de RAM, agissant comme filet de sécurité contre l'OOM killer et permettant l'hibernation.
