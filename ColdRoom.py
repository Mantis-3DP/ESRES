import random
import pandas as pd
from pathlib import Path


from sklearn.preprocessing import MultiLabelBinarizer
mlb = MultiLabelBinarizer()

class ColdRoom:
    ######## Constructor ########

    def __init__(self, *args, **kwargs):
        # if kwargs["length"] == None: TODO kann man so besser auf user eingaben abstimmen
        self.length = random.randint(3*100, 6*100)/100
        self.width = random.randint(3*100, 6*100)/100
        self.height = random.randint(2.5*100, 3.6*100)/100
        self.volume = self.length * self.width * self.height
        self.temp_outside = 24.0
        self.temp_inside = 5.0 
        self.q_person = 240

        ### Random Default Values ###
        self.n_person = random.randint(1,3) 
        self.t_person = random.randint(3*10, 5*10)/10
        self.load_light_electrical = 240 / 108 * self.volume
        self.t_light = self.t_person
        self.u_value = 0.242
        self.load_fan_electrical = 210 / 108 * self.volume
        self.t_fan = random.randint(16*10,18*10)/10

        # No Problems 
        self.problems = ["none"]
        self.defaultRoom = True
        self.dataRow = [] #needed for later
        
        if kwargs["default"] == False:
            problemOptions = kwargs.get("problemOptions")
            self.problems.clear() # Removes "none" from problems
            self.defaultRoom = False #sets this Room as not default, kann später dazu genutzt werden um "geheilte Räume" wieder zum lerenne zu verwenden
            if problemOptions["transmission_problem"]:   
                self.u_value = random.randint(3*100, 5*100)/1000
                self.problems.append("Insulation insufficient")

            if problemOptions["people_problem_1"]: 
                self.n_person = random.randint(4,6)
                self.problems.append("To many people in the Room")
    
            if problemOptions["people_problem_2"]:
                self.t_person = random.randint(6*10, 9*10)/10    
                self.problems.append("People too long in the Room")

            if problemOptions["light_problem_1"]:
                self.load_light_electrical = 240 / 108 * self.volume * (random.randint(110, 175)/100)
                self.problems.append("Light consumes too much energy")

            if problemOptions["light_problem_2"]:
                self.t_light = self.t_person + random.randint(1*10, 5*10)/10
                self.problems.append("Light is on for too long")

            if problemOptions["fan_problem"]: # KANN MAN GGFLS AUCH NOCH IN LEISTUNG UND ZEIT AUFTEILEN !!
                self.load_fan_electrical = 210 / 108 * self.volume * (random.randint(110,175)/100)
                self.t_fan = random.randint(16*10,18*10)/10
                self.problems.append("Fan consumes too much energy")

    ######## Variables ########


    ### DefaultValues (BestCaseCR) ###
    
    def calculateDefaultValues(self):
        # Weiterhin Zufallswerte, im Optimalfall noch durch Userabfragen eingrenzen...z.B. "Wie viele leute müssen täglich in den külraum" oder sowas...
        self.u_value_default = 0.242
        self.n_person_default = random.randint(1,3) 
        self.t_person_default = random.randint(3*10, 5*10)/10
        self.load_light_electrical_default = 240 / 108 * self.volume
        self.load_fan_electrical_default = 210 / 108 * self.volume
        self.t_fan_default = random.randint(16*10,18*10)/10

    ######## Methods for Calculating correct values ########

    def calculate_load_people(self, n_person, t_person): 
        # q_person = Wärmeabgabe pro Person (Standard = 240) [W]
        # n_person = Anzahl der Personen 
        # t_person = Aufenthaltszeit im Raum [h/day]
        load_people =  self.q_person * n_person * t_person 
        return load_people

    def calculate_load_light(self, load_electrical, t_light):
        # load_electrical = Anschlussleistung [W]
        # t_light = Zeit in welcher Belechtung genutzt wird [h/day] --> kann von t_person abweichen! 
        load_light = 1 * 1 * load_electrical * t_light 
        return load_light

    def calculate_load_transmission(self): 
        area = 2 * self.length * self.width + 2 * self.height * self.length + 2 * self.height * self.width
        load_transmission = self.u_value * area * (self.temp_outside-self.temp_inside) 
        return load_transmission
    
    def calculate_load_machine(self, load_electrical, efficiency, t_machine): 
        # load_electrical = Anschlussleistung [W]
        # efficiency = Wirkungsgrad
        # t_machine = Nutzungszeit [h/day]
        load_machine = load_electrical / efficiency * 1 * 0.8 * t_machine 
        return load_machine


    # load_total = (load_transmission + load_people + load_light + load_fan) * 1.45 #Faktor für die fehlenden Lasten
    # load_installed

    def calculateLoads(self):
        #Calculate Values   
        self.load_people = self.calculate_load_people(self.n_person,self.t_person) / 24000
        self.load_light = self.calculate_load_light(self.load_light_electrical,self.t_light) / 24000
        self.load_transmission = self.calculate_load_transmission() * 24 / 24000
        self.load_fan = self.calculate_load_machine(self.load_fan_electrical, 1, self.t_fan) / 24000
        self.load_total = (self.load_transmission + self.load_people + self.load_light + self.load_fan) * 1.45 #Faktor für die fehlenden Lasten
        if self.defaultRoom: 
            self.load_installed = self.load_total * 1.1
        else: 
            self.load_installed = self.load_total * random.randint(12,20)/10


    def createDataRow(self):
        self.calculateLoads()
        self.dataRow = [self.load_transmission, self.load_people, self.load_light, self.load_fan, self.load_total, self.load_installed, self.problems]
        return self.dataRow # Theoretisch auch zugriff über Objektatrribut möglich


############## DATA GENERATION ##########

def generateRandomColdRooms(*args, **kwargs):
    amount = kwargs["amount"]
    dataRows = []
    for i in range(amount):
        problemOptions = { "transmission_problem" : False, 
                    "people_problem_1": False, 
                    "people_problem_2": False, 
                    "light_problem_1": False, 
                    "light_problem_2": False, 
                    "fan_problem": False, 
                    "load_installed_problem": False}
        x = random.randint(0,1) # ANTEIL DER MIT FEHLER GENERIERTEN DATEN LÄSST SICH ÜBER ZWEITE ZAHL STEUERN 
        if x == 0: 
            #generate Random DEFAULT ColdRoom
            cr = ColdRoom(default=True)
            dataRows.append(cr.createDataRow())
        else:
            amount_problems = random.randint(1, len(problemOptions)) #Hiermit kann man beeinflussen wie viele Fehler maximal gemacht werden können 
            for p in range(amount_problems):                      #Mindestanzahl ist nicht direkt möglich in der Form, da nicht gecheckt wird ob Probleme "doppelt auf True" gesetzt werden 
                problemOptions[random.choice(list(problemOptions.keys()))] = True
            # generate Random FAULTY ColdRoom
            cr = ColdRoom(default=False, problemOptions=problemOptions)
            dataRows.append(cr.createDataRow())

    df_Data_mixed_mp = pd.DataFrame(dataRows, columns=["load_transmission", "load_people", "load_light", "load_fan", "load_total", "load_installed", "problems"]) # EIN S BEI PROBLEM MEHR!!
    
    temp = df_Data_mixed_mp
    if kwargs["csv"] == True:   
        ######## DATA PROCESSING ########
        print("Peak at generated Data: ")
        print(df_Data_mixed_mp.head())
        print("Processing generated Data")
        df_ENC = df_Data_mixed_mp.join(pd.DataFrame(mlb.fit_transform(df_Data_mixed_mp.pop("problems")), columns = mlb.classes_, index=df_Data_mixed_mp.index))
        print("Peak at processed Data")
        print(df_ENC.head())
        filename = "data/" + kwargs["filename"] + ".csv"
        exportPath = Path(__file__).parent / filename
        df_ENC.to_csv(exportPath, index=False)
        temp = "Saved Data as csv at " + str(exportPath)

    return temp


# Cheesy way die Methode zu callen, aber im Moment ausreichend, später über runme
# Parameter:
# amount legt die anzahl der generierten Daten fest
# csv = True/False sagt ob die Daten in einer csv Datei gespeichert werden sollen
# filename = "" -> Dateiname

print(generateRandomColdRooms(amount=10000, csv=True, filename="newData_vectoroutput"))
