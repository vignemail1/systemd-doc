# Diagnostic de systemd-timesyncd

```bash
systemctl status systemd-timesyncd
journalctl -u systemd-timesyncd -b
timedatectl timesync-status
timedatectl show-timesync --all
```

## Pas de synchronisation

Vérifier :

1. que le service est actif ;
2. que `NTP synchronized` n'est pas désactivé ;
3. que les noms des serveurs se résolvent ;
4. que UDP/123 est autorisé ;
5. que l'horloge locale n'est pas trop éloignée ;
6. qu'aucun autre client NTP ne se bat pour le socket ou l'horloge.

```bash
timedatectl show -p NTP -p NTPSynchronized
ss -uap | grep ':123'
```

## Source et qualité

`timedatectl timesync-status` affiche serveur, strate, délai, dispersion et dernière synchronisation. Une grande distance racine ou une forte dispersion peut faire rejeter une source.

## DNS indisponible

Tester temporairement avec une adresse IP dans `NTP=` pour distinguer un problème de résolution d'un problème NTP.
