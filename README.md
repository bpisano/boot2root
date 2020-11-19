# **Boot-2-root**

![Getting Started](./img/mister_robot.png)

Ce projet est une introduction à la pénetration d’un système.

Nous avons 2 **wripteup** pour la partie obligatoire et 3 **wripteup** pour la partie bonus.
Voici un résumé des différentes méthodes que nous avons utilisé pour devenir `root` sur la VM.

## **Ret2libc**


Pour la première méthode pour devenir `root`, nous avons utilisé la faille [Ret2libc](https://beta.hackndo.com/retour-a-la-libc/).
Cette faille consiste à utiliser un `buffer overflow`, nous allons simuler un appel valide à la fonction `system` pour qu'elle lance un `shell`. 

## **Rescue Shell**

Pour notre deuxième méthode pour devenir `root`, nous avons utilisé le mode `recovery`. Il nous suffit, au lancement de la VM d'appuyer sur une touche précise, nous permettant de lancer le mode `recovery`. Suite à cela, nous pouvons saisir une commande qui permet initalement de [réinitialiser le mot de passe root](https://wiki.archlinux.org/index.php/Reset_lost_root_password). 
# Partie bonus

## **Dirty COW**


Pour notre premier bonus, nous avons utilisé la faille [Dirty Cow](https://bond-o.medium.com/dirty-cow-2c79cd6859c9). Cette faille est très ancienne, et a perduré durant 9 ans. Notre version du kernel était compatible avec cette faille, nous avons donc pu récupérer le code source, le compiler puis l'éxécuter. 

## **Root Forum**


Pour notre quatrième bonus, nous avons choisis de devenir root sur le forum. En effet, lors du `writeup1`, nous avons accédé au forum ainsi qu'a la base de donnée du forum. Nous nous sommes aperçu, que nous pouvions faire une `update` dans la db, nous permettant de devenir `root`sur le forum.

## **Shell Code**


Pour notre cinquième et denier bonus, nous avons utilisé une variante de la faille `Ret2libC`. Ici, le but est grâce à `l'overflow`, d'écrire à un endroit précis de la mémoire pour faire comprendre à l'exécutable la prochaine instruction à exécuter.

---
Projet fait par [Bpisano](https://github.com/bpisano) et [Themarch](https://github.com/themarch)
