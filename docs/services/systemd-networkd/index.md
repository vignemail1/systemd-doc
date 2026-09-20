# systemd-networkd

`systemd-networkd` est un gestionnaire réseau intégré à systemd. Il configure les interfaces, les adresses, les routes, les VLAN, les bridges, les bonds et de nombreux tunnels, sans dépendre de NetworkManager ou d'un autre gestionnaire.

## Activation

```bash
sudo systemctl enable --now systemd-networkd.service
sudo systemctl enable --now systemd-resolved.service
sudo systemctl restart systemd-networkd
```

Si `systemd-resolved` est utilisé, vérifier que `/etc/resolv.conf` pointe vers son stub :

```bash
sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

## Emplacements des fichiers

Les fichiers sont lus notamment dans :

- `/etc/systemd/network/` : configuration administrateur ;
- `/run/systemd/network/` : configuration volatile ;
- `/usr/lib/systemd/network/` (ou `/lib/systemd/network/`) : configuration fournie par les paquets.

Les fichiers locaux priment sur ceux fournis par le système. Après toute modification :

```bash
sudo networkctl reload
sudo networkctl reconfigure <interface>
```

## Diagnostic

```bash
networkctl list
networkctl status eth0
networkctl lldp
journalctl -u systemd-networkd -b
```

Utiliser `networkctl status` pour vérifier l'état opérationnel, les adresses et les routes. Une configuration `.network` ne s'applique qu'à la première correspondance appropriée : l'ordre lexical des fichiers est donc important.

!!! warning
    Éviter de faire gérer la même interface par plusieurs gestionnaires réseau.
