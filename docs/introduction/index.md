# Introduction à systemd

systemd est le système d'initialisation (init system) et gestionnaire de services standard pour la majorité des distributions Linux modernes. Développé par Lennart Poettering et Kay Sievers, il a été conçu pour remplacer le traditionnel SysVinit tout en apportant des fonctionnalités modernes et une meilleure performance.

## Qu'est-ce que systemd ?

systemd est bien plus qu'un simple gestionnaire d'initialisation. C'est une suite complète d'outils système qui gère :

- **L'initialisation du système** : Premier processus lancé au démarrage (PID 1)
- **La gestion des services** : Démarrage, arrêt et supervision des daemons
- **La gestion des logs** : Système de journalisation centralisé
- **La gestion du réseau** : Configuration réseau et résolution DNS
- **La gestion des sessions** : Utilisateurs et sessions de connexion
- **Les tâches planifiées** : Alternative moderne à cron

## Pourquoi systemd ?

### Avantages par rapport à SysVinit

**Parallélisation**
: systemd démarre les services en parallèle plutôt que séquentiellement, réduisant significativement le temps de démarrage du système.

**Activation à la demande**
: Les services peuvent être démarrés uniquement lorsqu'ils sont nécessaires grâce à l'activation par socket, path ou device.

**Dépendances explicites**
: Les relations entre services sont clairement définies dans les fichiers d'unités, garantissant un ordre de démarrage correct.

**Supervision intégrée**
: systemd surveille l'état des services et peut les redémarrer automatiquement en cas d'échec.

**Journalisation structurée**
: Les logs sont stockés de manière binaire avec des métadonnées, permettant des recherches et filtres puissants.

### Adoption massive

systemd est aujourd'hui le standard sur :

- Red Hat Enterprise Linux / Rocky Linux / AlmaLinux (depuis RHEL 7)
- Fedora (depuis 2011)
- Debian (depuis Debian 8)
- Ubuntu (depuis 15.04)
- Arch Linux
- SUSE / openSUSE
- Et la majorité des autres distributions

## Architecture générale

systemd est organisé autour de plusieurs composants :

```
┌─────────────────────────────────────────┐
│         systemd (PID 1)                 │
│  Gestionnaire principal du système      │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌─────────┐ ┌──────────┐
│ systemctl│ │journalctl│ │ autres   │
│          │ │         │ │ outils   │
└──────────┘ └─────────┘ └──────────┘
      │           │           │
      ▼           ▼           ▼
┌──────────────────────────────────────┐
│  Services, Sockets, Timers, etc.     │
│  (Unités systemd)                    │
└──────────────────────────────────────┘
```

### Composants principaux

- **systemd** : Le gestionnaire système principal (PID 1)
- **systemd-journald** : Daemon de journalisation
- **systemd-logind** : Gestion des sessions utilisateur
- **systemd-udevd** : Gestion des périphériques
- **systemd-networkd** : Configuration réseau
- **systemd-resolved** : Résolution DNS
- **systemd-timesyncd** : Synchronisation NTP

## Concepts clés

### Unités (Units)

Les **unités** sont les éléments de base de systemd. Chaque unité est définie par un fichier de configuration et représente une ressource que systemd sait gérer. Il existe plusieurs types d'unités (services, sockets, timers, etc.) que nous détaillerons dans les sections suivantes.

### Targets

Les **targets** sont des groupes d'unités qui représentent un état du système. Ils remplacent les runlevels de SysVinit. Par exemple, `multi-user.target` correspond au mode multi-utilisateur sans interface graphique.

### Cgroups

systemd utilise les **cgroups** Linux pour organiser les processus de manière hiérarchique et appliquer des limites de ressources. Chaque service s'exécute dans son propre cgroup.

## Commande de base

Voici un aperçu rapide des commandes systemd les plus utilisées :

```bash
# Gestion des services
systemctl start service.service      # Démarrer un service
systemctl stop service.service       # Arrêter un service
systemctl restart service.service    # Redémarrer un service
systemctl status service.service     # Voir l'état d'un service

# Activation au démarrage
systemctl enable service.service     # Activer au boot
systemctl disable service.service    # Désactiver au boot

# Consultation des logs
journalctl -u service.service        # Logs d'un service
journalctl -f                        # Suivre les logs en temps réel

# État du système
systemctl list-units                 # Lister les unités actives
systemctl list-unit-files            # Lister tous les fichiers d'unités
```

## Ressources officielles

- [Site officiel systemd](https://systemd.io/)
- [Documentation freedesktop.org](https://www.freedesktop.org/software/systemd/man/)
- [Code source GitHub](https://github.com/systemd/systemd)

---

Dans les sections suivantes, nous explorerons en détail chaque aspect de systemd, de l'architecture aux cas d'usage pratiques.
