# Configuration de systemd-resolved

## Fichier principal

Le fichier `/etc/systemd/resolved.conf` configure le comportement global. Les fragments `.conf` placés dans `/etc/systemd/resolved.conf.d/` sont préférables pour les personnalisations locales.

```ini
[Resolve]
DNS=9.9.9.9 149.112.112.112
FallbackDNS=1.1.1.1 8.8.8.8
Domains=~.
DNSSEC=allow-downgrade
DNSOverTLS=opportunistic
LLMNR=no
MulticastDNS=no
Cache=yes
```

Les valeurs importantes sont :

- `DNS=` : serveurs DNS globaux ; une adresse peut inclure une interface avec `%`.
- `FallbackDNS=` : serveurs utilisés lorsque aucun DNS n'est connu.
- `Domains=` : domaines de recherche ; `~.` rend le lien global prioritaire pour tous les noms.
- `DNSSEC=` : `no`, `allow-downgrade` ou `yes`.
- `DNSOverTLS=` : `no`, `opportunistic` ou `yes`.
- `LLMNR=` et `MulticastDNS=` : activation de la résolution locale.
- `Cache=` : cache local (`yes`, `no` ou `positive`).

Après modification :

```bash
systemctl restart systemd-resolved
resolvectl status
```

## DNS par interface

Avec `systemd-networkd`, placer par exemple dans un fichier `.network` :

```ini
[Network]
DNS=192.0.2.53
Domains=example.internal
```

Pour un réglage temporaire :

```bash
resolvectl dns eth0 192.0.2.53
resolvectl domain eth0 '~example.internal'
```

Le préfixe `~` désigne un domaine de routage DNS ; `~.` correspond à la route par défaut.

## DNS over TLS

`DNSOverTLS=yes` exige un serveur compatible et un certificat valide. Le mode `opportunistic` tente TLS puis revient à DNS classique ; il ne garantit donc pas la confidentialité.

## DNSSEC

`DNSSEC=yes` impose la validation et peut rendre inaccessibles des zones mal configurées. `allow-downgrade` est plus tolérant mais ne fournit pas la même garantie.

## Lien resolv.conf

```bash
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

Choisir un seul mode et vérifier qu'aucun autre service ne réécrit ce lien.
