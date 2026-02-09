# Slices et Scopes

Les **slices** et **scopes** sont des unités spéciales de systemd qui organisent les processus de manière hiérarchique et permettent de gérer les ressources via les cgroups v2.

## Cgroups et systemd

Les **cgroups** (control groups) sont une fonctionnalité du noyau Linux qui permet de :

- **Limiter** les ressources (CPU, mémoire, I/O)
- **Prioriser** l'allocation des ressources
- **Mesurer** l'utilisation des ressources
- **Contrôler** les processus de manière groupée

systemd organise tous les processus dans une hiérarchie de cgroups via slices, scopes et services.

## Slices (.slice)

Les **slices** organisent les unités en arbre hiérarchique pour la gestion des ressources. Chaque service, scope ou slice enfant hérite des limites de son slice parent.

### Hiérarchie par défaut

```text

-.slice (root)

├── system.slice (services système)
│   ├── sshd.service
│   ├── nginx.service
│   └── postgresql.service
├── user.slice (sessions utilisateur)
│   ├── user-1000.slice
│   │   ├── session-1.scope
│   │   └── user@1000.service
│   └── user-1001.slice
└── machine.slice (conteneurs et VMs)
    ├── docker-abc123.scope
    └── systemd-nspawn@container.service
```text

### Slices système

**-.slice**

: Slice racine, contient tous les autres slices

**system.slice**

: Services système lancés par systemd

**user.slice**

: Services utilisateur et sessions

**machine.slice**

: Conteneurs et machines virtuelles

### Visualiser la hiérarchie

```bash
# Arbre complet des cgroups
systemd-cgls

# Par slice
systemd-cgls system.slice
systemd-cgls user.slice

# Avec utilisation ressources
systemd-cgtop

# Structure
systemctl status
```text

## Créer un slice personnalisé

### Structure d'un slice

```ini
# /etc/systemd/system/myapp.slice
[Unit]
Description=Slice for My Applications
Before=slices.target

[Slice]
CPUQuota=50%
MemoryMax=2G
```text

### Slice pour services web

```ini
# /etc/systemd/system/webservices.slice
[Unit]
Description=Web Services Slice
Before=slices.target

[Slice]
# Limites globales pour tous les services web
CPUQuota=200%        # Max 2 cores
MemoryMax=4G         # Max 4 Go RAM
TasksMax=1000        # Max 1000 processus/threads
```text

Utilisation dans un service :

```ini
# nginx.service
[Unit]
Description=Nginx Web Server

[Service]
Slice=webservices.slice
ExecStart=/usr/sbin/nginx

[Install]
WantedBy=multi-user.target
```text

Tous les services du slice `webservices.slice` partagent les limites.

### Slices imbriqués

```ini
# /etc/systemd/system/production.slice
[Unit]
Description=Production Services

[Slice]
CPUQuota=400%
MemoryMax=16G
```text

```ini
# /etc/systemd/system/production-web.slice
[Unit]
Description=Production Web Services

[Slice]
Slice=production.slice
CPUQuota=200%
MemoryMax=8G
```text

Hiérarchie :

```text
production.slice (4 cores, 16G)
  └── production-web.slice (2 cores, 8G)
      ├── nginx.service
      └── php-fpm.service
```text

## Scopes (.scope)

Les **scopes** groupent des processus externes lancés en dehors de systemd. Contrairement aux services, les scopes ne sont **pas** démarrés par systemd mais par d'autres programmes.

### Création de scopes

Les scopes sont créés **programmatiquement** via l'API D-Bus ou `systemd-run`.

### Exemples de scopes

**Sessions utilisateur**

```text
user-1000.slice
  └── session-1.scope
      ├── bash (PID 1234)
      └── vim (PID 1235)
```text

**Conteneurs Docker**

```text
machine.slice
  └── docker-abc123.scope
      └── processus du conteneur
```text

**Applications graphiques**

```text
user@1000.service
  └── app-firefox-123.scope
      └── firefox (tous les processus)
```text

### Créer un scope avec systemd-run

```bash
# Lancer une commande dans un scope
systemd-run --scope --unit=myapp \

  --slice=user.slice \
  --property=MemoryMax=1G \
  --property=CPUQuota=100% \

  /usr/bin/myapp

# Vérifier
systemctl status myapp.scope
```text

### Scope pour un groupe de processus

```bash
# Lancer plusieurs processus dans le même scope
systemd-run --scope --unit=build-job \

  --property=CPUQuota=400% \

  bash -c 'make -j4'
```text

## Gestion des ressources

### Options de limitation

#### CPU

**CPUWeight**

: Poids relatif du CPU (1-10000, défaut: 100)

```ini
[Slice]
CPUWeight=200  # Double priorité
```text

**CPUQuota**

: Quota absolu de CPU

```ini
[Slice]
CPUQuota=50%    # 0.5 core
CPUQuota=200%   # 2 cores
CPUQuota=400%   # 4 cores
```text

#### Mémoire

**MemoryMin**

: Mémoire minimale garantie

```ini
[Slice]
MemoryMin=512M
```text

**MemoryLow**

: Mémoire protégée (soft limit)

```ini
[Slice]
MemoryLow=1G
```text

**MemoryHigh**

: Seuil de throttling

```ini
[Slice]
MemoryHigh=2G
```text

**MemoryMax**

: Limite stricte

```ini
[Slice]
MemoryMax=4G
```text

**MemorySwapMax**

: Limite d'utilisation du swap

```ini
[Slice]
MemorySwapMax=1G
```text

#### I/O

**IOWeight**

: Poids relatif I/O (1-10000)

```ini
[Slice]
IOWeight=500
```text

**IOReadBandwidthMax** / **IOWriteBandwidthMax**

: Limites de bande passante

```ini
[Slice]
IOReadBandwidthMax=/dev/sda 50M
IOWriteBandwidthMax=/dev/sda 10M
```text

**IOReadIOPSMax** / **IOWriteIOPSMax**

: Limites d'IOPS

```ini
[Slice]
IOReadIOPSMax=/dev/sda 1000
IOWriteIOPSMax=/dev/sda 500
```text

#### Processus

**TasksMax**

: Nombre maximum de tâches (processus + threads)

```ini
[Slice]
TasksMax=500
```text

## Exemples pratiques

### Slice pour environnement de développement

```ini
# /etc/systemd/system/development.slice
[Unit]
Description=Development Environment

[Slice]
CPUQuota=800%        # 8 cores max
MemoryMax=32G        # 32 Go max
TasksMax=5000        # Beaucoup de processus
IOWeight=500         # Priorité I/O moyenne
```text

Services associés :

```ini
# docker.service, postgresql.service, redis.service
[Service]
Slice=development.slice
```text

### Slice pour base de données

```ini
# /etc/systemd/system/database.slice
[Unit]
Description=Database Services

[Slice]
CPUWeight=1000           # Haute priorité CPU
MemoryMin=8G             # Mémoire garantie
MemoryMax=32G            # Limite haute
IOWeight=1000            # Haute priorité I/O
IOReadIOPSMax=/dev/nvme0n1 50000
IOWriteIOPSMax=/dev/nvme0n1 10000
```text

### Slice pour jobs batch

```ini
# /etc/systemd/system/batch.slice
[Unit]
Description=Batch Processing Jobs

[Slice]
CPUWeight=50             # Basse priorité CPU
MemoryMax=16G
IOWeight=100             # Basse priorité I/O
TasksMax=2000
```text

### Limitation utilisateur

```ini
# /etc/systemd/system/user-1000.slice.d/50-limits.conf
[Slice]
CPUQuota=400%       # Max 4 cores pour cet utilisateur
MemoryMax=8G        # Max 8 Go
TasksMax=1000       # Max 1000 processus
```text

## Commandes de gestion

### Lister slices et scopes

```bash
# Tous les slices
systemctl list-units --type=slice

# Tous les scopes
systemctl list-units --type=scope

# Arbre complet
systemd-cgls

# Par slice
systemd-cgls system.slice
```text

### Voir les ressources

```bash
# Vue en temps réel
systemd-cgtop

# Utilisation d'un slice
systemctl status system.slice

# Propriétés
systemctl show system.slice

# Statistiques CPU/mémoire
systemctl show system.slice -p CPUUsageNSec,MemoryCurrent
```text

### Modifier dynamiquement

```bash
# Changer les limites temporairement
systemctl set-property nginx.service CPUQuota=50%
systemctl set-property nginx.service MemoryMax=2G

# Permanent
systemctl set-property --runtime=false nginx.service CPUQuota=50%
```text

### Déplacer un service

```bash
# Changer de slice
systemctl set-property nginx.service Slice=webservices.slice

# Redémarrer pour appliquer
systemctl restart nginx.service
```text

## Monitoring

### systemd-cgtop

Vue en temps réel des ressources par cgroup :

```bash
systemd-cgtop

# Trier par mémoire
systemd-cgtop --order=memory

# Trier par CPU
systemd-cgtop --order=cpu

# Détail I/O
systemd-cgtop --order=io
```text

### systemd-cgls

Arbre des cgroups :

```bash
# Arbre complet
systemd-cgls

# Slice spécifique
systemd-cgls system.slice

# Avec PIDs
systemd-cgls --all
```text

### Métriques détaillées

```bash
# CPU usage (en nanosecondes)
systemctl show nginx.service -p CPUUsageNSec

# Mémoire actuelle
systemctl show nginx.service -p MemoryCurrent

# Tâches actives
systemctl show nginx.service -p TasksCurrent

# I/O
systemctl show nginx.service -p IOReadBytes,IOWriteBytes
```text

## Débogage

### Vérifier les limites

```bash
# Limites configurées
systemctl show myapp.service | grep -E '(CPU|Memory|IO|Tasks)'

# Limites effectives (cgroup)
cat /sys/fs/cgroup/system.slice/myapp.service/cpu.max
cat /sys/fs/cgroup/system.slice/myapp.service/memory.max
```text

### Processus hors limite

```bash
# Voir si un service atteint ses limites
journalctl -u myapp.service | grep -i "limit"

# OOM kills
journalctl -k | grep -i "oom"
```text

### Cgroups v1 vs v2

```bash
# Vérifier la version
stat -fc %T /sys/fs/cgroup/

# cgroup2fs = v2 (unified hierarchy)
# tmpfs = v1 (legacy)
```text

systemd moderne utilise cgroups v2.

## Bonnes pratiques

1. **Organiser par fonction**

```text
   production.slice
     ├── production-web.slice
     ├── production-db.slice
     └── production-cache.slice
```text

2. **Définir MemoryMax**

   ```ini
   MemoryMax=4G  # Prévenir l'OOM
```text

3. **Utiliser CPUWeight pour priorités**

   ```ini
   CPUWeight=1000  # Services critiques
   CPUWeight=100   # Services normaux
   CPUWeight=50    # Batch jobs
```text

4. **Limiter TasksMax**

   ```ini
   TasksMax=500  # Prévenir fork bombs
```text

5. **Monitorer avec systemd-cgtop**

   ```bash
   systemd-cgtop --delay=1
```text

6. **Documenter les slices**

   ```ini
   [Unit]
   Description=Clear purpose of this slice
```text

7. **Tester les limites**

   ```bash
   systemd-run --scope --property=MemoryMax=100M stress --vm 1
```text

Les slices et scopes permettent une gestion fine et hiérarchique des ressources système, essentielles pour des environnements multi-tenants ou avec des workloads variés.
