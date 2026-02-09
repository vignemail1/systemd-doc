# Sécurité et isolation

systemd offre de nombreuses fonctionnalités de sécurité pour isoler et restreindre les services. Cette section couvre le sandboxing, les capacités Linux, les namespaces et la limitation d'accès aux ressources.

## Principe de moindre privilège

Chaque service devrait avoir uniquement les permissions nécessaires à son fonctionnement, rien de plus.

### Configuration minimale sécurisée

```ini
[Service]
# Utilisateur dédié
User=myapp
Group=myapp
DynamicUser=yes

# Pas de nouveaux privilèges
NoNewPrivileges=yes

# Isolation basique
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes

# Chemins en lecture seule
ReadOnlyPaths=/
ReadWritePaths=/var/lib/myapp
```text

## Utilisateurs et groupes

### Utilisateur statique

```bash
# Créer un utilisateur système
sudo useradd -r -s /usr/sbin/nologin -d /var/lib/myapp myapp
```text

```ini
[Service]
User=myapp
Group=myapp
```text

### Utilisateur dynamique

Création automatique d'un utilisateur éphémère :

```ini
[Service]
DynamicUser=yes
StateDirectory=myapp
CacheDirectory=myapp
LogsDirectory=myapp
```text

Avantages :

- Pas de pré-création nécessaire
- UID/GID aléatoires
- Nettoyage automatique
- Sécurité renforcée

### Groupes supplémentaires

```ini
[Service]
User=myapp
Group=myapp
SupplementaryGroups=ssl-cert docker
```text

## Isolation du système de fichiers

### ProtectSystem

Contrôle l'accès en écriture au système :

```ini
[Service]
# Niveau de protection
ProtectSystem=no       # Aucune protection
ProtectSystem=yes      # /usr et /boot en lecture seule
ProtectSystem=full     # + /etc en lecture seule
ProtectSystem=strict   # Tout en lecture seule
```text

**strict** est le plus sécurisé. Nécessite de définir explicitement les chemins écritables.

### ProtectHome

Restreint l'accès aux répertoires home :

```ini
[Service]
ProtectHome=no         # Accès complet
ProtectHome=yes        # /home, /root, /run/user inaccessibles
ProtectHome=read-only  # Accès en lecture seule
ProtectHome=tmpfs      # Monté en tmpfs vide
```text

### PrivateTmp

Isole `/tmp` et `/var/tmp` :

```ini
[Service]
PrivateTmp=yes
```text

Crée un namespace `/tmp` unique pour le service.

### ReadOnlyPaths / ReadWritePaths

Contrôle fin des accès :

```ini
[Service]
# Tout en lecture seule
ReadOnlyPaths=/

# Sauf ces chemins
ReadWritePaths=/var/lib/myapp
ReadWritePaths=/var/log/myapp
ReadWritePaths=/run/myapp
```text

### InaccessiblePaths

Rend des chemins complètement inaccessibles :

```ini
[Service]
InaccessiblePaths=/home
InaccessiblePaths=/root
InaccessiblePaths=/proc/kcore
```text

### TemporaryFileSystem

Monte un tmpfs à un emplacement :

```ini
[Service]
TemporaryFileSystem=/var:ro
BindReadOnlyPaths=/var/lib/myapp
```text

## Répertoires gérés

systemd peut créer et gérer automatiquement des répertoires :

```ini
[Service]
# Création automatique avec bonnes permissions
StateDirectory=myapp              # /var/lib/myapp
CacheDirectory=myapp              # /var/cache/myapp
LogsDirectory=myapp               # /var/log/myapp
ConfigurationDirectory=myapp     # /etc/myapp
RuntimeDirectory=myapp            # /run/myapp

# Permissions
StateDirectoryMode=0750
CacheDirectoryMode=0750

# Nettoyage automatique
RuntimeDirectoryPreserve=no      # Supprimé à l'arrêt
```text

## Isolation réseau

### PrivateNetwork

Isole complètement du réseau :

```ini
[Service]
PrivateNetwork=yes
```text

Le service n'a accès qu'à l'interface loopback.

### RestrictAddressFamilies

Limite les types de sockets :

```ini
[Service]
# Autoriser seulement IPv4 et IPv6
RestrictAddressFamilies=AF_INET AF_INET6

# Autoriser seulement Unix sockets
RestrictAddressFamilies=AF_UNIX

# Bloquer tout
RestrictAddressFamilies=none
```text

### IPAddressAllow / IPAddressDeny

Filterage par IP (nécessite cgroups v2) :

```ini
[Service]
# Autoriser seulement certaines IPs
IPAddressAllow=10.0.0.0/8 192.168.1.0/24
IPAddressDeny=any

# Ou bloquer certaines IPs
IPAddressDeny=192.168.1.100
```text

## Capacités Linux

Les capacités décomposent les privilèges root en permissions granulaires.

### Supprimer toutes les capacités

```ini
[Service]
CapabilityBoundingSet=
AmbientCapabilities=
```text

### Autoriser des capacités spécifiques

```ini
[Service]
# Bind sur ports < 1024
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
```text

### Capacités courantes

- **CAP*NET*BIND_SERVICE** : Bind ports < 1024
- **CAP*NET*RAW** : Sockets raw (ping)
- **CAP*NET*ADMIN** : Configuration réseau
- **CAP*SYS*ADMIN** : Opérations système (mount, etc.)
- **CAP*SYS*TIME** : Modifier l'horloge système
- **CAP*DAC*OVERRIDE** : Outrepasser permissions fichiers
- **CAP_CHOWN** : Changer propriétaire fichiers

### Exemple : serveur web

```ini
[Service]
User=www-data
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
NoNewPrivileges=yes
```text

Permet de binder sur le port 80/443 sans être root.

## Systèmes d'appel (seccomp)

Bloquer les syscalls dangereux avec seccomp :

### Profils prédéfinis

```ini
[Service]
# Bloquer tous sauf liste blanche
SystemCallFilter=@system-service

# Bloquer syscalls dangereux
SystemCallFilter=~@privileged @resources @obsolete
```text

### Groupes de syscalls

- **@system-service** : Liste blanche pour services
- **@privileged** : Syscalls privilégiés
- **@resources** : Modification ressources
- **@obsolete** : Syscalls obsolètes
- **@debug** : Débogage (ptrace, etc.)
- **@mount** : Montage systèmes de fichiers
- **@swap** : Gestion swap
- **@reboot** : Redémarrage
- **@module** : Chargement modules noyau
- **@raw-io** : I/O brut

### Exemple : service web sécurisé

```ini
[Service]
SystemCallFilter=@system-service
SystemCallFilter=~@privileged @resources @obsolete @debug
SystemCallErrorNumber=EPERM
```text

### Bloquer des syscalls spécifiques

```ini
[Service]
SystemCallFilter=~ptrace personality
```text

## Limitations diverses

### NoNewPrivileges

Empêche l'obtention de nouveaux privilèges :

```ini
[Service]
NoNewPrivileges=yes
```text

Bloquer setuid, setgid, file capabilities.

### ProtectKernelTunables

Protège `/proc/sys`, `/sys` en lecture seule :

```ini
[Service]
ProtectKernelTunables=yes
```text

### ProtectKernelModules

Empêche le chargement de modules noyau :

```ini
[Service]
ProtectKernelModules=yes
```text

### ProtectControlGroups

Protège la hiérarchie cgroups :

```ini
[Service]
ProtectControlGroups=yes
```text

### ProtectKernelLogs

Bloquer l'accès aux logs noyau :

```ini
[Service]
ProtectKernelLogs=yes
```text

### ProtectHostname

Empêche la modification du hostname :

```ini
[Service]
ProtectHostname=yes
```text

### ProtectClock

Empêche la modification de l'horloge :

```ini
[Service]
ProtectClock=yes
```text

### ProtectProc

Masque les informations `/proc` :

```ini
[Service]
ProtectProc=invisible    # Masquer les autres processus
ProtectProc=noaccess    # Bloquer accès /proc
```text

### ProcSubset

Limiter le contenu de `/proc` :

```ini
[Service]
ProcSubset=pid    # Seulement /proc/PID
```text

### PrivateDevices

Isole `/dev` :

```ini
[Service]
PrivateDevices=yes
```text

Accès seulement à /dev/null, /dev/zero, /dev/urandom.

### PrivateUsers

Namespace utilisateur :

```ini
[Service]
PrivateUsers=yes
```text

Map UID/GID du service vers des IDs non-privilégiés.

### PrivateIPC

Isole IPC (shared memory, semaphores) :

```ini
[Service]
PrivateIPC=yes
```text

## Restriction d'exécution

### LockPersonality

Empêche changement de personnalité :

```ini
[Service]
LockPersonality=yes
```text

### MemoryDenyWriteExecute

Bloquer W^X (write XOR execute) :

```ini
[Service]
MemoryDenyWriteExecute=yes
```text

Empêche les pages mémoire à la fois écritables et exécutables.

### RestrictRealtime

Bloquer le scheduling temps réel :

```ini
[Service]
RestrictRealtime=yes
```text

### RestrictSUIDSGID

Bloquer création fichiers SUID/SGID :

```ini
[Service]
RestrictSUIDSGID=yes
```text

### RestrictNamespaces

Limiter création de namespaces :

```ini
[Service]
RestrictNamespaces=yes

# Ou autoriser certains types
RestrictNamespaces=uts ipc
```text

## Exemple : Service ultra-sécurisé

```ini
[Unit]
Description=Highly Secured Service

[Service]
# Utilisateur
DynamicUser=yes
User=myapp

# Pas de privilèges
NoNewPrivileges=yes
CapabilityBoundingSet=
AmbientCapabilities=

# Isolation système de fichiers
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ReadOnlyPaths=/
ReadWritePaths=/var/lib/myapp
InaccessiblePaths=/home /root

# Répertoires gérés
StateDirectory=myapp
CacheDirectory=myapp
LogsDirectory=myapp
StateDirectoryMode=0700

# Isolation réseau
PrivateNetwork=yes
RestrictAddressFamilies=AF_UNIX

# Protection noyau
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectKernelLogs=yes
ProtectControlGroups=yes
ProtectHostname=yes
ProtectClock=yes

# Isolation proc et devices
ProtectProc=invisible
ProcSubset=pid
PrivateDevices=yes
PrivateUsers=yes
PrivateIPC=yes

# Restrictions exécution
LockPersonality=yes
MemoryDenyWriteExecute=yes
RestrictRealtime=yes
RestrictSUIDSGID=yes
RestrictNamespaces=yes

# Seccomp
SystemCallFilter=@system-service
SystemCallFilter=~@privileged @resources @obsolete @debug
SystemCallErrorNumber=EPERM

# Limites ressources
MemoryMax=512M
TasksMax=100

[Install]
WantedBy=multi-user.target
```text

## Audit de sécurité

### Analyser la sécurité d'un service

```bash
# Score de sécurité (systemd >= 248)
systemd-analyze security myapp.service

# Détails
systemd-analyze security --no-pager myapp.service

# Seulement les warnings
systemd-analyze security myapp.service | grep -E 'WARN|UNSAFE'
```text

### Vérifier les capacités

```bash
# Capacités d'un service
systemctl show myapp.service -p CapabilityBoundingSet
systemctl show myapp.service -p AmbientCapabilities
```text

### Vérifier les protections actives

```bash
systemctl show myapp.service | grep -E '(Protect|Private|Restrict)'
```text

## Bonnes pratiques

1. **Toujours utiliser NoNewPrivileges**

   ```ini
   NoNewPrivileges=yes
```text

2. **Privilèges minimaux**

   ```ini
   CapabilityBoundingSet=CAP_NET_BIND_SERVICE
```text

3. **Isolation maximale**

   ```ini
   ProtectSystem=strict
   PrivateTmp=yes
   PrivateDevices=yes
```text

4. **Utilisateurs dédiés**

   ```ini
   DynamicUser=yes
```text

5. **Bloquer syscalls dangereux**

   ```ini
   SystemCallFilter=@system-service
```text

6. **Auditer régulièrement**

   ```bash
   systemd-analyze security
```text

7. **Tester après changements**

   ```bash
   systemctl restart myapp
   journalctl -u myapp -f
```text

La sécurité systemd permet de créer des services robustes et isolés, réduisant considérablement la surface d'attaque.
