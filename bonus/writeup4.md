# ROOT FORUM
## Introduction
Après plusieurs recherches, nous nous sommes rendu compte que nous pouvions devenir administrateur du forum grâce à notre accès MYSQL.

## Récupération et exécution du code
Nous avons récupéré les accès PhpMyAdmin grace au writeup1.md.

On se connecte en administateur à [PhpyAdmin](https://192.168.56.101/phpmyadmin/) avec ces identifiants.
```
root
Fg-'kKXBj87E:aJ$
```
On rentre dans `forum_db` et on a accès à toutes les tables liées au forum.
La table `mlf2_userdata` liste les users présents dans le forum avec leurs informations de connexion.

On s'aperçoit qu'il y a une colonne `user_type`. Tous les utilisateurs ont la valeur `0` dans cette colonne, hormis le compte `admin` qui lui a un `2`.

On suppose donc qu'en modifiant le `user_type` de Lmezard, nous aurions les accès root sur le forum.  
```SQL
UPDATE `forum_db`.`mlf2_userdata` SET `user_type` = '2' WHERE `mlf2_userdata`.`user_name` = 'lmezard';
```
Lmezard a donc maintenant les mêmes droits que `Admin`
Nous nous connectons au [forum](https://192.168.56.101/forum/index.php?mode=login) pour vérifier.

```
lmezard
!q\]Ej?*5K5cy*AJ
```
Nous sommes **ROOT** sur le forum !