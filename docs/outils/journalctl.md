# journalctl

`journalctl` est l'outil de consultation du journal systemd (journald). Il permet de lire, filtrer, suivre et exporter les logs structurés collectés par `systemd-journald`.

## Syntaxe générale

```bash
journalctl [OPTIONS] [MATCHES]
```

## Lecture de base

```bash
# Tout le journal (du plus ancien au plus récent)
journalctl

# Depuis la fin (équivalent tail)
journalctl -e

# Suivre en temps réel (équivalent tail -f)
journalctl -f

# N dernières lignes
journalctl -n 100
journalctl -n 50 -f
```

## Filtres par unité

```bash
# Logs d'un service
journalctl -u nginx.service

# Plusieurs services
journalctl -u nginx.service -u postgresql.service

# Avec suivi en temps réel
journalctl -u nginx.service -f

# Logs du démarrage actuel seulement
journalctl -u nginx.service -b
```

## Filtres temporels

```bash
# Depuis une date/heure
journalctl --since "2026-05-20 08:00:00"
journalctl --since "2026-05-20"
journalctl --since "1 hour ago"
journalctl --since "yesterday"

# Entre deux dates
journalctl --since "2026-05-19" --until "2026-05-20"
journalctl --since "09:00" --until "10:00"

# Depuis le dernier boot
journalctl -b

# Boot précédent
journalctl -b -1

# Lister les boots disponibles
journalctl --list-boots
```

## Filtres par priorité

Les niveaux de priorité suivent la norme syslog (0 = emergency, 7 = debug) :

```bash
# Erreurs uniquement (niveaux 0-3)
journalctl -p err

# Avertissements et au-dessus
journalctl -p warning

# Entre deux niveaux
journalctl -p info..err

# Niveaux disponibles :
# emerg(0), alert(1), crit(2), err(3), warning(4), notice(5), info(6), debug(7)
```

## Filtres par processus / utilisateur

```bash
# Par PID
journalctl _PID=1234

# Par UID
journalctl _UID=1000

# Par EUID (effective)
journalctl _EUID=0

# Par exécutable
journalctl _EXE=/usr/bin/sshd

# Par commande
journalctl _COMM=nginx
```

## Filtres par champs journald

Le journal stocke des champs structurés (clé=valeur). On peut filtrer sur n'importe lequel :

```bash
# Par unité systemd
journalctl _SYSTEMD_UNIT=nginx.service

# Par hostname (utile sur un journal centralisé)
journalctl _HOSTNAME=serveur1

# Par transport
journalctl _TRANSPORT=kernel    # messages noyau
journalctl _TRANSPORT=syslog    # messages syslog
journalctl _TRANSPORT=stdout    # stdout/stderr des services

# Par identifiant syslog
journalctl SYSLOG_IDENTIFIER=sshd

# Combiner des filtres (ET logique)
journalctl _UID=0 _COMM=sudo

# OU logique (lignes séparées)
journalctl _COMM=nginx _COMM=apache2
```

## Formats de sortie

```bash
# Format court (défaut)
journalctl -o short

# Format court avec microsecondes
journalctl -o short-precise

# Format court sans timestamp
journalctl -o short-monotonic

# Format verbeux (tous les champs)
journalctl -o verbose

# Format JSON (une entrée par ligne)
journalctl -o json

# Format JSON indenté
journalctl -o json-pretty

# Format export (pour sauvegarde/réimport)
journalctl -o export

# Format cat (message seul, sans métadonnées)
journalctl -o cat
```

### Export JSON pratique

```bash
# Exporter les erreurs du jour en JSON
journalctl --since today -p err -o json > erreurs-$(date +%F).json

# Analyser avec jq
journalctl -u nginx -o json | jq '.MESSAGE' | tail -20
```

## Rotation et taille du journal

```bash
# Espace disque occupé par le journal
journalctl --disk-usage

# Nettoyer les entrées de plus de 2 semaines
journalctl --vacuum-time=2weeks

# Limiter à 500 Mo
journalctl --vacuum-size=500M

# Limiter à 1000 fichiers
journalctl --vacuum-files=100
```

## Vérification d'intégrité

```bash
# Vérifier la cohérence du journal
journalctl --verify
```

## Catalogue des messages

Le catalogue systemd contient des explications détaillées pour certains messages :

```bash
# Afficher le catalogue pour un message
journalctl -x

# Avec explications (catalog)
journalctl -u nginx -x
```

## Filtrage avancé — exemples pratiques

### Diagnostiquer un service en échec

```bash
# Dernières 100 lignes d'un service en échec
journalctl -u monservice.service -n 100 --no-pager

# Depuis le dernier redémarrage du service (utile après crash)
journalctl -u monservice.service -b --since "30 min ago"
```

### Détecter les tentatives SSH suspectes

```bash
journalctl _COMM=sshd -p notice --since "24 hours ago" | grep -i "failed\|invalid"
```

### Logs kernel uniquement

```bash
journalctl -k           # messages noyau (dmesg)
journalctl -k -b -1     # noyau du boot précédent
```

### Surveiller plusieurs services simultanément

```bash
journalctl -u nginx.service -u php-fpm.service -f
```

### Obtenir les logs d'un conteneur systemd-nspawn

```bash
journalctl -M monconteneur -u apache2 -f
```

## Options globales utiles

| Option | Description |
| ------ | ----------- |
| `-f` | Suivre en temps réel |
| `-e` | Aller à la fin du journal |
| `-n <N>` | N dernières entrées |
| `-b [N]` | Boot courant ou N-ième précédent |
| `-u <unité>` | Filtrer par unité |
| `-p <priorité>` | Filtrer par priorité |
| `--since` / `--until` | Filtres temporels |
| `-o <format>` | Format de sortie |
| `--no-pager` | Désactiver le paginateur |
| `-x` | Ajouter les explications du catalogue |
| `--disk-usage` | Espace disque utilisé |
| `--vacuum-time=` | Supprimer les entrées anciennes |
| `--vacuum-size=` | Limiter la taille totale |
| `-k` | Messages kernel uniquement |
| `-r` | Ordre inversé (plus récent en premier) |
| `-q` | Mode silencieux (suppress info) |
| `-M <machine>` | Journal d'un conteneur |
| `-H <host>` | Journal d'un hôte distant |

## Voir aussi

- [Configuration de journald](journald-config.md) — `journald.conf`, rotation, stockage persistant
- [Journal centralisé](journald-remote.md) — `systemd-journal-remote` et `systemd-journal-gatewayd`
- `man journalctl`
- `man systemd.journal-fields` — liste complète des champs
