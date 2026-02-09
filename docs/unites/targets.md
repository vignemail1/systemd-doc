# Targets (.target)

Les unités `.target` groupent d'autres unités et représentent des états du système. Elles remplacent les runlevels de SysVinit et permettent de synchroniser le démarrage de multiples services.

## Concept

Un target est un point de synchronisation qui ne fait rien par lui-même, mais qui permet de :

- **Grouper des unités** : Plusieurs services démarrent ensemble
- **Représenter un état** : Mode multi-utilisateur, graphique, etc.
- **Synchroniser le boot** : Attendre que plusieurs services soient prêts
- **Isoler des environnements** : Basculer entre différents états

## Targets système principaux

### poweroff.target

Arrêt complet du système.

```bash
systemctl isolate poweroff.target
# Équivalent à
systemctl poweroff
```

### rescue.target

Mode rescue (équivalent au runlevel 1 / single user mode).

```bash
systemctl isolate rescue.target
# Équivalent à
systemctl rescue
```

**Caractéristiques** :

- Shell root uniquement
- Services minimum
- Pas de réseau
- Utilisé pour la maintenance système

### multi-user.target

Mode multi-utilisateur sans interface graphique (équivalent au runlevel 3).

```bash
systemctl isolate multi-user.target
```

**Services typiques** :

- Réseau
- SSH
- Serveurs (web, base de données...)
- Pas de display manager

### graphical.target

Mode graphique complet (équivalent au runlevel 5).

```bash
systemctl isolate graphical.target
# Équivalent à
systemctl set-default graphical.target
```

**Dépendances** :

- Requiert `multi-user.target`
- Ajoute le display manager (GDM, SDDM, LightDM...)
- Interface graphique complète

### reboot.target

Redémarrage du système.

```bash
systemctl isolate reboot.target
# Équivalent à
systemctl reboot
```

## Targets de synchronisation

### network.target

Indique que le réseau est disponible (basique).

```ini
[Unit]
After=network.target
```

!!! warning "Attention"
    `network.target` signifie seulement que le réseau est *initialisé*, pas nécessairement *connecté*. Pour une connexion réseau complète, utilisez `network-online.target`.

### network-online.target

Indique que le réseau est réellement connecté et opérationnel.

```ini
[Unit]
After=network-online.target
Wants=network-online.target
```

Utilisé pour les services qui nécessitent une connexion réseau active (NFS, services cloud...).

### time-sync.target

Indique que l'horloge système est synchronisée.

```ini
[Unit]
After=time-sync.target
```

### local-fs.target

Tous les systèmes de fichiers locaux sont montés.

```ini
[Unit]
After=local-fs.target
```

### remote-fs.target

Systèmes de fichiers distants montés (NFS, CIFS...).

```ini
[Unit]
After=remote-fs.target
Requires=remote-fs.target
```

### basic.target

Services système de base démarrés (sockets, timers, paths, slices...).

```ini
[Unit]
After=basic.target
```

### sysinit.target

Initialisation système de base terminée.

### sockets.target

Tous les sockets sont créés.

### timers.target

Tous les timers sont activés.

### paths.target

Tous les path units sont actifs.

## Correspondance runlevels

| SysVinit Runlevel | systemd Target | Description |
| ------------------- | ---------------- | ------------- |
| 0 | poweroff.target | Arrêt système |
| 1, s, single | rescue.target | Mode rescue |
| 2, 3, 4 | multi-user.target | Multi-utilisateur sans GUI |
| 5 | graphical.target | Multi-utilisateur avec GUI |
| 6 | reboot.target | Redémarrage |

## Structure d'un target

```ini
[Unit]
Description=Multi-User System
Documentation=man:systemd.special(7)
Requires=basic.target
Conflicts=rescue.target
After=basic.target rescue.target
AllowIsolate=yes
```

### Options spécifiques

**AllowIsolate**

: Permet de basculer vers ce target avec `systemctl isolate`

```ini
AllowIsolate=yes
```

**Conflicts**

: Targets incompatibles (s'excluent mutuellement)

```ini
Conflicts=rescue.target shutdown.target
```

## Créer un target personnalisé

### Exemple : target de services web

```ini
# /etc/systemd/system/webstack.target
[Unit]
Description=Web Stack Services
Requires=multi-user.target
After=multi-user.target

[Install]
WantedBy=multi-user.target
```

Services associés :

```ini
# nginx.service
[Unit]
Description=Nginx Web Server
WantedBy=webstack.target

# php-fpm.service
[Unit]
Description=PHP FastCGI Process Manager
WantedBy=webstack.target

# mariadb.service
[Unit]
Description=MariaDB Database
WantedBy=webstack.target
```

Activation :

```bash
systemctl enable webstack.target
systemctl start webstack.target

# Démarre automatiquement nginx, php-fpm et mariadb
```

### Exemple : target de développement

```ini
# /etc/systemd/system/dev-environment.target
[Unit]
Description=Development Environment
Requires=multi-user.target
After=multi-user.target
AllowIsolate=yes

[Install]
WantedBy=multi-user.target
```

```ini
# docker.service
[Install]
WantedBy=dev-environment.target

# postgresql.service
[Install]
WantedBy=dev-environment.target

# redis.service
[Install]
WantedBy=dev-environment.target
```

## Gestion des targets

### Changer de target

```bash
# Basculer temporairement
systemctl isolate multi-user.target
systemctl isolate graphical.target

# Basculer vers rescue
systemctl rescue

# Emergency mode (shell root minimal)
systemctl emergency
```

### Target par défaut

```bash
# Voir le target par défaut
systemctl get-default

# Définir le target par défaut
systemctl set-default multi-user.target
systemctl set-default graphical.target

# Réinitialiser au défaut
systemctl set-default graphical.target
```

### Lister les targets

```bash
# Tous les targets disponibles
systemctl list-units --type=target
systemctl list-units --type=target --all

# Targets actifs
systemctl list-units --type=target --state=active

# Dépendances d'un target
systemctl list-dependencies graphical.target
systemctl list-dependencies --reverse graphical.target
```

### Analyser un target

```bash
# Voir la configuration
systemctl cat multi-user.target

# Voir les propriétés
systemctl show multi-user.target

# Services requis par le target
systemctl show -p Wants,Requires multi-user.target
```

## Targets et boot

### Sélectionner un target au boot

Au boot, dans GRUB, ajouter à la ligne kernel :

```ini
systemd.unit=rescue.target
systemd.unit=multi-user.target
systemd.unit=emergency.target
```

Ou de manière persistante :

```bash
systemctl set-default rescue.target
```

### Ordre de démarrage

```text
1. sysinit.target
   ↓
2. basic.target
   ↓
3. multi-user.target
   ↓
4. graphical.target (si défaut)
```

### Analyser le boot

```bash
# Temps de démarrage de chaque target
systemd-analyze critical-chain

# Visualiser le graphe de démarrage
systemd-analyze dot | dot -Tsvg > boot.svg
```

## Bonnes pratiques

### 1. Utiliser WantedBy plutôt que Requires

Pour une dépendance souple :

```ini
[Install]
WantedBy=multi-user.target  # Recommandé
```

Plutôt que :

```ini
[Unit]
Requires=multi-user.target   # Trop strict
```

### 2. Créer des targets métier

Grouper les services par fonction :

```ini
# monitoring.target
[Unit]
Description=Monitoring Stack
Requires=prometheus.service grafana.service
```

### 3. Utiliser AllowIsolate avec précaution

Seuls certains targets devraient autoriser l'isolation :

```ini
# OK pour les targets d'état système
AllowIsolate=yes  # multi-user, graphical, rescue

# Pas pour les targets de service
AllowIsolate=no   # network, sockets, timers
```

### 4. Documenter les targets personnalisés

```ini
[Unit]
Description=Production Web Services Stack
Documentation=https://wiki.example.com/webstack
Documentation=man:nginx(8)
```

### 5. Tester avant de set-default

```bash
# Tester d'abord
systemctl isolate my-custom.target

# Si OK, définir par défaut
systemctl set-default my-custom.target
```

## Dépannage

### Target ne démarre pas

```bash
# Voir les services en échec
systemctl list-dependencies my.target --failed

# Analyser les logs
journalctl -u my.target

# Vérifier les dépendances
systemctl list-dependencies my.target
```

### Impossible de basculer

```bash
# Vérifier AllowIsolate
systemctl show my.target -p AllowIsolate

# Voir les conflits
systemctl show my.target -p Conflicts
```

### Services ne démarrent pas avec le target

```bash
# Vérifier les WantedBy
systemctl show myservice.service -p WantedBy

# Réactiver le service
systemctl disable myservice.service
systemctl enable myservice.service

# Vérifier les liens symboliques
ls -l /etc/systemd/system/my.target.wants/
```

## Targets avancés

### shutdown.target

Arrêt du système (utilisé en interne).

### umount.target

Démontage des systèmes de fichiers.

### swap.target

Activation des espaces swap.

### cryptsetup.target

Déverrouillage des volumes chiffrés.

### hibernate.target / suspend.target

Modes de veille.

```bash
systemctl hibernate
systemctl suspend
systemctl hybrid-sleep
```

Les targets sont essentiels pour comprendre et contrôler le comportement de systemd. Ils permettent de structurer le démarrage du système et de créer des groupes logiques de services.
