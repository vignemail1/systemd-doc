# systemd-sysusers

`systemd-sysusers` crée les utilisateurs et groupes système déclarés dans des fichiers de configuration au format `sysusers.d`. Il est exécuté au démarrage via `systemd-sysusers.service`, avant le montage des systèmes de fichiers persistants, ce qui le rend particulièrement adapté à la gestion déclarative des comptes système nécessaires aux services.

## Prérequis

- Inclus dans tout système avec systemd
- Fichiers de configuration dans `/usr/lib/sysusers.d/`, `/etc/sysusers.d/`, `/run/sysusers.d/`

## Syntaxe générale

```
systemd-sysusers [OPTIONS] [FICHIER_CONF...]
```

Sans fichier spécifié, traite tous les fichiers `.conf` des répertoires standards.

## Utilisation courante

```bash
# Appliquer tous les fichiers sysusers.d (normalement fait au boot)
systemd-sysusers

# Appliquer uniquement un fichier spécifique
systemd-sysusers /etc/sysusers.d/mon-app.conf

# Mode dry-run : voir ce qui serait créé sans l'exécuter
systemd-sysusers --dry-run

# Afficher les actions sans les exécuter (alias de --dry-run)
systemd-sysusers --no-act

# Utiliser un répertoire racine alternatif (pour une image disque ou chroot)
systemd-sysusers --root=/mnt/image

# Utiliser une image systemd
systemd-sysusers --image=/path/to/image.raw
```

## Format des fichiers de configuration

Chaque ligne suit le format :

```
TYPE  NOM  ID  GECOS  RÉPERTOIRE  SHELL
```

Les champs `-` indiquent "valeur par défaut" ou "non applicable".

### Types

| Type | Description |
|------|-------------|
| `u` | Crée un utilisateur système (et son groupe primaire si absent) |
| `g` | Crée un groupe système |
| `m` | Ajoute un utilisateur à un groupe (membership) |
| `r` | Déclare une plage d'UIDs/GIDs réservée à l'allocation dynamique |

### Champ ID

- Nombre fixe : `65534` — UID/GID exact souhaité
- `-` : allocation automatique dans la plage système
- `999` et inférieur : plage système conventionnelle (peut varier selon la distro)

## Exemples de configuration

### Utilisateur système simple

```
# /usr/lib/sysusers.d/mon-daemon.conf
u mon-daemon - "Mon Daemon" /var/lib/mon-daemon /usr/sbin/nologin
```

Crée l'utilisateur `mon-daemon` avec UID alloué automatiquement, commentaire GECOS "Mon Daemon", répertoire home `/var/lib/mon-daemon`, shell `/usr/sbin/nologin`.

### Groupe seul

```
g ssl-cert - -
```

Crée uniquement le groupe `ssl-cert` sans utilisateur associé.

### Utilisateur avec UID fixe

```
u nfsnobody 65534 "NFS Nobody" / /usr/sbin/nologin
```

### Ajout à un groupe

```
m mon-daemon ssl-cert
```

Ajoute l'utilisateur `mon-daemon` au groupe `ssl-cert`. Les deux doivent exister ou être définis dans des fichiers traités lors du même appel.

### Plage d'UIDs réservée

```
r - 61184-65519
```

Déclare que la plage 61184-65519 est réservée à l'allocation dynamique de comptes système.

## Exemple complet pour un service

```
# /usr/lib/sysusers.d/prometheus.conf
u prometheus - "Prometheus monitoring" /var/lib/prometheus /usr/sbin/nologin
g prometheus -
m prometheus prometheus
```

Crée l'utilisateur et le groupe `prometheus`, puis s'assure que l'utilisateur est membre du groupe.

## Priorité des configurations

Même logique que `tmpfiles.d` :

1. `/etc/sysusers.d/*.conf` — surcharge locale (priorité maximale)
2. `/run/sysusers.d/*.conf` — configuration volatile
3. `/usr/lib/sysusers.d/*.conf` — configuration des paquets

Un fichier dans `/etc/sysusers.d/` remplace entièrement un fichier de même nom dans `/usr/lib/sysusers.d/`.

```bash
# Désactiver la création d'un utilisateur défini par un paquet
ln -s /dev/null /etc/sysusers.d/systemd-network.conf
```

## Intégration avec les paquets système

Les distributions modernes utilisent `sysusers.d` pour tous les comptes système créés par les paquets (ex. `nginx`, `postgres`, `prometheus`). Les scripts `adduser`/`useradd` dans les `%pre` RPM ou `preinst` Debian sont progressivement remplacés par des fichiers `.conf`.

```bash
# Voir les fichiers sysusers.d installés par les paquets
ls /usr/lib/sysusers.d/

# Voir ce qu'un fichier de paquet déclare
cat /usr/lib/sysusers.d/nginx.conf
```

## Utilisation lors de la construction d'images

`systemd-sysusers` est particulièrement utile dans les pipelines de construction d'images (conteneurs, images disque) :

```bash
# Pré-peupler les comptes dans une image en construction
systemd-sysusers --root=/mnt/build

# Ou via systemd-repart, mkosi, etc.
```

Cela évite de devoir exécuter `useradd` dans le contexte de construction, qui peut nécessiter des outils supplémentaires ou des accès PAM non disponibles.

## Diagnostic et débogage

```bash
# Tester la syntaxe d'un fichier
systemd-sysusers --dry-run /etc/sysusers.d/mon-app.conf

# Voir l'état du service au démarrage
systemctl status systemd-sysusers.service
journalctl -u systemd-sysusers.service

# Vérifier si un utilisateur a bien été créé
id mon-daemon
getent passwd mon-daemon
getent group mon-daemon
```

## Bonnes pratiques

- Toujours utiliser `/usr/sbin/nologin` ou `/bin/false` comme shell pour les utilisateurs système.
- Préférer l'allocation automatique d'UID (`-`) sauf besoin de compatibilité strict (NFS, LDAP, stockage partagé).
- Placer les fichiers de paquets dans `/usr/lib/sysusers.d/` et les personnalisations locales dans `/etc/sysusers.d/`.
- Utiliser `--dry-run` pour valider avant de déployer sur un système de production.
- Combiner avec `tmpfiles.d` pour créer le répertoire home du compte système avec les bonnes permissions.

## Voir aussi

- `man sysusers.d`
- `man systemd-sysusers`
- `man useradd`
- `man getent`
