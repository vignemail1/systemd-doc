# cgroups

Les **cgroups** (*control groups*) sont un mécanisme du noyau Linux permettant d'organiser les processus en groupes hiérarchiques et d'appliquer des **limites de ressources** (CPU, mémoire, I/O, processus) à chacun de ces groupes. systemd repose intégralement sur les cgroups : chaque unité de service, slice et scope correspond directement à un cgroup.

!!! note "v1 vs v2"
    Deux versions coexistent. cgroups v1 utilisait des hiérarchies multiples et indépendantes par contrôleur. cgroups v2 (Linux 4.5+) unifie tout dans une hiérarchie unique, simplifie la délégation et apporte PSI (Pressure Stall Information). Les distributions modernes — Debian 11+, Ubuntu 21.10+, RHEL 9+, Arch — utilisent le mode `unified` (v2 exclusif) par défaut. systemd fonctionne dans les deux modes mais ses fonctionnalités les plus avancées nécessitent v2.

## Hiérarchie et montage

En mode unifié (v2), cgroupfs est monté en un seul point :

```bash
mount | grep cgroup
# cgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot)
```

Chaque répertoire sous `/sys/fs/cgroup/` est un cgroup. Les fichiers à l'intérieur exposent l'état et les paramètres du groupe.

```bash
# Voir l'arbre complet des cgroups (avec systemd)
systemd-cgls

# Voir l'utilisation en temps réel
systemd-cgtop

# Naviguer directement dans le VFS
ls /sys/fs/cgroup/system.slice/sshd.service/
```

### Fichiers pseudo-FS communs à tous les cgroups

| Fichier | Contenu |
| ------- | ------- |
| `cgroup.procs` | PIDs des processus membres (lecture/écriture) |
| `cgroup.controllers` | Contrôleurs disponibles sur ce cgroup |
| `cgroup.subtree_control` | Contrôleurs activés pour les enfants |
| `cgroup.type` | `domain`, `domain threaded`, `threaded` |
| `cgroup.events` | Événements : `populated`, `frozen` |
| `cgroup.kill` | Écrire `1` tue tous les processus du groupe |

## Contrôleurs disponibles (v2)

| Contrôleur | Ressource gérée | Fichiers clés |
| ---------- | --------------- | ------------- |
| `cpu` | Part CPU et quota dur | `cpu.weight`, `cpu.max`, `cpu.stat` |
| `memory` | Mémoire anonyme et cache page | `memory.max`, `memory.high`, `memory.current`, `memory.events` |
| `io` | Bande passante et IOPS disque | `io.weight`, `io.max`, `io.stat` |
| `pids` | Nombre de processus/threads | `pids.max`, `pids.current` |
| `cpuset` | Affinité CPU et nœuds NUMA | `cpuset.cpus`, `cpuset.mems` |
| `rdma` | Ressources RDMA/InfiniBand | `rdma.max`, `rdma.current` |
| `misc` | Ressources hétérogènes (DMA-BUF…) | `misc.max`, `misc.current` |

### Vérifier les contrôleurs actifs sur le système

```bash
cat /sys/fs/cgroup/cgroup.controllers
# cpu io memory pids

# Contrôleurs délégués aux enfants au niveau racine
cat /sys/fs/cgroup/cgroup.subtree_control
```

## Contrôleur `cpu`

### Poids relatif (time-sharing)

`cpu.weight` exprime une part relative entre frères. La valeur par défaut est `100`. Un service avec `cpu.weight=200` obtiendra le double de CPU qu'un service à `100` lorsque la contention est forte.

```bash
cat /sys/fs/cgroup/system.slice/nginx.service/cpu.weight
# 100
```

### Quota dur (hard throttling)

`cpu.max` est au format `quota période` en microsecondes. La valeur `max` signifie aucune limite.

```bash
# Lire la limite actuelle d'un service
cat /sys/fs/cgroup/system.slice/nginx.service/cpu.max
# max 100000

# Lire les stats d'utilisation et de throttling
cat /sys/fs/cgroup/system.slice/nginx.service/cpu.stat
# usage_usec 4521389
# user_usec  3211004
# system_usec 1310385
# nr_periods  4521
# nr_throttled 12
# throttled_usec 8204
```

## Contrôleur `memory`

| Fichier | Rôle |
| ------- | ---- |
| `memory.current` | Usage actuel (octets) |
| `memory.max` | Limite dure — déclenche OOM-kill si dépassée |
| `memory.high` | Limite souple — déclenche throttling et réclamation de pages |
| `memory.min` | Réservation : ces pages ne sont jamais réclamées |
| `memory.low` | Priorité de protection : réclamées en dernier |
| `memory.swap.max` | Limite d'utilisation du swap |
| `memory.events` | Compteurs : `oom`, `oom_kill`, `high`, `max` |
| `memory.pressure` | PSI — saturation mémoire |

```bash
# Usage mémoire d'un service
cat /sys/fs/cgroup/system.slice/postgresql.service/memory.current

# Nombre d'OOM kills depuis le démarrage
grep oom_kill /sys/fs/cgroup/system.slice/postgresql.service/memory.events
```

## Contrôleur `io`

`io.weight` fonctionne comme `cpu.weight` : part relative entre groupes frères lorsque le disque est saturé.

`io.max` limite les débits et/ou le nombre d'opérations par seconde, au format `MAJ:MIN rbps=N wbps=N riops=N wiops=N` :

```bash
# Lire les stats I/O d'un service
cat /sys/fs/cgroup/system.slice/postgresql.service/io.stat
# 8:0 rbytes=204800 wbytes=1048576 rios=50 wios=256 dbytes=0 dios=0
```

## Contrôleur `pids`

Limite le nombre total de processus et threads dans le cgroup, agissant comme protection contre les fork bombs :

```bash
cat /sys/fs/cgroup/system.slice/apache2.service/pids.max
# 512
cat /sys/fs/cgroup/system.slice/apache2.service/pids.current
# 48
```

## PSI — Pressure Stall Information

Linux 4.20+ expose pour chaque contrôleur un fichier `*.pressure` indiquant le pourcentage de temps pendant lequel des tâches ont été bloquées en attente de la ressource.

```bash
# Pression mémoire sur un service
cat /sys/fs/cgroup/system.slice/mon-service.service/memory.pressure
# some avg10=0.12 avg60=0.03 avg300=0.01 total=1234567
# full avg10=0.00 avg60=0.00 avg300=0.00 total=0
```

- `some` : au moins une tâche était bloquée
- `full` : **toutes** les tâches étaient bloquées (saturation totale)
- `avg10/avg60/avg300` : moyennes glissantes en pourcentage sur 10 s, 1 min, 5 min

```bash
# Pression I/O système globale
cat /proc/pressure/io
```

## Intégration systemd

### Directives de ressources dans les unités

| Directive systemd | Contrôleur cgroup | Fichier cgroupfs |
| ----------------- | ----------------- | ---------------- |
| `CPUWeight=` | `cpu` | `cpu.weight` |
| `CPUQuota=` | `cpu` | `cpu.max` |
| `MemoryMax=` | `memory` | `memory.max` |
| `MemoryHigh=` | `memory` | `memory.high` |
| `MemoryMin=` | `memory` | `memory.min` |
| `MemoryLow=` | `memory` | `memory.low` |
| `MemorySwapMax=` | `memory` | `memory.swap.max` |
| `IOWeight=` | `io` | `io.weight` |
| `IOReadBandwidthMax=` | `io` | `io.max` |
| `IOWriteBandwidthMax=` | `io` | `io.max` |
| `IOReadIOPSMax=` | `io` | `io.max` |
| `IOWriteIOPSMax=` | `io` | `io.max` |
| `TasksMax=` | `pids` | `pids.max` |
| `AllowedCPUs=` | `cpuset` | `cpuset.cpus` |
| `AllowedMemoryNodes=` | `cpuset` | `cpuset.mems` |

### Exemple d'unité avec limites de ressources

```ini
[Unit]
Description=Serveur applicatif Java

[Service]
User=appuser
ExecStart=/opt/app/bin/start.sh

# CPU : 50 % d'un cœur au maximum, poids relatif réduit
CPUQuota=50%
CPUWeight=50

# Mémoire : throttling à 512 Mo, OOM-kill à 768 Mo
MemoryHigh=512M
MemoryMax=768M
MemorySwapMax=0

# I/O : limiter l'écriture sur /dev/sda (identifier le device avec lsblk)
IOWriteBandwidthMax=/dev/sda 20M

# Nombre de processus/threads maximum
TasksMax=128

[Install]
WantedBy=multi-user.target
```

### Modifier les limites à chaud avec `systemctl set-property`

Les limites de ressources peuvent être ajustées sans redémarrer le service :

```bash
# Augmenter la limite mémoire à chaud
sudo systemctl set-property mon-service.service MemoryMax=1G

# Limiter le quota CPU à 25 %
sudo systemctl set-property mon-service.service CPUQuota=25%

# Appliquer de manière non persistante (annulé au redémarrage)
sudo systemctl set-property --runtime mon-service.service MemoryHigh=256M

# Voir les propriétés actuelles
systemctl show mon-service.service -p MemoryMax -p CPUQuota -p TasksMax
```

!!! tip "Persistance"
    Sans `--runtime`, `set-property` écrit un fichier drop-in dans `/etc/systemd/system/mon-service.service.d/50-CPUQuota.conf`. Ces fichiers sont visibles avec `systemctl cat mon-service.service`.

## Slices

Les **slices** forment l'ossature de l'arbre cgroup de systemd. Elles regroupent des services partageant une même politique de ressources.

```
systemd (root)
├── system.slice      ← services système
│   ├── nginx.service
│   └── postgresql.service
├── user.slice        ← sessions utilisateurs
│   └── user-1000.slice
│       └── session-3.scope
└── machine.slice     ← VMs et containers nspawn/podman
    └── mon-container.scope
```

```bash
# Rattacher un service à une slice dédiée
# /etc/systemd/system/mon-service.service
# [Service]
# Slice=app.slice

# Créer une slice avec des limites qui s'appliquent à tous ses enfants
# /etc/systemd/system/app.slice
# [Slice]
# MemoryMax=4G
# CPUWeight=200
```

## Délégation

La délégation (`Delegate=yes`) transfère le contrôle d'un sous-arbre cgroup à un processus non-root — typiquement un gestionnaire de containers rootless.

```ini
[Service]
User=podman-user
Delegate=yes
DelegateControllers=cpu memory pids io
ExecStart=/usr/bin/podman start --log-driver=journald mon-container
```

!!! warning "Sécurité de la délégation"
    Un cgroup délégué peut positionner ses propres limites, mais ne peut pas dépasser celles définies par le parent. La délégation ne donne pas accès aux cgroups frères. Vérifier que le service ne dispose pas de capabilities permettant de modifier des cgroups hors de son sous-arbre.

```bash
# Vérifier qu'une délégation est en place
systemctl show podman.service -p Delegate -p DelegateControllers
```

## Monitoring

### `systemd-cgtop`

```bash
# Vue temps réel de l'utilisation par cgroup
systemd-cgtop

# Trier par mémoire
systemd-cgtop --order=memory

# Rafraîchissement toutes les 2 secondes, 5 itérations
systemd-cgtop --delay=2 --iterations=5
```

### `systemctl status`

`systemctl status` inclut les statistiques cgroup du processus principal :

```bash
systemctl status postgresql.service
# ● postgresql.service - PostgreSQL RDBMS
#   ...
#   Memory: 156.3M (max: 512.0M available: 355.6M)
#   CPU: 1.234s
#   CGroup: /system.slice/postgresql.service
#           └─1234 /usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/15/main
```

### Lecture directe pour le scripting

```bash
# Usage mémoire en octets d'un service
cat /sys/fs/cgroup/system.slice/nginx.service/memory.current

# Part CPU consommée depuis le démarrage (en microsecondes)
grep usage_usec /sys/fs/cgroup/system.slice/nginx.service/cpu.stat

# Nombre de processus dans un service
cat /sys/fs/cgroup/system.slice/nginx.service/pids.current

# Lister tous les PIDs d'un service
cat /sys/fs/cgroup/system.slice/nginx.service/cgroup.procs
```

## Diagnostics courants

### Service tué par l'OOM killer

```bash
# Voir le statut et les derniers messages du service
systemctl status mon-service.service

# Compter les OOM kills depuis le démarrage
grep oom_kill /sys/fs/cgroup/system.slice/mon-service.service/memory.events

# Chercher dans le journal
journalctl -u mon-service.service -g 'oom|OOM|killed'

# Voir l'event noyau
journalctl -k -g 'oom_kill'
```

### Service throttlé sur le CPU

```bash
# Vérifier si le service subit du throttling
cat /sys/fs/cgroup/system.slice/mon-service.service/cpu.stat
# Si nr_throttled > 0, le service est limité par CPUQuota=

# Voir la valeur actuelle du quota
systemctl show mon-service.service -p CPUQuota
```

### `TasksMax` atteint — fork impossible

```bash
# Voir l'événement dans le journal
journalctl -u mon-service.service -g 'fork|Tasks'

# Voir la limite et l'usage actuels
cat /sys/fs/cgroup/system.slice/mon-service.service/pids.max
cat /sys/fs/cgroup/system.slice/mon-service.service/pids.current

# Augmenter la limite
sudo systemctl set-property mon-service.service TasksMax=256
```

### Identifier le cgroup d'un processus

```bash
# Depuis le PID
cat /proc/1234/cgroup
# 0::/system.slice/nginx.service

# Voir les limites qui s'appliquent au processus
PID=1234
CGROUP=$(cat /proc/${PID}/cgroup | cut -d: -f3)
ls "/sys/fs/cgroup${CGROUP}/"
```

### Migration d'un système v1/v2 hybride

```bash
# Vérifier le mode cgroup actif
mount | grep cgroup

# Forcer le mode unifié v2 (paramètre noyau à ajouter dans le bootloader)
# systemd.unified_cgroup_hierarchy=1
```

## Bonnes pratiques

- **Toujours définir `MemoryMax=`** sur les services produisant de la charge variable — un service sans limite peut épuiser la mémoire du système entier.
- **Utiliser `MemoryHigh=` comme garde-fou** avant `MemoryMax=` : le throttling progressif évite les OOM kills brutaux.
- **Surveiller PSI** plutôt que d'attendre les OOM events pour détecter une saturation naissante.
- **Préférer les slices** pour appliquer des politiques groupées plutôt que de dupliquer les directives dans chaque service.
- **Ne pas déléguer sans restriction explicite** : préciser `DelegateControllers=` pour limiter ce que le processus délégué peut modifier.
- **Tester les limites en environnement de staging** : `MemoryMax=` trop bas peut tuer un service en production lors d'un pic de charge légitime.

## Voir aussi

- [namespaces](namespaces.md) — isolation de vue des ressources, complémentaire aux cgroups
- [capabilities](capabilities.md) — permissions nécessaires pour modifier des cgroups hors délégation
- [systemd-nspawn](../outils/systemd-nspawn.md) — containers légers avec cgroups et namespaces
- `man 7 cgroups` — référence noyau complète
- `man 5 systemd.resource-control` — toutes les directives de contrôle de ressources
- `man 1 systemd-cgls` et `man 1 systemd-cgtop`
- [Documentation kernel cgroups v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
