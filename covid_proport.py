#Objectif du nombre de doses
obj_1_dose = 50000000
obj_tot_dose = 35000000

#Objectif de proportion de primo-vaccinés de plus de 50 ans
obj_50_ans_1_dose = 0.85

#Objectif de proportion primo-vaccinés et vaccinés de plus de 18 ans
obj_18_ans_1_dose = 0.75
obj_18_ans_tot_dose = 0.66

#Population française de plus de 50 ans et 18 ans
pop_50_ans = 26700000
pop_18_ans = 26000000 + pop_50_ans

from operator import  itemgetter
import matplotlib.pyplot as plt
import numpy as np

#Fonction à usage répété
def format_date(date):
    date = date.rsplit("-")
    new_date = date[2]
    if date[1] == "01": new_date += " Jan"
    elif date[1] == "02": new_date += " Fev"
    elif date[1] == "03": new_date += " Mar"
    elif date[1] == "04": new_date += " Avr"
    elif date[1] == "05": new_date += " Mai"
    elif date[1] == "06": new_date += " Jun"
    elif date[1] == "07": new_date += " Jul"
    elif date[1] == "08": new_date += " Aou"
    elif date[1] == "09": new_date += " Sep"
    elif date[1] == "10": new_date += " Oct"
    elif date[1] == "11": new_date += " Nov"
    else: new_date += " Dec"
    return new_date


def Importation(nom_fichier):
    fichier = open(nom_fichier,"r")
    ligne_descripteurs = fichier.readline()
    lst_descripteurs = ligne_descripteurs.rstrip().rsplit(";")
    lignes = fichier.readlines()
    table = []
    for ligne in lignes:
        lst = ligne.rstrip().split(";")
        del lst[0]
        lst[0] = int(lst[0])
        del lst[2]
        del lst[2]
        lst[2] = int(lst[2])
        lst[3] = int(lst[3])
        del lst[4]
        del lst[4]
        lst[0], lst[1] = lst[1], lst[0]
        table.append(lst)
    fichier.close()
    table = sorted(table, key=itemgetter(0, 1))
    
    liste_dates = []
    
    primo_injections_18_ans = []
    primo_injections_50_ans = []
    primo_injections_totales = []
    injections_completes_18_ans = []
    injections_completes_totales = []
          
    cumul_primo_injections_18_ans = 0
    cumul_injections_completes_18_ans = 0
    cumul_primo_injections_50_ans = 0
    
    for donnes in table:
      
      date = donnes[0]
      age = donnes[1]
      primo_injections = donnes[2]
      injections_completes = donnes[3]

    
      if age == 0:
        primo_injections_totales.append(primo_injections/obj_1_dose*100)
        injections_completes_totales.append(injections_completes/obj_tot_dose*100)
        liste_dates.append(format_date(date))
      
      elif 18 <= age <= 49:
        cumul_primo_injections_18_ans += primo_injections
        cumul_injections_completes_18_ans += injections_completes
      
      elif 50 <= age <= 79:
        cumul_primo_injections_50_ans += primo_injections
        cumul_primo_injections_18_ans += primo_injections
        cumul_injections_completes_18_ans += injections_completes
      
      elif age == 80:
        cumul_primo_injections_50_ans += primo_injections
        primo_injections_50_ans.append(cumul_primo_injections_50_ans/pop_50_ans/obj_50_ans_1_dose*100)
        cumul_primo_injections_50_ans = 0
        
        cumul_primo_injections_18_ans += primo_injections
        cumul_injections_completes_18_ans += injections_completes
        primo_injections_18_ans.append(cumul_primo_injections_18_ans/pop_18_ans/obj_18_ans_1_dose*100)
        injections_completes_18_ans.append(cumul_injections_completes_18_ans/pop_18_ans/obj_18_ans_tot_dose*100)
        cumul_primo_injections_18_ans = 0
        cumul_injections_completes_18_ans = 0
        
    date_limite = str(liste_dates[-1])
    while liste_dates[-1][0:2] != "31" and liste_dates[-1][3:7] == "Juil":
        liste_dates.append(str(int(liste_dates[-1][0:2])+1)+" Juil")
            
    liste_dates.append("01 Aou")
        
    while int(liste_dates[-1][0:2]) < 9 and liste_dates[-1][3:6] == "Aou":
        liste_dates.append("0"+str(int(liste_dates[-1][0:2])+1)+" Aou")
        
    while liste_dates[-1][0:2] != "31" and liste_dates[-1][3:6] == "Aou":
        liste_dates.append(str(int(liste_dates[-1][0:2])+1)+" Aou")
    
    def projectionObjectif(fonction):
        projection = list(fonction)
        coeff =  (fonction[-1]-fonction[-8])/7
        while len(liste_dates) != len(projection):
            projection.append(projection[-1]+coeff)
        return projection
    
    plt.figure(figsize=(45,8))
    plt.tick_params(axis = 'x', rotation = 80)
    
    plt.axhline(y=100,color='gray',linestyle='--')
    
    plt.plot(liste_dates, projectionObjectif(primo_injections_totales), "red", label = f"Objectif de primo-vaccinés ({int(obj_1_dose/1000000)} M)")
    plt.plot(liste_dates, projectionObjectif(injections_completes_totales), "firebrick", label = f"Objectif de vaccinés ({int(obj_tot_dose/1000000)} M)")
    plt.plot(liste_dates, projectionObjectif(primo_injections_50_ans), "orange", label = f"Objectif des +50 ans primo-vaccinés ({int(obj_50_ans_1_dose*100)} %)")
    plt.plot(liste_dates, projectionObjectif(primo_injections_18_ans), "lawngreen", label = f"Objectif des +18 ans primo-vaccinés ({int(obj_18_ans_1_dose*100)} %)")
    plt.plot(liste_dates, projectionObjectif(injections_completes_18_ans), "darkgreen", label = f"Objectif des +18 ans vaccinés ({int(obj_18_ans_tot_dose*100)} %)")
    
    plt.axvline(x=date_limite,color='gray',linestyle='--')
    plt.axvspan(date_limite, liste_dates[-1], alpha=0.5, color='lightgray')
    plt.axvline(x=liste_dates[-1],color='gray',linestyle='--')
    plt.yticks(np.arange(0, 110, 10))
    plt.ylim(0, 110)
    
    
    plt.legend()
    plt.margins(0, 0)
    plt.title(f"Etat des objectifs gouvernementaux pour la fin aout (Données du {format_date(nom_fichier[12:22])} à {nom_fichier[23:28]})")
    plt.xlabel("Dates")
    plt.ylabel("Pourcentage atteint des objectifs (%)")
    plt.savefig(f"Tableau {date}.png", dpi=170, bbox_inches='tight')
    plt.show()


Importation("vacsi-a-fra-2021-07-23-19h05.csv")
