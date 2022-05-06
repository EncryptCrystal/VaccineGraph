#Imporations de divers modules
from urllib import request
from urllib.request import urlopen 
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np
import os
from os.path import basename

#Paramètres des jeux de données
lienTelechargementDonnees = "https://www.data.gouv.fr/fr/datasets/r/54dd5f8d-1e2e-4ccb-8fb8-eac68245befd"
nomFichier = basename(urlopen(lienTelechargementDonnees).url)                   #Nom du jeu de données
lieuTelechargement = "Archives Données/"                                        #Répertoire où sont entreposés les fichiers de données
"""anneeTelechargement = nomFichier[12:17]
moisTelechargement = nomFichier[17:19]
jourTelechargement = nomFichier[22:17]
heureTelechargement = nomFichier[12:17]"""


#Paramètres du graphique
limiteDateDebut = "2021-01-01"                                                  #Indique la première date des données (0 pour conserver la liste)
limiteDateFin = 0                                                               #Exclure les données à partir d'une certaine date (0 pour conserver la liste)
limiteNombreJour = 0                                                            #Indique le nombre de dates à inscrire sur l'axe des abscisses (0 ou 1 conserve la liste)
limiteEcartJour = 112                                                           #Espace de n jours les dates (1 pour conserver la liste)
nbJourPrediction = 7                                                            #Fait des prévisions sur les jours suivants à partir des n derniers jours
seuilImmuniteCollective = 0                                                     #Définit le seuil d'immunité collective (trace une ligne horizontale à ce pourcentage)
empecherValeursPrevisionnelles = False                                          #Par défaut, ne pas empêcher de tracer les valeurs prévisionnelles
limiteDateDebutExiste = False                                                   #Par défaut, ne pas supprimer des dates sans vérifier que la limite de début existe
yMin = 0                                                                        #Définit le pourcentage minimum affiché
yMax = 100                                                                      #Définit le pourcentage maximum affiché


#Liste des courbes demandées, en format (age minimal, age maximal, nb de doses, si la courbe doit obligatoirement aller jusqu'aux 100%, couleur du tracé)
listeCourbes = [( 0, 80, 1, False, "red"),
                ( 0, 80, 2, True, "brown"),
                #(12, 80, 1, False, "pink"),
                #(12, 80, 2, True, "purple"),
                (60, 80, 1, False, "cyan"),
                (60, 80, 2, False, "darkblue"),
                (18, 59, 1, False, "yellow"),
                (18, 59, 2, False, "orange"),
                (12, 17, 1, False, "lawngreen"),
                (12, 17, 2, False, "darkgreen")]


#Données sur la population en format (age minimal concerné, population de la tranche d'âge) (Insee, 2021)
#(https://www.insee.fr/fr/outil-interactif/5367857/details/20_DEM/21_POP/21C_Figure3#)
listeDonneesPopulation = [  ( 0, 3570743),
                            ( 5, 4008669),
                            (10, 1703214),
                            (12, 5124913),
                            (18, 5610876),
                            (25, 3699678),
                            (30, 8234477),
                            (40, 8561785),
                            (50, 8882961),
                            (60, 4165483),
                            (65, 3895934),
                            (70, 3704374),
                            (75, 2522324),
                            (80, 4127965)]


#Sert à limiter une liste à limiteNombreJour de manière uniforme
def reduction(liste):
    if limiteNombreJour == 0 or limiteNombreJour == 1: return liste             #limiteNombreJour ne doit pas être égal à 0 ou 1 (risque d'erreur)
    listeCompressee = []
    coeff = len(liste)/(limiteNombreJour-1)                                     #Calcule l'écart idéal entre 2 éléments de la liste à compresser
    listeCompressee.append(liste[0])                                            #Ajoute le premier élément de la liste à compresser
    for i in range(len(liste)):
        if int(i/coeff) == len(listeCompressee):                                #Si la position de l'élément est supérieure ou égale à sa position dans la liste compressée
            listeCompressee.append(liste[i-1])                                  #Alors ajouter l'élément à la liste compressée
    listeCompressee.append(liste[-1])                                           #Ajoute le dernier élément de la liste dans la liste à compresser
    return listeCompressee


#Sert à la projection des courbes
def projectionObjectif(liste):
    coeff = (liste[-1]-liste[-1-nbJourPrediction])/nbJourPrediction             #Évolution de la courbe calculé à partir des n derniers jours
    while len(listeDates) != len(liste): liste.append(liste[-1]+coeff)          #Tant que la projection n'égale pas la date de fin, continuer la projection
    return liste


#Sert à espacer les dates selon limiteEcartJour
def ecartDate(liste):
    newListe = []
    for i in range(len(liste)):
        if i % limiteEcartJour == 0: newListe.append(liste[i])
    return newListe


#Sert à séparer les nombres par milliers, millions...
def formatNombre(nombre):
    nombre = str(nombre)
    j = 0
    for i in range(1,len(nombre)):
        if i%3 == 0:
            nombre = nombre[:-i-j] + " " + nombre[-i-j:]
            j += 1
    return nombre


#Analyse les courbes afin de définir s'il faut continuer d'allonger le graphique
def analyseListeDonnees(listeDates, listeCourbes):
    listeNbElementCourbe = []

    #Tant que que chacune ne comporte pas autant d'éléments que la liste des dates
    for courbe in listeCourbes:
        listeNbElementCourbe.append(len(courbe))
        if len(courbe) != len(listeDates): return True

    #ET que la courbe actuelle n'est pas celle qui a le maximum de points, continuer la boucle
    if max(listeNbElementCourbe) != len(listeCourbes[numeroPassageCourbe]): return True
    
    return False

#Si un graphique du même nom n'a pas encore été créé, alors télécharger le jeu de données
if os.path.exists(lieuTelechargement+nomFichier) == False:
    lignes = str(request.urlopen(lienTelechargementDonnees).read()).strip("b'").split("\\n")
    fichier = open(lieuTelechargement+nomFichier, "w")
    for ligne in lignes: fichier.write(ligne + "\n")
    fichier.close()

#Début du script
fichier = open(lieuTelechargement+nomFichier, "r")                              #Ouvre le fichier
ligneDescripteurs = fichier.readline().rstrip().rsplit(";")                     #Sépare la première ligne (titres des colonnes) du reste des valeurs numériques
lignes = fichier.readlines()                                                    #Le reste est entreposée dans "lignes"
table = []

for ligne in lignes:
    ligne = ligne.rstrip().split(";")
    if ligne[0] == "": break                                                    #Une ligne vide correspond à la fin du fichier csv : on sort de la boucle
    del ligne[0]                                                                #Supression des valeurs du pays de l'injection (toutes dans le fichier sont en France)
    ligne[0] = int(ligne[0])                                                    #Conversion de l'âge des vaccinés en nombre entier (de base une chaîne de caractères)
    del ligne[2]                                                                #Suppression des primo-injections quotidiennes
    del ligne[2]                                                                #Suppression des injections complètes quotidiennes
    del ligne[2]                                                                #Suppression des injections de rappel quotidiennes
    ligne[2] = int(ligne[2])                                                    #Conversion du cumul des primo-injections en nombre entier
    ligne[3] = int(ligne[3])                                                    #Conversion du cumul des injections complètes en nombre entier
    del ligne[4]                                                                #Suppression du cumul des injection de rappel
    del ligne[4]                                                                #Suppression du taux de primo-vaccinés
    del ligne[4]                                                                #Suppression du taux de vaccinés
    del ligne[4]                                                                #Suppression du taux de rappel
    table.append(ligne)
    if ligne[1] == limiteDateDebut: limiteDateDebutExiste = True                #Limiter le nombre de dates si la limite existe dans le fichier
fichier.close()                                                                 #Ferme le fichier
table = sorted(table, key=itemgetter(1, 0))                                     #Tri les données par date, puis par âge

#Tant que la date limite de début n'est pas atteinte et si elle existe, continuer de supprimer les données
while limiteDateDebutExiste and table[0][1] != limiteDateDebut: del table[0]

#Vérifie la présense de données de données ultérieurs à la date limite de fin
for i in range(len(table)):
    if table[i][1] == limiteDateFin:                                            #Si c'est le cas...
        del table[i+15:]                                                        #Supprime ces données
        empecherValeursPrevisionnelles = True                                   #Empeche la signalisation des valeurs prévisionelles (pas besoin)
        break                                                                   #Casse la boucle et empêche d'éventuelles erreurs

#Initialisation des variables des dates et des 7 autres courbes
listeDates = []                                                                 #Stocke la liste des dates en abscisse
listeDonnees = []                                                               #Stocke la liste des données par jour et par âge

for i in range(28): listeDonnees.append([])                                     #Ajout de listes vides sur lesquelles ajouter les données par âge

#Répartit les données dans les différentes listes
for donnees in table:
    #Afin de faciliter la compréhension du code, les 4 colonnes sont assignés à des variables
    age = donnees[0]
    date = donnees[1]
    primoInjections = donnees[2]
    injectionsCompletes = donnees[3]

    #Dans le cas où la ligne concerne les injections tout âge confondu...
    if age == 0:
        listeDates.append(date)
    
    #Dans le cas où la ligne concerne les injections de personnes entre 0 et 79 ans...
    elif 4 <= age <= 79:
        for i in range(len(listeDonneesPopulation)-1):
            if age == int(listeDonneesPopulation[i+1][0])-1:
                listeDonnees[i*2].append(primoInjections)
                listeDonnees[i*2+1].append(injectionsCompletes)
    
    #Dans le cas où la ligne concerne les injections de personnes de plus de 80 ans...
    else:
        listeDonnees[26].append(primoInjections)
        listeDonnees[27].append(injectionsCompletes)


positionDateLimite = len(listeDates)-1                                          #Sauvegarde de la position du dernier jour dont on a les données
dernierJour = listeDates[-1]                                                    #Sauvegarde le dernier jour dont on a les données


#Trace les courbes
listeNomCourbe = []                                                             #Liste contenant l'ensemble des noms des différentes courbes
listeRoadTo100 = []                                                             #Liste contenant la demande (ou non) pour une courbe d'étirer la courbe jusqu'à ses 100%
listeCouleur = []                                                               #Liste contenant l'ensemble des couleurs des différentes courbes

for courbe in listeCourbes:                                                     #On prend une à une les courbes demandées
    courbeFinale = [0]*len(listeDonnees[0])                                     #Contient le nombre final d'injection pour l'ensemble des tranches d'âge demandées
    populationConsernee = 0                                                     #Variable contenant la population totale consernée par la courbe actuelle
    listeAge = []                                                               #Contient les différentes tranches d'âge de l'ensemble des tranches d'âge demandées
    for positionAge in range(len(listeDonneesPopulation)):                      #On balaye la liste de données de population pour savoir si l'âge appartient à l'ensemble des tranches d'âge demandées, et si c'est le cas :
        if courbe[0] <= listeDonneesPopulation[positionAge][0] < courbe[1] or listeDonneesPopulation[positionAge][0] == 80 == courbe[1]:
            populationConsernee += listeDonneesPopulation[positionAge][1]       #Ajouter la population sélectionnée au total de population consernée
            listeAge.append(listeDonneesPopulation[positionAge][0])             #Ajouter à la liste des âges utilisées le plus petit âge de l'ensemble des tranches d'âge demandées
            for i in range(len(listeDonnees[0])):                               #Additionner les injections à la courbe totale, en prenant en compte la distinction primo-injection/injection finale
                courbeFinale[i] += listeDonnees[positionAge*2+courbe[2]-1][i]
    
    #Les données passent du nombre d'injection au pourcentage de population
    for i in range(len(courbeFinale)): courbeFinale[i] = 100*courbeFinale[i]/populationConsernee

    #Si l'âge maximal n'est pas 80 ans, recherchez quelle est la classe d'âge supérieure, et y retirer 1
    #Ceci pour éviter que la tranche x-y ans, y appartienne à une autre tranche d'âge
    if listeAge[-1] != 80:
        for i in range(len(listeDonneesPopulation)):
            if listeDonneesPopulation[i][0] == listeAge[-1]:
                listeAge.append(listeDonneesPopulation[i+1][0]-1)
    
    if listeAge[0] == 0 and listeAge[-1] == 80: titre = "Français"              #Si la part d'âge demandée couvre l'ensemble des Français, alors mettre "Français" dans le titre
    elif listeAge[-1] == 80: titre = f"+{listeAge[0]} ans"                      #Sinon, si la tranche d'âge demandée va jusqu'à l'âge maximal, mettre "+[âge minimal]" dans le titre
    else: titre = f"{listeAge[0]}-{listeAge[-1]} ans"                           #Sinon, mettre "[âge minimal]-[âge maximal]" dans le titre
    
    if courbe[2] == 1: titre += " primo-vaccinés"
    else: titre += " vaccinés"
    
    listeNomCourbe.append(titre)                                                #Ajout du titre de chaque courbe dans une liste à part
    listeRoadTo100.append(courbe[3])                                            #Ajout de la demande (ou non) pour une courbe d'étirer la courbe jusqu'à ses 100%
    listeCouleur.append(courbe[4])                                              #Ajout de la couleur de chaque courbe dans une liste à part
    listeCourbes[listeCourbes.index(courbe)] = courbeFinale


listeCoeff = []                                                                 #Liste contenant le coefficient d'évolution de chaque courbe des n derniers jours
numeroPassageCourbe = 0

#Ajout des différents coefficients dans la liste adéquate
for i in range(len(listeCourbes)): listeCoeff.append((listeCourbes[i][-1]-listeCourbes[i][-1-nbJourPrediction])/nbJourPrediction)

#Tant que les différentes courbes ne sont pas toutes au moins à 100% ET qu'elles ne sont pas au même nombre de point
#ET que la limite d'écart entre les dates (s'il y en a une) n'est pas respectée, étendre le graphique
while analyseListeDonnees(listeDates, listeCourbes) or (limiteDateFin == 0 and (listeCourbes[numeroPassageCourbe][-1] < 100 or ((len(listeCourbes[numeroPassageCourbe])-1)%limiteEcartJour) != 0))   or   (limiteDateFin != 0 and (limiteDateFin not in listeDates or len(listeDates) != len(listeCourbes[numeroPassageCourbe]) or ((len(listeCourbes[numeroPassageCourbe])-1)%limiteEcartJour) != 0)):
    listeCourbes[numeroPassageCourbe].append(listeCourbes[numeroPassageCourbe][-1]+listeCoeff[numeroPassageCourbe])
    if len(listeCourbes[numeroPassageCourbe]) > len(listeDates):
            date = date[0:8] + str(int(date[8:])+1)
            if len(date[8:]) == 1: date = date[0:8] + "0" + date[-1] 
            if date[5:7] == "01" and date[8:10] == "32": date = date[0:5] + "02-01"
            elif date[5:7] == "02" and date[8:10] == "29" and int(date[0:4])%4 != 0: date = date[0:5] + "03-01"
            elif date[5:7] == "02" and date[8:10] == "30" and int(date[0:4])%4 == 0: date = date[0:5] + "03-01"
            elif date[5:7] == "03" and date[8:10] == "32": date = date[0:5] + "04-01"
            elif date[5:7] == "04" and date[8:10] == "31": date = date[0:5] + "05-01"
            elif date[5:7] == "05" and date[8:10] == "32": date = date[0:5] + "06-01"
            elif date[5:7] == "06" and date[8:10] == "31": date = date[0:5] + "07-01"
            elif date[5:7] == "07" and date[8:10] == "32": date = date[0:5] + "08-01"
            elif date[5:7] == "08" and date[8:10] == "32": date = date[0:5] + "09-01"
            elif date[5:7] == "09" and date[8:10] == "31": date = date[0:5] + "10-01"
            elif date[5:7] == "10" and date[8:10] == "32": date = date[0:5] + "11-01"
            elif date[5:7] == "11" and date[8:10] == "31": date = date[0:5] + "12-01"
            elif date[5:7] == "12" and date[8:10] == "32": date = str(int(date[0:4])+1) + "-01-01"
            listeDates.append(date)
    numeroPassageCourbe = (numeroPassageCourbe + 1)%len(listeCourbes)

#Passe le format de toutes les dates : AAAA-MM-JJ -> JJ/MM
for i in range(len(listeDates)): listeDates[i] = listeDates[i][8:11]+"/"+listeDates[i][5:7]

listeDatesReduite = ecartDate(reduction(listeDates))                            #Réduit la liste de dates tout en conservant l'original


#Début de la contruction du graphique
plt.figure(figsize = (16, 5))                                                   #Définit une dimension en 16/5
plt.tick_params(axis = 'x', rotation = 80)                                      #Tourne les dates à 80° afin qu'elles restent visibles

#Trace les courbes continues (données factuelles) et pointillées (données prévisionnelles) pour chaque ensemble de données
for i in range(len(listeCourbes)):
    plt.plot(listeDatesReduite[:positionDateLimite//limiteEcartJour+1], ecartDate(reduction(projectionObjectif(listeCourbes[i])))[:positionDateLimite//limiteEcartJour+1], listeCouleur[i], label = listeNomCourbe[i])
    plt.plot(listeDatesReduite[positionDateLimite//limiteEcartJour:], ecartDate(reduction(projectionObjectif(listeCourbes[i])))[positionDateLimite//limiteEcartJour:], listeCouleur[i], linestyle = '--')


#Trace une ligne de pointillé horizontale au niveau des 100% si le seuil d'immunité collective n'est pas égal à 0% ou 100%
#et affiche un texte sur le seuil actuel supposé
if 0 < seuilImmuniteCollective < 100:
    plt.axhline(y = 100 * seuilImmuniteCollective, color = 'black', linestyle = '--')
    plt.text(len(listeDatesReduite)/2, 100 * seuilImmuniteCollective + 1.2, f"Seuil d'immunité collective ({int(seuilImmuniteCollective*100)}%)", horizontalalignment = 'center')

#Trace une zone en gris clair délimitée par une ligne verticale en pointillé pour désigner les prédictions
#des courbes (si les données n'ont pas été raccourcies)
if empecherValeursPrevisionnelles == False:
    plt.axvline(x = listeDatesReduite[positionDateLimite//limiteEcartJour], color = 'gray', linestyle = '--')
    plt.axvspan(listeDatesReduite[positionDateLimite//limiteEcartJour], listeDatesReduite[-1], alpha = 0.5, color = 'lightgray')

plt.yticks(np.arange(yMin, yMax+0.01, 10))                                      #Limite le maximum en y à 105% et force la création de jalons de 10%
plt.ylim(yMin, yMax+0.01)                                                       #Force le tableau à n'afficher y qu'entre 0% et 105%

plt.grid()                                                                      #Ajout d'un grillage
plt.legend()                                                                    #Affiche les légendes associés à la courbe correspondante
plt.margins(0, 0)                                                               #Force la disparition des marges intérieures

#Défini les titres du graphe et des axes x et y, et ajoute des notes en bas du graphe
plt.title(f"Avancement de la vaccination (données du {nomFichier[20:22]}/{nomFichier[17:19]}/{nomFichier[12:16]})")
plt.xlabel(f"""Dates\n\nLes prévisions sont faites à partir des {formatNombre(nbJourPrediction)} jours précédents. En considérant une répartition de la population égale à celle indiquée par l'Insee en 2021.
Dernier jour de remontée des données : {dernierJour[8:]}/{dernierJour[5:7]}/{dernierJour[:4]}. Source des données sur Data.gouv et code du graphique disponible sur https://github.com/A2drien/VaccineGraph.""")
plt.ylabel("Pourcentage de vaccinés (%)")

#Arret des images, la segonde dose de rappel crée des bugs

#Sauvegarde l'image (avec la date des données dans les archives) et supprime les marges extérieures
#plt.savefig(f"Objectifs Vaccination.png", bbox_inches = 'tight')
#plt.savefig(f"Archives Objectifs Vaccination/Objectifs Vaccination {nomFichier[12:22]}.png", bbox_inches = 'tight')
