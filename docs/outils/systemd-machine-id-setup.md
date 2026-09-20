# systemd-machine-id-setup

`systemd-machine-id-setup` initialise `/etc/machine-id` lorsque celui-ci est absent ou vide. L'identifiant est utilisé par plusieurs composants systemd pour identifier durablement la machine.

```bash
sudo systemd-machine-id-setup
cat /etc/machine-id
```

Dans une image système destinée à être clonée, il est courant de supprimer ou de vider l'identifiant lors de la préparation de l'image afin qu'il soit généré au premier démarrage. Suivre les recommandations de l'outil de construction d'image utilisé.
