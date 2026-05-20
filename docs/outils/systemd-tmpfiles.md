# systemd-tmpfiles

`systemd-tmpfiles` gère la création, la suppression et le nettoyage des fichiers et répertoires temporaires ou volatils selon des règles déclaratives. Il est exécuté au démarrage via `systemd-tmpfiles-setup.service` et périodiquement via `systemd-tmpfiles-clean.timer` pour assurer la cohérence de l'arborescence système.

## Prérequis

- Inclus par défaut dans toute installation systemd
- Les fichiers de configuration sont dans `/usr/lib/tmpfiles.d/`, `/etc/tmpfiles.d/` et `/run/tmpfiles.d/`

## Syntaxe générale

```text
systemd-tmpfiles [OPTIONS] [FICHIER_CONF...]
```

Sans fichier spécifié, traite tous les fichiers de configuration trouvés dans les répertoires standards.

## Actions principales

```bash
# Créer les entrées marquées pour la création
systemd-tmpfiles --create

# Nettoyer les entrées avec une politique d'âge dépassée
systemd-tmpfiles --clean

# Supprimer les entrées marquées pour suppression
systemd-tmpfiles --remove

# Appliquer toutes les actions sur un fichier spécifique
systemd-tmpfiles --create --clean --remove /etc/tmpfiles.d/mon-app.conf

# Mode dry-run : afficher ce qui serait fait sans l'exécuter
systemd-tmpfiles --create --dry-run
```

## Format des fichiers de configuration

Chaque ligne d'un fichier `.conf` suit le format :

```text
TYPE  CHEMIN  MODE  UID  GID  AGE  ARGUMENT
```

Les champs `-` indiquent "valeur par défaut".

### Types courants

| Type | Description |
|------|-------------|
| `d` | Crée un répertoire, nettoie son contenu selon l'AGE |
| `D` | Comme `d`, mais supprime le répertoire lui-même si vide après nettoyage |
| `f` | Crée un fichier vide s'il n'existe pas |
| `F` | Crée ou tronque un fichier |
| `w` | Écrit dans un fichier existant (utile pour sysctl, cgroups) |
| `L` | Crée un lien symbolique |
| `c` | Crée un fichier spécial (character device) |
| `b` | Crée un fichier spécial (block device) |
| `p` | Crée un FIFO (named pipe) |
| `x` | Exclut un chemin du nettoyage récursif |
| `X` | Exclut un chemin et ses sous-répertoires du nettoyage |
| `r` | Supprime un fichier |
| `R` | Supprime récursivement |
| `z` | Restaure le contexte SELinux et les permissions |
| `Z` | Restaure récursivement |
| `t` | Applique des attributs xattr |
| `T` | Supprime des attributs xattr |
| `a` | Applique des ACL (mode additif) |
| `A` | Applique des ACL récursivement |

### Format de l'AGE

L'AGE définit la durée de conservation avant nettoyage. Il est combinable :

- `10d` — 10 jours
- `2w` — 2 semaines
- `1h` — 1 heure
- `30s` — 30 secondes
- `~10d` — nettoyage uniquement si le répertoire parent n'a pas été modifié depuis 10 jours

## Exemples de configuration

### Répertoire temporaire applicatif

```bash
# /etc/tmpfiles.d/mon-app.conf
d /run/mon-app 0755 mon-app mon-app -
d /var/cache/mon-app 0750 mon-app mon-app 30d
```

Crée `/run/mon-app` à chaque démarrage (aucun âge = jamais nettoyé par `--clean`).  
Nettoyage du cache après 30 jours.

### Fichier de configuration système

```bash
# Crée /etc/mon-app/config.yaml s'il n'existe pas
f /etc/mon-app/config.yaml 0640 root mon-app -
```

### Écriture dans un fichier pseudo-FS

```bash
# Ajuster un paramètre sysctl via cgroup
w /proc/sys/net/ipv4/ip_forward - - - - 1
w /sys/kernel/mm/transparent_hugepage/enabled - - - - madvise
```

### Lien symbolique

```bash
L /run/lock - - - - /var/lock
```

### Nettoyage du répertoire temporaire avec exclusion

```bash
d /tmp 1777 root root 10d
x /tmp/.X*
x /tmp/.ICE*
```

Nettoyage de `/tmp` après 10 jours, en excluant les sockets X11 et ICE.

## Priorité et surcharge des configurations

Les fichiers sont cherchés dans l'ordre de priorité décroissante :

1. `/etc/tmpfiles.d/*.conf` — configuration locale (surcharge tout)
2. `/run/tmpfiles.d/*.conf` — configuration volatile (runtime)
3. `/usr/lib/tmpfiles.d/*.conf` — configuration système (paquets)

Un fichier `/etc/tmpfiles.d/tmp.conf` remplace entièrement `/usr/lib/tmpfiles.d/tmp.conf`. Pour désactiver une configuration système, créer un fichier vide ou un lien vers `/dev/null` dans `/etc/tmpfiles.d/`.

```bash
# Désactiver la configuration tmpfiles d'un paquet
ln -s /dev/null /etc/tmpfiles.d/journal-nocow.conf
```

## Tester et valider

```bash
# Vérifier la syntaxe sans appliquer
systemd-tmpfiles --create --dry-run /etc/tmpfiles.d/mon-app.conf

# Appliquer uniquement un fichier en test
systemd-tmpfiles --create /etc/tmpfiles.d/mon-app.conf

# Voir ce qui serait nettoyé
systemd-tmpfiles --clean --dry-run
```

## Services et timers associés

| Unité | Rôle |
|-------|------|
| `systemd-tmpfiles-setup.service` | Exécute `--create --remove` au démarrage |
| `systemd-tmpfiles-setup-dev-early.service` | Gère `/dev` très tôt au boot |
| `systemd-tmpfiles-clean.service` | Exécute `--clean` (déclenché par le timer) |
| `systemd-tmpfiles-clean.timer` | Déclenche le nettoyage périodique (défaut : 1 jour) |

```bash
# Voir l'état du timer de nettoyage
systemctl status systemd-tmpfiles-clean.timer

# Forcer un nettoyage immédiat
systemctl start systemd-tmpfiles-clean.service
```

## Cas pratique : répertoire runtime d'un service

Plutôt que de créer le répertoire dans l'unité `.service` avec `ExecStartPre`, la pratique recommandée est de le déclarer dans `tmpfiles.d` :

```bash
# /etc/tmpfiles.d/mon-daemon.conf
d /run/mon-daemon 0750 mon-daemon mon-daemon -
Z /run/mon-daemon - mon-daemon mon-daemon -
```

Puis dans l'unité systemd :

```ini
[Service]
RuntimeDirectory=mon-daemon
RuntimeDirectoryMode=0750
```

!!! note
    La directive `RuntimeDirectory=` dans les unités systemd est souvent préférable à `tmpfiles.d` pour les répertoires de runtime, car elle lie automatiquement le cycle de vie du répertoire à celui du service.

## Bonnes pratiques

- Placer les configurations personnalisées dans `/etc/tmpfiles.d/`, jamais dans `/usr/lib/tmpfiles.d/` (réservé aux paquets).
- Toujours tester avec `--dry-run` avant d'appliquer une nouvelle configuration.
- Utiliser `RuntimeDirectory=` dans les unités systemd pour les répertoires `/run/` liés à un service unique.
- Documenter l'AGE choisi dans un commentaire pour en expliquer le choix.
- Ne jamais utiliser le type `R` (suppression récursive) sans avoir vérifié soigneusement le chemin cible.

## Voir aussi

- `man tmpfiles.d`
- `man systemd-tmpfiles`
- `man systemd.exec` (directive `RuntimeDirectory`)
