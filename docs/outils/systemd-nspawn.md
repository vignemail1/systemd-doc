# systemd-nspawn

`systemd-nspawn` est un outil de conteneurisation léger intégré à systemd, conçu pour exécuter un système complet ou un processus dans un espace de noms isolé (namespaces Linux). Il constitue une alternative évoluée à `chroot` et s'intègre nativement avec `systemd-machined` et `machinectl`.

## Prérequis

- Kernel Linux avec support des namespaces (`user`, `mnt`, `pid`, `net`, `uts`, `ipc`)
- Un répertoire racine contenant un système Linux minimal (arborescence `/usr`, `/etc`, etc.)
- Paquets : `systemd-container` sur Debian/Ubuntu, inclus dans `systemd` sur Arch et Fedora

## Syntaxe générale

```
systemd-nspawn [OPTIONS] [COMMANDE [ARGS...]]
```

Sans commande, lance le processus `init` du conteneur (démarrage complet).

## Démarrage d'un conteneur

### Accéder à un répertoire racine (mode chroot évolué)

```bash
sudo systemd-nspawn -D /var/lib/machines/debian12
```

Ouvre un shell dans le conteneur. L'arborescence `/var/lib/machines/debian12` est montée comme racine.

### Démarrer un conteneur complet avec systemd

```bash
sudo systemd-nspawn -bD /var/lib/machines/debian12
```

L'option `-b` (`--boot`) lance le process init du conteneur, permettant l'exécution de services systemd à l'intérieur.

### Exécuter une commande spécifique

```bash
sudo systemd-nspawn -D /var/lib/machines/debian12 /bin/bash
sudo systemd-nspawn -D /var/lib/machines/debian12 apt-get update
```

## Options principales

| Option | Description |
|--------|-------------|
| `-D DIR`, `--directory=DIR` | Répertoire racine du conteneur |
| `-b`, `--boot` | Démarre le processus init (démarrage complet) |
| `-M NAME`, `--machine=NAME` | Nom de la machine (pour `machinectl`) |
| `--bind=SRC:DST` | Monte un répertoire hôte dans le conteneur |
| `--bind-ro=SRC:DST` | Montage en lecture seule |
| `--overlay=SRC:DST` | Overlay filesystem (OverlayFS) |
| `--network-veth` | Crée une interface réseau virtuelle dédiée |
| `--network-bridge=BR` | Connecte le conteneur à un bridge réseau |
| `--private-network` | Isole complètement le réseau du conteneur |
| `--private-users` | Active le mapping d'UIDs (user namespaces) |
| `--private-users-ownership` | Ajuste la propriété des fichiers pour les user namespaces |
| `--resolv-conf=MODE` | Gère `/etc/resolv.conf` du conteneur |
| `-u USER`, `--user=USER` | Lance la commande en tant qu'utilisateur donné |
| `--capability=CAP` | Ajoute une capability Linux |
| `--drop-capability=CAP` | Retire une capability |
| `--read-only` | Monte la racine en lecture seule |
| `--ephemeral` | Copie temporaire ; les modifications sont perdues à l'arrêt |
| `--image=IMAGE` | Utilise une image disque raw ou GPT directement |

## Intégration avec machinectl

Quand un conteneur est démarré avec `-b`, il devient gérable via `machinectl` :

```bash
# Lister les machines actives
machinectl list

# Ouvrir un shell dans un conteneur actif
machinectl shell debian12

# Voir le statut d'une machine
machinectl status debian12

# Arrêter proprement
machinectl poweroff debian12

# Démarrer au boot (service systemd-nspawn@.service)
machinectl enable debian12
```

L'activation via `machinectl enable` crée et active l'unité `systemd-nspawn@debian12.service`.

## Réseau dans les conteneurs

### Partage du réseau hôte (défaut)

Par défaut, le conteneur partage le réseau de l'hôte. Simple mais non isolé.

### Interface virtuelle dédiée

```bash
sudo systemd-nspawn -bD /var/lib/machines/debian12 --network-veth
```

Crée une paire `veth` : `ve-debian12` côté hôte, `host0` côté conteneur. L'adresse IP doit être configurée manuellement ou via `systemd-networkd`.

### Bridge réseau

```bash
sudo systemd-nspawn -bD /var/lib/machines/debian12 \
  --network-bridge=br0
```

Attache directement le conteneur à un bridge existant.

### Réseau privé complet

```bash
sudo systemd-nspawn -D /var/lib/machines/debian12 --private-network
```

Isolement total : pas d'accès réseau depuis le conteneur.

## Montages et partage de données

```bash
# Monter un répertoire hôte en lecture-écriture
sudo systemd-nspawn -D /var/lib/machines/debian12 \
  --bind=/srv/data:/mnt/data

# Monter en lecture seule
sudo systemd-nspawn -D /var/lib/machines/debian12 \
  --bind-ro=/etc/ssl/certs:/etc/ssl/certs

# Monter un socket
sudo systemd-nspawn -D /var/lib/machines/debian12 \
  --bind=/run/docker.sock
```

## Conteneurs éphémères

```bash
sudo systemd-nspawn --ephemeral -D /var/lib/machines/debian12 -b
```

Crée une copie temporaire du répertoire racine. Toutes les modifications sont perdues à l'arrêt du conteneur, ce qui est utile pour des environnements de test reproductibles.

## Créer un conteneur minimal

### Via debootstrap (Debian/Ubuntu)

```bash
sudo debootstrap stable /var/lib/machines/debian12 http://deb.debian.org/debian
sudo systemd-nspawn -D /var/lib/machines/debian12
```

### Via pacstrap (Arch Linux)

```bash
sudo pacstrap -c /var/lib/machines/archlinux base
sudo systemd-nspawn -bD /var/lib/machines/archlinux
```

### Via dnf (Fedora)

```bash
sudo dnf --releasever=40 --installroot=/var/lib/machines/fedora40 \
  install systemd passwd dnf fedora-release
sudo systemd-nspawn -bD /var/lib/machines/fedora40
```

## Scénarios de diagnostic

### Le conteneur refuse de démarrer avec `-b`

Vérifier que le répertoire racine contient un init systemd :

```bash
ls /var/lib/machines/debian12/usr/lib/systemd/systemd
```

Si absent, installer `systemd` dans le conteneur ou utiliser sans `-b`.

### Erreur de permission avec les user namespaces

```bash
sudo systemd-nspawn -D /var/lib/machines/debian12 \
  --private-users=pick \
  --private-users-ownership=chown
```

`--private-users-ownership=chown` ajuste automatiquement les propriétaires de fichiers pour correspondre au mapping d'UIDs.

### Résolution DNS non fonctionnelle dans le conteneur

```bash
sudo systemd-nspawn -D /var/lib/machines/debian12 \
  --resolv-conf=copy-host
```

Copie le `/etc/resolv.conf` de l'hôte dans le conteneur au démarrage.

## Bonnes pratiques

- Stocker les machines dans `/var/lib/machines/` pour l'intégration native avec `machinectl`.
- Utiliser `--ephemeral` pour les environnements de test afin d'éviter la pollution de l'image de base.
- Préférer `--network-veth` + `systemd-networkd` pour un réseau isolé et gérable.
- Ne pas utiliser `--capability=CAP_SYS_ADMIN` sauf nécessité absolue.
- Pour la production, préférer des solutions comme Docker, Podman ou LXC/LXD qui offrent des garanties de sécurité supplémentaires.

## Voir aussi

- `man systemd-nspawn`
- `man machinectl`
- `man systemd.nspawn` (fichiers de configuration `.nspawn`)
- [`machinectl`](https://www.freedesktop.org/software/systemd/man/latest/machinectl.html)
