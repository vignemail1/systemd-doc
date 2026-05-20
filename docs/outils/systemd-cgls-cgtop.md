# systemd-cgls et systemd-cgtop

`systemd-cgls` et `systemd-cgtop` sont deux outils complémentaires pour inspecter et surveiller les cgroups (control groups) gérés par systemd. Ils permettent de visualiser l'arborescence des cgroups et de suivre la consommation de ressources en temps réel.

## systemd-cgls

`systemd-cgls` affiche l'arborescence complète des cgroups sous forme d'arbre, avec les processus contenus dans chaque cgroup.

### Syntaxe

```
systemd-cgls [OPTIONS] [CGROUP...]
```

### Utilisation de base

```bash
# Afficher l'arborescence complète
systemd-cgls

# Afficher un cgroup spécifique et ses enfants
systemd-cgls system.slice
systemd-cgls user.slice
systemd-cgls machine.slice

# Afficher le cgroup d'un service précis
systemd-cgls system.slice/nginx.service

# Afficher sans couleurs (pour scripts)
systemd-cgls --no-pager

# Utiliser un chemin absolu de cgroup (hiérarchie v2)
systemd-cgls /sys/fs/cgroup/system.slice
```

### Lire la sortie

```
Control group /:
-.slice
├─user.slice
│ └─user-1000.slice
│   ├─user@1000.service
│   │ └─session.scope
│   │   ├─1234 /usr/bin/bash
│   │   └─5678 systemd-cgls
│   └─session-3.scope
│     └─2345 sshd: sebastien [priv]
└─system.slice
  ├─nginx.service
  │ ├─891 nginx: master process
  │ └─892 nginx: worker process
  └─systemd-journald.service
    └─456 /usr/lib/systemd/systemd-journald
```

Chaque ligne montre le cgroup, ses sous-cgroups et les PIDs des processus qu'il contient directement.

### Options principales

| Option | Description |
|--------|-------------|
| `-l`, `--full` | Affiche les lignes de commande complètes (non tronquées) |
| `-k`, `--kernel` | Inclut les threads noyau |
| `--unit=UNIT` | Filtre sur une unité systemd |
| `--user-unit=UNIT` | Filtre sur une unité utilisateur |
| `--no-pager` | Désactive le pager |
| `-M NAME`, `--machine=NAME` | Inspecte les cgroups d'une machine/conteneur |

## systemd-cgtop

`systemd-cgtop` affiche les cgroups triés par consommation de ressources, de manière similaire à `top` mais par cgroup. Il est utile pour identifier quel service, slice ou unité consomme le plus de CPU, mémoire ou I/O.

### Syntaxe

```text
systemd-cgtop [OPTIONS] [CGROUP]
```

### Utilisation de base

```bash
# Monitoring interactif (rafraîchissement toutes les secondes par défaut)
systemd-cgtop

# Restreindre à un sous-cgroup
systemd-cgtop system.slice
systemd-cgtop user.slice

# Trier par mémoire
systemd-cgtop --order=memory

# Trier par I/O
systemd-cgtop --order=io

# Rafraîchissement toutes les 2 secondes
systemd-cgtop --delay=2

# Mode batch (non interactif, pour scripts)
systemd-cgtop --batch --iterations=1

# Afficher n itérations puis quitter
systemd-cgtop --iterations=5
```

### Colonnes affichées

| Colonne | Description |
|---------|-------------|
| `Path` | Chemin du cgroup dans la hiérarchie |
| `Tasks` | Nombre de processus/threads |
| `%CPU` | Utilisation CPU (cumulée sur tous les cœurs) |
| `Memory` | Mémoire résidente (RSS) |
| `Input/s` | Débit lecture I/O |
| `Output/s` | Débit écriture I/O |

!!! note
    Les données I/O ne sont disponibles que si le contrôleur `io` est activé dans la hiérarchie cgroup v2. Sur cgroup v1, seuls CPU et mémoire sont disponibles.

### Raccourcis clavier (mode interactif)

| Touche | Action |
|--------|--------|
| `p` | Trier par CPU |
| `m` | Trier par mémoire |
| `i` | Trier par I/O |
| `t` | Trier par nombre de tâches |
| `%` | Basculer entre valeurs absolues et pourcentages |
| `q` | Quitter |
| `+` / `-` | Augmenter/diminuer l'intervalle de rafraîchissement |

### Options principales

| Option | Description |
|--------|-------------|
| `-o ORDER`, `--order=ORDER` | Tri : `path`, `tasks`, `cpu`, `memory`, `io` |
| `-d DELAY`, `--delay=DELAY` | Intervalle de rafraîchissement en secondes |
| `-n N`, `--iterations=N` | Nombre d'itérations avant de quitter |
| `-b`, `--batch` | Mode non interactif (compatible scripts) |
| `-r`, `--raw` | Valeurs brutes sans unités humaines |
| `-M NAME`, `--machine=NAME` | Inspecte les cgroups d'une machine/conteneur |
| `--depth=N` | Profondeur maximale de l'arborescence affichée |
| `--cpu=TYPE` | `time` (défaut) ou `percentage` |

## Cas pratiques

### Identifier quel service consomme le plus de mémoire

```bash
systemd-cgtop --order=memory --iterations=1 --batch
```

Affiche un instantané trié par mémoire, sans interaction, exploitable dans un script ou une alerte.

### Surveiller la consommation d'un slice applicatif

```bash
systemd-cgtop system.slice --order=cpu
```

Restreint la vue aux seuls services de `system.slice`, trié par CPU.

### Inspecter les processus d'un service récalcitrant

```bash
# Voir quels PIDs sont dans le cgroup du service
systemd-cgls system.slice/mon-service.service

# Puis vérifier l'arbre des processus
ps --ppid $(systemctl show -p MainPID --value mon-service.service) --forest
```

### Surveiller les conteneurs nspawn

```bash
# Voir l'arborescence cgroup des machines
systemd-cgls machine.slice

# Suivre les ressources d'un conteneur précis
systemd-cgtop machine.slice/machine-debian12.scope
```

### Vérifier la hiérarchie cgroup v2

```bash
# Confirmer l'utilisation de cgroup v2
cat /proc/mounts | grep cgroup
ls /sys/fs/cgroup/

# Voir les contrôleurs disponibles et actifs
cat /sys/fs/cgroup/cgroup.controllers
cat /sys/fs/cgroup/cgroup.subtree_control
```

## Relation avec systemctl

`systemctl status NOM.service` affiche déjà le cgroup et les processus associés. `systemd-cgls` et `systemd-cgtop` sont utiles quand :

- On veut une vue globale de toute la hiérarchie, pas d'un seul service
- On cherche à identifier quel service consomme des ressources sans connaître son nom à l'avance
- On travaille sur les slices et scopes directement (sessions utilisateur, machines)

## Bonnes pratiques

- Utiliser `systemd-cgtop --batch --iterations=1` dans les scripts de monitoring pour des snapshots ponctuels.
- Préférer `systemd-cgls` à `ls /sys/fs/cgroup/` pour la lisibilité : la hiérarchie est affichée avec les noms systemd plutôt que les chemins bruts.
- Vérifier avec `systemd-cgls machine.slice` que les conteneurs nspawn sont bien isolés dans leur propre sous-arborescence.
- Coupler avec `systemctl show -p CPUAccounting -p MemoryAccounting NOM.service` pour s'assurer que la comptabilité est activée sur les unités qu'on veut surveiller.

## Voir aussi

- `man systemd-cgls`
- `man systemd-cgtop`
- `man systemd.resource-control` (directives CPUWeight, MemoryMax, etc.)
- `man cgroups` (7)
