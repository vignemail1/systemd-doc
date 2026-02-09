# Outils de l'écosystème systemd

systemd fournit un ensemble complet d'outils en ligne de commande pour administrer et interagir avec le système. Ces outils offrent un contrôle granulaire sur tous les aspects du système.

## Outils principaux

### Gestion du système

**systemctl**
: Outil principal de contrôle de systemd

```bash
systemctl start nginx.service
systemctl status nginx.service
systemctl enable nginx.service
```

Contrôle les services, targets, et toutes les unités systemd.

**systemd-analyze**
: Analyse des performances et de la configuration

```bash
systemd-analyze time
systemd-analyze blame
systemd-analyze verify myapp.service
```

Permet d'optimiser le temps de boot et vérifier les configurations.

### Journalisation

**journalctl**
: Consultation et filtrage des logs systemd

```bash
journalctl -u nginx.service
journalctl -f
journalctl --since "1 hour ago"
```

Accès au journal systemd avec filtrage puissant.

### Réseau

**networkctl**
: Gestion et statut des interfaces réseau

```bash
networkctl status
networkctl list
```

Utilisé avec systemd-networkd.

**resolvectl** / **systemd-resolve**
: Gestion DNS et résolution de noms

```bash
resolvectl status
resolvectl query example.com
```

Contrôle systemd-resolved.

### Sessions et utilisateurs

**loginctl**
: Gestion des sessions utilisateur

```bash
loginctl list-sessions
loginctl show-user username
loginctl terminate-session 1
```

Contrôle systemd-logind.

### Système

**hostnamectl**
: Gestion du nom d'hôte

```bash
hostnamectl
hostnamectl set-hostname server01
```

**timedatectl**
: Gestion de la date et l'heure

```bash
timedatectl
timedatectl set-timezone Europe/Paris
timedatectl set-ntp true
```

**localectl**
: Gestion de la locale et du clavier

```bash
localectl
localectl set-locale LANG=fr_FR.UTF-8
localectl set-keymap fr
```

### Boot et firmware

**bootctl**
: Gestion du gestionnaire de démarrage systemd-boot

```bash
bootctl status
bootctl install
bootctl list
```

### Autres outils

**systemd-run**
: Exécuter des commandes comme services temporaires

```bash
systemd-run --unit=backup /usr/local/bin/backup.sh
systemd-run --scope --slice=background.slice make
```

**systemd-cgls**
: Visualiser l'arborescence des cgroups

```bash
systemd-cgls
systemd-cgls system.slice
```

**systemd-cgtop**
: Monitorer l'utilisation des ressources par cgroup

```bash
systemd-cgtop
systemd-cgtop --order=memory
```

**systemd-delta**
: Voir les modifications de configuration

```bash
systemd-delta
systemd-delta --type=overridden
```

**systemd-path**
: Afficher les chemins systemd

```bash
systemd-path
systemd-path system-unit
systemd-path user-unit
```

**busctl**
: Interagir avec D-Bus

```bash
busctl list
busctl status org.freedesktop.systemd1
busctl tree org.freedesktop.systemd1
```

## Catégories d'outils

### Administration
- systemctl
- systemd-analyze
- systemd-run

### Logs et debugging
- journalctl
- systemd-cgls
- systemd-cgtop

### Réseau
- networkctl
- resolvectl

### Utilisateurs
- loginctl

### Configuration système
- hostnamectl
- timedatectl
- localectl

### Boot
- bootctl

### Bas niveau
- busctl
- systemd-delta
- systemd-path

## Installation

La plupart des outils sont installés avec systemd :

```bash
# Debian/Ubuntu
apt install systemd

# RHEL/Rocky Linux
dnf install systemd

# Arch Linux
pacman -S systemd
```

Certains outils optionnels :
```bash
# systemd-boot
apt install systemd-boot

# Outils réseau
apt install systemd-resolved systemd-networkd
```

## Pages de manuel

Chaque outil a une documentation complète :

```bash
man systemctl
man journalctl
man systemd-analyze
man networkctl
man loginctl
```

Documentation générale :
```bash
man systemd
man systemd.unit
man systemd.service
man systemd.timer
```

## Complétion shell

La plupart des shells modernes supportent l'autocomplétion pour les commandes systemd :

```bash
# Bash
source /usr/share/bash-completion/completions/systemctl

# Zsh
autoload -U compinit && compinit

# Fish
fish_update_completions
```

## Alias utiles

Quelques alias pratiques :

```bash
# ~/.bashrc ou ~/.zshrc
alias sc='systemctl'
alias scs='systemctl status'
alias scr='systemctl restart'
alias sce='systemctl enable'
alias scd='systemctl disable'
alias jc='journalctl'
alias jcf='journalctl -f'
alias jce='journalctl -e'
```

---

Dans les sections suivantes, nous explorerons en détail chaque outil principal avec des exemples pratiques et des cas d'usage avancés.
