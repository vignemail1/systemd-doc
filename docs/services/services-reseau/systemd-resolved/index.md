# systemd-resolved

`systemd-resolved` fournit la résolution de noms et la gestion DNS locale. Il peut recevoir les paramètres DNS de `systemd-networkd`, gérer le DNS par lien et exposer un stub local sur `127.0.0.53`.

## Rôle

- Résolution DNS, LLMNR et mDNS selon la configuration.
- Cache local et validation DNSSEC.
- DNS différent par interface réseau.
- Résolution des noms de machines et des domaines de recherche.

## Architecture

Le service est généralement activé par `systemd-resolved.service`. Les applications utilisent `/etc/resolv.conf`, qui devrait pointer vers `/run/systemd/resolve/stub-resolv.conf` pour utiliser le stub local, ou vers `resolved-resolv.conf` pour exposer directement les serveurs connus.

```bash
systemctl enable --now systemd-resolved
readlink -f /etc/resolv.conf
resolvectl status
```

!!! warning
    Un autre gestionnaire DNS (NetworkManager, dnsmasq, unbound ou un résolveur statique) ne doit pas écouter sur le même port local.

## Relation avec networkd

`systemd-networkd` peut fournir les serveurs DNS et domaines par interface. `resolvectl status` permet de vérifier la configuration effectivement reçue.

## Commandes utiles

```bash
resolvectl query example.org
resolvectl statistics
resolvectl flush-caches
resolvectl dns eth0 192.0.2.53
resolvectl revert eth0
```
