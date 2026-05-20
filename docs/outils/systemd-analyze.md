# systemd-analyze

`systemd-analyze` est l'outil d'analyse des performances et de débogage de systemd. Il permet de mesurer le temps de démarrage, de visualiser les dépendances, de vérifier la syntaxe des fichiers d'unités et d'évaluer la sécurité des services.

## Mesure du temps de boot

```bash
# Temps total de boot
systemd-analyze time
```

Exemple de sortie :

```text
Startup finished in 3.653s (firmware) + 1.500s (loader) + 2.122s (kernel)
  + 8.215s (initrd) + 12.447s (userspace) = 27.937s
multi-user.target reached after 12.342s in userspace.
```

```bash
# Temps par unité (du plus lent au plus rapide)
systemd-analyze blame

# Limiter l'affichage
systemd-analyze blame | head -20
```

## Chaîne critique

La chaîne critique est le chemin le plus long dans le graphe de dépendances — c'est elle qui détermine le temps de boot.

```bash
# Chaîne critique globale
systemd-analyze critical-chain

# Chaîne critique d'une unité spécifique
systemd-analyze critical-chain nginx.service
systemd-analyze critical-chain multi-user.target
```

Lecture de la sortie :

```text
graphical.target @12.442s
└─multi-user.target @12.442s
  └─postgresql.service @8.213s +2.108s   # +2.108s = durée de démarrage
    └─network-online.target @7.891s
      └─NetworkManager-wait-online.service @2.015s +5.874s
```

Les `@` indiquent le temps absolu depuis le boot. Les `+` indiquent la durée de démarrage de l'unité.

## Graphe de dépendances (DOT)

```bash
# Générer un graphe au format DOT
systemd-analyze dot > boot.dot

# Convertir en SVG (nécessite graphviz)
dot -Tsvg boot.dot > boot.svg

# Filtrer sur des unités spécifiques
systemd-analyze dot nginx.service postgresql.service > services.dot

# Filtrer par pattern
systemd-analyze dot 'nginx.*' > nginx.dot
```

## Graphique SVG du boot

```bash
# Générer un graphe SVG du boot complet
systemd-analyze plot > boot.svg

# Ouvrir dans un navigateur
xdg-open boot.svg
```

Ce graphe montre visuellement la parallélisation des services au démarrage.

## Vérification de la configuration

### Vérifier la syntaxe d'un fichier d'unité

```bash
# Vérifier un ou plusieurs fichiers
systemd-analyze verify monservice.service
systemd-analyze verify /etc/systemd/system/monservice.service

# Vérifier tous les fichiers d'unités activés
systemd-analyze verify $(systemctl list-unit-files --state=enabled -o json \
  | jq -r '.[].unit_file')
```

### Afficher la configuration effective

```bash
# Afficher la configuration finale (avec tous les overrides appliqués)
systemd-analyze cat-config systemd/system/nginx.service
systemd-analyze cat-config systemd/journald.conf
systemd-analyze cat-config systemd/resolved.conf
```

Équivalent à `systemctl cat` mais opère directement sur les fichiers (sans daemon actif).

## Score de sécurité

Depuis systemd 248, `systemd-analyze security` évalue le niveau de sandboxing d'un service :

```bash
# Score de sécurité d'un service
systemd-analyze security nginx.service
systemd-analyze security sshd.service

# Tous les services actifs
systemd-analyze security

# Afficher seulement les problèmes
systemd-analyze security nginx.service | grep -E 'UNSAFE|MEDIUM|OK'
```

Exemple de sortie :

```text
  NAME                         DESCRIPTION                              EXPOSURE
✗ PrivateNetwork=              Service has access to the host network    0.5
✗ User=/DynamicUser=           Service runs as root user                0.4
✓ NoNewPrivileges=             Service cannot acquire new privileges     ...
...
→ Overall exposure level for nginx.service: 9.6 UNSAFE
```

Le score va de 0 (parfaitement isolé) à 10 (aucune isolation). Un score < 4 est considéré comme bon.

!!! tip "Améliorer le score de sécurité"
    Combiner avec la page [Sécurité et isolation](../securite/index.md) pour appliquer
    les directives suggérées par `systemd-analyze security`.

## Analyse des conditions et assertions

```bash
# Tester les conditions d'une unité
systemd-analyze condition monservice.service
```

Permet de comprendre pourquoi une unité ne démarre pas à cause d'une condition (`ConditionPathExists=`, `ConditionVirtualization=`, etc.).

## Inspection des unités

```bash
# Afficher les propriétés calculées d'une unité
systemd-analyze dump nginx.service
systemd-analyze dump > /tmp/systemd-dump.txt  # dump complet

# Calendrier d'un timer
systemd-analyze calendar "Mon-Fri 09:00:00"
systemd-analyze calendar "*-*-* 00/6:00:00"  # toutes les 6 heures
```

Exemple de sortie pour le calendrier :

```text
  Original form: Mon-Fri 09:00:00
Normalized form: Mon..Fri *-*-* 09:00:00
    Next elapse: Mon 2026-05-25 09:00:00 CEST
       (in UTC): Mon 2026-05-25 07:00:00 UTC
       From now: 4 days 23h left
```

## Analyse du mode utilisateur

```bash
# Analyser l'instance utilisateur
systemd-analyze --user time
systemd-analyze --user blame
systemd-analyze --user security monservice.service
```

## Récapitulatif des sous-commandes

| Sous-commande | Description |
| ------------- | ----------- |
| `time` | Temps de boot par phase |
| `blame` | Temps de démarrage par unité |
| `critical-chain [unité]` | Chemin critique de démarrage |
| `plot` | Graphe SVG du boot |
| `dot [unité]` | Graphe DOT des dépendances |
| `verify [unité]` | Vérification syntaxique |
| `cat-config <fichier>` | Configuration effective |
| `security [unité]` | Score de sandboxing |
| `condition [unité]` | Test des conditions |
| `calendar <spec>` | Analyse d'une expression calendrier |
| `dump [unité]` | Dump des propriétés internes |

## Voir aussi

- [Sécurité et isolation](../securite/index.md) — appliquer les recommandations du score de sécurité
- [Unités : timers](../unites/timers.md) — syntaxe des expressions calendrier
- `man systemd-analyze`
