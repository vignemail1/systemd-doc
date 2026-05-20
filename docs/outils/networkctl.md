# networkctl

`networkctl` est l'outil de gestion et d'inspection de `systemd-networkd`. Il permet d'afficher l'état des interfaces réseau, de forcer leur reconfiguration, et d'interroger les liens, adresses et routes gérés par `systemd-networkd`.

!!! note "Prérequis"
    `networkctl` nécessite que `systemd-networkd` soit actif. Sur une machine utilisant NetworkManager ou un autre gestionnaire réseau, les informations affichées seront partielles ou absentes.

    ```bash
    sudo systemctl enable --now systemd-networkd
    ```

## Syntaxe générale

```bash
networkctl [OPTIONS] COMMANDE [LIEN...]
```

## Inspection — vue d’ensemble

### Lister les interfaces

```bash
# Vue tabulaire de tous les liens connus
networkctl list

# Filtrer sur un ou plusieurs liens
networkctl list eth0 wlan0

# Sans paginateur (utile en script)
networkctl --no-pager list
```

La colonne `SETUP` indique l’état de configuration par `systemd-networkd` :

| Valeur | Signification |
| ------ | ------------- |
| `configured` | Interface configurée avec succès |
| `configuring` | Configuration en cours |
| `degraded` | Configurée mais au moins un paramètre manquant (ex. pas d’adresse IPv6) |
| `unmanaged` | Non gérée par `systemd-networkd` |
| `pending` | En attente d’un événement (lien physique absent) |
| `failed` | Échec de configuration |
| `linger` | Lien supprimé mais encore référencé |

### Détail d’un lien

```bash
# Informations complètes : adresses, routes, DNS, NTP, métadonnées
networkctl status eth0

# Vue condensed (pas de section détaillée)
networkctl status --brief eth0

# Plusieurs interfaces en même temps
networkctl status eth0 eth1

# Vue globale du système (sans argument)
networkctl status
```

`networkctl status` affiche notamment :

- adresses IPv4 / IPv6 assignées
- routes actives
- serveurs DNS et domaines de recherche
- serveurs NTP
- fichier `.network` actif
- état du lien physique (carrier, speed, duplex)
- information DHCP (bail, serveur, expiration)

## Propriétés brutes

```bash
# Lister toutes les propriétés d’un lien
networkctl lldp eth0      # voisins LLDP
networkctl label          # mapping numéros de label/adresse

# Afficher les informations de lien bas niveau
networkctl cat eth0       # afficher le fichier .network actif
```

## Gestion des liens

### Reconfigurer un lien

```bash
# Forcer la relecture du fichier .network et reconfiguration
sudo networkctl reconfigure eth0

# Reconfigurer plusieurs liens
sudo networkctl reconfigure eth0 eth1 wlan0

# Reconfigurer tous les liens gérés
sudo networkctl reconfigure
```

Utilisé après modification d’un fichier `.network` dans `/etc/systemd/network/` sans redémarrer `systemd-networkd`.

### Recharger la configuration

```bash
# Recharger tous les fichiers .network / .netdev / .link sans redémarrer
sudo networkctl reload
```

Différence avec `reconfigure` : `reload` relit les fichiers de configuration sur disque, `reconfigure` reapplique la configuration courante sur un lien spécifique.

### Activer / désactiver un lien

```bash
# Désactiver administrativement un lien
sudo networkctl down eth1

# Réactiver
sudo networkctl up eth1
```

### Renommer un lien

```bash
# Renommer (le lien doit être inactif)
sudo networkctl down eth1
sudo networkctl rename eth1 lan1
```

## LLDP — Link Layer Discovery Protocol

`systemd-networkd` peut envoyer et recevoir des annonces LLDP. Cette fonctionnalité est activée dans le fichier `.network` avec `LLDP=yes` et `EmitLLDP=yes`.

```bash
# Afficher les voisins LLDP détectés
networkctl lldp

# LLDP pour un lien spécifique
networkctl lldp eth0
```

Les informations affichées incluent l’identifiant du voisin, les capacités système, le port annoncé et le nom de système distant — très utile pour cartographier un réseau physique.

## Adresses et routes

```bash
# Vue synthétique de toutes les adresses
ip address show   # outil ip, complémentaire

# Via networkctl : adresses dans le contexte de la gestion networkd
networkctl status   # section "Address" de la vue globale
```

!!! tip "Complémentarité avec `ip`"
    `networkctl` se concentre sur ce que `systemd-networkd` gère (configuration, fichiers `.network`, bail DHCP). La commande `ip` reste l’outil de référence pour inspecter l’état noyau des adresses, routes et règles en temps réel.

## Diagnostics courants

### Interface en état `unmanaged`

```bash
# Vérifier que systemd-networkd est actif
systemctl status systemd-networkd

# Vérifier qu’un fichier .network correspond à l’interface
ls /etc/systemd/network/
networkctl cat eth0   # affiche le fichier .network actif, erreur si aucun
```

Une interface est `unmanaged` si aucun fichier `.network` avec une section `[Match]` correspondante n’existe.

### Interface en état `degraded`

```bash
networkctl status eth0
# Chercher dans la sortie :
# - absence d’adresse IPv6 alors qu’une route par défaut est attendue
# - échec de résolution DNS
# - NTP non joignable
```

`degraded` n’est pas forcément problématique : une interface IPv4-only sans IPv6 apparaît souvent en `degraded` selon la configuration attendue dans le fichier `.network`.

### Pas d’adresse après `reconfigure`

```bash
# Vérifier les logs de networkd en temps réel
journalctl -u systemd-networkd -f

# Vérifier les erreurs spécifiques au lien
journalctl -u systemd-networkd | grep eth0

# Vérifier la syntaxe des fichiers .network
systemd-analyze verify /etc/systemd/network/*.network
```

### Vérifier l’état du bail DHCP

```bash
networkctl status eth0
# Section "DHCP Lease" : serveur, adresse allouée, expiration, gateway
```

## Options globales utiles

| Option | Description |
| ------ | ----------- |
| `--no-pager` | Désactiver le paginateur |
| `--no-legend` | Supprimer les en-têtes de colonnes |
| `-a`, `--all` | Inclure les interfaces sans fichier `.network` |
| `--brief` | Affichage résumé pour `status` |
| `-n <lignes>` | Limiter le nombre de lignes de journal affichées dans `status` |
| `-H <hôte>` | Hôte distant (via SSH) |
| `-M <machine>` | Machine / conteneur systemd-nspawn |
| `--json=short` | Sortie JSON compact (utile pour scripts) |
| `--json=pretty` | Sortie JSON formatée |

```bash
# Exemple : sortie JSON pour parsing
networkctl --json=short list | jq '.[] | select(.SetupState != "configured")'
```

## Voir aussi

- [systemctl](systemctl.md) — gestion générale des unités systemd
- `man networkctl` — référence complète
- `man systemd-networkd.service` — documentation du démon réseau
- `man systemd.network` — format des fichiers `.network`
- `man systemd.netdev` — format des fichiers `.netdev` (bridges, VLANs, tunnels…)
