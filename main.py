#Imporations de divers modules
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np


nom_fichier = "vacsi-a-fra-2021-08-06-20h05.csv"                                #Nom du fichier de données à traiter

#Paramètres du graphique
limite_date_debut = 0                                                           #Indique la première date des données (0 pour conserver la liste)
limite_date_fin = 0                                                             #Exclure les données à partir d'une certaine date (0 pour conserver la liste)
limite_nombre_jour = 0                                                          #Indique le nombre de dates à inscrire sur l'axe des abscisses (0 ou 1 conserve la liste)
limite_ecart_jour = 7                                                           #Espace de n jours les dates
nb_jour_prediction = 7                                                          #Fait des prévisions sur les jours suivants à partir des n derniers jours
y_min = 0                                                                       #Définit le pourcentage minimum affiché
y_max = 100                                                                     #Définit le pourcentage maximum affiché

#Données sur la population (Insee, 2021) (https://www.insee.fr/fr/outil-interactif/5367857/details/20_DEM/21_POP/21C_Figure3#)
pop_50_79_ans = 22772098                                                        #22 772 098 Français ont entre 50 et 79 ans
pop_18_49_ans = 26026248                                                        #26 026 248 Français ont entre 18 et 49 ans



#Sert à limiter une liste à limite_nombre_jour de manière uniforme
def reduction(liste):
    if limite_nombre_jour == 0 or limite_nombre_jour == 1: return liste         #limite_nombre_jour ne doit pas être égal à 0 ou 1
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
    if limite_ecart_jour == 0: return liste
    new_liste = []
    for i in range(len(liste)):
        if i % limite_ecart_jour == 0: new_liste.append(liste[i])
    return new_liste


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
    lst[4] = float(lst[4])                                                      #Conversion du taux de primo-vaccinés en nombre entier
    lst[5] = float(lst[5])                                                      #Conversion du taux de vaccinés en nombre entier
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
        break

#Initialisation des variables des dates et des 7 autres courbes
liste_dates = []                                                                #Stocke la liste des dates en abscisse

proportion_primo_vaccines = []                                                  #Stocke la proportion de primo-vaccinés
proportion_primo_injections_12_17_ans = []                                      #Stocke la liste de la proportion de primo-vaccinés des 12-17 ans
proportion_primo_injections_18_49_ans = []                                      #Stocke la liste de la proportion de primo-vaccinés des 18-49 ans
proportion_primo_injections_50_79_ans = []                                      #Stocke la liste de la proportion de primo-vaccinés des 50-79 ans
proportion_primo_injections_80_ans = []                                         #Stocke la liste de la proportion de primo-vaccinés des +80 ans

proportion_vaccines = []                                                        #Stocke la proportion de complètement vaccinés
proportion_injections_completes_12_17_ans = []                                  #Stocke la liste de la proportion de vaccinés des 12-17 ans
proportion_injections_completes_18_49_ans = []                                  #Stocke la liste de la proportion de vaccinés des 18-49 ans
proportion_injections_completes_50_79_ans = []                                  #Stocke la liste de la proportion de vaccinés des 50-79 ans
proportion_injections_completes_80_ans = []                                     #Stocke la liste de la proportion de vaccinés des +80 ans

#Variables de transition entre les différentes classes d'âges
cumul_proportion_primo_injections_18_49_ans = 0
cumul_proportion_injections_completes_18_49_ans = 0
cumul_proportion_primo_injections_50_79_ans = 0
cumul_proportion_injections_completes_50_79_ans = 0
    
for donnees in table:
    #Afin de faciliter la compréhension du code, les 6 colonnes sont assignés à des variables
    age = donnees[0]
    date = donnees[1]
    primo_injections = donnees[2]
    injections_completes = donnees[3]
    taux_primo_vaccines = donnees[4]
    taux_vaccines = donnees[5]

    #Dans le cas où la ligne concerne les injections tout âge confondu...
    if age == 0:
        liste_dates.append(date)
        proportion_primo_vaccines.append(taux_primo_vaccines)
        proportion_vaccines.append(taux_vaccines)
    
    #Dans le cas où la ligne concerne les injections de personnes entre 12 et 17 ans...
    elif age == 17:
        proportion_primo_injections_12_17_ans.append(taux_primo_vaccines)
        proportion_injections_completes_12_17_ans.append(taux_vaccines)

    #Dans le cas où la ligne concerne les injections de personnes entre 18 et 49 ans...
    elif 18 <= age <= 49:
        cumul_proportion_primo_injections_18_49_ans += primo_injections
        cumul_proportion_injections_completes_18_49_ans += injections_completes

        if age == 49:
            proportion_primo_injections_18_49_ans.append(cumul_proportion_primo_injections_18_49_ans/pop_18_49_ans)
            proportion_injections_completes_18_49_ans.append(cumul_proportion_injections_completes_18_49_ans/pop_18_49_ans)

    #Dans le cas où la ligne concerne les injections de personnes entre 50 et 74 ans...
    elif 50 <= age <= 79:
        cumul_proportion_primo_injections_50_79_ans += primo_injections
        cumul_proportion_injections_completes_50_79_ans += injections_completes
    
        if age == 79:
            proportion_primo_injections_50_79_ans.append(cumul_proportion_primo_injections_50_79_ans/pop_50_79_ans)
            proportion_injections_completes_50_79_ans.append(cumul_proportion_injections_completes_50_79_ans/pop_50_79_ans)

    #Dans le cas où la ligne concerne les injections de personnes de plus de 80 ans...
    elif age == 80:
        proportion_primo_injections_80_ans.append(taux_primo_vaccines)
        proportion_injections_completes_80_ans.append(taux_vaccines)

position_date_limite = len(liste_dates)-1                                       #Sauvegarde de la position du dernier jour dont on a les données

#Tant que la proportion de vaccinés n'est pas de 100%, étendre le graphique
coeff = (proportion_vaccines[-1]-proportion_vaccines[-1-nb_jour_prediction])/nb_jour_prediction
i = 0
while i <= int((100-proportion_vaccines[-1])/coeff)+1 or len(liste_dates)%limite_ecart_jour !=0:
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

#Passe le format de toutes les dates : AAAA-MM-JJ -> JJ/MM
for i in range(len(liste_dates)): liste_dates[i] = liste_dates[i][8:11]+"/"+liste_dates[i][5:7]

liste_dates_reduite = ecartDate(reduction(liste_dates))                         #Reduit la liste de dates tout en conservant l'original


#Début de la contruction du graphique
plt.figure(figsize = (16, 5))                                                   #Définit une dimension en 16/5
plt.tick_params(axis = 'x', rotation = 80)                                      #Tourne les dates à 80° afin qu'elles restent visibles

#Trace les courbe
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_vaccines))), "red", label = "Français primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_vaccines))), "brown", label = "Français vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_injections_80_ans))), "cyan", label = "+80 ans primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_injections_completes_80_ans))), "darkblue", label = "+80 ans vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_injections_50_79_ans))), "yellow", label = "50-79 ans primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_injections_completes_50_79_ans))), "orange", label = "50-79 ans vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_injections_18_49_ans))), "lawngreen", label = "18-49 ans primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_injections_completes_18_49_ans))), "darkgreen", label = "18-49 ans vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_primo_injections_12_17_ans))), "pink", label = "12-17 ans primo-vaccinés")
plt.plot(liste_dates_reduite, ecartDate(reduction(projectionObjectif(proportion_injections_completes_12_17_ans))), "purple", label = "12-17 ans vaccinés")

#Trace une zone en gris clair délimitée par une ligne verticales en pointillé pour désigner les prédictions des courbes (si les données n'ont pas été raccourcis)
if empecher_valeurs_previsionnelles == False:
    plt.axvline(x = liste_dates_reduite[position_date_limite//limite_ecart_jour], color = 'gray', linestyle = '--')
    plt.axvspan(liste_dates_reduite[position_date_limite//limite_ecart_jour], liste_dates_reduite[-1], alpha = 0.5, color = 'lightgray')

plt.yticks(np.arange(y_min, y_max+0.01, 10))                                    #Limite le maximum en y à 105% et force la création de jalons de 10%
plt.ylim(y_min, y_max+0.01)                                                     #Force le tableau à n'afficher y qu'entre 0% et 105%

plt.grid()                                                                      #Ajout d'un grillage
plt.legend()                                                                    #Affiche les légendes associés à la courbe correspondante
plt.margins(0, 0)                                                               #Force la disparition des marges intérieures

#Défini les titres du graphe et des axes x et y
plt.title(f"Avancement de la vaccination (données du {nom_fichier[20:22]}/{nom_fichier[17:19]}/{nom_fichier[12:16]})")
plt.xlabel("Dates")
plt.ylabel("Pourcentage de vaccinés (%)")

plt.savefig(f"Tableau {nom_fichier[12:22]}.png", bbox_inches = 'tight')         #Sauvegarde l'image avec la date des données et supprime et les marges exterieures
