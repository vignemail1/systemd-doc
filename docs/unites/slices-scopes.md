# Slices et Scopes

Les **slices** (`.slice`) et **scopes** (`.scope`) sont des unités spéciales qui organisent hiérarchiquement les processus pour la gestion des ressources via cgroups.

## Slices (.slice)

Les slices créent une hiérarchie de groupes de ressources. Elles servent à :

- **Organiser** les services en groupes logiques
- **Limiter** les ressources (CPU, mémoire, I/O) par groupe
- **Isoler** différents types de charges de travail
- **Monitorer** l'utilisation des ressources par groupe

### Hiérarchie par défaut

systemd crée automatiquement trois slices racines :

```
-.slice (root)
├── system.slice       # Services système
├── user.slice          # Sessions utilisateur
└── machine.slice       # Conteneurs et VMs
```

### Nommage hiérarchique

Les slices utilisent une notation hiérarchique avec `-` :

```
parent-child.slice
parent-child-grandchild.slice

Exemples:
system.slice
system-app.slice
system-app-web.slice
```

### Structure d'un fichier .slice

```ini
[Unit]
Description=Applications Slice
Before=slices.target

[Slice]
CPUQuota=50%
MemoryLimit=4G
TasksMax=500
```

## Section [Slice]

Les options de ressources disponibles :

### Limites CPU

**CPUQuota**
: Pourcentage de CPU alloué

```ini
CPUQuota=50%      # 50% d'un core
CPUQuota=200%     # 2 cores complets
CPUQuota=400%     # 4 cores complets
```

**CPUWeight**
: Poids relatif du CPU (1-10000, défaut 100)

```ini
CPUWeight=100     # Poids normal
CPUWeight=500     # 5x plus de CPU en cas de contention
CPUWeight=1000    # 10x plus
```

**CPUAccounting**
: Activer la comptabilité CPU

```ini
CPUAccounting=yes
```

### Limites mémoire

**MemoryMax**
: Limite maximale de mémoire (hard limit)

```ini
MemoryMax=2G
MemoryMax=512M
MemoryMax=50%     # 50% de la RAM
```

**MemoryHigh**
: Seuil d'avertissement (soft limit)

```ini
MemoryHigh=1.5G
```

**MemorySwapMax**
: Limite de swap

```ini
MemorySwapMax=1G
MemorySwapMax=0   # Pas de swap
```

### Limites I/O

**IOWeight**
: Poids relatif des I/O (1-10000)

```ini
IOWeight=500
```

**IOReadBandwidthMax** / **IOWriteBandwidthMax**
: Limite de bande passante I/O

```ini
IOReadBandwidthMax=/dev/sda 50M
IOWriteBandwidthMax=/dev/sda 20M
```

### Limites de processus

**TasksMax**
: Nombre maximum de tâches (threads/processus)

```ini
TasksMax=500
TasksMax=50%
TasksMax=infinity
```

## Exemples de slices

### Slice pour applications web

```ini
# /etc/systemd/system/system-webapps.slice
[Unit]
Description=Web Applications Slice
Before=slices.target

[Slice]
CPUQuota=200%
MemoryMax=8G
TasksMax=1000
CPUAccounting=yes
MemoryAccounting=yes
```

Utiliser dans un service :
```ini
# /etc/systemd/system/webapp.service
[Service]
Slice=system-webapps.slice
ExecStart=/usr/bin/webapp
```

### Slice pour bases de données

```ini
# /etc/systemd/system/system-databases.slice
[Unit]
Description=Database Services Slice
Before=slices.target

[Slice]
CPUWeight=1000        # Haute priorité
MemoryMax=16G
MemoryHigh=14G        # Warning à 14G
IOWeight=1000         # I/O prioritaire
TasksMax=2000
```

### Slice pour tâches de fond

```ini
# /etc/systemd/system/system-background.slice
[Unit]
Description=Background Tasks Slice
Before=slices.target

[Slice]
CPUQuota=25%          # Limité à 25%
CPUWeight=10          # Basse priorité
MemoryMax=2G
IOWeight=10           # I/O basse priorité
```

### Slice utilisateur personnalisé

```ini
# /etc/systemd/system/user-developer.slice
[Unit]
Description=Developer User Slice
Before=slices.target

[Slice]
CPUQuota=400%         # 4 cores
MemoryMax=32G
TasksMax=infinity
```

Assigner à un utilisateur :
```bash
# Dans /etc/systemd/system/user@1000.service.d/slice.conf
[Service]
Slice=user-developer.slice
```

### Hiérarchie multi-niveaux

```ini
# Slice parent
# /etc/systemd/system/system-production.slice
[Slice]
MemoryMax=20G

# Slice enfant
# /etc/systemd/system/system-production-frontend.slice
[Slice]
MemoryMax=8G   # Max 8G du parent

# Slice petit-enfant
# /etc/systemd/system/system-production-frontend-nginx.slice
[Slice]
MemoryMax=4G   # Max 4G de son parent
```

## Scopes (.scope)

Les scopes sont des unités créées **programmatiquement** (pas de fichiers manuels) pour grouper des processus externes lancés en dehors de systemd.

### Caractéristiques

- **Création dynamique** : Via D-Bus ou `systemd-run`
- **Pas de configuration** : Pas de fichiers `.scope` manuels
- **Sessions utilisateur** : Principalement utilisés pour les sessions
- **Processus externes** : Pour grouper des processus non-systemd

### Exemples de scopes

Scopes créés automatiquement :

```bash
# Sessions utilisateur
session-1.scope
session-2.scope

# Processus de connexion
user@1000.service
```

Lister les scopes :
```bash
systemctl list-units --type=scope
```

### Créer un scope avec systemd-run

```bash
# Lancer un processus dans un scope
systemd-run --scope \
    --unit=myapp-scope \
    --slice=system-webapps.slice \
    --property=MemoryMax=1G \
    --property=CPUQuota=50% \
    /usr/bin/myapp
```

### Créer un scope via D-Bus (programmatique)

En Python :
```python
import dbus

bus = dbus.SystemBus()
systemd = bus.get_object('org.freedesktop.systemd1',
                         '/org/freedesktop/systemd1')
manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')

# Créer un scope
props = [
    ('MemoryMax', dbus.UInt64(1024*1024*1024)),  # 1GB
    ('CPUQuota', dbus.UInt64(50)),  # 50%
]

pids = [1234, 5678]  # PIDs à grouper

manager.StartTransientUnit(
    'myapp.scope',
    'fail',
    props,
    [(pids, dbus.Array([], signature='(sv)'))]
)
```

## Gestion des slices

### Commandes de base

```bash
# Lister les slices
systemctl list-units --type=slice

# Voir l'arborescence
systemd-cgls

# Arborescence avec ressources
systemd-cgtop

# Statut d'une slice
systemctl status system-webapps.slice

# Propriétés
systemctl show system-webapps.slice
```

### Voir la hiérarchie cgroups

```bash
# Arborescence complète
systemd-cgls

# Slice spécifique
systemd-cgls system-webapps.slice

# Format arbre avec PID
systemd-cgls -u webapp.service
```

### Monitorer les ressources

```bash
# Vue top-like des cgroups
systemd-cgtop

# Rafraîchissement automatique
systemd-cgtop -d 1

# Trier par CPU
systemd-cgtop --order=cpu

# Trier par mémoire
systemd-cgtop --order=memory
```

## Assigner des services à des slices

### Dans le fichier service

```ini
[Service]
Slice=system-webapps.slice
ExecStart=/usr/bin/webapp
```

### Avec un override

```bash
systemctl edit webapp.service
```

Ajouter :
```ini
[Service]
Slice=system-webapps.slice
```

### Temporairement avec systemd-run

```bash
systemd-run \
    --slice=system-background.slice \
    --unit=backup-temp \
    /usr/local/bin/backup.sh
```

## Limites dynamiques

Modifier les limites d'une slice en cours d'exécution :

```bash
# Changer la limite CPU
systemctl set-property system-webapps.slice CPUQuota=100%

# Changer la limite mémoire
systemctl set-property system-webapps.slice MemoryMax=4G

# Plusieurs propriétés
systemctl set-property system-webapps.slice \
    CPUQuota=200% \
    MemoryMax=8G \
    TasksMax=1000

# --runtime : temporaire (jusqu'au reboot)
systemctl set-property --runtime system-webapps.slice CPUQuota=50%
```

## Cas d'usage pratiques

### Isolation de charges de travail

```ini
# Production slice - haute priorité
[Slice]
CPUWeight=1000
MemoryMax=80%
IOWeight=1000

# Development slice - basse priorité
[Slice]
CPUWeight=100
MemoryMax=20%
IOWeight=100
```

### Limitation de services gourmands

```ini
# Slice pour compilation
[Slice]
CPUQuota=400%       # Max 4 cores
MemoryMax=8G
TasksMax=1000
```

Assigner :
```bash
systemctl set-property build-service.service \
    Slice=system-build.slice
```

### Protection système

```ini
# Slice pour services critiques
# /etc/systemd/system/system-critical.slice
[Slice]
CPUWeight=2000       # Priorité maximale
MemoryMax=infinity   # Pas de limite
IOWeight=2000
```

Services critiques (sshd, systemd-journald) assignés à cette slice.

## Debugging et monitoring

### Voir l'utilisation actuelle

```bash
# Vue d'ensemble
systemd-cgtop

# Slice spécifique
systemctl status system-webapps.slice

# Métriques détaillées
systemctl show system-webapps.slice | grep -E '(CPU|Memory|Tasks)'
```

### Identifier les processus

```bash
# Processus dans une slice
systemd-cgls system-webapps.slice

# PIDs dans un service
systemctl show webapp.service -p MainPID -p ControlPID
```

### Logs

```bash
# Logs de tous les services d'une slice
journalctl _SYSTEMD_SLICE=system-webapps.slice

# Dernière heure
journalctl _SYSTEMD_SLICE=system-webapps.slice --since "1 hour ago"
```

## Bonnes pratiques

1. **Hiérarchie logique** : Organiser les slices par fonction (web, db, background)
2. **Limites raisonnables** : Ne pas trop restreindre, laisser de la marge
3. **Weights vs Quotas** : Préférer CPUWeight (partage) à CPUQuota (hard limit)
4. **Monitoring** : Utiliser systemd-cgtop régulièrement
5. **Testing** : Tester les limites avant production
6. **Documentation** : Documenter pourquoi chaque limite existe
7. **Accounting** : Activer *Accounting=yes pour le monitoring

## Limites et considérations

### Cgroups v2

Systemd utilise cgroups v2 par défaut sur les systèmes récents. Vérifier :

```bash
stat -fc %T /sys/fs/cgroup/
# cgroup2fs = v2
# tmpfs = v1
```

### Overhead

Les limites de ressources ont un léger overhead. Ne pas créer trop de slices inutiles.

### Héritage

Les limites sont héritées hiérarchiquement. Une slice enfant ne peut pas dépasser son parent.

Les slices et scopes sont essentiels pour la gestion avancée des ressources dans systemd, permettant une isolation et un contrôle précis de l'utilisation CPU, mémoire et I/O.
