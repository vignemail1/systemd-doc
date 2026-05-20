# bootctl

`bootctl` est l'outil de gestion de `systemd-boot`, le gestionnaire de démarrage UEFI intégré à systemd. Il permet d'installer, mettre à jour et inspecter le boot loader, ainsi que de gérer les entrées de démarrage EFI.

!!! note "Prérequis UEFI"
    `bootctl` nécessite un système démarré en mode UEFI avec une partition EFI (ESP) montée. Il ne fonctionne pas sur les systèmes BIOS/Legacy.

    ```bash
    # Vérifier le mode de boot
    [ -d /sys/firmware/efi ] && echo "UEFI" || echo "BIOS"
    ```

## Syntaxe générale

```bash
bootctl [OPTIONS] COMMANDE
```

## État et informations

```bash
# Vue complète : état de l'ESP, entrées de boot, boot loader actuel
bootctl status

# Vue condensée
bootctl

# Lister uniquement les entrées de boot
bootctl list

# Vérifier la configuration (diagnostic)
bootctl is-installed
bootctl is-installed --graceful
```

## Installation et mise à jour

```bash
# Installer systemd-boot sur l'ESP
sudo bootctl install

# Installer sur une ESP non standard
sudo bootctl install --esp-path=/efi

# Mettre à jour le boot loader (sans toucher aux entrées)
sudo bootctl update

# Désinstaller systemd-boot (conserve les fichiers de boot)
sudo bootctl remove
```

!!! tip "Mise à jour automatique"
    Activer `systemd-boot-update.service` pour mettre à jour automatiquement `systemd-boot` lors des mises à jour du paquet systemd :

    ```bash
    sudo systemctl enable systemd-boot-update.service
    ```

## Structure de l'ESP

Après installation, l'ESP contient :

```
/boot/efi/ (ou /efi/)
├── EFI/
│   ├── systemd/
│   │   └── systemd-bootx64.efi      # boot loader
│   └── BOOT/
│       └── BOOTX64.EFI              # fallback EFI
└── loader/
    ├── loader.conf                   # configuration globale
    └── entries/
        ├── linux.conf                # entrée Linux
        └── linux-rescue.conf         # entrée de secours
```

## Configuration du boot loader

### `loader/loader.conf`

```ini
# Entrée de boot par défaut (nom du fichier .conf sans extension, ou @saved)
default linux

# Délai avant démarrage automatique (secondes, 0 = immédiat, -1 = menu permanent)
timeout 3

# Résolution de la console
console-mode max

# Éditeur de ligne de commande dans le menu (désactiver en production)
editor no

# Activer le mode auto (choisit l'entrée selon les variables EFI)
auto-entries yes
auto-firmware yes
```

### Entrées de boot (`loader/entries/*.conf`)

```ini
# loader/entries/linux.conf
title   Debian GNU/Linux
linux   /vmlinuz
initrd  /initrd.img
options root=/dev/sda2 rw quiet splash
```

```ini
# loader/entries/linux-rescue.conf
title   Debian GNU/Linux (rescue)
linux   /vmlinuz
initrd  /initrd.img
options root=/dev/sda2 rw single
```

## Gestion des variables EFI

```bash
# Lire la variable EFI de l'entrée par défaut
bootctl set-default linux

# Définir l'entrée au prochain boot uniquement
bootctl set-oneshot linux-rescue

# Lister les entrées de boot EFI (hors systemd-boot)
bootctl list

# Lire l'entrée suivante définie
efibootmgr  # outil complémentaire
```

## Diagnostics courants

### Vérifier l'état de l'installation

```bash
bootctl status
# Chercher :
# - "System:" : confirme UEFI
# - "Boot Loader:" : version de systemd-boot installée
# - "Good Partitions:" : ESP correctement détectée
# - "Boot Entries:" : liste les entrées disponibles
```

### ESP non trouvée

```bash
# Vérifier le montage de l'ESP
findmnt /boot/efi
findmnt /efi
lsblk -o NAME,PARTTYPE,MOUNTPOINT | grep -i efi

# Monter si nécessaire
sudo mount /dev/sda1 /boot/efi
```

### Entrée de boot manquante après mise à jour noyau

```bash
# Sur Debian/Ubuntu, le script de post-install du paquet linux-image
# doit copier le noyau et l'initrd dans l'ESP
ls /boot/efi/

# Forcer la mise à jour des entrées
sudo kernel-install add $(uname -r) /boot/vmlinuz-$(uname -r)
```

### Boot loader non mis à jour

```bash
# Version installée vs version du paquet
bootctl status | grep -A2 "Boot Loader"
bootctl status | grep -A2 "Available Versions"

# Mettre à jour manuellement
sudo bootctl update
```

## Récapitulatif des sous-commandes

| Sous-commande | Description |
| ------------- | ----------- |
| `status` | État complet de l'ESP et du boot loader |
| `list` | Lister les entrées de boot disponibles |
| `install` | Installer systemd-boot sur l'ESP |
| `update` | Mettre à jour le boot loader |
| `remove` | Désinstaller systemd-boot |
| `set-default` | Définir l'entrée par défaut |
| `set-oneshot` | Définir l'entrée pour le prochain boot uniquement |
| `is-installed` | Vérifier si systemd-boot est installé |
| `reboot-to-firmware` | Redémarrer vers le menu UEFI du firmware |

## Options globales utiles

| Option | Description |
| ------ | ----------- |
| `--esp-path=` | Chemin de l'ESP (défaut : `/boot` ou `/efi`) |
| `--boot-path=` | Chemin de boot alternatif |
| `--no-pager` | Désactiver le paginateur |
| `--graceful` | Ne pas échouer si systemd-boot n'est pas installé |
| `--json=short` | Sortie JSON compacte |

## Voir aussi

- [systemd-analyze](systemd-analyze.md) — analyse du boot et des performances
- `man bootctl`
- `man systemd-boot(7)` — documentation du boot loader
- `man loader.conf(5)` — format de la configuration du boot loader
- `man systemd.boot-credentials(7)` — credentials au démarrage
