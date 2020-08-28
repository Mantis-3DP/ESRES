import random
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import MultiLabelBinarizer
import math

mlb = MultiLabelBinarizer()


class ColdRoom:
    # Modes: problem, default, user

    ######## Constructor ########

    def __init__(self, *args, **kwargs):
        if "length" not in kwargs:  # TODO kann man so besser auf user eingaben abstimmen
            self.length = random.randint(3 * 100, 6 * 100) / 100
        else:
            self.length = kwargs["length"]
        if "width" not in kwargs:
            self.width = random.randint(3 * 100, 6 * 100) / 100
        else:
            self.width = kwargs["width"]
        if "height" not in kwargs:
            self.height = random.randint(2.5 * 100, 3.6 * 100) / 100
        else:
            self.height = kwargs["height"]

        self.volume = self.length * self.width * self.height

        # Konstanten für diesen Proof of Concept
        self.temp_outside = 24.0
        self.temp_inside = 5.0
        self.q_person = 240

        ### Random Default Values ###
        if "n_person" not in kwargs:
            self.n_person = random.randint(1, 3)
        else:
            self.n_person = kwargs["n_person"]
        if "t_person" not in kwargs:
            self.t_person = random.randint(3 * 10, 5 * 10) / 10
        else:
            self.t_person = kwargs["t_person"]
        if "load_light_electrical" not in kwargs:
            self.load_light_electrical = 240 / 108 * self.volume
        else:
            self.load_light_electrical = kwargs["load_light_electrical"]
        if "t_light" not in kwargs:
            self.t_light = self.t_person
        else:
            self.t_light = kwargs["t_light"]
        if "u_value" not in kwargs:
            self.u_value = 0.242
        else:
            self.u_value = kwargs["u_value"]
        if "load_fan_electrical" not in kwargs:
            self.load_fan_electrical = 210 / 108 * self.volume
        else:
            self.load_fan_electrical = kwargs["load_fan_electrical"]

        self.t_fan = random.randint(16 * 10, 18 * 10) / 10
        self.load_installed = 0.0

        if "load_installed" in kwargs:
            self.load_installed = kwargs["load_installed"]

        self.dataRow = []
        self.mode = kwargs.get("mode")
        self.problems = []

        if self.mode == "default":
            self.problems = ["none"]
            self.defaultRoom = True
        elif self.mode == "user":
            self.defaultRoom = False
        elif self.mode == "problem":
            self.problemOptions = kwargs.get("problemOptions")
            self.defaultRoom = False  # sets this Room as not default, kann später dazu genutzt werden um "geheilte Räume" wieder zum lerenne zu verwenden
            if self.problemOptions["transmission_problem"]:
                self.u_value = random.randint(3 * 100, 5 * 100) / 1000
                self.problems.append("Insulation insufficient")

            if self.problemOptions["people_problem_1"]:
                self.n_person = random.randint(4, 6)
                self.problems.append("To many people in the Room")

            if self.problemOptions["people_problem_2"]:
                self.t_person = random.randint(6 * 10, 9 * 10) / 10
                self.problems.append("People too long in the Room")

            if self.problemOptions["light_problem_1"]:
                self.load_light_electrical = 240 / 108 * self.volume * (random.randint(110, 175) / 100)
                self.problems.append("Light consumes too much energy")

            if self.problemOptions["light_problem_2"]:
                self.t_light = self.t_person + random.randint(1 * 10, 5 * 10) / 10
                self.problems.append("Light is on for too long")

            if self.problemOptions["fan_problem"]:  # KANN MAN GGFLS AUCH NOCH IN LEISTUNG UND ZEIT AUFTEILEN !!
                self.load_fan_electrical = 210 / 108 * self.volume * (random.randint(110, 175) / 100)
                self.t_fan = random.randint(16 * 10, 18 * 10) / 10
                self.problems.append("Fan consumes too much energy")

    ### DefaultValues (BestCaseCR) ###

    def calculateDefaultValues(self):
        # Weiterhin Zufallswerte, im Optimalfall noch durch Userabfragen eingrenzen...z.B. "Wie viele leute müssen täglich in den külraum" oder sowas...
        self.u_value_default = 0.242
        self.n_person_default = random.randint(1, 3)
        self.t_person_default = random.randint(3 * 10, 5 * 10) / 10
        self.load_light_electrical_default = 240 / 108 * self.volume
        self.t_light_default = self.t_person_default
        self.load_fan_electrical_default = 210 / 108 * self.volume
        self.t_fan_default = random.randint(16 * 10, 18 * 10) / 10

    ######## Methods for Calculating correct values ########

    def calculate_load_people(self, n_person, t_person):
        # q_person = Wärmeabgabe pro Person (Standard = 240) [W]
        # n_person = Anzahl der Personen
        # t_person = Aufenthaltszeit im Raum [h/day]
        load_people = self.q_person * n_person * t_person
        return load_people

    def calculate_load_light(self, load_electrical, t_light):
        # load_electrical = Anschlussleistung [W]
        # t_light = Zeit in welcher Belechtung genutzt wird [h/day] --> kann von t_person abweichen!
        load_light = 1 * 1 * load_electrical * t_light
        return load_light

    def calculate_load_transmission(self, u_value):
        area = 2 * self.length * self.width + 2 * self.height * self.length + 2 * self.height * self.width
        load_transmission = u_value * area * (self.temp_outside - self.temp_inside)
        return load_transmission

    def calculate_load_machine(self, load_electrical, efficiency, t_machine):
        # load_electrical = Anschlussleistung [W]
        # efficiency = Wirkungsgrad
        # t_machine = Nutzungszeit [h/day]
        load_machine = load_electrical / efficiency * 1 * 0.8 * t_machine
        return load_machine

    def calculateLoads(self):
        # Calculate Values
        self.load_people = self.calculate_load_people(self.n_person, self.t_person) / 24000
        self.load_light = self.calculate_load_light(self.load_light_electrical, self.t_light) / 24000
        self.load_transmission = self.calculate_load_transmission(self.u_value) * 24 / 24000
        self.load_fan = self.calculate_load_machine(self.load_fan_electrical, 1, self.t_fan) / 24000
        self.load_total = (
                                      self.load_transmission + self.load_people + self.load_light + self.load_fan) * 1.45  # Faktor für die fehlenden Lasten
        if self.mode == "default":
            self.load_installed = self.load_total * 1.1
        elif self.mode == "problem":
            if self.problemOptions["load_installed_problem"]:
                self.load_installed = self.load_total * random.randint(12, 20) / 10
                self.problems.append("Installed Load too high")
            else:
                self.load_installed = self.load_total * 1.1

    ###### Create Table Rows ######

    def createDataRow(self):
        self.calculateLoads()
        self.dataRow = [self.load_transmission, self.load_people, self.n_person, self.load_light, self.load_fan,
                        self.load_total, self.load_installed, self.problems]
        return self.dataRow

    def createDataFrame(self):
        dataRow = self.createDataRow()
        df_temp = pd.DataFrame([dataRow],
                               columns=["load_transmission", "load_people", "n_person", "load_light", "load_fan",
                                        "load_total", "load_installed", "problems"])
        df_ENC = df_temp.join(
            pd.DataFrame(mlb.fit_transform(df_temp.pop("problems")), columns=mlb.classes_, index=df_temp.index))
        return df_ENC


    def calculatebestCaseLoads(self):
        totalSavings = 0.0
        for problem in self.problems:
            if problem == "Fan consumes too much energy":
                diff = self.load_fan - (self.calculate_load_machine(self.load_fan_electrical_default, 1,
                                                                    self.t_fan_default) / 24000)
                totalSavings += diff

            elif problem == "Insulation insufficient":
                diff = self.load_transmission - (self.calculate_load_transmission(self.u_value_default) * 24 / 24000)
                totalSavings += diff

            elif problem == "Light consumes too much energy":
                diff = self.load_light - (
                            self.calculate_load_light(self.load_light_electrical_default, self.t_light) / 24000)
                totalSavings += diff

            elif problem == "Light is on for too long":
                diff = self.load_light - (
                            self.calculate_load_light(self.load_light_electrical, self.t_light_default) / 24000)
                totalSavings += diff

            elif problem == "People too long in the Room":
                diff = self.load_people - (self.calculate_load_people(self.n_person, self.t_person_default) / 24000)
                totalSavings += diff

            elif problem == "To many people in the Room":
                diff = self.load_people - (self.calculate_load_people(self.n_person_default, self.t_person) / 24000)
                totalSavings += diff

            elif problem == "Installed Load too high":
                diff = self.load_installed - (self.load_total * 1.1)
                totalSavings += diff

            elif problem == "none":
                pass
        print("Total possible Savings: " + str(round(totalSavings, 3)) + "kW")

    ######################## CALCULATE MEASURE IMPACTS ########################

    # Festlegen der Stromkosten
    energycost = 0.3  # Euro/kWh

    #### "Wirtschaftlichkeitsfunktionen" (sehr trivial) ###

    def clean_fan(self):
        diff = self.load_fan - (
                    self.calculate_load_machine(self.load_fan_electrical_default, 1, self.t_fan_default) / 24000)
        savings = diff * 24 * 365 * self.energycost * random.randint(15, 30) / 100
        # Annahme: Mit Reinigung kann nur 15 bis 30 Prozent der Einsparungen erreicht werden, Reinigung kostet 200 Euro
        investion = 300
        a_years = investion / savings
        return a_years

    def new_fan(self):
        diff = self.load_fan - (
                    self.calculate_load_machine(self.load_fan_electrical_default, 1, self.t_fan_default) / 24000)
        savings = diff * 24 * 365 * self.energycost
        # Annahme Kosten neuer Lüfter:
        investion = 1450  # TODO Theoretisch skalierbar mit Volumen -> Wollen wir das?
        a_years = investion / savings
        return a_years

    def install_countdown(self):
        # Ersprarnis im Vergleich zu default
        diff = self.load_people - (self.calculate_load_people(self.n_person, self.t_person_default) / 24000)
        # Ersparnis pro Jahr in Euro
        savings = diff * 24 * 365 * self.energycost
        # Investitionskosten
        # Annahme Pro Fläche von 15m² wird ein timer für 1100 Euro benötigt, Nur ganze Timer sind möglich -> 15m² -> 1 16m²-> 2
        investion = math.ceil(self.length * self.width / 15) * 775
        # print(investion)
        # Armortisierungszeitraum
        a_years = investion / savings
        return a_years

    def school_workers(self):
        diff = self.load_people - (self.calculate_load_people(self.n_person, self.t_person_default) / 24000)
        savings = diff * 24 * 365 * self.energycost
        # Annahme Schulungskosten pro person von 300 Euro
        investion = self.n_person * 300
        a_years = investion / savings
        return a_years

    measures = {
        "Fan consumes too much energy":
            {"clean_fan": clean_fan, "new_fan": new_fan},
        "People too long in the Room":
            {"install_countdown": install_countdown, "school_workers": school_workers}
    }

    def add_measure_columns(self):
        measure_datarow = []
        measure_columns = []
        for problem in self.problems:
            if problem in self.measures:
                for measure in self.measures[problem]:
                    measure_datarow.append(self.measures[problem][measure](self))
                    measure_columns.append(measure)
        df_measures = pd.DataFrame([measure_datarow], columns=measure_columns)
        return df_measures


############## DATA GENERATION ##########

def generateRandomColdRooms(*args, **kwargs):
    amount = kwargs["amount"]
    if "fault_share" in kwargs:
        fault_share = kwargs["fault_share"]
    else:
        fault_share = 1
    dataRows = []
    coldRooms = []
    for i in range(amount):
        problemOptions = {"transmission_problem": False,
                          "people_problem_1": False,
                          "people_problem_2": False,
                          "light_problem_1": False,
                          "light_problem_2": False,
                          "fan_problem": False,
                          "load_installed_problem": False}
        x = random.randint(0, fault_share)
        if x == 0:
            # generate Random DEFAULT ColdRoom
            cr = ColdRoom(mode="default")
            coldRooms.append(cr)
            dataRows.append(cr.createDataRow())
        else:
            amount_problems = random.randint(1, int(len(
                problemOptions) / 2))  # Hiermit kann man beeinflussen wie viele Fehler maximal gemacht werden können
            chosen_problems = random.sample(list(problemOptions.keys()), k=amount_problems)
            for problems in chosen_problems:
                problemOptions[problems] = True
            # generate Random FAULTY ColdRoom
            cr = ColdRoom(mode="problem", problemOptions=problemOptions)
            coldRooms.append(cr)
            dataRows.append(cr.createDataRow())

    df_Data_mixed_mp = pd.DataFrame(dataRows,
                                    columns=["load_transmission", "load_people", "n_person", "load_light", "load_fan",
                                             "load_total", "load_installed", "problems"])  # EIN S BEI PROBLEM MEHR!!

    temp = df_Data_mixed_mp
    if kwargs["csv"] == True:
        ######## DATA PROCESSING ########
        print("Peak at generated Data: ")
        print(df_Data_mixed_mp.head())
        print("Processing generated Data")
        df_ENC = df_Data_mixed_mp.join(
            pd.DataFrame(mlb.fit_transform(df_Data_mixed_mp.pop("problems")), columns=mlb.classes_,
                         index=df_Data_mixed_mp.index))
        print("Peak at processed Data")
        print(df_ENC.head())
        filename = "Data/" + kwargs["filename"] + ".csv"
        exportPath = Path(__file__).parent / filename
        df_ENC.to_csv(exportPath, index=False)
        temp = "Saved Data as csv at " + str(exportPath)

    # FÜR Übergabe von Objekten
    if kwargs["object"] == True:
        print("exported " + str(len(coldRooms)) + "ColdRooms in List")
        temp = coldRooms
    return temp