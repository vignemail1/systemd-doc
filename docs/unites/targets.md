# Targets (.target)

Les **targets** sont des unités de groupement qui représentent un état du système. Ils remplacent les runlevels de SysVinit et permettent de synchroniser le démarrage de plusieurs unités.

## Concept des targets

Un target n'exécute rien par lui-même. C'est un point de synchronisation qui :

- **Groupe** plusieurs unités ensemble
- **Représente** un état ou une étape du système
- **Permet** d'activer/désactiver plusieurs services en une commande
- **Définit** des dépendances entre groupes d'unités

## Targets système principaux

### poweroff.target

Arrêt du système.

```bash
systemctl isolate poweroff.target
# Équivalent à
systemctl poweroff
```

### rescue.target

Mode rescue (single-user), équivalent au runlevel 1 de SysVinit.

```bash
systemctl isolate rescue.target
# Équivalent à
systemctl rescue
```

Caractéristiques :
- Shell root unique
- Services minimaux
- Système de fichiers monté
- Pas de réseau

### multi-user.target

Mode multi-utilisateur complet sans interface graphique, équivalent au runlevel 3.

```bash
systemctl isolate multi-user.target
```

C'est le target standard pour les serveurs.

### graphical.target

Mode graphique complet, équivalent au runlevel 5.

```bash
systemctl isolate graphical.target
```

Inclut tout ce qui est dans `multi-user.target` plus l'environnement graphique.

### reboot.target

Redémarrage du système.

```bash
systemctl isolate reboot.target
# Équivalent à
systemctl reboot
```

### emergency.target

Mode d'urgence, encore plus minimal que rescue.

```bash
systemctl isolate emergency.target
# Équivalent à
systemctl emergency
```

Caractéristiques :
- Shell root
- Système de fichiers root en lecture seule
- Aucun service
- Pour réparations critiques

## Correspondance runlevels SysVinit

| SysVinit | systemd | Description |
|----------|---------|-------------|
| runlevel 0 | poweroff.target | Arrêt |
| runlevel 1 | rescue.target | Mode rescue |
| runlevel 2,3,4 | multi-user.target | Multi-utilisateur |
| runlevel 5 | graphical.target | Graphique |
| runlevel 6 | reboot.target | Redémarrage |

## Targets de boot

### sysinit.target

Initialisation système de base (montage filesystems, swap, etc.).

### basic.target

Services de base du système (après sysinit.target).

### network.target

Réseau configuré et disponible.

!!! warning "Attention"
    `network.target` ne garantit pas que le réseau est complètement opérationnel, seulement que la configuration a démarré.

### network-online.target

Réseau complètement opérationnel et connecté.

```ini
[Unit]
After=network-online.target
Wants=network-online.target
```

Utiliser pour les services nécessitant une connectivité réseau active.

### time-sync.target

Horloge système synchronisée.

### remote-fs.target

Systèmes de fichiers distants montés (NFS, CIFS, etc.).

### local-fs.target

Systèmes de fichiers locaux montés.

## Targets de services

### sockets.target

Tous les sockets activés.

### timers.target

Tous les timers activés.

### paths.target

Tous les path units activés.

## Structure d'un fichier target

```ini
[Unit]
Description=Mon Target Personnalisé
Requires=basic.target
After=basic.target
Conflicts=rescue.target

# Pas de section [Target] dans la plupart des cas

[Install]
WantedBy=multi-user.target
```

Les targets sont généralement très simples, contenant surtout des métadonnées et dépendances.

## Créer un target personnalisé

### Exemple : target pour services web

```ini
# /etc/systemd/system/webstack.target
[Unit]
Description=Web Stack (Nginx + PHP-FPM + PostgreSQL)
Requires=nginx.service php-fpm.service postgresql.service
After=network-online.target
Wants=network-online.target

[Install]
WantedBy=multi-user.target
```

Utilisation :
```bash
# Activer
systemctl enable webstack.target

# Démarrer tous les services du stack
systemctl start webstack.target

# Arrêter tous les services
systemctl stop webstack.target
```

### Exemple : target pour environnement de développement

```ini
# /etc/systemd/system/devenv.target
[Unit]
Description=Development Environment
Requires=postgresql.service redis.service docker.service
After=multi-user.target

[Install]
WantedBy=multi-user.target
```

## Isolation de targets

La commande `isolate` permet de passer à un target en arrêtant tous les services non nécessaires :

```bash
# Passer en mode multi-user (arrête l'interface graphique)
systemctl isolate multi-user.target

# Revenir en mode graphique
systemctl isolate graphical.target
```

!!! warning "Attention avec isolate"
    `isolate` arrête tous les services qui ne sont pas requis par le target cible. À utiliser avec précaution en production.

## Voir et gérer les targets

### Lister les targets

```bash
# Tous les targets chargés
systemctl list-units --type=target

# Tous les targets disponibles
systemctl list-unit-files --type=target

# Targets actifs
systemctl list-units --type=target --state=active
```

### Target par défaut

```bash
# Voir le target par défaut au boot
systemctl get-default

# Changer le target par défaut
systemctl set-default multi-user.target
systemctl set-default graphical.target
```

Cela crée un lien symbolique : `/etc/systemd/system/default.target` → `multi-user.target`

### Dépendances d'un target

```bash
# Voir ce qui est requis par le target
systemctl list-dependencies multi-user.target

# Avec plus de détails
systemctl list-dependencies --all multi-user.target

# Dépendances inverses (qui dépend du target)
systemctl list-dependencies --reverse multi-user.target
```

## Boot vers un target spécifique

### Temporairement (une seule fois)

Ajouter à la ligne de boot du kernel :

```
systemd.unit=rescue.target
systemd.unit=multi-user.target
systemd.unit=emergency.target
```

Dans GRUB, appuyer sur `e` pour éditer et ajouter à la ligne `linux`.

### En permanence

```bash
systemctl set-default rescue.target
```

## Cas d'usage pratiques

### Grouper des services de production

```ini
# /etc/systemd/system/production-stack.target
[Unit]
Description=Production Stack
Requires=nginx.service
Requires=gunicorn.service
Requires=postgresql.service
Requires=redis.service
Requires=celery.service
After=network-online.target
Wants=network-online.target

[Install]
WantedBy=multi-user.target
```

```bash
# Gérer tout le stack en une commande
systemctl start production-stack.target
systemctl status production-stack.target
systemctl restart production-stack.target
```

### Target conditionnel

```ini
# /etc/systemd/system/monitoring.target
[Unit]
Description=Monitoring Services
ConditionPathExists=/etc/monitoring/enabled
Requires=prometheus.service
Requires=grafana.service
Requires=alertmanager.service

[Install]
WantedBy=multi-user.target
```

Le target ne s'active que si `/etc/monitoring/enabled` existe.

### Target pour backup

```ini
# /etc/systemd/system/backup-services.target
[Unit]
Description=Backup Services
Requires=backup-database.service
Requires=backup-files.service
Requires=backup-logs.service

[Install]
WantedBy=multi-user.target
```

Peut être déclenché par un timer :

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily Backup

[Timer]
OnCalendar=daily
Persistent=true
Unit=backup-services.target

[Install]
WantedBy=timers.target
```

## Options avancées

### Section [Target]

Rarement utilisée, mais existe :

```ini
[Target]
DefaultDependencies=no
```

**DefaultDependencies=no** : Désactive les dépendances implicites (jobs, shutdown, etc.). Utile pour les targets système de bas niveau.

### Conflicts

Définir des targets incompatibles :

```ini
[Unit]
Conflicts=rescue.target emergency.target
```

Empêche le target d'être actif si rescue ou emergency est actif.

## Debugging

### Voir l'état d'un target

```bash
systemctl status multi-user.target
```

### Identifier pourquoi un target n'est pas actif

```bash
# Vérifier les dépendances
systemctl list-dependencies multi-user.target --failed

# Voir les services en échec
systemctl --failed
```

### Analyser le graphe de dépendances

```bash
# Générer un graphe DOT
systemd-analyze dot multi-user.target > multi-user.dot

# Convertir en SVG
dot -Tsvg multi-user.dot > multi-user.svg
```

## Bonnes pratiques

1. **Nommer clairement** : Utiliser des noms explicites pour les targets personnalisés
2. **Documenter** : Ajouter une description claire
3. **Utiliser Wants vs Requires** : Préférer `Wants=` pour des dépendances non critiques
4. **Éviter l'isolation en production** : `isolate` peut arrêter des services importants
5. **Tester** : Valider les targets personnalisés avant déploiement en production
6. **Grouper logiquement** : Créer des targets pour des ensembles cohérents de services

## Exemples de la vie réelle

### Target Kubernetes

```ini
# /etc/systemd/system/k8s-node.target
[Unit]
Description=Kubernetes Node Services
Requires=docker.service
Requires=kubelet.service
Requires=kube-proxy.service
After=network-online.target
Wants=network-online.target

[Install]
WantedBy=multi-user.target
```

### Target base de données

```ini
# /etc/systemd/system/database-cluster.target
[Unit]
Description=Database Cluster
Requires=postgresql-primary.service
Requires=postgresql-replica1.service
Requires=postgresql-replica2.service
Requires=pgbouncer.service
After=network-online.target

[Install]
WantedBy=multi-user.target
```

Les targets sont essentiels pour organiser et gérer des ensembles complexes de services dans systemd. Ils offrent une flexibilité bien supérieure aux anciens runlevels de SysVinit.
