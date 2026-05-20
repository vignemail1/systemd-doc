# loginctl

`loginctl` est l'outil en ligne de commande permettant d'interagir avec **systemd-logind**, le démon responsable de la gestion des sessions utilisateur, des sièges (*seats*) et de l'état de connexion.

## Vue d'ensemble

systemd-logind surveille les connexions des utilisateurs, gère l'accès aux périphériques d'entrée/sortie et contrôle les états d'alimentation. `loginctl` en est l'interface d'administration.

```bash
loginctl [OPTIONS] COMMANDE [ARGUMENTS]
```

## Gestion des sessions

### Lister les sessions actives

```bash
loginctl list-sessions
```

Affiche toutes les sessions actives avec leur ID, UID, utilisateur, siège et TTY.

### Afficher les détails d'une session

```bash
loginctl show-session 1
loginctl show-session c1  # session graphique
```

Affiche toutes les propriétés D-Bus de la session : type (x11, wayland, tty), état (active, online, closing), TTY, display, PID du leader de session, etc.

### Activer / désactiver une session

```bash
loginctl activate 3        # activer la session 3
loginctl lock-session 2    # verrouiller la session 2
loginctl unlock-session 2  # déverrouiller la session 2
```

### Terminer une session

```bash
loginctl terminate-session 3
```

!!! warning "Attention"
    Terminer une session tue tous les processus qui y sont rattachés, y compris les applications graphiques.

### Tuer un processus dans une session

```bash
loginctl kill-session 3 --signal=SIGTERM
```

## Gestion des utilisateurs

### Lister les utilisateurs connectés

```bash
loginctl list-users
```

### Afficher les informations d'un utilisateur

```bash
loginctl show-user alice
loginctl show-user 1000  # par UID
```

Propriétés utiles retournées :

- `Sessions` : liste des sessions actives
- `Linger` : le lingering est-il activé ?
- `State` : active, online, offline, lingering
- `Slice` : slice cgroup de l'utilisateur (`user-1000.slice`)

### Terminer toutes les sessions d'un utilisateur

```bash
loginctl terminate-user alice
```

## Le Lingering — clé pour les services utilisateur

Par défaut, les services `systemd --user` (unités dans `~/.config/systemd/user/`) sont **stoppés dès que toutes les sessions de l'utilisateur se ferment**. Le *lingering* permet de maintenir l'instance systemd utilisateur active même en l'absence de session ouverte.

### Cas d'usage typiques

- Lancer un bot, un agent, un service réseau sans session interactive
- Conserver des timers utilisateur actifs 24h/24
- Maintenir des conteneurs Podman rootless au démarrage

### Activer le lingering

```bash
# Activer pour l'utilisateur courant
loginctl enable-linger

# Activer pour un utilisateur spécifique (nécessite root)
sudo loginctl enable-linger alice
sudo loginctl enable-linger 1001
```

### Désactiver le lingering

```bash
loginctl disable-linger
sudo loginctl disable-linger alice
```

### Vérifier l'état du lingering

```bash
loginctl show-user alice | grep Linger
# Linger=yes

# Ou directement :
ls /var/lib/systemd/linger/
```

La présence du fichier `/var/lib/systemd/linger/<username>` indique que le lingering est activé.

!!! tip "Démarrage automatique d'un service utilisateur"
    Pour qu'un service utilisateur (`~/.config/systemd/user/monservice.service`) démarre au boot :

    ```bash
    # 1. Activer le lingering
    loginctl enable-linger

    # 2. Activer le service en tant qu'utilisateur
    systemctl --user enable monservice.service
    ```

## Gestion des sièges (seats)

Un *seat* représente un ensemble de périphériques (écran, clavier, souris) associé à un poste de travail local.

```bash
# Lister les sièges
loginctl list-seats

# Afficher les détails d'un siège
loginctl show-seat seat0

# Lister les périphériques d'un siège
loginctl seat-status seat0
```

## Options courantes

| Option | Description |
| ------ | ----------- |
| `-H <host>` | Opérer sur un hôte distant via SSH |
| `-M <container>` | Opérer dans un conteneur systemd-nspawn |
| `--no-pager` | Désactiver le paginateur |
| `--no-legend` | Supprimer les en-têtes de tableaux |
| `-p <propriété>` | Afficher une propriété spécifique |
| `--signal=<SIG>` | Signal à envoyer avec `kill-*` |

## Exemples pratiques

### Identifier qui est connecté sur une machine multi-utilisateurs

```bash
loginctl list-sessions --no-pager
loginctl list-users
```

### Déconnexion forcée d'un utilisateur

```bash
sudo loginctl terminate-user bob
```

### Vérifier si un service utilisateur peut tourner au boot

```bash
loginctl show-user alice | grep -E 'Linger|State'
systemctl --user --machine=alice@ status monservice.service
```

### Surveiller les événements de session en temps réel

```bash
# Via journald, filtrer les messages de logind
journalctl -f -u systemd-logind
```

### Script : activer le lingering pour tous les utilisateurs ayant un répertoire systemd/user

```bash
for user in $(ls /home); do
  if [ -d "/home/${user}/.config/systemd/user" ]; then
    loginctl enable-linger "${user}"
    echo "Linger activé pour ${user}"
  fi
done
```

## Propriétés clés de `show-session`

| Propriété | Description |
| --------- | ----------- |
| `Id` | Identifiant de la session |
| `User` | Nom d'utilisateur |
| `Name` | Nom affiché |
| `Timestamp` | Date/heure de connexion |
| `Remote` | Session locale ou distante |
| `RemoteHost` | Hôte distant (si SSH) |
| `Service` | Service d'origine (ssh, gdm, getty…) |
| `Scope` | Scope cgroup (`session-N.scope`) |
| `Leader` | PID du processus leader |
| `Seat` | Siège associé |
| `TTY` | Terminal |
| `Display` | Variable DISPLAY |
| `Active` | Session active ou en arrière-plan |
| `State` | online, active, closing |
| `Type` | tty, x11, wayland, mir, unspecified |
| `Class` | user, greeter, lock-screen, background |

## Voir aussi

- [`systemctl --user`](../utilisateur/index.md) — gestion des services utilisateur
- [`journalctl`](journalctl.md) — consultation des logs de systemd-logind
- `man loginctl` — référence complète
- `man logind.conf` — configuration de systemd-logind
