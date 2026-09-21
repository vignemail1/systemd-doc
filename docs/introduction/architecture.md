# Architecture de systemd

systemd suit une architecture modulaire où le daemon principal (PID 1) coordonne un ensemble de composants spécialisés. Cette conception permet une séparation claire des responsabilités tout en maintenant une intégration étroite entre les différents services système.

## Le daemon principal : systemd (PID 1)

Le processus systemd s'exécute avec le PID 1, ce qui en fait le premier processus lancé par le noyau Linux après le boot. Il est le parent direct ou indirect de tous les autres processus du système.

### Responsabilités principales

- **Initialisation du système** : Montage des systèmes de fichiers, configuration réseau de base
- **Gestion des unités** : Chargement, démarrage, arrêt et supervision des unités
- **Gestion des dépendances** : Résolution de l'ordre de démarrage basé sur les dépendances
- **Supervision des processus** : Surveillance et redémarrage automatique des services
- **Gestion des cgroups** : Organisation hiérarchique des processus

### Communication avec systemd

Les utilisateurs et programmes interagissent avec systemd principalement via :

- **D-Bus** : Interface de communication inter-processus pour les commandes et événements
- **systemctl** : Interface en ligne de commande principale
- **API socket** : Pour les applications nécessitant une intégration profonde

## Composants de l'écosystème

### systemd-journald

Le daemon de journalisation collecte et stocke les logs du système.

**Fonctionnalités** :

- Stockage binaire structuré avec métadonnées
- Indexation pour recherche rapide
- Rotation automatique des logs
- Forward vers syslog si nécessaire
- Collecte des logs kernel, services et applications

**Fichiers de configuration** : `/etc/systemd/journald.conf`

### systemd-logind

Gère les sessions utilisateur et les sièges (seats) multi-utilisateurs.

**Fonctionnalités** :

- Suivi des sessions utilisateur
- Gestion de l'alimentation (suspend, hibernate)
- Contrôle d'accès aux périphériques
- Support multi-seat

**Commande associée** : `loginctl`

### systemd-udevd

Gère les événements des périphériques matériels.

**Fonctionnalités** :

- Détection dynamique du matériel
- Chargement automatique des modules kernel
- Création des nœuds de périphériques dans `/dev`
- Application de règles udev personnalisées

**Répertoire de règles** : `/etc/udev/rules.d/`, `/lib/udev/rules.d/`

### systemd-networkd

Daemon de gestion réseau pour la configuration des interfaces.

**Fonctionnalités** :

- Configuration des interfaces réseau
- Support DHCP client et serveur
- Configuration de VLAN, bridges, bonds
- Routage statique

**Fichiers de configuration** : `/etc/systemd/network/*.network`

**Commande associée** : `networkctl`

### systemd-resolved

Service de résolution DNS avec cache intégré.

**Fonctionnalités** :

- Résolution DNS avec cache
- Support DNSSEC
- Support mDNS et LLMNR
- Intégration avec systemd-networkd

**Fichiers de configuration** : `/etc/systemd/resolved.conf`

**Commandes associées** : `resolvectl`, `systemd-resolve`

### systemd-timesyncd

Client SNTP léger pour la synchronisation horaire.

**Fonctionnalités** :

- Synchronisation NTP basique
- Alternative légère à ntpd/chrony
- Stockage du temps dans `/var/lib/systemd/timesync/`

**Fichiers de configuration** : `/etc/systemd/timesyncd.conf`

**Commande associée** : `timedatectl`

### systemd-boot (anciennement gummiboot)

Gestionnaire de démarrage UEFI simple.

**Fonctionnalités** :

- Boot sur systèmes UEFI
- Interface minimale
- Configuration simple

**Commande associée** : `bootctl`

## Hiérarchie des répertoires

systemd utilise une structure de répertoires bien définie :

### Fichiers d'unités

```mermaid
graph TB
    root["/"]
    etc["/etc/systemd/system/<br/>(Config admin - Priorité haute)"]
    run["/run/systemd/system/<br/>(Runtime volatile - Priorité moyenne)"]
    usr["/usr/lib/systemd/system/<br/>(Packages système - Priorité basse)"]
    
    root --> etc
    root --> run
    root --> usr
    
    style etc fill:#64B5F6
    style run fill:#90CAF9
    style usr fill:#BBDEFB
    style root fill:#E3F2FD
```

**Ordre de priorité** : `/etc` > `/run` > `/usr/lib`

### Configuration

```mermaid
graph LR
    etc["/etc/systemd/"]
    system["system/"]
    user["user/"]
    journald["journald.conf"]
    logind["logind.conf"]
    resolved["resolved.conf"]
    networkd["networkd.conf"]
    timesyncd["timesyncd.conf"]
    
    etc --> system
    etc --> user
    etc --> journald
    etc --> logind
    etc --> resolved
    etc --> networkd
    etc --> timesyncd
    
    style etc fill:#81C784
    style system fill:#C8E6C9
    style user fill:#C8E6C9
    style journald fill:#C8E6C9
    style logind fill:#C8E6C9
    style resolved fill:#C8E6C9
    style networkd fill:#C8E6C9
    style timesyncd fill:#C8E6C9
```

### Données runtime

```text
/run/systemd/
  ├── system/                 # État runtime du système
  ├── sessions/               # Sessions utilisateur actives
  └── units/                  # État des unités
```

### Données persistantes

```text
/var/lib/systemd/
  ├── catalog/                # Catalogues de messages du journal
  ├── coredump/               # Core dumps des applications
  └── timesync/               # Données de synchronisation horaire
```

## Gestion des cgroups

systemd organise tous les processus dans une hiérarchie de cgroups (control groups) qui permet de :

- Limiter les ressources (CPU, mémoire, I/O)
- Mesurer l'utilisation des ressources
- Isoler les processus
- Tuer tous les processus d'un service de manière fiable

### Hiérarchie typique

```mermaid
graph TB
    root["/sys/fs/cgroup/"]
    system["system.slice"]
    user["user.slice"]
    machine["machine.slice"]
    
    sshd["sshd.service"]
    nginx["nginx.service"]
    postgres["postgresql.service"]
    
    user1000["user-1000.slice"]
    
    root --> system
    root --> user
    root --> machine
    
    system --> sshd
    system --> nginx
    system --> postgres
    
    user --> user1000
    
    style root fill:#FFB74D
    style system fill:#FFE0B2
    style user fill:#FFE0B2
    style machine fill:#FFE0B2
    style sshd fill:#FFF3E0
    style nginx fill:#FFF3E0
    style postgres fill:#FFF3E0
    style user1000 fill:#FFF3E0
```

Chaque service systemd s'exécute dans son propre cgroup, permettant une isolation et un contrôle précis.

## Communication D-Bus

systemd utilise intensivement D-Bus pour la communication inter-processus.

### Bus système

Le bus D-Bus système permet :

- L'envoi de commandes à systemd
- La notification d'événements système
- L'intégration avec d'autres services système

### Activation par bus

Les services peuvent être activés automatiquement lors d'une requête D-Bus, permettant un démarrage à la demande.

## Intégration kernel

systemd s'appuie sur plusieurs fonctionnalités du noyau Linux :

- **cgroups v2** : Organisation et limitation des ressources
- **namespaces** : Isolation des processus
- **capabilities** : Privilèges granulaires
- **seccomp** : Filtrage des appels système
- **autofs** : Montage automatique
- **fanotify/inotify** : Surveillance du système de fichiers

## Schéma d'ensemble

```mermaid
graph TB
    kernel["Noyau Linux<br/>cgroups, namespaces<br/>capabilities, seccomp"]
    systemd["systemd (PID 1)<br/>Gestion unités, dépendances, cgroups"]
    
    journald["systemd-<br/>journald"]
    logind["systemd-<br/>logind"]
    networkd["systemd-<br/>networkd"]
    resolved["systemd-<br/>resolved"]
    udevd["systemd-<br/>udevd"]
    timesyncd["systemd-<br/>timesyncd"]
    
    tools["Outils utilisateur<br/>systemctl, journalctl<br/>networkctl, loginctl, etc."]
    
    kernel <--> systemd
    
    systemd --> journald
    systemd --> logind
    systemd --> networkd
    systemd --> resolved
    systemd --> udevd
    systemd --> timesyncd
    
    journald --> tools
    logind --> tools
    networkd --> tools
    resolved --> tools
    udevd --> tools
    timesyncd --> tools
    systemd ==> tools
    
    style kernel fill:#FFCDD2
    style systemd fill:#E1BEE7
    style journald fill:#C5CAE9
    style logind fill:#C5CAE9
    style networkd fill:#C5CAE9
    style resolved fill:#C5CAE9
    style udevd fill:#C5CAE9
    style timesyncd fill:#C5CAE9
    style tools fill:#B2DFDB
```

Cette architecture modulaire et intégrée fait de systemd un système d'initialisation puissant et flexible, capable de gérer tous les aspects du cycle de vie d'un système Linux moderne.
