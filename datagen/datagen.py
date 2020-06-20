import random
import pandas as pd


def calcuate_load_people(q_person, n_person, t_person): 
    # q_person = Wärmeabgabe pro Person (Standard = 240) [W]
    # n_person = Anzahl der Personen 
    # t_person = Aufenthaltszeit im Raum [h/day]
    load_people =  q_person * n_person * t_person
    return load_people

def calcuate_load_light(load_electrical, t_light):
    # load_electrical = Anschlussleistung [W]
    # t_light = Zeit in welcher Belechtung genutzt wird [h/day] --> kann von t_person abweichen! 
    load_light = 1 * 1 * load_electrical * t_light
    # print("load light")
    # print(load_electrical)
    # print(t_light)
    # print(load_light)
    return load_light

def calcuate_load_transmission(u_value, cr_lenght, cr_width, cr_height, temp_outside, temp_inside): 
    area = 2*cr_lenght*cr_width + 2*cr_height*cr_lenght + 2*cr_height*cr_width
    # print(area)
    load_transmission = u_value * area * (temp_outside-temp_inside)
    return load_transmission

def calcuate_load_machine(load_electrical, efficiency, t_machine): 
    # load_electrical = Anschlussleistung [W]
    # efficiency = Wirkungsgrad
    # t_machine = Nutzungszeit [h/day]
    load_machine = load_electrical / efficiency * 1 * 0.8 * t_machine
    # print(load_electrical)
    # print(efficiency)
    # print(t_machine)
    # print(load_machine)
    
    return load_machine

    
def generateData_default(amount):
    data_rows = []
    # Define default Values:
    q_person = 240
    u_value = 0.242 # bei deltaT = 19 Grad und 100mm PUR überall
    temp_inside = 5 
    temp_outside = 24 
    for i in range(amount):
        # Define random numbers that make sense

        # Personen zwischen 1 und 3
        n_person = random.randint(1,3) 
        # Zeit zwischen 3 und 5 Stunden (eine Nachkommastelle)
        t_person = random.randint(3*10, 5*10)/10
        # Beleuchtungszeit (hier genauso lange wie Aufenthaltszeit -> ergo nur licht wenn leute im Raum sind)
        t_light = t_person
        # Länge zwischen 3 und 6m 
        cr_lenght = random.randint(3*100, 6*100)/100
        # Breite zwischen 3 und 6m
        cr_width = random.randint(3*100, 6*100)/100
        # Höhe zwischen 2,5 und 3,6m
        cr_height = random.randint(2.5*100, 3.6*100)/100
        cr_volume = cr_height * cr_lenght * cr_width
        # Anschlussleistung Licht mit Verhältnis zum Standard Danfoss raum ermitteln
        load_light_electrical = 240 / 108 * cr_volume
        # Anschlussleistung Lüfter mit Verhältnis zum Standard Danfoss raum ermitteln 
        # Deswegen später kein Wirkungsgrad mehr!!
        load_fan_electrical = 210 / 108 * cr_volume
        t_fan = random.randint(16*10,18*10)/10

        #Calculate Values   
        load_people = calcuate_load_people(q_person,n_person,t_person)/24000
        load_light = calcuate_load_light(load_light_electrical,t_light)/24000
        load_transmission = calcuate_load_transmission(u_value,cr_lenght, cr_width, cr_height, temp_outside, temp_inside)*24/24000
        load_fan = calcuate_load_machine(load_fan_electrical, 1, t_fan)/24000
        load_total = (load_transmission + load_people + load_light + load_fan) * 1.45 #Faktor für die fehlenden Lasten
        # print("volume: ")
        # print(cr_volume)
        # print("total load: ")
        # print(load_total)
        load_installed = load_total + 0.150 #Puffer für installierte Leistung (Defaultbedingungen)

        

        data_rows.append([load_transmission, load_people, load_light, load_fan, load_total, load_installed])
    
    # create DataFrame
    df = pd.DataFrame(data_rows, columns=["load_transmission", "load_people", "load_light", "load_fan", "load_total", "load_installed"])
    return df



print("jetzt gehts los")

print("GENERATING DATA")
print(generateData_default(1000))