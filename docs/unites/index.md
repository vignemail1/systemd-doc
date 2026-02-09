# Unités systemd

Les **unités** (units) sont les briques fondamentales de systemd. Chaque unité représente une ressource que systemd sait gérer : un service, un point de montage, un périphérique, un socket, etc.

## Qu'est-ce qu'une unité ?

Une unité systemd est définie par un fichier de configuration qui décrit :

- **Ce qu'elle représente** : Type de ressource (service, socket, timer...)
- **Comment la gérer** : Commandes de démarrage, arrêt, rechargement
- **Ses dépendances** : Relations avec d'autres unités
- **Quand l'activer** : Conditions de démarrage

## Types d'unités

systemd gère 11 types d'unités principaux, identifiés par leur extension :

### Services (`.service`)

Représentent des processus ou daemons système. C'est le type le plus courant.

**Exemples** : `nginx.service`, `sshd.service`, `postgresql.service`

### Sockets (`.socket`)

Définissent des points de communication (sockets Unix, TCP, UDP) pour l'activation à la demande.

**Exemples** : `sshd.socket`, `docker.socket`

### Timers (`.timer`)

Planifient l'exécution de services, remplacent cron de manière moderne.

**Exemples** : `logrotate.timer`, `backup.timer`

### Targets (`.target`)

Groupent des unités et représentent des états du système (remplacent les runlevels).

**Exemples** : `multi-user.target`, `graphical.target`

### Points de montage (`.mount`)

Gèrent les systèmes de fichiers montés.

**Exemples** : `tmp.mount`, `home.mount`

### Montage automatique (`.automount`)

Activent des points de montage à la demande lors du premier accès.

**Exemples** : `proc-sys-fs-binfmt_misc.automount`

### Chemins (`.path`)

Surveillent des fichiers ou répertoires et déclenchent des services.

**Exemples** : `cups.path` (surveille le répertoire d'impression)

### Périphériques (`.device`)

Représentent des périphériques matériels exposés par udev.

**Exemples** : `dev-sda.device`

### Swap (`.swap`)

Gèrent les espaces de swap (mémoire virtuelle).

**Exemples** : `dev-sda2.swap`

### Scopes (`.scope`)

Groupent des processus externes lancés par d'autres programmes (créés programmatiquement).

**Exemples** : `session-1.scope` (session utilisateur)

### Slices (`.slice`)

Organisent hiérarchiquement les unités pour la gestion des ressources via cgroups.

**Exemples** : `system.slice`, `user.slice`, `machine.slice`

## Nommage des unités

Les noms d'unités suivent des conventions strictes :

```
<nom>[@<instance>].<type>
```

### Exemples

- `nginx.service` : Service nginx
- `sshd.socket` : Socket SSH
- `backup.timer` : Timer de sauvegarde
- `getty@tty1.service` : Instance de getty sur tty1
- `systemd-fsck@dev-sda1.service` : Fsck pour /dev/sda1

### Unités instanciées

Le caractère `@` permet de créer plusieurs instances d'une même unité :

```ini
# getty@.service (template)
[Unit]
Description=Getty on %I

[Service]
ExecStart=/sbin/agetty %I
```

Instances :
- `getty@tty1.service`
- `getty@tty2.service`
- `getty@ttyS0.service`

## Emplacements des fichiers d'unités

systemd recherche les fichiers d'unités dans plusieurs répertoires, par ordre de priorité :

### 1. `/etc/systemd/system/` (priorité haute)

Unités créées ou modifiées par l'administrateur système.

```bash
/etc/systemd/system/
├── myapp.service              # Service personnalisé
├── nginx.service.d/           # Overrides pour nginx
│   └── custom.conf
└── multi-user.target.wants/   # Dépendances
    └── myapp.service -> /etc/systemd/system/myapp.service
```

### 2. `/run/systemd/system/` (priorité moyenne)

Unités runtime volatiles, créées dynamiquement (perdues au reboot).

### 3. `/usr/lib/systemd/system/` (priorité basse)

Unités fournies par les packages des distributions.

```bash
/usr/lib/systemd/system/
├── sshd.service
├── nginx.service
├── postgresql.service
└── ...
```

!!! warning "Ordre de priorité"
    Si un fichier d'unité existe dans plusieurs emplacements, celui dans `/etc` prend toujours la priorité.

## Structure d'un fichier d'unité

Tous les fichiers d'unités partagent une structure commune :

```ini
[Unit]
# Métadonnées et dépendances
Description=...
Documentation=...
After=...
Requires=...

[<Type>]  # [Service], [Socket], [Timer], etc.
# Configuration spécifique au type

[Install]
# Comportement lors de l'activation
WantedBy=...
RequiredBy=...
```

### Section `[Unit]`

Commune à tous les types d'unités, définit les métadonnées et dépendances.

### Section spécifique au type

`[Service]`, `[Socket]`, `[Timer]`, etc. selon le type d'unité.

### Section `[Install]`

Définit comment activer l'unité avec `systemctl enable`.

## Commandes de base

### Lister les unités

```bash
# Unités actives
systemctl list-units

# Tous les fichiers d'unités
systemctl list-unit-files

# Unités d'un type spécifique
systemctl list-units --type=service
systemctl list-units --type=timer

# Unités en échec
systemctl list-units --state=failed
```

### Inspecter une unité

```bash
# Voir le contenu du fichier
systemctl cat nginx.service

# Voir la configuration effective (avec overrides)
systemctl show nginx.service

# Voir les dépendances
systemctl list-dependencies nginx.service
```

### Gérer les unités

```bash
# Démarrer
systemctl start myapp.service

# Arrêter
systemctl stop myapp.service

# Redémarrer
systemctl restart myapp.service

# Recharger la configuration (sans redémarrage)
systemctl reload myapp.service

# Voir l'état
systemctl status myapp.service

# Activer au boot
systemctl enable myapp.service

# Désactiver
systemctl disable myapp.service
```

## États d'une unité

Une unité peut être dans plusieurs états :

### État de chargement (Load State)

- **loaded** : Unité correctement chargée
- **not-found** : Fichier d'unité introuvable
- **bad-setting** : Erreur de syntaxe
- **error** : Autre erreur
- **masked** : Unité masquée (désactivée complètement)

### État actif (Active State)

- **active** : Unité active et fonctionnelle
- **inactive** : Unité arrêtée
- **activating** : En cours de démarrage
- **deactivating** : En cours d'arrêt
- **failed** : Échec de démarrage ou crash
- **reloading** : En cours de rechargement

### Sous-état (Sub State)

Plus précis, varie selon le type d'unité :

**Pour les services** :
- `running` : Processus en cours d'exécution
- `exited` : Processus terminé avec succès (normal pour Type=oneshot)
- `dead` : Arrêté
- `failed` : Terminé en erreur

## Relations entre unités

systemd gère automatiquement les dépendances déclarées :

```bash
# Visualiser le graphe de dépendances
systemd-analyze dot nginx.service | dot -Tsvg > nginx-deps.svg

# Afficher les dépendances en arbre
systemctl list-dependencies nginx.service

# Dépendances inverses (qui dépend de cette unité)
systemctl list-dependencies --reverse nginx.service
```

## Overrides et drop-ins

Plutôt que de modifier directement les fichiers dans `/usr/lib`, utilisez les overrides :

```bash
# Créer un override
systemctl edit nginx.service

# Crée automatiquement :
# /etc/systemd/system/nginx.service.d/override.conf
```

**Avantage** : Les mises à jour du package n'écrasent pas vos modifications.

## Masquage d'unités

Le masquage empêche complètement le démarrage d'une unité :

```bash
# Masquer
systemctl mask bluetooth.service
# Crée un lien symbolique vers /dev/null

# Démasquer
systemctl unmask bluetooth.service
```

## Validation

Vérifier la syntaxe d'un fichier d'unité :

```bash
systemd-analyze verify myapp.service
```

Détecte les erreurs de syntaxe et dépendances circulaires.

---

Dans les sections suivantes, nous explorerons en détail chaque type d'unité avec des exemples concrets et des cas d'usage pratiques.
