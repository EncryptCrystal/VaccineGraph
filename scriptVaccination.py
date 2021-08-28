#Imporations de divers modules
from operator import itemgetter

import matplotlib.pyplot as plt
import numpy as np

nom_fichier = "vacsi-a-fra-2021-08-26-19h10.csv"                                #Nom du fichier de données à traiter

#Paramètres du graphique
limite_date_debut = "2021-01-01"                                                #Indique la première date des données (0 pour conserver la liste)
limite_date_fin = 0                                                             #Exclure les données à partir d'une certaine date (0 pour conserver la liste)
limite_nombre_jour = 0                                                          #Indique le nombre de dates à inscrire sur l'axe des abscisses (0 ou 1 conserve la liste)
limite_ecart_jour = 7                                                           #Espace de n jours les dates (1 pour conserver la liste)
nb_jour_prediction = 7                                                          #Fait des prévisions sur les jours suivants à partir des n derniers jours
seuil_immunite_collective = 0.90                                                #Définit le seuil d'immunité collective (trace une ligne honrizontale à ce pourcentage)
y_min = 0                                                                       #Définit le pourcentage minimum affiché
y_max = 100                                                                     #Définit le pourcentage maximum affiché

#Données sur la population (Insee, 2021) (https://www.insee.fr/fr/outil-interactif/5367857/details/20_DEM/21_POP/21C_Figure3#)
pop_0_4_ans   = 0 #34 840 410 Français ont entre 18 et 59 ans
pop_5_9_ans   = 0
pop_10_11_ans = 0
pop_12_17_ans = 0
pop_18_24_ans = 0
pop_25_29_ans = 0
pop_30_39_ans = 0
pop_40_49_ans = 0
pop_50_59_ans = 0
pop_60_69_ans = 0
pop_70_74_ans = 0
pop_75_79_ans = 0
pop_80_ans    = 0

"""
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_vaccines))), "red", label = "Français primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_vaccines))), "brown", label = "Français vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_injections_60_ans))), "cyan", label = "+60 ans primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_injections_completes_60_ans))), "darkblue", label = "+60 ans vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_injections_18_59_ans))), "yellow", label = "18-59 ans primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_injections_completes_18_59_ans))), "orange", label = "18-59 ans vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_injections_12_17_ans))), "lawngreen", label = "12-17 ans primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_injections_completes_12_17_ans))), "darkgreen", label = "12-17 ans vaccinés")
"""


liste_courbes_demandees = [ ( 0, 80, 1, "red"),
                            ( 0, 80, 2, "brown"),
                            (60, 80, 1, "cyan"),
                            (60, 80, 2, "darkblue"),
                            (18, 59, 1, "yellow"),
                            (18, 59, 2, "orange"),
                            (12, 17, 1, "lawngreen"),
                            (12, 17, 2, "darkgreen")
]

liste_donnees_population = [ 0, pop_0_4_ans,
                             5, pop_5_9_ans,
                            10, pop_10_11_ans,
                            12, pop_12_17_ans,
                            18, pop_18_24_ans,
                            25, pop_25_29_ans,
                            30, pop_30_39_ans,
                            40, pop_40_49_ans,
                            50, pop_50_59_ans,
                            60, pop_60_69_ans,
                            70, pop_70_74_ans,
                            75, pop_75_79_ans,
                            80, pop_80_ans]

#Sert à limiter une liste à limite_nombre_jour de manière uniforme
def reduction(liste):
    if limite_nombre_jour == 0 or limite_nombre_jour == 1: return liste         #limite_nombre_jour ne doit pas être égal à 0 ou 1 (risque d'erreur)
    liste_compressee = []
    coeff = len(liste)/(limite_nombre_jour-1)                                   #Calcule l'écart idéal entre 2 éléments de la liste à compresser
    liste_compressee.append(liste[0])                                           #Ajoute le premier élement de la liste à compresser
    for i in range(len(liste)):
        if int(i/coeff) == len(liste_compressee):                               #Si la position de l'élément est supérieure ou égale à sa position dans la liste compressée
            liste_compressee.append(liste[i-1])                                 #Alors ajouter l'élement à la liste compressée
    liste_compressee.append(liste[-1])                                          #Ajoute le dernier élement de la liste dans la liste à compresser
    return liste_compressee

#Sert à la projection des courbes
def projectionObjectif(liste):
    coeff = (liste[-1]-liste[-1-nb_jour_prediction])/nb_jour_prediction         #Évolution de la courbe calculé à partir des 7 derniers jours
    while len(liste_dates) != len(liste): liste.append(liste[-1]+coeff)         #Tant que la projection n'égale pas la date de fin, continuer la projection
    return liste

#Sert à espacer les dates selon limite_ecart_jour
def ecartDate(liste):
    new_liste = []
    for i in range(len(liste)):
        if i % limite_ecart_jour == 0: new_liste.append(liste[i])
    return new_liste

#Sert à espacer un nombre par milliers, millions...
def formatNombre(nombre):
    nombre = str(nombre)
    j = 0
    for i in range(1,len(nombre)):
        if i%3 == 0:
            nombre = nombre[:-i-j] + " " + nombre[-i-j:]
            j += 1
    return nombre

#Début du script
fichier = open(nom_fichier,"r")                                                 #Ouvre le fichier
ligne_descripteurs = fichier.readline()
lst_descripteurs = ligne_descripteurs.rstrip().rsplit(";")                      #Sépare la première ligne (titres des colonnes) du reste des valeurs numériques
lignes = fichier.readlines()                                                    #Le reste est entreposée dans "lignes"
table = []

empecher_valeurs_previsionnelles = False                                        #Par défaut, ne pas empêcher de tracer les valeurs prévisionnelles
limite_date_debut_existe = False                                                #Par défaut, ne pas supprimer des dates sans vérifier que la limite de début existe

for ligne in lignes:
    lst = ligne.rstrip().split(";")
    del lst[0]                                                                  #Supression des valeurs du pays de l'injection (toutes dans le fichier sont en France)
    lst[0] = int(lst[0])                                                        #Conversion de l'âge des vaccinés en nombre entier (de base une chaine de caractères)
    del lst[2]                                                                  #Suppression des primo-injections quotidiennes
    del lst[2]                                                                  #Suppression des injections complètes quotidiennes
    lst[2] = int(lst[2])                                                        #Conversion du cumul des primo-injections en nombre entier
    lst[3] = int(lst[3])                                                        #Conversion du cumul des injections complètes en nombre entier
    del lst[4]                                                                  #Suppression du taux de primo-vaccinés en nombre entier
    del lst[4]                                                                  #Suppression du taux de vaccinés en nombre entier
    table.append(lst)
    if lst[1] == limite_date_debut: limite_date_debut_existe = True             #Limiter le nombre de dates si la limite existe dans le fichier
fichier.close()                                                                 #Ferme le fichier
table = sorted(table, key=itemgetter(1, 0))                                     #Tri les données par date, puis par âge

#Tant que la date limite de début n'est pas atteinte et si elle existe, continuer de supprimer les données
while limite_date_debut_existe and table[0][1] != limite_date_debut: del table[0]

#Vérifie la présense de données de données ultérieurs à la date limite de fin
for i in range(len(table)):
    if table[i][1] == limite_date_fin:                                          #Si c'est le cas...
        del table[i+15:]                                                        #Supprime ces données
        empecher_valeurs_previsionnelles = True                                 #Empeche la signalisation des valeurs prévisionelles (pas besoin)
        break                                                                   #Casse la boucle et empêche d'éventuelles erreurs

#Initialisation des variables des dates et des 7 autres courbes
liste_dates = []                                                                #Stocke la liste des dates en abscisse

liste_donnees = []
for i in range(28): liste_donnees.append([])


#Répartit les données dans les différentes listes
for donnees in table:
    #Afin de faciliter la compréhension du code, les 4 colonnes sont assignés à des variables
    age = donnees[0]
    date = donnees[1]
    primo_injections = donnees[2]
    injections_completes = donnees[3]
    print(donnees)
    #Dans le cas où la ligne concerne les injections tout âge confondu...
    if age == 0:
        liste_dates.append(date)
        liste_donnees[0].append(primo_injections)
        liste_donnee[1].append(injections_completes)
    
    #Dans le cas où la ligne concerne les injections de personnes entre 12 et 17 ans...
    elif age == 4:
        liste_donnees[2].append(primo_injections)
        liste_donnee[3].append(injections_completes)

    elif age == 9:
        liste_donnees[4].append(primo_injections)
        liste_donnee[5].append(injections_completes)
    
    elif age == 11:
        liste_donnees[6].append(primo_injections)
        liste_donnee[7].append(injections_completes)

    elif age == 17:
        liste_donnees[8].append(primo_injections)
        liste_donnee[9].append(injections_completes)
    
    elif age == 24:
        liste_donnees[10].append(primo_injections)
        liste_donnee[11].append(injections_completes)
    
    elif age == 29:
        liste_donnees[12].append(primo_injections)
        liste_donnee[13].append(injections_completes)    
    
    elif age == 39:
        liste_donnees[14].append(primo_injections)
        liste_donnee[15].append(injections_completes)
    
    elif age == 49:
        liste_donnees[16].append(primo_injections)
        liste_donnee[17].append(injections_completes)
    
    elif age == 59:
        liste_donnees[18].append(primo_injections)
        liste_donnee[19].append(injections_completes)
    
    elif age == 69:
        liste_donnees[20].append(primo_injections)
        liste_donnee[21].append(injections_completes)
    
    elif age == 74:
        liste_donnees[22].append(primo_injections)
        liste_donnee[23].append(injections_completes)
    
    elif age == 79:
        liste_donnees[24].append(primo_injections)
        liste_donnee[25].append(injections_completes)
    
    else:
        liste_donnees[26].append(primo_injections)
        liste_donnee[27].append(injections_completes)


position_date_limite = len(liste_dates)-1                                       #Sauvegarde de la position du dernier jour dont on a les données

#Tant que la proportion de vaccinés n'est pas de 100%, étendre le graphique
coeff = (proportion_vaccines[-1]-proportion_vaccines[-1-nb_jour_prediction])/nb_jour_prediction
i = 0
limite_atteinte = False
#Si il n'y a pas de date limite de fin, alors créer des dates jusqu'à ce que les 100% de vaccinés soient atteints et/ou dépassés ET que la limite d'écart entre les dates soit respecté
#Sinon, alors créer des dates jusqu'à ce que la date limite soit atteinte et/ou dépassée ET que la limite d'écart entre les dates soit respecté
while (limite_date_fin == 0 and (i <= (100-proportion_vaccines[-1]) /coeff or ( len(liste_dates)-1) % limite_ecart_jour != 0) ) or (limite_atteinte == False and (len(liste_dates)-1)%limite_ecart_jour != 0):
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
    i += 1
    liste_dates.append(date)
    if date == limite_date_fin: limite_atteinte = True

#Passe le format de toutes les dates : AAAA-MM-JJ -> JJ/MM
for i in range(len(liste_dates)): liste_dates[i] = liste_dates[i][8:11]+"/"+liste_dates[i][5:7]

liste_dates_reduite = ecartDate(reduction(liste_dates))                         #éeduit la liste de dates tout en conservant l'original


#Début de la contruction du graphique
plt.figure(figsize = (16, 5))                                                   #Définit une dimension en 16/5
plt.tick_params(axis = 'x', rotation = 80)                                      #Tourne les dates à 80° afin qu'elles restent visibles

#Trace une ligne de pointillé verticale au niveau des 100% si le seuil d'immunité collective n'est pas égal à 0
if seuil_immunite_collective != 0: plt.axhline(y = 100 * seuil_immunite_collective, color = 'black', linestyle = '--')

#Trace une ligne de pointillé horizontale indiquant le seuil d'immunité colllective
plt.text(len(liste_dates_reduite)/2, 100 *seuil_immunite_collective + 2, f"Seuil d'immunité collective ({int(seuil_immunite_collective*100)}%)", horizontalalignment = 'center')

#Trace les courbes
for courbe_demandée in liste_courbes_demandees:                                 #On prend une à une les courbes demandées
    courbe_finale = [0]*len(liste_donnees[0])                                   #Contient le nombre final d'injection pour la tranche d'âge demandée
    liste_age = []                                                              #Contient les différentes tranches d'âge utilisées
    for age in range(0, len(liste_donnees_population)+1, 2):                    #On balaye la liste de données de population pour savoir si l'âge correspond à la demande
        if courbe_demandée[0] <= age < courbe_demandée[1] or age == 80 == courbe_demandée[1]:         #Si c'est le cas :
            liste_age.append(courbe_demandée[0])                                #Ajouter à la liste des âges utilisées l'âge minimum utilisé
            for i in range(liste_donnees[0]):                                   #Additionner les injections à la courbe totale, en prenant en compte la distanction primo-injection/injecction finale
                courbe_finale[i] += liste_donnees[age+liste_courbes_demandees[2]-1][i]
    if liste_age[0] == 0 and liste_age[-1] == 80: titre == "Français"           #Si la part d'âge demandée couvre l'ensemble des Français, alors mettre "Français" dans le titre
    elif liste_age[-1] == 80: titre = f"+{liste_age[0]} ans"                    #Sinon, si la tranche d'âge demandée va jusqu'à l'âge maximal, mettre "+[âge minimal]" dans le titre
    else: titre = f"{liste_age[0]}-{liste_age[-1]} ans"                         #Sinon, mettre "[âge minimal]-[âge maximal]" dans le titre
    if liste_courbes_demandees[2] == 1: titre += " primo-vaccinés"
    else: titre += " vaccinés"
    couleur = liste_courbes_demandees[3]
    plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(courbe_finale))), couleur, label = titre)

#Trace une zone en gris clair délimitée par une ligne verticales en pointillé pour désigner les prédictions des courbes (si les données n'ont pas été raccourcis)
if empecher_valeurs_previsionnelles == False:
    plt.axvline(x = liste_dates_reduite[position_date_limite//limite_ecart_jour], color = 'gray', linestyle = '--')
    plt.axvspan(liste_dates_reduite[position_date_limite//limite_ecart_jour], liste_dates_reduite[-1], alpha = 0.5, color = 'lightgray')

plt.yticks(np.arange(y_min, y_max+0.01, 10))                                    #Limite le maximum en y à 105% et force la création de jalons de 10%
plt.ylim(y_min, y_max+0.01)                                                     #Force le tableau à n'afficher y qu'entre 0% et 105%

plt.grid()                                                                      #Ajout d'un grillage
plt.legend()                                                                    #Affiche les légendes associés à la courbe correspondante
plt.margins(0, 0)                                                               #Force la disparition des marges intérieures

#Défini les titres du graphe et des axes x et y, et ajoute des notes en bas du graphe
plt.title(f"Avancement de la vaccination (données du {nom_fichier[20:22]}/{nom_fichier[17:19]}/{nom_fichier[12:16]})")
plt.xlabel(f"""Dates\n\nLes prévisions sont faites à partir des {formatNombre(nb_jour_prediction)} jours précédents. En considérant une population égale à celle indiquée par l'Insee, en 2021.
Source des données sur Data.gouv et code du graphique disponible sur https://github.com/A2drien/VaccineGraph.""")
plt.ylabel("Pourcentage de vaccinés (%)")

#Sauvegarde l'image avec la date des données et supprime et les marges exterieures
plt.savefig(f"Objectifs Vaccination {nom_fichier[12:22]}.png", bbox_inches = 'tight')
