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

{% dot systemd_unit_directories.svg
    digraph G {
        rankdir=TB;
        node [shape=folder, style=filled, fillcolor="#E3F2FD"];
        
        root [label="/", fillcolor="#BBDEFB"];
        etc [label="/etc/systemd/system/", fillcolor="#64B5F6"];
        run [label="/run/systemd/system/", fillcolor="#90CAF9"];
        usr [label="/usr/lib/systemd/system/", fillcolor="#BBDEFB"];
        
        root -> etc [label="  Priorité haute", fontsize=10];
        root -> run [label="  Priorité moyenne", fontsize=10];
        root -> usr [label="  Priorité basse", fontsize=10];
        
        etc [label="/etc/systemd/system/\n(Config admin)"];
        run [label="/run/systemd/system/\n(Runtime volatile)"];
        usr [label="/usr/lib/systemd/system/\n(Packages système)"];
    }
%}

**Ordre de priorité** : `/etc` > `/run` > `/usr/lib`

### Configuration

{% dot systemd_config_tree.svg
    digraph G {
        rankdir=LR;
        node [shape=folder, style=filled, fillcolor="#E8F5E9"];
        
        etc [label="/etc/systemd/", fillcolor="#81C784"];
        system [label="system/"];
        user [label="user/"];
        journald [label="journald.conf", shape=note, fillcolor="#C8E6C9"];
        logind [label="logind.conf", shape=note, fillcolor="#C8E6C9"];
        resolved [label="resolved.conf", shape=note, fillcolor="#C8E6C9"];
        networkd [label="networkd.conf", shape=note, fillcolor="#C8E6C9"];
        timesyncd [label="timesyncd.conf", shape=note, fillcolor="#C8E6C9"];
        
        etc -> system;
        etc -> user;
        etc -> journald;
        etc -> logind;
        etc -> resolved;
        etc -> networkd;
        etc -> timesyncd;
    }
%}

### Données runtime

```
/run/systemd/
  ├── system/                 # État runtime du système
  ├── sessions/               # Sessions utilisateur actives
  └── units/                  # État des unités
```

### Données persistantes

```
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

{% dot cgroups_hierarchy.svg
    digraph G {
        rankdir=TB;
        node [shape=box, style="rounded,filled", fillcolor="#FFF3E0"];
        
        root [label="/sys/fs/cgroup/", fillcolor="#FFB74D"];
        system [label="system.slice", fillcolor="#FFE0B2"];
        user [label="user.slice", fillcolor="#FFE0B2"];
        machine [label="machine.slice", fillcolor="#FFE0B2"];
        
        sshd [label="sshd.service"];
        nginx [label="nginx.service"];
        postgres [label="postgresql.service"];
        
        user1000 [label="user-1000.slice"];
        
        root -> system;
        root -> user;
        root -> machine;
        
        system -> sshd;
        system -> nginx;
        system -> postgres;
        
        user -> user1000;
    }
%}

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

{% dot systemd_architecture.svg
    digraph G {
        rankdir=TB;
        node [shape=box, style="rounded,filled"];
        
        // Kernel
        kernel [label="Noyau Linux\ncgroups, namespaces\ncapabilities, seccomp", fillcolor="#FFCDD2", shape=box, style="filled"];
        
        // systemd core
        systemd [label="systemd (PID 1)\nGestion unités, dépendances, cgroups", fillcolor="#E1BEE7", shape=box, style="rounded,filled"];
        
        // Composants systemd
        journald [label="systemd-\njournald", fillcolor="#C5CAE9"];
        logind [label="systemd-\nlogind", fillcolor="#C5CAE9"];
        networkd [label="systemd-\nnetworkd", fillcolor="#C5CAE9"];
        resolved [label="systemd-\nresolved", fillcolor="#C5CAE9"];
        udevd [label="systemd-\nudevd", fillcolor="#C5CAE9"];
        timesyncd [label="systemd-\ntimesyncd", fillcolor="#C5CAE9"];
        
        // Outils utilisateur
        tools [label="Outils utilisateur\nsystemctl, journalctl\nnetworkctl, loginctl, etc.", fillcolor="#B2DFDB", shape=box, style="filled"];
        
        // Relations
        kernel -> systemd [dir=both, label="  API kernel"];
        
        systemd -> journald;
        systemd -> logind;
        systemd -> networkd;
        systemd -> resolved;
        systemd -> udevd;
        systemd -> timesyncd;
        
        journald -> tools;
        logind -> tools;
        networkd -> tools;
        resolved -> tools;
        udevd -> tools;
        timesyncd -> tools;
        systemd -> tools [label="  systemctl", style=bold];
    }
%}

Cette architecture modulaire et intégrée fait de systemd un système d'initialisation puissant et flexible, capable de gérer tous les aspects du cycle de vie d'un système Linux moderne.
