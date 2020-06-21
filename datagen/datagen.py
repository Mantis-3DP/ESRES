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

    
def generateData_default(amount, add_problem):
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
        load_installed = load_total * 1.1 #Puffer für installierte Leistung (Defaultbedingungen)
        problem = ["none"]

        
        if add_problem:
            data_rows.append([load_transmission, load_people, load_light, load_fan, load_total, load_installed, problem])
            # create DataFrame
            df = pd.DataFrame(data_rows, columns=["load_transmission", "load_people", "load_light", "load_fan", "load_total", "load_installed", "problem"])
        else: 
            data_rows.append([load_transmission, load_people, load_light, load_fan, load_total, load_installed])
            # create DataFrame
            df = pd.DataFrame(data_rows, columns=["load_transmission", "load_people", "load_light", "load_fan", "load_total", "load_installed"])
    return df



print("jetzt gehts los")

# print("GENERATING DATA")
# print(generateData_default(10, True))



# def generateData_fake_old(amount, add_problem, transmission_fake, people_fake_1, people_fake_2, light_fake_1, light_fake_2, fan_fake, load_installed_fake):
#     data_rows = []
#     # Define default Values:
#     q_person = 240
#     temp_inside = 5 
#     temp_outside = 24 
#     
    
#     for i in range(amount):
          # problem = []

#         # Länge zwischen 3 und 6m 
#         cr_lenght = random.randint(3*100, 6*100)/100
#         # Breite zwischen 3 und 6m
#         cr_width = random.randint(3*100, 6*100)/100
#         # Höhe zwischen 2,5 und 3,6m
#         cr_height = random.randint(2.5*100, 3.6*100)/100
#         cr_volume = cr_height * cr_lenght * cr_width
        

#         if transmission_fake:   
#             u_value = random.randint(3*100, 5*100)/1000
#             problem.append("Insulation insufficient")
#         else:
#             u_value = 0.242 # bei deltaT = 19 Grad und 100mm PUR überall

#         # Define random numbers that make sense
#         if people_fake_1: 
#             n_person = random.randint(4,6)
#             problem.append("To many people in the Room")
#         else:
#             # Personen zwischen 1 und 3
#             n_person = random.randint(1,3) 
        
#         if people_fake_2:
#             t_person = random.randint(6*10, 9*10)/10    
#             problem.append("People too long in the Room")
#         else:
#             # Zeit zwischen 3 und 5 Stunden (eine Nachkommastelle)
#             t_person = random.randint(3*10, 5*10)/10

#         if light_fake_1:
#             load_light_electrical = 240 / 108 * cr_volume * (random.randint(110,175)/100)
#             problem.append("Light consumes too much energy")
#         else:
#             # Anschlussleistung Licht mit Verhältnis zum Standard Danfoss raum ermitteln
#             load_light_electrical = 240 / 108 * cr_volume   

#         if light_fake_2:
#             t_light = t_person + random.randint(1*10, 5*10)/10
#             problem.append("Light is on for too long")
#         else:
#             # Beleuchtungszeit (hier genauso lange wie Aufenthaltszeit -> ergo nur licht wenn leute im Raum sind)
#             t_light = t_person

#         if fan_fake: # KANN MAN GGFLS AUCH NOCH IN LEISTUNG UND ZEIT AUFTEILEN !!
#             load_fan_electrical = 210 / 108 * cr_volume * (random.randint(110,175)/100)
#             problem.append("Fan consumes too much energy")
#         else:
#             # Anschlussleistung Lüfter mit Verhältnis zum Standard Danfoss raum ermitteln 
#             # Deswegen später kein Wirkungsgrad mehr!!
#             load_fan_electrical = 210 / 108 * cr_volume
#             t_fan = random.randint(16*10,18*10)/10

    
        
#         #Calculate Values   
#         load_people = calcuate_load_people(q_person,n_person,t_person)/24000
#         load_light = calcuate_load_light(load_light_electrical,t_light)/24000
#         load_transmission = calcuate_load_transmission(u_value,cr_lenght, cr_width, cr_height, temp_outside, temp_inside)*24/24000
#         load_fan = calcuate_load_machine(load_fan_electrical, 1, t_fan)/24000
#         load_total = (load_transmission + load_people + load_light + load_fan) * 1.45 #Faktor für die fehlenden Lasten
#         # print("volume: ")
#         # print(cr_volume)
#         # print("total load: ")
#         # print(load_total)

#         if load_installed_fake:
#             load_installed = load_total * random.randint(12, 20)/10
#             problem.append("Installed load ist too hight")
#         else:
#             load_installed = load_total * 1.1 #Puffer für installierte Leistung (Defaultbedingungen)
       

        
#         if add_problem: 
#             data_rows.append([load_transmission, load_people, load_light, load_fan, load_total, load_installed, problem])
#         else: 
#             data_rows.append([load_transmission, load_people, load_light, load_fan, load_total, load_installed])
#     if add_problem:
#         # create DataFrame
#         df = pd.DataFrame(data_rows, columns=["load_transmission", "load_people", "load_light", "load_fan", "load_total", "load_installed", "problem"])
#     else: 
#         df = pd.DataFrame(data_rows, columns=["load_transmission", "load_people", "load_light", "load_fan", "load_total", "load_installed"])
#     return df

# print("GENERATING FAKEDATA")
# print(generateData_fake(1, True, True, True, False, False, False, False, False))


def generateData_fake(amount, add_problem, fakeOptions):
    data_rows = []
    # Define default Values:
    q_person = 240
    temp_inside = 5 
    temp_outside = 24 
    
    
    for i in range(amount):
        problem = []

        # Länge zwischen 3 und 6m 
        cr_lenght = random.randint(3*100, 6*100)/100
        # Breite zwischen 3 und 6m
        cr_width = random.randint(3*100, 6*100)/100
        # Höhe zwischen 2,5 und 3,6m
        cr_height = random.randint(2.5*100, 3.6*100)/100
        cr_volume = cr_height * cr_lenght * cr_width
        

        if fakeOptions["transmission_fake"]:   
            u_value = random.randint(3*100, 5*100)/1000
            problem.append("Insulation insufficient")
        else:
            u_value = 0.242 # bei deltaT = 19 Grad und 100mm PUR überall

        # Define random numbers that make sense
        if fakeOptions["people_fake_1"]: 
            n_person = random.randint(4,6)
            problem.append("To many people in the Room")
        else:
            # Personen zwischen 1 und 3
            n_person = random.randint(1,3) 
        
        if fakeOptions["people_fake_2"]:
            t_person = random.randint(6*10, 9*10)/10    
            problem.append("People too long in the Room")
        else:
            # Zeit zwischen 3 und 5 Stunden (eine Nachkommastelle)
            t_person = random.randint(3*10, 5*10)/10

        if fakeOptions["light_fake_1"]:
            load_light_electrical = 240 / 108 * cr_volume * (random.randint(110,175)/100)
            problem.append("Light consumes too much energy")
        else:
            # Anschlussleistung Licht mit Verhältnis zum Standard Danfoss raum ermitteln
            load_light_electrical = 240 / 108 * cr_volume   

        if fakeOptions["light_fake_2"]:
            t_light = t_person + random.randint(1*10, 5*10)/10
            problem.append("Light is on for too long")
        else:
            # Beleuchtungszeit (hier genauso lange wie Aufenthaltszeit -> ergo nur licht wenn leute im Raum sind)
            t_light = t_person

        if fakeOptions["fan_fake"]: # KANN MAN GGFLS AUCH NOCH IN LEISTUNG UND ZEIT AUFTEILEN !!
            load_fan_electrical = 210 / 108 * cr_volume * (random.randint(110,175)/100)
            t_fan = random.randint(16*10,18*10)/10
            problem.append("Fan consumes too much energy")
        else:
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

        if fakeOptions["load_installed_fake"]:
            load_installed = load_total * random.randint(12, 20)/10
            problem.append("Installed load ist too hight")
        else:
            load_installed = load_total * 1.1 #Puffer für installierte Leistung (Defaultbedingungen)
       

        
        if add_problem: 
            data_rows.append([load_transmission, load_people, load_light, load_fan, load_total, load_installed, problem])
        else: 
            data_rows.append([load_transmission, load_people, load_light, load_fan, load_total, load_installed])

    if add_problem:
        # create DataFrame
        df = pd.DataFrame(data_rows, columns=["load_transmission", "load_people", "load_light", "load_fan", "load_total", "load_installed", "problem"])
    else: 
        df = pd.DataFrame(data_rows, columns=["load_transmission", "load_people", "load_light", "load_fan", "load_total", "load_installed"])
    return df





############################ GENERATE TRAINING DATA ############################

print("-------------- GENERATING TRAINING DATA -----------------")

## Training Data DEFAULT - NO PROBLEMS ##
def generateTrainingData_default(amount):
    # [amount] Datensätze mit "none" in Problem-Spalte
    df_trainingData_default = generateData_default(amount, True)
    return df_trainingData_default

print(generateTrainingData_default(10))

def generateTrainignData_fake_sp(amount): 
    df_trainingData_fake_sp = pd.DataFrame()
    fakeOptions = { "transmission_fake" : False, 
                "people_fake_1": False, 
                "people_fake_2": False, 
                "light_fake_1": False, 
                "light_fake_2": False, 
                "fan_fake": False, 
                "load_installed_fake": False}
            
    # jeweils [amount] Datensätze mit dem selben Problem 
    for fakeOption in fakeOptions.keys():
        fakeOptions[fakeOption] = True
        df_trainingData_fake_sp = df_trainingData_fake_sp.append(generateData_fake(amount, True, fakeOptions), ignore_index = True)
        fakeOptions[fakeOption] = False
    return df_trainingData_fake_sp

 

print("\n FAKE TRAINING DATA \n")
print(generateTrainignData_fake_sp(2))


############################ GENERATE TEST DATA ############################

#TODO Enscheiden ob dataframe mit oder Label/Target Spalte 

def generateTestData_mixed_sp(amount): 
    df_TestData_mixed_sp = pd.DataFrame()

    for i in range(amount):
        fakeOptions = { "transmission_fake" : False, 
                "people_fake_1": False, 
                "people_fake_2": False, 
                "light_fake_1": False, 
                "light_fake_2": False, 
                "fan_fake": False, 
                "load_installed_fake": False}
        x = random.randint(0,1) # ANTEIL DER MIT FEHLER GENERIERTEN DATEN LÄSST SICH ÜBER ZWEITE ZAHL STEUERN 
        if x == 0: 
            df_TestData_mixed_sp = df_TestData_mixed_sp.append(generateTrainingData_default(1), ignore_index = True)
        else:
            # fakeOptions[fakeOptions.keys()[random.randint(0, fakeOptions.keys().lenght()-1)] = True     
            fakeOptions[random.choice(list(fakeOptions.keys()))] = True 
            df_TestData_mixed_sp = df_TestData_mixed_sp.append(generateData_fake(1, True, fakeOptions))
    return df_TestData_mixed_sp

print("------------------ TEST GENERATE MIXED TEST DATA ----------------------")
print(generateTestData_mixed_sp(10))
        



fakeOptionsTest = { "transmission_fake" : True, 
                "people_fake_1": False, 
                "people_fake_2": False, 
                "light_fake_1": True, 
                "light_fake_2": False, 
                "fan_fake": True, 
                "load_installed_fake": False}

print(generateData_fake(10, True, fakeOptionsTest))