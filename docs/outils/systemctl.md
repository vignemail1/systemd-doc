# systemctl

`systemctl` est l'outil central de contrôle de systemd. Il permet de gérer les unités (services, timers, sockets, montages…), d'inspecter l'état du système et de contrôler le démon systemd lui-même.

## Syntaxe générale

```bash
systemctl [OPTIONS] COMMANDE [UNITÉ...]
```

## Gestion des unités

### Commandes de base

```bash
# Démarrer / arrêter / redémarrer
systemctl start nginx.service
systemctl stop nginx.service
systemctl restart nginx.service

# Recharger la configuration sans interruption
systemctl reload nginx.service

# Redémarrer seulement si déjà actif
systemctl try-restart nginx.service

# Reload ou restart
systemctl reload-or-restart nginx.service
```

### Activation au démarrage

```bash
# Activer (créer le symlink dans .wants/)
systemctl enable nginx.service

# Activer ET démarrer immédiatement
systemctl enable --now nginx.service

# Désactiver
systemctl disable nginx.service

# Désactiver ET arrêter immédiatement
systemctl disable --now nginx.service

# Masquer (empêche tout démarrage, même manuel)
systemctl mask nginx.service
systemctl unmask nginx.service
```

### État d'une unité

```bash
# Vue d'ensemble avec logs récents
systemctl status nginx.service

# Vérifier rapidement si actif
systemctl is-active nginx.service   # retourne 0 si actif
systemctl is-enabled nginx.service  # retourne 0 si activé
systemctl is-failed nginx.service   # retourne 0 si en échec
```

## Inspection et listing

### Lister les unités

```bash
# Toutes les unités chargées
systemctl list-units

# Filtrer par type
systemctl list-units --type=service
systemctl list-units --type=timer
systemctl list-units --type=socket

# Afficher aussi les inactives
systemctl list-units --all

# Unités en échec
systemctl list-units --state=failed

# Unités chargées mais inactives
systemctl list-units --state=inactive
```

### Lister les fichiers d'unités

```bash
# Tous les fichiers d'unités (actifs ou non)
systemctl list-unit-files

# Filtrer par type
systemctl list-unit-files --type=service

# Filtrer par état
systemctl list-unit-files --state=enabled
systemctl list-unit-files --state=disabled
systemctl list-unit-files --state=masked
```

### Dépendances

```bash
# Arbre des dépendances d'une unité
systemctl list-dependencies nginx.service

# Dépendances inverses (qui dépend de cette unité ?)
systemctl list-dependencies --reverse nginx.service

# Dépendances récursives
systemctl list-dependencies --all nginx.service
```

### Jobs en cours

```bash
# Lister les jobs actifs (démarrages/arrêts en cours)
systemctl list-jobs
```

## Affichage des propriétés

```bash
# Toutes les propriétés d'une unité
systemctl show nginx.service

# Propriété spécifique
systemctl show nginx.service -p MainPID
systemctl show nginx.service -p ActiveState
systemctl show nginx.service -p FragmentPath

# Plusieurs propriétés
systemctl show nginx.service -p MainPID,ActiveState,SubState
```

### Propriétés utiles

| Propriété | Description |
| --------- | ----------- |
| `ActiveState` | active, inactive, failed, activating… |
| `SubState` | running, dead, exited, failed… |
| `MainPID` | PID du processus principal |
| `ExecMainStartTimestamp` | Date de dernier démarrage |
| `FragmentPath` | Chemin du fichier .service |
| `UnitFileState` | enabled, disabled, masked… |
| `NRestarts` | Nombre de redémarrages |
| `MemoryCurrent` | Mémoire consommée (cgroups) |
| `CPUUsageNSec` | Temps CPU consommé |

## Contenu des fichiers d'unités

```bash
# Afficher le contenu du fichier d'unité
systemctl cat nginx.service

# Éditer un fichier d'unité (crée un override dans /etc/systemd/system/)
systemctl edit nginx.service

# Éditer le fichier complet (pas seulement un override)
systemctl edit --full nginx.service

# Après modification, recharger la configuration systemd
systemctl daemon-reload
```

!!! tip "Overrides"
    `systemctl edit` crée un fichier `/etc/systemd/system/nginx.service.d/override.conf`
    qui ne remplace que les directives modifiées, sans toucher au fichier d'origine.
    C'est la méthode recommandée pour personnaliser des unités système.

## Mode utilisateur (`--user`)

Systemd peut fonctionner en mode utilisateur, avec une instance par utilisateur gérant les services dans `~/.config/systemd/user/`.

```bash
# Toutes les commandes précédentes s'appliquent avec --user
systemctl --user start monservice.service
systemctl --user enable --now monservice.service
systemctl --user status monservice.service
systemctl --user list-units --type=service

# Recharger la configuration utilisateur
systemctl --user daemon-reload

# Afficher les variables d'environnement de l'instance utilisateur
systemctl --user show-environment
systemctl --user set-environment VAR=valeur
systemctl --user unset-environment VAR
```

## Opérations à distance

```bash
# Opérer sur un hôte distant (via SSH)
systemctl -H user@serveur.example.com status nginx
systemctl -H root@192.168.1.10 restart postgresql

# Opérer dans un conteneur systemd-nspawn
systemctl -M monconteneur status nginx
```

## Gestion du système

```bash
# Recharger la configuration de systemd (après modification de fichiers d'unités)
systemctl daemon-reload

# Ré-exécuter le démon systemd (sans tuer les services)
systemctl daemon-reexec

# Annuler les jobs en attente
systemctl cancel
```

### États d'alimentation

```bash
systemctl poweroff     # Arrêt
systemctl reboot       # Redémarrage
systemctl suspend      # Suspension
systemctl hibernate    # Hibernation
systemctl hybrid-sleep # Hybride (suspend + hibernate)
systemctl halt         # Arrêt sans extinction (rarement utilisé)
```

### Changer de target

```bash
# Basculer vers un target (équivalent des runlevels SysV)
systemctl isolate multi-user.target
systemctl isolate graphical.target
systemctl isolate rescue.target

# Définir le target par défaut
systemctl set-default multi-user.target
systemctl get-default
```

## Options globales utiles

| Option | Description |
| ------ | ----------- |
| `--user` | Opérer sur l'instance utilisateur |
| `--system` | Opérer sur l'instance système (défaut) |
| `-H <host>` | Hôte distant |
| `-M <container>` | Machine/conteneur |
| `--no-pager` | Désactiver le paginateur |
| `--no-legend` | Supprimer les en-têtes |
| `--plain` | Sortie sans couleur ni arbre |
| `-q` | Mode silencieux |
| `--now` | Combiné à enable/disable |
| `--force` | Forcer (ex: enable sans symlink) |
| `-p <prop>` | Filtrer sur une propriété |
| `--state <état>` | Filtrer par état |
| `--type <type>` | Filtrer par type d'unité |
| `--all` | Inclure les inactifs |

## Voir aussi

- [Gestion des services](../gestion-services/index.md)
- [Unités systemd](../unites/index.md)
- [systemd-analyze](systemd-analyze.md) — performances et débogage
- `man systemctl`
