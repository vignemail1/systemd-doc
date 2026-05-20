# Namespaces Linux

Les **namespaces** Linux isolent la *vue* qu'a un groupe de processus sur les ressources globales du noyau. Là où les [cgroups](cgroups.md) limitent les *quantités* de ressources consommables, les namespaces contrôlent ce que les processus *voient* : quels fichiers, quels PID, quelles interfaces réseau, quel hostname. Un container est à la base un ensemble de namespaces combiné à un cgroup.

!!! note "API noyau"
    Trois appels système gouvernent les namespaces : `clone(2)` crée un processus dans un nouveau namespace, `unshare(2)` fait basculer le processus appelant dans un nouveau namespace sans `fork`, et `setns(2)` permet de rejoindre un namespace existant via son descripteur de fichier (`/proc/PID/ns/`).

## Les huit types de namespaces

| Namespace | Flag `clone` | Isole | Depuis |
| --------- | ------------ | ----- | ------ |
| `mnt` | `CLONE_NEWNS` | Arbre de montage (`/proc/mounts`) | Linux 2.4.19 |
| `uts` | `CLONE_NEWUTS` | Hostname et domainname | Linux 2.6.19 |
| `ipc` | `CLONE_NEWIPC` | SysV IPC, POSIX message queues | Linux 2.6.19 |
| `pid` | `CLONE_NEWPID` | Espace de PIDs (PID 1 = init du namespace) | Linux 3.8 |
| `net` | `CLONE_NEWNET` | Interfaces, routes, iptables, ports | Linux 3.0 |
| `user` | `CLONE_NEWUSER` | UIDs et GIDs (root interne ≠ root hôte) | Linux 3.8 |
| `cgroup` | `CLONE_NEWCGROUP` | Vue de la hiérarchie cgroup | Linux 4.6 |
| `time` | `CLONE_NEWTIME` | Horloges monotoniques et boottime | Linux 5.6 |

## Détail de chaque type

### `mnt` — montages

Isole l'arbre de montage : chaque namespace `mnt` dispose de sa propre liste de points de montage. Un `mount` effectué dans un namespace n'est pas visible depuis l'hôte ni depuis d'autres namespaces (sauf si la propagation est configurée via `--make-shared`).

Cas d'usage : isoler `/tmp`, monter un overlay FS pour un container, exposer un chemin différent selon l'environnement.

!!! warning "Propagation de montage"
    Par défaut sur les systèmes modernes, les montages sont `shared`. Un namespace `mnt` hérite des montages partagés de son parent. Utiliser `mount --make-rprivate /` au sein du namespace pour couper toute propagation bidirectionnelle.

### `uts` — hostname

Permet à un processus de positionner un hostname différent sans affecter l'hôte. `sethostname(2)` et `setdomainname(2)` n'ont d'effet qu'à l'intérieur du namespace.

```bash
# Créer un namespace uts isolé et y fixer un hostname
sudo unshare --uts bash
hostname container-test
hostname
# container-test
# (le hostname de l'hôte est inchangé)
```

### `ipc` — communication inter-processus

Isole les objets SysV IPC (sémaphores, files de messages, mémoire partagée) et les POSIX message queues. Les processus hors du namespace ne peuvent pas accéder aux objets IPC créés à l'intérieur.

```bash
# Vérifier les IPC visibles
ipcs
```

### `pid` — espace de PIDs

Crée un espace de PIDs indépendant. Le premier processus créé dans le namespace reçoit le PID 1 à l'intérieur, mais conserve son PID réel vu depuis l'hôte. Les processus du namespace ne voient pas les processus de l'hôte.

```bash
# L'hôte voit toujours les PIDs réels
ls /proc/PID_HOTE/ns/pid

# Depuis l'intérieur d'un namespace pid
ps aux
# Les PIDs commencent à 1
```

!!! note "PID 1 dans un namespace"
    Le processus PID 1 d'un namespace `pid` reçoit les signaux orphelins de ses descendants (comme `init`). S'il se termine, tous les processus du namespace reçoivent `SIGKILL`. Dans un container, c'est souvent `tini` ou un init minimaliste qui joue ce rôle.

### `net` — réseau

Isole la pile réseau complète : interfaces (`lo` uniquement par défaut), tables de routage, règles iptables/nftables, sockets, ports. Deux processus dans des namespaces `net` différents peuvent écouter sur le même numéro de port sans conflit.

Les namespaces `net` peuvent être connectés entre eux via des **veth pairs** (interfaces virtuelles appairées) ou des **bridges**.

```bash
# Créer un namespace réseau nommé (persisté dans /run/netns/)
sudo ip netns add test-ns
sudo ip netns exec test-ns ip link show
# Seul lo est présent

# Créer une paire veth pour connecter le namespace à l'hôte
sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth1 netns test-ns
sudo ip netns exec test-ns ip addr add 192.168.100.2/24 dev veth1
sudo ip netns exec test-ns ip link set veth1 up

# Supprimer le namespace
sudo ip netns del test-ns
```

### `user` — utilisateurs et groupes

Isole les UIDs et GIDs. Un processus peut être UID 0 (root) *à l'intérieur* du namespace sans être root sur l'hôte. C'est le fondement des **containers rootless**.

C'est le seul namespace créable sans `CAP_SYS_ADMIN` sur l'hôte (sous réserve que `kernel.unprivileged_userns_clone=1`).

Voir la section [User namespaces en détail](#user-namespaces-en-detail) ci-dessous.

### `cgroup` — vue des cgroups

Isole la vue de la hiérarchie cgroup : le cgroup racine du namespace devient `/` à l'intérieur. Un container ne voit pas les cgroups frères ni parents, ce qui évite les fuites d'information sur la topologie du système hôte.

### `time` — horloges (Linux 5.6+)

Permet d'exposer des valeurs différentes pour les horloges `CLOCK_MONOTONIC` et `CLOCK_BOOTTIME` à l'intérieur du namespace. Utile pour les scénarios de checkpoint/restore (CRIU) où un processus restauré doit retrouver une horloge cohérente avec son état sauvegardé.

```bash
# Vérifier la disponibilité
ls /proc/self/ns/time
```

## Inspection des namespaces

### `/proc/PID/ns/`

Chaque namespace actif est représenté par un fichier dans `/proc/PID/ns/`. Deux processus partageant le même namespace ont le même inode.

```bash
# Voir les namespaces du processus courant
ls -la /proc/self/ns/
# lrwxrwxrwx cgroup -> cgroup:[4026531835]
# lrwxrwxrwx ipc    -> ipc:[4026531839]
# lrwxrwxrwx mnt    -> mnt:[4026531840]
# lrwxrwxrwx net    -> net:[4026531992]
# lrwxrwxrwx pid    -> pid:[4026531836]
# lrwxrwxrwx time   -> time:[4026531834]
# lrwxrwxrwx user   -> user:[4026531837]
# lrwxrwxrwx uts    -> uts:[4026531838]

# Comparer les namespaces de deux processus
stat -L /proc/1/ns/net /proc/1234/ns/net
# Même inode = même namespace réseau
```

### `lsns`

```bash
# Lister tous les namespaces actifs du système
lsns

# Filtrer par type
lsns --type net
lsns --type pid

# Voir les namespaces d'un PID particulier
lsns -p 1234
```

### `nsenter`

`nsenter` permet de rejoindre un ou plusieurs namespaces d'un processus existant — utile pour entrer dans un container sans passer par son runtime.

```bash
# Entrer dans tous les namespaces du PID 1234
sudo nsenter -t 1234 --all bash

# Entrer uniquement dans le namespace réseau et pid
sudo nsenter -t 1234 --net --pid bash

# Rejoindre le namespace réseau d'un container Docker
DOCKER_PID=$(docker inspect -f '{{.State.Pid}}' mon-container)
sudo nsenter -t "${DOCKER_PID}" --net ip addr
```

### `unshare`

`unshare` crée un ou plusieurs nouveaux namespaces depuis le shell, sans écrire de code C.

```bash
# Namespace mnt isolé (monter sans affecter l'hôte)
sudo unshare --mount bash

# Namespace réseau isolé (loopback uniquement)
sudo unshare --net bash

# Namespace complet (simulation container léger)
sudo unshare --mount --uts --ipc --pid --net --fork bash

# User namespace sans root (rootless)
unshare --user --map-root-user bash
capsh --print
# uid=0(root) gid=0(root) — root dans le namespace uniquement
```

## User namespaces en détail

Le namespace `user` est le plus important pour la sécurité et le cas rootless. Il est le seul créable sans privilège sur l'hôte.

### Mapping UID/GID

Chaque user namespace définit une table de correspondance entre les UIDs internes et les UIDs hôte, via `/proc/PID/uid_map` et `/proc/PID/gid_map`. Format : `uid_interne uid_hote longueur`.

```bash
# Voir le mapping UID d'un container
cat /proc/1234/uid_map
# 0  1000  1
# Signifie : UID 0 interne = UID 1000 hôte, sur 1 entrée

# Mapping étendu (subuid) pour containers rootless
cat /etc/subuid
# sebastien:100000:65536
# Permet de mapper 65536 UIDs à partir du 100000 hôte
```

### Capabilities dans un user namespace

Un processus peut avoir des [capabilities](capabilities.md) complètes à l'intérieur de son user namespace, mais ces capabilities ne lui donnent des droits que sur les ressources **possédées par ce namespace**. `CAP_NET_ADMIN` dans un netns isolé permet de configurer les interfaces de ce netns, pas celles de l'hôte.

### Contrôles système

```bash
# Vérifier si les user namespaces non-root sont autorisés
sysctl kernel.unprivileged_userns_clone
# 1 = autorisé (défaut sur la plupart des distributions)

# Limite du nombre de user namespaces imbriqués
sysctl user.max_user_namespaces

# Désactiver (durcissement sécurité si rootless non requis)
# echo 0 > /proc/sys/kernel/unprivileged_userns_clone
```

!!! warning "Surface d'attaque"
    Les user namespaces ont été à l'origine de plusieurs LPE (Local Privilege Escalation). Sur des serveurs où le rootless n'est pas nécessaire, désactiver `kernel.unprivileged_userns_clone` réduit significativement la surface d'attaque.

## Intégration systemd

systemd utilise les namespaces dans ses directives de sandboxing pour isoler les services sans conteneurisation complète.

### Directives de sandboxing et namespaces utilisés

| Directive | Namespace | Effet |
| --------- | --------- | ----- |
| `PrivateTmp=yes` | `mnt` | Monte un `tmpfs` dédié sur `/tmp` et `/var/tmp` |
| `PrivateDevices=yes` | `mnt` | Monte un `/dev` minimal en lecture seule |
| `PrivateMounts=yes` | `mnt` | Isole tous les montages du service |
| `PrivateNetwork=yes` | `net` | Réseau coupé (loopback uniquement) |
| `PrivatePids=yes` | `pid` | Le service ne voit pas les PID extérieurs (Linux 6.9+) |
| `PrivateUsers=yes` | `user` | User namespace dédié, root interne ≠ root hôte |
| `ProtectHostname=yes` | `uts` | Hostname isolé, les écritures sur hostname n'affectent pas l'hôte |
| `InaccessiblePaths=` | `mnt` | Bind-mount `tmpfs` sur les chemins sensibles |
| `ReadOnlyPaths=` | `mnt` | Remonte des chemins en lecture seule |
| `BindPaths=` | `mnt` | Bind-mount un chemin hôte dans le namespace du service |

### Exemple de service fortement sandboxé

```ini
[Unit]
Description=Service isolé avec namespaces

[Service]
User=appuser
ExecStart=/usr/local/bin/mon-app

# Namespaces
PrivateTmp=yes
PrivateDevices=yes
PrivateNetwork=yes
PrivateUsers=yes
ProtectHostname=yes

# Protection système de fichiers
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/mon-app

# Capabilities
CapabilityBoundingSet=
NoNewPrivileges=yes

[Install]
WantedBy=multi-user.target
```

!!! tip "`systemd-analyze security`"
    La commande `systemd-analyze security mon-service.service` évalue le niveau de sandboxing d'un service et liste les directives de protection manquantes. C'est un excellent point de départ pour renforcer un service existant.

```bash
systemd-analyze security sshd.service
# → Affiche un score et les vecteurs d'attaque encore ouverts
```

## `systemd-nspawn` et namespaces

`systemd-nspawn` crée un ensemble complet de namespaces pour ses containers. Par défaut il isole :

| Namespace | Activé par défaut | Option pour modifier |
| --------- | ----------------- | -------------------- |
| `mnt` | Oui | `--bind=`, `--overlay=` |
| `uts` | Oui | `--hostname=` |
| `ipc` | Oui | `--share-system` |
| `pid` | Oui | — |
| `net` | Oui (veth ou lo) | `--network-veth`, `--network-macvlan`, `--private-network` |
| `user` | Non par défaut | `--private-users=` |
| `cgroup` | Oui | — |

```bash
# Lancer un container avec user namespace
sudo systemd-nspawn --private-users=pick -D /var/lib/machines/debian12 bash

# Vérifier les namespaces du PID principal du container
MACHINE_PID=$(machinectl show mon-container -p Leader --value)
lsns -p "${MACHINE_PID}"
```

## Diagnostics courants

### Un service ne voit pas une interface réseau attendue

```bash
# Identifier si le service tourne dans un namespace net isolé
PID=$(systemctl show mon-service.service -p MainPID --value)
lsns -p "${PID}" --type net

# Comparer avec le namespace net de l'hôte
stat -L /proc/1/ns/net /proc/"${PID}"/ns/net
# Inodes différents = namespaces séparés

# Vérifier si PrivateNetwork=yes est actif
systemctl show mon-service.service -p PrivateNetwork
```

### Hostname différent à l'intérieur d'un service

```bash
# Vérifier si ProtectHostname=yes est actif
systemctl show mon-service.service -p ProtectHostname

# Voir le hostname vu par le service
PID=$(systemctl show mon-service.service -p MainPID --value)
sudo nsenter -t "${PID}" --uts hostname
```

### Conflit UID entre hôte et container

```bash
# Voir le mapping UID d'un processus container
PID=$(systemctl show mon-container.service -p MainPID --value)
cat /proc/"${PID}"/uid_map

# Vérifier les subuid disponibles
cat /etc/subuid
grep "$(id -un)" /etc/subuid
```

### PID 1 inattendu dans un namespace pid

```bash
# Voir le PID hôte du processus PID 1 interne
# (visible dans /proc via le mapping)
cat /proc/"${PID}"/status | grep NSpid
# NSpid: 4321  1
# Signifie : PID 4321 hôte = PID 1 dans le namespace
```

### Diagnostiquer les droits dans un user namespace

```bash
# Depuis l'extérieur, voir les capabilities réelles du processus
grep -E 'Cap(Prm|Eff|Bnd)' /proc/"${PID}"/status
capsh --decode=$(grep CapEff /proc/"${PID}"/status | awk '{print $2}')
```

## Bonnes pratiques

- **Activer `PrivateTmp=yes` systématiquement** sur tous les services : isole `/tmp` avec zéro coût fonctionnel et évite les race conditions entre services.
- **Combiner `PrivateNetwork=yes` avec les services sans besoin réseau** (taches de fond, workers locaux) : élimine toute la surface d'attaque réseau.
- **Utiliser `systemd-analyze security`** comme audit régulier des services en production.
- **Ne pas désactiver `kernel.unprivileged_userns_clone`** si le système exécute des containers rootless (podman, buildah) — les deux sont incompatibles.
- **Tester `nsenter`** plutôt que `docker exec` ou les commandes équivalentes des runtimes pour comprendre précisément dans quel namespace un processus tourne.
- **Prendre garde aux namespaces `mnt` partagés** : un bind mount créé dans un namespace `shared` se propage à l'hôte si la propagation n'a pas été explicitement coupée.

## Voir aussi

- [cgroups](cgroups.md) — limites de ressources, complémentaires aux namespaces
- [capabilities](capabilities.md) — interaction entre capabilities et user namespaces
- [systemd-nspawn](../outils/systemd-nspawn.md) — containers légers combinant namespaces et cgroups
- `man 7 namespaces` — référence noyau complète
- `man 7 user_namespaces` — détail du namespace user et des mappings UID/GID
- `man 1 unshare`, `man 1 nsenter`, `man 8 lsns`
- `man 5 systemd.exec` — toutes les directives de sandboxing systemd
- [Linux Namespaces — LWN series](https://lwn.net/Articles/531114/)
