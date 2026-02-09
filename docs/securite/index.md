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
```

## Utilisateurs et groupes

### Utilisateur statique

```bash
# Créer un utilisateur système
sudo useradd -r -s /usr/sbin/nologin -d /var/lib/myapp myapp
```

```ini
[Service]
User=myapp
Group=myapp
```

### Utilisateur dynamique

Création automatique d'un utilisateur éphémère :

```ini
[Service]
DynamicUser=yes
StateDirectory=myapp
CacheDirectory=myapp
LogsDirectory=myapp
```

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
```

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
```

**strict** est le plus sécurisé. Nécessite de définir explicitement les chemins écritables.

### ProtectHome

Restreint l'accès aux répertoires home :

```ini
[Service]
ProtectHome=no         # Accès complet
ProtectHome=yes        # /home, /root, /run/user inaccessibles
ProtectHome=read-only  # Accès en lecture seule
ProtectHome=tmpfs      # Monté en tmpfs vide
```

### PrivateTmp

Isole `/tmp` et `/var/tmp` :

```ini
[Service]
PrivateTmp=yes
```

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
```

### InaccessiblePaths

Rend des chemins complètement inaccessibles :

```ini
[Service]
InaccessiblePaths=/home
InaccessiblePaths=/root
InaccessiblePaths=/proc/kcore
```

### TemporaryFileSystem

Monte un tmpfs à un emplacement :

```ini
[Service]
TemporaryFileSystem=/var:ro
BindReadOnlyPaths=/var/lib/myapp
```

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
```

## Isolation réseau

### PrivateNetwork

Isole complètement du réseau :

```ini
[Service]
PrivateNetwork=yes
```

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
```

### IPAddressAllow / IPAddressDeny

Filterage par IP (nécessite cgroups v2) :

```ini
[Service]
# Autoriser seulement certaines IPs
IPAddressAllow=10.0.0.0/8 192.168.1.0/24
IPAddressDeny=any

# Ou bloquer certaines IPs
IPAddressDeny=192.168.1.100
```

## Capacités Linux

Les capacités décomposent les privilèges root en permissions granulaires.

### Supprimer toutes les capacités

```ini
[Service]
CapabilityBoundingSet=
AmbientCapabilities=
```

### Autoriser des capacités spécifiques

```ini
[Service]
# Bind sur ports < 1024
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
```

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
```

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
```

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
```

### Bloquer des syscalls spécifiques

```ini
[Service]
SystemCallFilter=~ptrace personality
```

## Limitations diverses

### NoNewPrivileges

Empêche l'obtention de nouveaux privilèges :

```ini
[Service]
NoNewPrivileges=yes
```

Bloquer setuid, setgid, file capabilities.

### ProtectKernelTunables

Protège `/proc/sys`, `/sys` en lecture seule :

```ini
[Service]
ProtectKernelTunables=yes
```

### ProtectKernelModules

Empêche le chargement de modules noyau :

```ini
[Service]
ProtectKernelModules=yes
```

### ProtectControlGroups

Protège la hiérarchie cgroups :

```ini
[Service]
ProtectControlGroups=yes
```

### ProtectKernelLogs

Bloquer l'accès aux logs noyau :

```ini
[Service]
ProtectKernelLogs=yes
```

### ProtectHostname

Empêche la modification du hostname :

```ini
[Service]
ProtectHostname=yes
```

### ProtectClock

Empêche la modification de l'horloge :

```ini
[Service]
ProtectClock=yes
```

### ProtectProc

Masque les informations `/proc` :

```ini
[Service]
ProtectProc=invisible    # Masquer les autres processus
ProtectProc=noaccess    # Bloquer accès /proc
```

### ProcSubset

Limiter le contenu de `/proc` :

```ini
[Service]
ProcSubset=pid    # Seulement /proc/PID
```

### PrivateDevices

Isole `/dev` :

```ini
[Service]
PrivateDevices=yes
```

Accès seulement à /dev/null, /dev/zero, /dev/urandom.

### PrivateUsers

Namespace utilisateur :

```ini
[Service]
PrivateUsers=yes
```

Map UID/GID du service vers des IDs non-privilégiés.

### PrivateIPC

Isole IPC (shared memory, semaphores) :

```ini
[Service]
PrivateIPC=yes
```

## Restriction d'exécution

### LockPersonality

Empêche changement de personnalité :

```ini
[Service]
LockPersonality=yes
```

### MemoryDenyWriteExecute

Bloquer W^X (write XOR execute) :

```ini
[Service]
MemoryDenyWriteExecute=yes
```

Empêche les pages mémoire à la fois écritables et exécutables.

### RestrictRealtime

Bloquer le scheduling temps réel :

```ini
[Service]
RestrictRealtime=yes
```

### RestrictSUIDSGID

Bloquer création fichiers SUID/SGID :

```ini
[Service]
RestrictSUIDSGID=yes
```

### RestrictNamespaces

Limiter création de namespaces :

```ini
[Service]
RestrictNamespaces=yes

# Ou autoriser certains types
RestrictNamespaces=uts ipc
```

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
```

## Audit de sécurité

### Analyser la sécurité d'un service

```bash
# Score de sécurité (systemd >= 248)
systemd-analyze security myapp.service

# Détails
systemd-analyze security --no-pager myapp.service

# Seulement les warnings
systemd-analyze security myapp.service | grep -E 'WARN|UNSAFE'
```

### Vérifier les capacités

```bash
# Capacités d'un service
systemctl show myapp.service -p CapabilityBoundingSet
systemctl show myapp.service -p AmbientCapabilities
```

### Vérifier les protections actives

```bash
systemctl show myapp.service | grep -E '(Protect|Private|Restrict)'
```

## Bonnes pratiques

1. **Toujours utiliser NoNewPrivileges**

   ```ini
   NoNewPrivileges=yes
   ```

2. **Privilèges minimaux**

   ```ini
   CapabilityBoundingSet=CAP_NET_BIND_SERVICE
   ```

3. **Isolation maximale**

   ```ini
   ProtectSystem=strict
   PrivateTmp=yes
   PrivateDevices=yes
   ```

4. **Utilisateurs dédiés**

   ```ini
   DynamicUser=yes
   ```

5. **Bloquer syscalls dangereux**

   ```ini
   SystemCallFilter=@system-service
   ```

6. **Auditer régulièrement**

   ```bash
   systemd-analyze security
   ```

7. **Tester après changements**

   ```bash
   systemctl restart myapp
   journalctl -u myapp -f
   ```

La sécurité systemd permet de créer des services robustes et isolés, réduisant considérablement la surface d'attaque.
