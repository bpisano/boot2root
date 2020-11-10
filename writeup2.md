# Rescue Shell
Sur notre machine Ubuntu, il existe un mode recoevry, qui permet, au démarrage, de choisir avec quels paramètres on souhaite lancer la VM. Il est initialement conçu en cas d'oubli de mot de passe pour réintialiser la VM, mais nous allons l'exploiter pour lancer un shell administrateur.

Au lancement de la VM, il suffit de rester appuyé sur <kbd>Shift</kbd> pour lancer le mode recovery. La commande pour lancer un shelle sur Linux est `init=/bin/bash`.
```
boot: init=/bin/bash
Could not find kernel image: /init/bash
```
Une simple tabulation nous donne l'indice sur le label à inclure :
```
boot: live ini/bin/bash
```
Une fois le shell lancé, un `whoami` nous indique `root`.
