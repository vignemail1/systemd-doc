# Outils de l'écosystème systemd

systemd fournit une suite complète d'outils pour gérer et administrer le système. Ces utilitaires couvrent tous les aspects de la gestion système, de la configuration réseau à la consultation des logs.

## Outils principaux

### systemctl

L'outil central de contrôle de systemd.

**Fonctions** :
- Gérer les unités (start, stop, enable, disable...)
- Voir l'état du système
- Contrôler les targets
- Recharger la configuration

```bash
systemctl status nginx.service
systemctl restart postgresql.service
systemctl list-units --type=service
```text

### journalctl

Consultation et analyse des logs systemd.

**Fonctions** :
- Lire les logs structurés
- Filtrer par unité, priorité, période
- Suivre les logs en temps réel
- Exporter les logs

```bash
journalctl -u nginx.service
journalctl --since "1 hour ago"
journalctl -f
```text

### systemd-analyze

Analyse des performances et débogage.

**Fonctions** :
- Temps de boot
- Chaînes critiques
- Vérification de configuration
- Graphes de dépendances

```bash
systemd-analyze time
systemd-analyze blame
systemd-analyze critical-chain
```text

## Outils réseau

### systemd-networkd

Gestion de la configuration réseau.

**Fonctions** :
- Configuration des interfaces
- DHCP client
- Routage statique
- VLAN, bridges, bonds

**Commande associée** : `networkctl`

### systemd-resolved

Résolution DNS avec cache.

**Fonctions** :
- Cache DNS
- Support DNSSEC
- mDNS et LLMNR
- Gestion de `/etc/resolv.conf`

**Commandes associées** : `resolvectl`, `systemd-resolve`

## Outils de gestion système

### systemd-logind

Gestion des sessions utilisateur.

**Fonctions** :
- Suivi des connexions
- Gestion de l'alimentation
- Contrôle d'accès aux périphériques
- Support multi-seat

**Commande associée** : `loginctl`

### systemd-timesyncd

Synchronisation horaire SNTP.

**Fonctions** :
- Client NTP léger
- Synchronisation automatique
- Alternative à ntpd/chrony

**Commande associée** : `timedatectl`

### systemd-udevd

Gestion des périphériques.

**Fonctions** :
- Détection matériel
- Chargement de modules
- Création de nœuds /dev
- Application de règles

**Commande associée** : `udevadm`

## Outils de configuration

### hostnamectl

Configuration du nom d'hôte.

```bash
hostnamectl set-hostname myserver
hostnamectl status
```text

### localectl

Configuration locale et clavier.

```bash
localectl set-locale LANG=fr_FR.UTF-8
localectl set-keymap fr
```text

### timedatectl

Configuration date, heure et fuseau horaire.

```bash
timedatectl set-timezone Europe/Paris
timedatectl set-ntp true
```text

## Outils avancés

### systemd-nspawn

Conteneurs légers (alternative à chroot).

```bash
systemd-nspawn -D /var/lib/machines/container
```text

### systemd-boot (bootctl)

Gestionnaire de démarrage UEFI.

```bash
bootctl status
bootctl install
```text

### systemd-tmpfiles

Gestion des fichiers temporaires.

```bash
systemd-tmpfiles --create
systemd-tmpfiles --clean
```text

### systemd-sysusers

Création d'utilisateurs et groupes système.

```bash
systemd-sysusers
```text

## Outils de débogage

### systemd-cgls

Arbre des cgroups.

```bash
systemd-cgls
systemd-cgls system.slice
```text

### systemd-cgtop

Monitoring des ressources par cgroup.

```bash
systemd-cgtop
```text

### coredumpctl

Gestion des core dumps.

```bash
coredumpctl list
coredumpctl info
coredumpctl debug
```text

## Tableau récapitulatif

| Outil | Fonction principale | Commande exemple |
| ------- | --------------------- | ------------------ |
| systemctl | Gestion des unités | `systemctl status` |
| journalctl | Consultation logs | `journalctl -u service` |
| systemd-analyze | Analyse performances | `systemd-analyze blame` |
| networkctl | Gestion réseau | `networkctl status` |
| resolvectl | Résolution DNS | `resolvectl status` |
| loginctl | Sessions utilisateur | `loginctl list-sessions` |
| timedatectl | Date et heure | `timedatectl status` |
| hostnamectl | Nom d'hôte | `hostnamectl status` |
| localectl | Locale et clavier | `localectl status` |
| udevadm | Périphériques | `udevadm info /dev/sda` |
| bootctl | Boot UEFI | `bootctl status` |
| coredumpctl | Core dumps | `coredumpctl list` |

## Organisation de la documentation

Chaque outil est détaillé dans sa propre page avec :

- Vue d'ensemble et cas d'usage
- Syntaxe et options principales
- Exemples pratiques
- Astuces et bonnes pratiques
- Dépannage

---

Les sections suivantes explorent chaque outil en détail.
