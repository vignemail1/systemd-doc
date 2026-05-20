# Linux capabilities

Les **capabilities** Linux découpent les privilèges traditionnellement réservés à `root` en unités indépendantes, attribuables séparément à des threads ou à des binaires. Un processus ne détient ainsi que les privilèges strictement nécessaires à son fonctionnement, sans avoir à s'exécuter en root complet.

!!! note "Historique"
    Introduites par POSIX.1e (brouillon) et implémentées dans Linux 2.2, les capabilities ont été enrichies progressivement : capability sets sur les fichiers (Linux 2.6.24), bounding set par thread (2.6.25), ambient set (4.3), et `CAP_CHECKPOINT_RESTORE` (5.9) pour la derniière en date courante.

## Modèle général

Chaque **thread** possède cinq ensembles (*sets*) de capabilities indépendants. Les vérifications de permission du kernel s'effectuent uniquement sur le set **effective** (`pE`).

| Set | Abréviation | Rôle |
| --- | ----------- | ---- |
| Effective | `pE` | Capabilities actives — celles que le kernel vérifie pour autoriser une opération |
| Permitted | `pP` | Superset maximal de `pE` — une capability peut être montée dans `pE` uniquement si elle est dans `pP` |
| Inheritable | `pI` | Capabilities pouvant être transmises à un nouveau binaire via `execve` si le fichier les déclare également héritables |
| Bounding | `pB` | Plafond global, décroissant seulement — aucune capability absente de `pB` ne peut jamais rejoindre `pP` |
| Ambient | `pA` | Capabilities préservées à travers un `execve` vers un binaire non privilégié (non setuid, sans file capabilities) |

```
           ┌──────────────┐
           │  pB (plafond) │  réductible, jamais augmenté
           └──────┬───────┘
                  │ contraint
  ┌───────────────▼──────────────────┐
  │         pP (permitted)           │
  │  ┌───────────────────────────┐   │
  │  │       pE (effective)      │   │
  │  └───────────────────────────┘   │
  │  ┌──────────┐  ┌──────────────┐  │
  │  │  pI      │  │  pA (ambient)│  │
  │  └──────────┘  └──────────────┘  │
  └──────────────────────────────────┘
```

## File capabilities

En plus des sets par thread, les binaires exécutables peuvent porter des capabilities directement dans leurs **attributs étendus** (`security.capability`). Le kernel combine les sets du thread parent et ceux du fichier lors d'un `execve`.

| Set fichier | Abréviation | Rôle |
| ----------- | ----------- | ---- |
| Permitted | `fP` | Capabilities ajoutées à `pP` du nouveau processus (intersectées avec `pB`) |
| Inheritable | `fI` | Capabilities ajoutées à `pP` si elles sont aussi dans `pI` du thread |
| Effective bit | `fE` | Bit unique — si positionné, `pP` est entièrement recopié dans `pE` après `execve` |

### Règle de transition à `execve` (simplifiée)

Après un `execve`, les nouveaux sets du thread sont calculés ainsi :

```
pP' = (fP & pB) | (fI & pI) | pA
pE' = pP'  si fE est positionné, sinon pE' = pA
pI' = pI
pA' = pA  (perdu si le binaire est setuid ou porte des file capabilities)
```

!!! warning "Interactions avec setuid"
    Si le binaire est setuid root, les règles sont différentes : `pP'` devient le bounding set complet du processus parent. Les ambient capabilities sont également réinitialisées à zéro. Ne pas mélanger setuid et file capabilities.

## Inspection et manipulation

### Voir les capabilities d'un processus

```bash
# Ses propres capabilities (capabilities du shell courant)
grep -E 'Cap(Inh|Prm|Eff|Bnd|Amb)' /proc/self/status

# D'un processus par son PID
grep -E 'Cap' /proc/1234/status

# Lecture lisible avec capsh
capsh --decode=$(grep CapEff /proc/self/status | awk '{print $2}')

# capsh affiche tous les sets du shell courant
capsh --print
```

### Voir les file capabilities d'un binaire

```bash
# Un binaire
getcap /usr/bin/ping

# Audit de tous les binaires du système
sudo getcap -r / 2>/dev/null
```

### Attribuer des file capabilities

```bash
# Donner cap_net_raw à ping (remplace le bit setuid)
sudo chmod u-s /usr/bin/ping
sudo setcap cap_net_raw=+ep /usr/bin/ping

# tcpdump : capture réseau sans root
sudo setcap 'cap_net_admin,cap_net_raw=ep' /usr/sbin/tcpdump

# Service HTTP sur port 80 sans root
sudo setcap cap_net_bind_service=+ep /usr/local/bin/mon-serveur

# Supprimer toutes les file capabilities
sudo setcap -r /usr/bin/ping
```

### Notation de `setcap`

La syntaxe de `setcap` est :

```
cap_nom[,cap_nom...]=(e|i|p)[+|-]
```

| Lettre | Set ciblé |
| ------ | --------- |
| `e` | Effective bit (`fE`) |
| `i` | Inheritable (`fI`) |
| `p` | Permitted (`fP`) |

Exemple : `cap_net_bind_service=+eip` active les trois sets pour ce fichier.

## Ambient capabilities

Les ambient capabilities (`pA`) résolvent le cas fréquent d'un service qui exécute un script ou un binaire secondaire non setuid et doit lui transmettre certains privilèges sans modifier le binaire.

### Conditions d'utilisation

Une capability peut être ajoutée dans `pA` seulement si elle est déjà dans `pP` **et** dans `pI`. Elle est automatiquement supprimée de `pA` si le processus exécute un binaire setuid ou un binaire portant des file capabilities.

### Via `prctl` (code C)

```c
// Ajouter CAP_NET_ADMIN dans le set ambient
prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_RAISE, CAP_NET_ADMIN, 0, 0);

// Supprimer une ambient capability
prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_LOWER, CAP_NET_ADMIN, 0, 0);

// Vider le set ambient
prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL, 0, 0, 0);
```

### Via `capsh` (expérimentation shell)

```bash
# Ouvrir un sous-shell avec cap_net_admin en ambient
sudo capsh \
  --caps='cap_net_admin+eip' \
  --keep=1 \
  --user=unpriv \
  --addamb=cap_net_admin \
  -- -c 'capsh --print'
```

## Intégration systemd

systemd expose directement les capability sets dans les unités de service, ce qui évite de modifier les binaires.

```ini
[Service]
User=unpriv

# Restreindre le bounding set : le service ne peut jamais acquérir
# de capabilities en dehors de cette liste
CapabilityBoundingSet=CAP_NET_BIND_SERVICE CAP_NET_ADMIN

# Remplir le set ambient : transmis à tous les exec() du service
# (doit être un sous-ensemble de CapabilityBoundingSet)
AmbientCapabilities=CAP_NET_BIND_SERVICE

# Interdire toute élévation de privilèges via setuid ou file caps
NoNewPrivileges=yes

ExecStart=/usr/local/bin/mon-daemon
```

!!! tip "Ordre des directives"
    `CapabilityBoundingSet=` agit en premier (plafond), `AmbientCapabilities=` en second (ce qui est injecté). Toute capability dans `AmbientCapabilities=` absent du `CapabilityBoundingSet=` est ignorée silencieusement par systemd. Activer `NoNewPrivileges=yes` est fortement recommandé car il empêche tout retour en arrière via un binaire setuid.

### Correspondance sets systemd → thread

| Directive systemd | Set thread modifié |
| ----------------- | ------------------ |
| `CapabilityBoundingSet=` | `pB` |
| `AmbientCapabilities=` | `pA` (et implicitement `pP`, `pI`) |
| `SecureBits=` | Flags de sécurité (`SECBIT_*`) influençant les transitions |

## Référence des capabilities importantes

!!! note
    La liste complète (plus de 40 capabilities sur noyaux récents) est dans `man 7 capabilities`. Cette section détaille les plus courantes, classées par domaine.

### Système de fichiers

| Capability | Description | Danger |
| ---------- | ----------- | ------ |
| `CAP_CHOWN` | Modifier le propriétaire d'un fichier | Moyen |
| `CAP_DAC_OVERRIDE` | Ignorer les permissions de lecture/écriture/exécution | **Élevé** |
| `CAP_DAC_READ_SEARCH` | Ignorer les permissions de lecture et de traversée de répertoire | **Élevé** |
| `CAP_FOWNER` | Opérations sur les fichiers dont l'UID ne correspond pas | Moyen |
| `CAP_FSETID` | Conserver les bits setuid/setgid lors d'une écriture | Faible |
| `CAP_MKNOD` | Créer des fichiers spéciaux (`/dev/*`) | Moyen |
| `CAP_LINUX_IMMUTABLE` | Positionner les attributs `FS_IMMUTABLE` et `FS_APPEND` | Faible |

### Processus et utilisateurs

| Capability | Description | Danger |
| ---------- | ----------- | ------ |
| `CAP_SETUID` | Modifier l'UID réel/effectif/sauvegardé | **Élevé** |
| `CAP_SETGID` | Modifier le GID réel/effectif/sauvegardé | **Élevé** |
| `CAP_SETPCAP` | Modifier les capability sets d'autres processus ou le bounding set propre | **Élevé** |
| `CAP_KILL` | Envoyer des signaux à des processus d'autres utilisateurs | Moyen |
| `CAP_SYS_NICE` | Modifier les priorités d'ordonnancement | Faible |
| `CAP_SYS_RESOURCE` | Ignorer les limites de ressources (`ulimit`) | Moyen |
| `CAP_SYS_PTRACE` | `ptrace()` de n'importe quel processus | **Élevé** |

### Réseau

| Capability | Description | Danger |
| ---------- | ----------- | ------ |
| `CAP_NET_BIND_SERVICE` | Écouter sur des ports < 1024 | Faible |
| `CAP_NET_ADMIN` | Configuration réseau (interfaces, routes, firewall, namespaces réseau) | **Élevé** |
| `CAP_NET_RAW` | Sockets `AF_PACKET` et `SOCK_RAW` (ping, tcpdump, scapy) | Moyen |
| `CAP_NET_BROADCAST` | Envoi et réception de broadcast/multicast | Faible |

### Kernel et système

| Capability | Description | Danger |
| ---------- | ----------- | ------ |
| `CAP_SYS_ADMIN` | Fourre-tout : montage FS, namespaces, BPF, quotas, audit, keyrings… | **Critique** |
| `CAP_SYS_BOOT` | `reboot()` et `kexec_load()` | **Élevé** |
| `CAP_SYS_MODULE` | Charger/décharger des modules noyau | **Critique** |
| `CAP_SYS_TIME` | Modifier l'horloge système | Moyen |
| `CAP_SYS_CHROOT` | `chroot()` | Moyen |
| `CAP_SYSLOG` | Accès aux logs noyau (`dmesg`) | Faible |
| `CAP_BPF` | Charger des programmes BPF privilégiés | **Élevé** |
| `CAP_PERFMON` | Accès aux compteurs de performance noyau | Moyen |
| `CAP_CHECKPOINT_RESTORE` | CRIU — checkpoint/restore de processus | Moyen |

### Sécurité et audit

| Capability | Description | Danger |
| ---------- | ----------- | ------ |
| `CAP_SETFCAP` | Modifier les file capabilities de n'importe quel fichier | **Élevé** |
| `CAP_AUDIT_WRITE` | Écrire dans le journal d'audit noyau | Faible |
| `CAP_AUDIT_CONTROL` | Configurer l'audit noyau | Moyen |
| `CAP_MAC_ADMIN` | Modifier les politiques MAC (SELinux, AppArmor) | **Élevé** |
| `CAP_MAC_OVERRIDE` | Ignorer les politiques MAC | **Critique** |

!!! warning "`CAP_SYS_ADMIN` et `CAP_SYS_MODULE`"
    Ces deux capabilities sont quasi-équivalentes à root complet. `CAP_SYS_ADMIN` couvre plus de 200 opérations noyau distinctes ; un binaire portant cette capability peut sortir de la plupart des sandboxes. Les éviter impérativement dans un service — préférer une capability spécifique.

## Capabilities et namespaces (containers)

Dans un user namespace ou un réseau namespace, certaines capabilities donnent des droits uniquement à l'intérieur du namespace, sans affecter l'hôte.

```bash
# Créer un user namespace sans aucun privilège hôte
unshare --user --map-root-user --net bash

# Dans le namespace, on est "root" mais les capabilities
# sont limitées à ce namespace
capsh --print
```

!!! note "systemd-nspawn"
    `systemd-nspawn` retire par défaut plusieurs capabilities dangereuses (`CAP_SYS_MODULE`, `CAP_SYS_BOOT`, `CAP_MAC_ADMIN`…) et crée un user namespace isolé. La directive `--capability=` permet d'en ajouter explicitement. Voir [systemd-nspawn](../outils/systemd-nspawn.md).

## Diagnostics courants

### Vérifier pourquoi une opération échoue avec `EPERM`

```bash
# Identifier quelle capability serait nécessaire
strace -e trace=all commande 2>&1 | grep EPERM

# Afficher les sets du processus courant de manière lisible
capsh --print

# Décoder la valeur hexadécimale de /proc/PID/status
capsh --decode=$(grep CapEff /proc/self/status | awk '{print $2}')
```

### Auditer les binaires avec des file capabilities

```bash
# Lister tous les binaires avec des capabilities sur le système
sudo getcap -r / 2>/dev/null

# Filtrer les binaires setuid (complémentaire)
find / -perm /4000 -type f 2>/dev/null
```

### Vérifier les capabilities d'un service systemd

```bash
# Voir les capabilities effectives du processus principal d'un service
systemctl show mon-service.service -p MainPID --value | \
  xargs -I{} sh -c 'grep Cap /proc/{}/status'

# Via systemd directement
systemctl show mon-service.service -p CapabilityBoundingSet
```

### Tester un bounding set réduit avec `capsh`

```bash
# Simuler un service avec uniquement cap_net_bind_service
sudo capsh \
  --drop=cap_sys_admin,cap_setuid,cap_setgid \
  --caps='cap_net_bind_service+eip' \
  -- -c 'capsh --print && mon-binaire'
```

## Bonnes pratiques

- **Principe du moindre privilège** : identifier précisément quelle capability est nécessaire avant d'en accorder une. La page `man 7 capabilities` décrit opération par opération ce que couvre chaque capability.
- **Éviter `CAP_SYS_ADMIN`** : si un service en a besoin, analyser laquelle de ses sous-opérations est réellement utilisée — il existe souvent une capability plus fine.
- **Préférer les directives systemd** aux file capabilities quand c'est possible : les directives sont versionables, auditables et n'affectent pas le binaire sur disque.
- **Toujours combiner avec `NoNewPrivileges=yes`** dans systemd : empêche qu'un fils `exec()` d'un service récupère des privileges supplémentaires via setuid ou file capabilities.
- **Auditer régulièrement** avec `getcap -r /` : les mises à jour de packages peuvent réinstaller des binaires sans conserver les file capabilities, ou au contraire en ajouter.
- **Méfiance dans les containers** : `CAP_NET_ADMIN` dans un netns isolé ne donne pas accès au réseau hôte, mais `CAP_SYS_ADMIN` dans un container mal configuré peut le faire sortir de son isolation.

## Voir aussi

- [systemd-nspawn](../outils/systemd-nspawn.md) — containers légers et gestion des capabilities
- [systemd.exec](https://www.freedesktop.org/software/systemd/man/systemd.exec.html) — directives `CapabilityBoundingSet=`, `AmbientCapabilities=`, `NoNewPrivileges=`
- `man 7 capabilities` — référence complète avec toutes les capabilities et les règles de transition
- `man 8 setcap` et `man 8 getcap` — manipulation des file capabilities
- `man 1 capsh` — shell avec capabilities réduites, outil de test
- `man 2 prctl` — API noyau pour manipuler les sets depuis le code
- [Slides Michael Kerrisk — The Linux capabilities model](https://man7.org/training/download/capns_caps_slides-mkerrisk-man7.org.pdf)
