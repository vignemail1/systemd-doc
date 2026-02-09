# Swap (.swap)

Les unités `.swap` permettent à systemd de gérer les espaces de swap (mémoire virtuelle). Elles fonctionnent de manière similaire aux unités mount.

## Concept du swap

Le swap est un espace disque utilisé comme extension de la RAM lorsque celle-ci est pleine. systemd peut gérer cet espace via des unités `.swap`.

## Types de swap

### Partition swap

Partition dédiée sur le disque :
```bash
/dev/sda2   # Partition swap
```

### Fichier swap

Fichier utilisé comme swap :
```bash
/swapfile   # Fichier swap
```

### Swap sur LVM/LUKS

Swap sur volumes logiques ou chiffrés :
```bash
/dev/mapper/vg0-swap
/dev/mapper/swap_crypt
```

## Convention de nommage

Comme pour les mount units, le nom doit correspondre au chemin :

```
/dev/sda2 → dev-sda2.swap
/swapfile → swapfile.swap
/dev/mapper/vg0-swap → dev-mapper-vg0\x2dswap.swap
```

## Structure d'un fichier .swap

```ini
[Unit]
Description=Swap Partition

[Swap]
What=/dev/sda2
Priority=10

[Install]
WantedBy=swap.target
```

## Section [Swap]

### Options principales

**What**
: Device ou fichier de swap (obligatoire)

```ini
# Partition
What=/dev/sda2

# UUID
What=UUID=xxx-xxx-xxx

# Fichier
What=/swapfile

# LVM
What=/dev/mapper/vg0-swap
```

**Priority**
: Priorité du swap (-1 à 32767, plus haute = utilisée en premier)

```ini
Priority=10   # Priorité basse
Priority=100  # Priorité haute
Priority=-1   # Valeur par défaut du kernel
```

**Options**
: Options de montage du swap

```ini
Options=discard    # TRIM pour SSD
Options=nofail     # Ne pas échouer si indisponible
```

**TimeoutSec**
: Timeout pour l'activation

```ini
TimeoutSec=30s
```

## Exemples

### Swap sur partition

```ini
# /etc/systemd/system/dev-sda2.swap
[Unit]
Description=Swap Partition on /dev/sda2

[Swap]
What=/dev/sda2
Priority=10

[Install]
WantedBy=swap.target
```

Activation :
```bash
systemctl enable dev-sda2.swap
systemctl start dev-sda2.swap

# Vérifier
swapon --show
free -h
```

### Swap avec UUID

```ini
# /etc/systemd/system/dev-disk-by\x2duuid-xxx.swap
[Unit]
Description=Swap by UUID

[Swap]
What=UUID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
Priority=10

[Install]
WantedBy=swap.target
```

Utiliser UUID est recommandé pour la stabilité.

### Swap file

```ini
# /etc/systemd/system/swapfile.swap
[Unit]
Description=Swap File
ConditionPathExists=/swapfile

[Swap]
What=/swapfile
Priority=5

[Install]
WantedBy=swap.target
```

Création du fichier swap :
```bash
# Créer un fichier de 4G
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096 status=progress
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Activer au boot
sudo systemctl enable swapfile.swap
```

### Swap sur SSD avec TRIM

```ini
# /etc/systemd/system/dev-nvme0n1p2.swap
[Unit]
Description=Swap on NVMe SSD

[Swap]
What=/dev/nvme0n1p2
Options=discard
Priority=20

[Install]
WantedBy=swap.target
```

L'option `discard` active le TRIM pour les SSD.

### Swap chiffré (LUKS)

```ini
# /etc/systemd/system/dev-mapper-swap_crypt.swap
[Unit]
Description=Encrypted Swap
After=systemd-cryptsetup@swap_crypt.service
Requires=systemd-cryptsetup@swap_crypt.service

[Swap]
What=/dev/mapper/swap_crypt
Priority=10

[Install]
WantedBy=swap.target
```

Configuration crypttab :
```bash
# /etc/crypttab
swap_crypt  /dev/sda3  /dev/urandom  swap,cipher=aes-xts-plain64,size=256
```

### Multiples swaps avec priorités

```ini
# Swap rapide (SSD) - priorité haute
# /etc/systemd/system/dev-nvme0n1p2.swap
[Swap]
What=/dev/nvme0n1p2
Priority=100
Options=discard

# Swap lent (HDD) - priorité basse
# /etc/systemd/system/dev-sda2.swap
[Swap]
What=/dev/sda2
Priority=10
```

Le swap SSD sera utilisé en premier.

## Gestion du swap

### Commandes systemctl

```bash
# Lister les swaps systemd
systemctl list-units --type=swap
systemctl list-unit-files --type=swap

# Activer un swap
systemctl start dev-sda2.swap

# Désactiver
systemctl stop dev-sda2.swap

# Activer au boot
systemctl enable dev-sda2.swap

# Statut
systemctl status dev-sda2.swap
```

### Commandes swap traditionnelles

```bash
# Voir les swaps actifs
swapon --show
cat /proc/swaps
free -h

# Activer manuellement
sudo swapon /dev/sda2
sudo swapon /swapfile

# Désactiver
sudo swapoff /dev/sda2
sudo swapoff -a  # Tous les swaps

# Priorité
sudo swapon --priority 100 /dev/sda2
```

## Target swap.target

Le target `swap.target` regroupe tous les swaps :

```bash
# Voir tous les swaps gérés
systemctl list-dependencies swap.target

# Désactiver tous les swaps
systemctl stop swap.target

# Statut
systemctl status swap.target
```

## Migration depuis /etc/fstab

### Entrée fstab

```
UUID=xxx  none  swap  defaults  0  0
```

### Équivalent systemd

```ini
# /etc/systemd/system/dev-disk-by\x2duuid-xxx.swap
[Unit]
Description=Swap Partition

[Swap]
What=UUID=xxx

[Install]
WantedBy=swap.target
```

systemd lit aussi `/etc/fstab`, les deux coexistent.

## Configuration du swappiness

Le swappiness contrôle l'agressivité du swap (0-100) :

```bash
# Voir la valeur actuelle
cat /proc/sys/vm/swappiness

# Modifier temporairement
sudo sysctl vm.swappiness=10

# Modifier en permanence
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

Valeurs communes :
- **60** : Défaut (Linux)
- **10** : Serveurs (minimise le swap)
- **1** : Swap uniquement en dernier recours
- **100** : Swap agressif

## Hibernation

Pour l'hibernation, le swap doit être au moins aussi grand que la RAM :

```ini
# /etc/systemd/system/dev-sda2.swap
[Unit]
Description=Swap for Hibernation

[Swap]
What=/dev/sda2
Priority=10

[Install]
WantedBy=swap.target
```

Configuration hibernation :
```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX="resume=UUID=xxx"

# Rebuilder grub
sudo update-grub  # Debian/Ubuntu
sudo grub2-mkconfig -o /boot/grub2/grub.cfg  # RHEL/Rocky
```

## Zram (swap en RAM compressé)

Alternative moderne : zram (swap compressé en RAM) :

```bash
# Installer zram
sudo dnf install zram-generator  # RHEL/Rocky
sudo apt install zram-tools      # Debian/Ubuntu

# Configuration
# /etc/systemd/zram-generator.conf
[zram0]
zram-size = ram / 2
compression-algorithm = lz4
```

Plus rapide que le swap disque.

## Monitoring

### Utilisation actuelle

```bash
# Vue d'ensemble
free -h

# Détails par swap
swapon --show

# Statistiques
vmstat 1

# Processus utilisant le swap
for file in /proc/*/status; do 
    awk '/VmSwap|Name/{printf $2 " " $3}END{ print ""}' $file
done | sort -k 2 -n -r | head
```

### Logs systemd

```bash
journalctl -u dev-sda2.swap
journalctl -u swap.target
journalctl -b | grep -i swap
```

## Troubleshooting

### Swap ne s'active pas

```bash
# Vérifier le service
systemctl status dev-sda2.swap

# Vérifier la partition
sudo blkid | grep swap
sudo fdisk -l

# Formater si nécessaire
sudo mkswap /dev/sda2

# Tester manuellement
sudo swapon /dev/sda2
swapon --show
```

### Erreur "device busy"

```bash
# Désactiver le swap
sudo swapoff /dev/sda2

# Vérifier qu'il est désactivé
swapon --show

# Redémarrer le service
systemctl restart dev-sda2.swap
```

### Performance swap lente

```bash
# Vérifier les I/O
sudo iotop -o

# Statistiques
vmstat 1 10

# Considérer :
# - Réduire swappiness
# - Ajouter plus de RAM
# - Utiliser zram
# - Swap sur SSD avec priorité haute
```

## Bonnes pratiques

1. **Utiliser UUID** : Plus fiable que les noms de devices
2. **Priorités** : SSD haute, HDD basse
3. **TRIM pour SSD** : Option `discard`
4. **Taille** : 1-2x la RAM pour desktop, 0.5x pour serveurs
5. **Swappiness** : 10 pour serveurs, 60 pour desktop
6. **Hibernation** : Swap ≥ RAM
7. **Monitoring** : Surveiller l'utilisation du swap
8. **Zram** : Considérer pour les systèmes modernes

## Recommandations de taille

| RAM | Swap (sans hibernation) | Swap (avec hibernation) |
|-----|------------------------|-------------------------|
| < 2 GB | 2x RAM | 3x RAM |
| 2-8 GB | 1x RAM | 2x RAM |
| 8-64 GB | 0.5x RAM | 1.5x RAM |
| > 64 GB | 4-8 GB | 1x RAM |

## Sécurité

### Swap chiffré

Toujours chiffrer le swap en production :

```bash
# /etc/crypttab
swap  /dev/sda3  /dev/urandom  swap,cipher=aes-xts-plain64
```

Ou utiliser LUKS :
```bash
sudo cryptsetup luksFormat /dev/sda3
sudo cryptsetup open /dev/sda3 swap_crypt
sudo mkswap /dev/mapper/swap_crypt
```

### Swap file permissions

```bash
# Toujours 600 pour les fichiers swap
sudo chmod 600 /swapfile

# Vérifier
ls -l /swapfile
# -rw------- 1 root root
```

Les unités swap permettent une gestion flexible de la mémoire virtuelle, avec support des priorités, chiffrement et intégration complète avec systemd.
