import pyxel
from time import sleep
from random import randint, choice

pyxel.init(128,128, title="Clef des Champs")
pyxel.load('my_resource.pyxres')
pyxel.playm(3,loop=True)

x_perso, y_perso = -8,96
vies = 2
liste_sauts = []
direction = 1 # 1 droite // -1 gauche
gravites = True # True la gravité est activé // False désactivé
saut_ON = False
clef = 0 # 0 non // 1 oui // 2 porte ouverte // 3 entré dans la porte
porte = False # False si fermée // True si ou&verte
x_abeille, y_abeille = 25, 27
direction_abeille = [1, 2] # [1 gauche // -1 droite] [0 droit // 1 haut // 2 bas]
couleurs_abeille_ok = [1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14] # couleurs que l'abeille peut traverser

x_bernacle, y_bernacle = 89, 81 #coordonnées bernacle
liste_tir = [] #boule de feu

image_marche = [0, 72]#image quand le perso marche
n_marche_image = 1
image_echelle = [24, 72]#image du perso quand il est sur l'échelle
image_saut = [0, 88]#image du perso quand il saute
x_image, y_image = image_marche[0], image_marche[1]

main_menu=0 #menu

def perso_deplacement(x, y, direction):
    """Déplacement du personnage vers la gauche ou vers la droite avec les touches flèche droite et flèche gauche"""
    if pyxel.btn(pyxel.KEY_RIGHT) and x <=120:
        x +=1
        direction = 1

    if pyxel.btn(pyxel.KEY_LEFT) and x >= 0 :
        # On verifie qu'il bloque au niveau de la marche
        if not (x == 56 and y >= 80):
            x -=1
            direction = -1
    return x, y, direction


def marche_fluide(image_marche):
    """Alterne l'image du personnage quand il marche à chaque frame (il y a trois images différentes) afin de rendre le mouvement plus vivant"""
    global n_marche_image

    if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_RIGHT):
        if n_marche_image % 2 == 0:
            image_marche = [8,88]
        elif n_marche_image % 3 == 0:
            image_marche = [0,80]
        else:
            image_marche = [0,72]

        n_marche_image += 1
    return image_marche


def gravite(x, y):
    """@x, @y,
    Récupère les coordonnées du perso et détermine si le perso est dans les airs ou pas (en vérifiant la couleur sous les pieds du personnages, et si la gravite est activé (voir fonction échelle)) si oui, elle décrémente de 1 la coordonnée y recue
    Elle renvoie alors les nouvelles coordonnées à affecter au personnage
    """
    global saut_ON, x_image, y_image
    # coté gauche du perso
    if not (pyxel.pget(x+1, y+8) == 11 or pyxel.pget(x+1, y+8) == 3) and gravites == True:
        #coté droit du perso
        if not (pyxel.pget(x+6, y+8) == 11 or pyxel.pget(x+6, y+8) == 3):
            y += 1
            saut_ON = True
            x_image, y_image = image_saut[0], image_saut[1]
        else:
            saut_ON = False
    else:
        saut_ON = False
    return x, y


def saut(y):
    """ Si le personnage a appuyé sur la touche espace, et qu’il n’est pas en train de sauté, on ajoute 2 fois les coordonnées y du personnage à liste_sauts et on désactive la gravité (saut_ON = True). """
    global saut_ON
    if pyxel.btnr(pyxel.KEY_SPACE) and liste_sauts == []:
        liste_sauts.append(y)
        liste_sauts.append(y)
        pyxel.play(3,4)
        saut_ON = True


def saut_deplacement(y):
    """Cette fonction sert à faire sauter le personnage, si un saut est en cours.

A chaque fois qu’un saut est en cours, à chaque appelle de la fonction on y ajoute la nouvelle coordonnée y, si les 2 dernières coordonnées sont les mêmes alors le personnage a été immobile donc le saut est fini et on remet des images de marche et on réactive la gravité.  """
    global liste_sauts, x_image, y_image, saut_ON
    # S'il ya un saut
    if liste_sauts != []:
        x_image, y_image = image_saut[0], image_saut[1]
        # pour plus tard verifier si le personnage est stable pour pouvoir resauter
        liste_sauts.append(y)
        # On verifie s'il a assez sauté
        if liste_sauts[0] > liste_sauts[1] - 15:
            liste_sauts[0] -= 3
            y = liste_sauts[0]
        # Si le perso etait fixe alors il a été sur une surface plane
        elif liste_sauts[-1] == liste_sauts[-2]:
            liste_sauts = []
            x_image, y_image = image_marche[0], image_marche[1]
            saut_ON = False
    return y


def grande_echelle(x, y) :
    """Elle vérifie si le personnage et sur la grande échelle (s'il est dans les coordonnées de l’échelle) et si la flèche du haut ou du bas est pressée. Si flèche du haut alors le perso monte (décrémente y) si flèche du bas alors le perso descend (incrémente y)."""
    global x_image, y_image, gravites
    gravites = True

    if x > 21 and x < 26 and y <= 80 and y >= 40:
        gravites = False
        x_image, y_image = image_echelle[0], image_echelle[1]

    if pyxel.btn(pyxel.KEY_UP) and gravites == False:
        if y == 41: y -= 1
        if not y <= 40: y -= 2

    if pyxel.btn(pyxel.KEY_DOWN) and gravites == False:
        if y == 79: y += 1
        if not y >= 80: y += 2

    if (y <= 40 or gravites == True or y >= 80) and saut_ON == False:
        x_image, y_image = image_marche[0], image_marche[1]

    return y


def petite_echelle(x, y):
    """Elle vérifie si le personnage et sur la petite échelle (s'il est dans les coordonnées de l’échelle) et si la flèche du haut ou du bas est pressée. Si flèche du haut alors le perso monte (décrémente y) si flèche du bas alors le perso descend (incrémente y). """
    global x_image, y_image, gravites

    if x > 53 and x < 60 and y <= 40 and y >= 24:
        gravites = False
        x_image, y_image = image_echelle[0], image_echelle[1]

    if pyxel.btn(pyxel.KEY_UP) and gravites == False and x > 53 and x < 59:
        if y == 25: y -= 1
        if not y <= 24: y -= 2

    if pyxel.btn(pyxel.KEY_DOWN) and gravites == False and x > 53 and x < 59:
        if y == 39: y += 1
        if not y >= 40: y += 2

    if (y == 24 or y == 40) and saut_ON == False:
        x_image, y_image = image_marche[0], image_marche[1]

    return y


def key(x, y):
    """Elle vérifie si le personnage passe sur la clef, si les coordonnées du point central du perso sont celles du point central de la clef. """
    global clef
    if x == 96 and y == 8 and clef == 0:
        clef = 1


def epines(x, y):
    """Elle vérifie si le personnage touche du gris (la couleur des épines). Si oui elle appelle la fonction vie_perdue"""
    global vies
    if (pyxel.pget(x+4, y+8) == 13 or pyxel.pget(x, y+4) == 13 or pyxel.pget(x+7, y+4) == 13) and y >50:
        vie_perdue()


def verif_porte(x, y):
    global porte, clef, x_image, y_image, vies, direction
    if (pyxel.pget(x, y+4) == 2 or pyxel.pget(x+7, y+4) == 2) and y >50 and clef == 1:
        porte = True
        clef = 2
    if clef == 2 and porte == True and pyxel.btn(pyxel.KEY_UP) and (pyxel.pget(x+3, y+7) == 0 or pyxel.pget(x+4, y+7) == 0) and y >= 50 and x > 90:
        x_image, y_image = image_echelle[0], image_echelle[1]
        clef = 3 # Pour arreter tous les mouvement et aller au niveau suivant
        x, y = 112, 88
        direction = 1
    return x, y


def abeille_deplacement(x, y):
    global direction_abeille
    change = False

    if randint(0,180) == 1:
        change = True
    # haut
    if direction_abeille[1] == 1 and pyxel.pget(x, y-1) in couleurs_abeille_ok and pyxel.pget(x+7, y-1) in couleurs_abeille_ok and change == False:
        y -= 1
    # bas
    elif direction_abeille[1] == 2 and pyxel.pget(x, y+9) in couleurs_abeille_ok and pyxel.pget(x+7, y+9) in couleurs_abeille_ok and change == False:
        y += 1
    # gauche
    elif direction_abeille[0] == 1 and pyxel.pget(x-1, y+1) in couleurs_abeille_ok and pyxel.pget(x-1, y+8) in couleurs_abeille_ok and pyxel.pget(x-1, y+4) in couleurs_abeille_ok and change == False:
        x -= 1
    # droite
    elif direction_abeille[0] == -1 and pyxel.pget(x+8, y+1) in couleurs_abeille_ok and pyxel.pget(x+8, y+7) in couleurs_abeille_ok and pyxel.pget(x+8, y+4) in couleurs_abeille_ok and change == False:
        x += 1

    else:
        choice1 = [-1, 1]
        choice1.remove(direction_abeille[0])
        choice2 = [0, 0, 1, 1, 1, 2, 2, 2]
        choice2.remove(direction_abeille[1])

        direction_abeille[0] = choice1[0]
        direction_abeille[1] = choice(choice2)

    return x, y


def abeille_colision(x_abeille, y_abeille):
    global x_perso, y_perso, vies
    if abs(x_abeille - x_perso) < 7 and abs(y_abeille - y_perso) < 8:
        vie_perdue()
        x_abeille, y_abeille = 25, 27
    return x_abeille, y_abeille


def bernacle_deplacement(x,y) :
    y=89
    if x_perso > x and x < 89:
        x+=1
    elif x_perso < x and x > 14:
        x-=1
    if x<56 :
        y=81
    return x, y


def creation_tir() :
    if pyxel.frame_count%90==0 :
        liste_tir.append([x_bernacle+2, y_bernacle-5])


def tir_deplacement():
    for tir in liste_tir :
        tir[1]-= 1
        if tir[1]<-4 :
            liste_tir.remove(tir)


def collision() :
    global vies, x_perso, y_perso
    for tir in liste_tir :
        if tir[0]>x_perso-3 and tir[0]+4<x_perso+10 and tir[1]> y_perso-3 and tir[1]+4< y_perso+10:
            vie_perdue()


def vie_perdue():
    global vies, x_perso, y_perso, x_abeille, y_abeille
    vies -= 1
    x_perso, y_perso = 2, 70

def anim() :
    global x_perso, y_perso
    x_perso+=1
    if x_perso>128 :
        x_perso=-8


def update():
    global x_perso, y_perso, liste_sauts, direction, vies, clef, gravites, x_image, y_image, porte, x_abeille, y_abeille, liste_tir, x_bernacle, y_bernacle, image_marche, saut_ON, main_menu

    if main_menu==0 :#menu
        direction = 1
        anim()
        if pyxel.btnr(pyxel.KEY_RETURN):
            main_menu=1
            vies = 2
            x_perso, y_perso = 2, 70
            clef = 0
            gravites = True
            x_image, y_image = image_marche[0], image_marche[1]
            porte = False
            saut_ON = False
            x_bernacle, y_bernacle = 89, 81
            liste_tir = []

    elif main_menu==1: #jeu
        # LE JEU
        # Deplacement du personnage (fleches)
        x_perso, y_perso, direction = perso_deplacement(x_perso, y_perso, direction)
        # si l'utilisateur a appuyé sur esapce pour sauter
        saut(y_perso)
        # Pour effectuer le mouvement du saut
        y_perso = saut_deplacement(y_perso)
        # Si le personnage veut monter ou descendre l'echelle
        y_perso = grande_echelle(x_perso, y_perso)
        y_perso = petite_echelle(x_perso, y_perso)
        # La gravite pour etre constament en dessente
        x_perso, y_perso = gravite(x_perso, y_perso)
        # Si le personnage attrape la clef
        key(x_perso, y_perso)
        # Si porte et clef
        x_perso, y_perso = verif_porte(x_perso, y_perso)
        # marche fluide
        if pyxel.frame_count % 4 == 0:
            image_marche = marche_fluide(image_marche)

        # ENNEMIS
        # si le personnage est sur les epines
        epines(x_perso, y_perso)
        # abeille deplacement
        x_abeille, y_abeille = abeille_deplacement(x_abeille, y_abeille)
        # COLISION AVEC L'ABEILLE
        x_abeille, y_abeille = abeille_colision(x_abeille, y_abeille)
        #bernacle et boule de feu
        if pyxel.frame_count%3==0 :
            x_bernacle, y_bernacle = bernacle_deplacement(x_bernacle,y_bernacle)
        #boule de feu
        creation_tir()
        tir_deplacement()
        collision()

        if vies<1 :
            main_menu=2
        
        # Si le personnage est entré dans la porte
        if clef == 3:
            sleep(1)
            main_menu=2

    elif main_menu==2 :#game over ou gagné
        if pyxel.btnr(pyxel.KEY_RETURN):
            main_menu=0
            x_image, y_image = image_marche[0], image_marche[1]
            x_perso=-8
            y_perso=96



def draw():
    global vies
    pyxel.cls(5)

    if main_menu==0 :
        pyxel.bltm(0,0,0,128,192,128,128)
        # Personnage
        pyxel.blt(x_perso, y_perso, 0, x_image, y_image, direction*8, 8, colkey=5)
        pyxel.text(9,80,"Clique sur ENTRER pour JOUER",10)

    elif main_menu==1:
        # Decor
        pyxel.bltm(0,0,0,0,0,128,128)
        # Si la porte est ouverte
        if porte == True:
            pyxel.blt(112, 85, 0, 8, 45, 8, 11, colkey=5)
        # Vies
        for i in range(2):
            pyxel.blt(2+i*10,2,0,0,97,8,7,colkey=0)
        if vies >= 1:
            pyxel.blt(2,2,0,8,97,8,7,colkey=0)
        if vies >= 2:
            pyxel.blt(12,2,0,8,97,8,7,colkey=0)
        # Si la clef est attrapé on l'a dessine
        if clef == 1:
            pyxel.blt(120, 2, 0, 0, 48, 8, 8, colkey=5)
            pyxel.blt(96, 8, 0, 0, 40, 8, 8, colkey=5)
        elif clef == 2 or clef == 3:
            pyxel.blt(96, 8, 0, 0, 40, 8, 8, colkey=5)
        else:
            pyxel.blt(120, 2, 0, 0, 40, 8, 8, colkey=5)
        # abeille
        pyxel.blt(x_abeille, y_abeille, 0, 16, 102, direction_abeille[0] * 8, 10, colkey=14)
        #tirs
        for tir in liste_tir :
            pyxel.blt(tir[0],tir[1],0,32,96,4,4,colkey=14)
        # Personnage
        pyxel.blt(x_perso, y_perso, 0, x_image, y_image, direction*8, 8, colkey=5)

        pyxel.blt(x_bernacle, y_bernacle, 0, 32, 105, 7, 7, colkey=14)

    elif main_menu==2 :
        if clef == 3:
            pyxel.text(30, 50, "BRAVO TU AS GAGNE", 7)
            pyxel.text(15, 65, "'ENTRER' pour recommencer", 7)
        else:
            pyxel.text(45, 50, "GAME OVER", 7)
            pyxel.text(15, 65, "'ENTRER' pour recommencer", 7)

pyxel.run(update, draw)