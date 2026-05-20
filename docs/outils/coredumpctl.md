# coredumpctl

`coredumpctl` est l'outil d'interrogation et d'analyse des core dumps collectés par `systemd-coredump`. Il permet de lister, inspecter et déboguer les crashs d'applications enregistrés dans le journal systemd.

!!! note "Prérequis"
    `systemd-coredump` doit être configuré comme gestionnaire de core dumps. Vérifier :

    ```bash
    cat /proc/sys/kernel/core_pattern
    # Doit retourner : |/usr/lib/systemd/systemd-coredump %P %u %g %s %t %c %h
    ```

## Syntaxe générale

```bash
coredumpctl [OPTIONS] COMMANDE [ARGUMENT...]
```

## Lister les core dumps

```bash
# Tous les core dumps enregistrés
coredumpctl list

# Filtrer par nom d'exécutable
coredumpctl list nginx
coredumpctl list python3

# Filtrer par PID
coredumpctl list 1234

# Filtrer par UID
coredumpctl list _UID=1000

# N derniers core dumps
coredumpctl list -n 10

# Depuis une date
coredumpctl list --since="1 hour ago"
coredumpctl list --since="yesterday"
```

Colonnes de la sortie :

| Colonne | Description |
| ------- | ----------- |
| `TIME` | Date et heure du crash |
| `PID` | PID du processus crashé |
| `UID` / `GID` | Identité du processus |
| `SIGNAL` | Signal ayant provoqué le crash (`SIGSEGV`, `SIGABRT`…) |
| `COREFILE` | `present` si le binaire du core est stocké, `missing` si purgé |
| `EXE` | Chemin de l'exécutable |

## Informations détaillées

```bash
# Informations complètes sur le dernier crash
coredumpctl info

# Informations sur le crash d'un exécutable spécifique
coredumpctl info nginx

# Informations sur un crash par PID
coredumpctl info 1234

# Informations sur le Nième crash (index depuis la liste)
coredumpctl info 2  # le 3e depuis la fin
```

La sortie inclut : exécutable, UID/GID, signal, stacktrace, variables d'environnement, unité systemd, et message d'erreur si disponible.

## Débogage avec GDB

```bash
# Ouvrir le dernier core dump dans GDB
coredumpctl debug

# Ouvrir le core dump d'un exécutable spécifique
coredumpctl debug nginx

# Passer des arguments à GDB
coredumpctl debug nginx -- -ex 'bt full' -batch

# Utiliser un debugger alternatif
coredumpctl debug nginx --debugger=lldb
```

Dans GDB après ouverture :

```gdb
(gdb) bt           # backtrace
(gdb) bt full      # backtrace avec variables locales
(gdb) info threads # lister les threads
(gdb) thread 2     # basculer sur le thread 2
(gdb) frame 3      # basculer sur le frame 3
(gdb) list         # afficher le code source (si symboles présents)
(gdb) quit
```

## Exporter un core dump

```bash
# Extraire le fichier core dump brut
coredumpctl dump nginx > nginx.core
coredumpctl dump nginx -o /tmp/nginx.core

# Extraire par PID
coredumpctl dump 1234 -o /tmp/crash-1234.core

# Analyser le core exporté avec GDB
gdb /usr/sbin/nginx /tmp/nginx.core
```

## Configuration de systemd-coredump

Le fichier de configuration est `/etc/systemd/coredump.conf` (ou `/etc/systemd/coredump.conf.d/*.conf`).

```ini
[Coredump]
# Stocker les core dumps (journal ou external)
Storage=external

# Compresser les core dumps stockés
Compress=yes

# Taille max d'un core dump à stocker
ProcessSizeMax=2G

# Taille max totale des core dumps
ExternalSizeMax=2G

# Durée de rétention
KeepFree=1G

# Limite de taille totale du répertoire
MaxUse=
```

```bash
# Voir la configuration effective
systemd-analyze cat-config systemd/coredump.conf

# Appliquer
sudo systemctl restart systemd-coredump.socket
```

### Modes de stockage

| `Storage=` | Comportement |
| ---------- | ------------ |
| `external` | Fichier dans `/var/lib/systemd/coredump/` (défaut) |
| `journal` | Embarqué dans le journal systemd (déconseillé pour gros binaires) |
| `none` | Enregistré dans le journal sans stocker le binaire |

## Nettoyage

```bash
# Voir l'espace occupé par les core dumps
ls -lh /var/lib/systemd/coredump/

# Supprimer tous les core dumps stockés
sudo rm /var/lib/systemd/coredump/*.zst

# Le vacuum du journal supprime aussi les core dumps embarqués
sudo journalctl --vacuum-time=30d
```

## Diagnostics courants

### Aucun core dump dans la liste

```bash
# Vérifier que systemd-coredump est le gestionnaire actif
cat /proc/sys/kernel/core_pattern

# Vérifier que le socket est actif
systemctl status systemd-coredump.socket

# Vérifier les limites de taille
ulimit -c
# Si 0, les core dumps sont désactivés pour ce shell
# systemd-coredump contourne cela via le kernel core_pattern
```

### `COREFILE=missing` dans la liste

```bash
# Le core a été purgé (taille trop grande ou vacuum)
# Les métadonnées (backtrace partiel, signal) sont encore dans le journal
coredumpctl info 1234

# Ajuster la taille maximale
# /etc/systemd/coredump.conf.d/size.conf
[Coredump]
ProcessSizeMax=4G
ExternalSizeMax=8G
```

### Core dump sans symboles (backtrace illisible)

```bash
# Installer les symboles de debug du paquet concerné
# Debian/Ubuntu
sudo apt install nginx-dbg

# RHEL/Fedora (debuginfo)
sudo dnf debuginfo-install nginx

# Relancer coredumpctl debug après installation
coredumpctl debug nginx
```

## Options globales utiles

| Option | Description |
| ------ | ----------- |
| `--no-pager` | Désactiver le paginateur |
| `--no-legend` | Supprimer les en-têtes |
| `-n <N>` | Limiter aux N derniers core dumps |
| `--since=` | Filtrer depuis une date |
| `--until=` | Filtrer jusqu'à une date |
| `-o <fichier>` | Fichier de sortie pour `dump` |
| `--debugger=` | Debugger alternatif (`lldb`, etc.) |
| `--json=short` | Sortie JSON compacte |
| `--json=pretty` | Sortie JSON formatée |

## Voir aussi

- `man coredumpctl`
- `man systemd-coredump(8)`
- `man coredump.conf(5)`
