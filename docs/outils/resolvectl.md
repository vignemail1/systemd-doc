# resolvectl

`resolvectl` est l'outil d'interrogation et de configuration de `systemd-resolved`, le résolveur DNS avec cache intégré à systemd. Il permet de résoudre des noms, d'inspecter le cache, de configurer les serveurs DNS par interface et de vérifier l'état DNSSEC.

## Syntaxe générale

```bash
resolvectl [OPTIONS] COMMANDE [ARGUMENT...]
```

## État global

```bash
# Vue d'ensemble : DNS global, DNSSEC, mDNS, LLMNR, état des interfaces
resolvectl status

# État d'une interface spécifique
resolvectl status eth0
resolvectl status eth0 wlan0

# Sans paginateur
resolvectl --no-pager status
```

La sortie montre pour chaque interface : les serveurs DNS en cours d'utilisation, les domaines de recherche, l'état DNSSEC et mDNS.

## Résolution DNS

```bash
# Résoudre un nom (A + AAAA)
resolvectl query example.com

# Résolution inverse (PTR)
resolvectl query 93.184.216.34
resolvectl query 2606:2800:220:1:248:1893:25c8:1946

# Forcer un type d'enregistrement
resolvectl query --type=MX example.com
resolvectl query --type=TXT example.com
resolvectl query --type=NS example.com
resolvectl query --type=SRV _https._tcp.example.com

# Forcer une classe DNS
resolvectl query --class=IN example.com

# Désactiver le cache pour cette requête
resolvectl query --cache=no example.com

# Requête via une interface spécifique
resolvectl query --interface=eth0 example.com
```

## Résolution de services (SRV/DNS-SD)

```bash
# Rechercher un service DNS-SD
resolvectl service _http._tcp example.com

# Rechercher un service mDNS local
resolvectl service _ssh._tcp local
```

## DNSSEC

```bash
# Vérifier la chaîne DNSSEC d'un domaine
resolvectl query --validate example.com

# Afficher les enregistrements DNSKEY
resolvectl query --type=DNSKEY example.com

# Afficher les enregistrements DS
resolvectl query --type=DS example.com
```

## Gestion du cache

```bash
# Statistiques du cache (hits, misses, taille)
resolvectl statistics

# Vider le cache DNS
resolvectl flush-caches

# Réinitialiser les statistiques
resolvectl reset-statistics
```

## Configuration DNS par interface

Ces réglages sont temporaires (perdus au redémarrage ou à la reconfiguration de l'interface). Pour une configuration persistante, utiliser un fichier `.network`.

```bash
# Définir des serveurs DNS pour une interface
resolvectl dns eth0 9.9.9.9 149.112.112.112
resolvectl dns eth0 2620:fe::fe 2620:fe::9

# Définir des domaines de recherche
resolvectl domain eth0 example.com internal.example.com

# Domaine de routage (préfixe ~ = routage DNS split)
resolvectl domain eth0 ~internal.example.com

# Activer/désactiver DNSSEC par interface
resolvectl dnssec eth0 yes
resolvectl dnssec eth0 no
resolvectl dnssec eth0 allow-downgrade

# Activer/désactiver mDNS par interface
resolvectl mdns eth0 yes
resolvectl mdns eth0 no
resolvectl mdns eth0 resolve   # recevoir seulement, sans émettre

# Activer/désactiver LLMNR par interface
resolvectl llmnr eth0 yes
resolvectl llmnr eth0 no
```

## Logs DNS (DNSSEC debugging)

```bash
# Voir les requêtes DNS en temps réel
resolvectl log-level debug
journalctl -u systemd-resolved -f

# Remettre au niveau normal
resolvectl log-level info
```

## Diagnostics courants

### Vérifier quel serveur DNS est utilisé

```bash
resolvectl status
# Chercher "DNS Servers" et "DNS Domain" par interface
# "Current DNS Server" indique le serveur actif
```

### Tester la résolution pas à pas

```bash
# Résolution avec détail du chemin DNSSEC
resolvectl query --validate --legend=yes example.com

# Comparer avec une résolution directe (bypasse resolved)
dig @9.9.9.9 example.com
```

### `resolved` et `/etc/resolv.conf`

```bash
# Vérifier le mode de gestion de resolv.conf
ls -la /etc/resolv.conf
# → lien vers /run/systemd/resolve/stub-resolv.conf  (mode stub, recommandé)
# → lien vers /run/systemd/resolve/resolv.conf       (mode uplink)
# → fichier statique                                  (non géré par resolved)

# Recréer le lien si supprimé
sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

### Résolution échoue sur une interface VPN

```bash
# Vérifier les domaines de routage DNS de l'interface VPN
resolvectl status tun0

# Forcer le routage DNS pour un domaine vers cette interface
resolvectl domain tun0 ~corp.example.com
```

## Options globales utiles

| Option | Description |
| ------ | ----------- |
| `--no-pager` | Désactiver le paginateur |
| `--no-legend` | Supprimer les en-têtes |
| `-i, --interface=` | Interface réseau cible |
| `-p, --protocol=` | Protocole : `dns`, `llmnr`, `mdns` |
| `-t, --type=` | Type d'enregistrement DNS |
| `--validate` | Activer la validation DNSSEC |
| `--cache=no` | Ignorer le cache pour la requête |
| `--json=short` | Sortie JSON compacte |
| `--json=pretty` | Sortie JSON formatée |

## Voir aussi

- [networkctl](networkctl.md) — configuration réseau des interfaces
- `man resolvectl`
- `man systemd-resolved.service`
- `man resolved.conf`
