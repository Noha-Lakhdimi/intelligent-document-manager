import spacy
from spacy.util import minibatch, compounding
import random
from spacy.training.example import Example
from pathlib import Path
from spacy.training.iob_utils import offsets_to_biluo_tags

nlp = spacy.load("fr_core_news_sm")

ner = nlp.get_pipe("ner")
LABEL_MARCHE = "NUM_MARCHE"
LABEL_VERSION = "VERSION_DOCUMENT"
LABEL_ORG = "ORG"
LABEL_LOC = "LOC"

for label in [LABEL_MARCHE, LABEL_VERSION, LABEL_ORG, LABEL_LOC]:
    ner.add_label(label)

TRAIN_DATA = [

    (
        "La présente étude, confiée par l’ONEP/DPL, au bureau d’études ADI, dans le cadre du "
        "marché n°1208/E/DPL/2008, a pour objet la réalisation de l'étude de faisabilité pour le "
         "renforcement d’alimentation en eau potable de la ville d’Agadir, des centres et douars "
         "avoisinants par le dessalement d’eau de mer. Cette étude sera réalisée selon les "
         "quatre missions suivantes : - - - - "
         "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins – ressources ;  "
         "Mission II : Identification des sites d’implantation de l’usine de dessalement et "
         "définition des schémas d’adduction ; "
         "Mission III : Evaluation environnementale ; "
         "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque "
         "site, évaluation économique et synthèse des résultats. "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue la "
         "note de synthèse du rapport définitif de la Mission I, relative à l’analyse de la "
         "situation actuelle d'AEP et l’actualisation du bilan besoins – ressources.",
         {
             "entities": [
                 (62, 65, "LABEL_ORG"),                  # ADI
                 (93, 108, "LABEL_MARCHE"),              # 1208/E/DPL/2008
                 (229, 235, "LABEL_LOC"),                # Agadir
                 (887, 896, "LABEL_VERSION")             # définitif
             ]
         }
    ),

    (
        "La présente étude, confiée par l’ONEP/DPL, au bureau d’études ADI, dans le cadre du "
        "marché n°1208/E/DPL/2008, a pour objet la réalisation de l'étude de faisabilité pour le "
        "renforcement d’alimentation en eau potable de la ville d’Agadir, des centres et douars "
        "avoisinants par le dessalement d’eau de mer. Cette étude sera réalisée selon les "
        "quatre missions suivantes : - - - - "
        "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins – ressources ;  "
        "Mission II : Identification des sites d’implantation de l’usine de dessalement et "
        "définition des schémas d’adduction ; "
        "Mission III : Evaluation environnementale ; "
        "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque "
        "site, évaluation économique et synthèse des résultats. "
        "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le "
        "rapport définitif de la Mission I, relative à l’Analyse de la Situation Actuelle d'AEP et "
        "l’Actualisation du Bilan Besoins – Ressources. Il comprend les chapitres suivants : "
        "Chapitre I   : Données générales sur la zone d’études ; "
        "Chapitre II   : Situation actuelle de l’AEP dans la zone d’études ; "
        "Chapitre III : Situation des ressources en eau ; "
        "Chapitre IV : Etude de la demande en eau de la zone du projet ; "
        "Chapitre V  : Bilans besoins-ressources et besoins-capacité de transit.",
        {
            "entities": [
                (62, 65, "LABEL_ORG"),              # ADI
                (93, 108, "LABEL_MARCHE"),          # 1208/E/DPL/2008
                (229, 235, "LABEL_LOC"),            # Agadir
                (867, 876, "LABEL_VERSION")         # définitif
            ]
        }
    ),

    (
        "La présente étude, confiée par l’ONEP/DPL, au bureau d’études ADI, dans le cadre du "
        "marché n°1208/E/DPL/2008, a pour objet la réalisation de l'étude de faisabilité pour le "
        "renforcement d’alimentation en eau potable de la ville d’Agadir, des centres et douars "
        "avoisinants par le dessalement d’eau de mer. Cette étude sera réalisée selon les "
        "quatre missions suivantes : - - - - "
        "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins – ressources ;  "
        "Mission II : Identification des sites d’implantation de l’usine de dessalement et "
        "définition des schémas d’adduction ; "
        "Mission III : Evaluation environnementale ; "
        "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque "
        "site, évaluation économique et synthèse des résultats. "
        "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le "
        "rapport définitif de la Mission II, relative à l’identification des sites d’implantation de "
        "l’usine de dessalement et la définition des schémas d’adduction. Il comprend les "
        "chapitres suivants : "
        "Chapitre I   : Rappel des principaux résultats de la mission I ; "
        "Chapitre II   : Description technique des installations de dessalement ; "
        "Chapitre III : Identification, analyse et choix des sites potentiels ; "
        "Chapitre IV : Définition et étude technico-économique des schémas d’alimentation.",
        {
            "entities": [
                (62, 65, "LABEL_ORG"),                      # ADI
                (93, 108, "LABEL_MARCHE"),                  # 1208/E/DPL/2008
                (229, 235, "LABEL_LOC"),                    # Agadir
                (867, 876, "LABEL_VERSION")                 # définitif
            ]
        }
    ),

    (
        "La présente étude, confiée par l’ONEP/DPL, au bureau d’études ADI, dans le cadre du "
         "marché n°1208/E/DPL/2008, a pour objet la réalisation de l'étude de faisabilité pour le "
         "renforcement d’alimentation en eau potable de la ville d’Agadir, des centres et douars "
         "avoisinants par le dessalement d’eau de mer. Cette étude sera réalisée selon les "
         "quatre missions suivantes : - - - - "
         "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins – ressources ;  "
         "Mission II : Identification des sites d’implantation de l’usine de dessalement et "
         "définition des schémas d’adduction ; "
         "Mission III : Evaluation environnementale ; "
         "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque "
         "site, évaluation économique et synthèse des résultats. "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue la "
         "note de synthèse du rapport définitif de la Mission II.",
         {
             "entities": [
                 (62, 65, "LABEL_ORG"),             # ADI
                 (93, 108, "LABEL_MARCHE"),         # 1208/E/DPL/2008
                 (229, 235, "LABEL_LOC"),           # Agadir
                 (887, 896, "LABEL_VERSION")        # définitif
             ]
         }
    ),

    (
        "Dans le cadre du marché N° 373/E/DPS/2007, l'Office National de l'Eau Potable (ONEP) a confié "
         "à l'Ingénieur Conseil CID, l’étude de faisabilité du dessalement d’eau de mer pour l’alimentation "
         "en eau potable à long terme de la ville d’Al Hoceima et des centres et communes avoisinants. "
         "L'étude comporte les quatre missions suivantes : "
         " Mission I : Actualisation du bilan besoins-ressources ; "
         " Mission II : Identification des sites d'implantation des usines de dessalement et définition "
         "du schéma d’adduction ; "
         " Mission III : Evaluation environnementale ; "
         " Mission IV : Définition du procédé de dessalement le plus approprié pour chaque site et "
         "évaluation économique. "
         "Le présent rapport concerne la note de synthèse de la Mission II établie tenant compte des "
         "conclusions de la mission III (Evaluation environnementale).",
         {
             "entities": [
                 (27, 41, "LABEL_MARCHE"),              # 373/E/DPS/2007
                 (116, 119, "LABEL_ORG"),               # CID
                 (234, 244, "LABEL_LOC"),               # Al Hoceima
             ]
         }
    ),

    (
        "La présente étude, confiée par l’ONEP/DPL, au bureau d’études ADI, dans le cadre du "
        "marché n°1208/E/DPL/2008, a pour objet la réalisation de l'étude de faisabilité pour le "
        "renforcement d’alimentation en eau potable de la ville d’Agadir, des centres et douars "
        "avoisinants par le dessalement d’eau de mer. Cette étude sera réalisée selon les "
        "quatre missions suivantes : - - - - "
        "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins – ressources ;  "
        "Mission II : Identification des sites d’implantation de l’usine de dessalement et "
        "définition des schémas d’adduction ; "
        "Mission III : Evaluation environnementale ; "
        "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque "
        "site, évaluation économique et synthèse des résultats. "
        "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le "
        "rapport définitif de la Mission IV. Il comprend les chapitres suivants : "
        "Chapitre I   : Données de base et inventaire des sites et procédés de dessalement "
        "d’eau de mer ;  "
        "Chapitre II   : Etude technico-économique pour le choix du procédé de "
        "dessalement approprié pour chaque site.",
        {
            "entities": [
                (62, 65, "LABEL_ORG"),               # ADI
                (93, 108, "LABEL_MARCHE"),           # 1208/E/DPL/2008
                (229, 235, "LABEL_LOC"),             # Agadir
                (867, 876, "LABEL_VERSION")          # définitif
            ]
        }
    ),

    (
        "L’Ingénieur Conseil CID, a été chargé par le Conseil de la Province d’Al Haouz dans le "
        "cadre du marché n°15/2020 de l’Etude d’approvisionnement en eau potable de la "
        "populaton rurale de la province d’Al Haouz. "
        "Cette étude sera scindée en trois (3) missions suivantes : - - - "
        "Mission I   : Etude des schémas de desserte (APS) ;  "
        "Mission II   : Etude d’Avant Projet Détaillée (APD) ;  "
        "Mission III   : Dossier de consultation des Entreprises (DCE). "
        "Le présent mémoire constitue le rapport provisoire de la mission I, qui porte sur la "
        "définition des schémas de desserte plausibles, le dimenionnement des ouvrages et la "
        "comparaison technico-économique des différentes variantes envisageables pour l’AEP "
        "des centres et douars de la zone d’étude.  "
        "Pour ce faire, il y est taité les principaux aspects suivants : "
        "Données Générales sur la zone d’étude ; "
        "Description des systèmes actuels d’AEP ; "
        "Etude de la demande en eau ;  "
        "Projection démographiques et calcul la demande en eau ; "
        "Analyse de la situation actuelle en matière des ressources en eau souterraines "
        "et superficielles ; "
        "Établissement des bilans besoins – ressources et bilans besoins – capacité de "
        "transit ; "
        "Définition des schémas de desserte ;  "
        "Conception et dimensionnement des ouvrages ;  "
        "Coût d’investissement des ouvrages.",
        {
            "entities": [
                (20, 23, "LABEL_ORG"),              # CID
                (105, 112, "LABEL_MARCHE"),         # 15/2020
                (199, 207, "LABEL_LOC"),            # Al Haouz
                (485, 495, "LABEL_VERSION")         # provisoire
            ]
        }
    ),

    (
        "Dans le cadre du marché N° 930/E/DPL/2012, la Direction Planification de l'ONEE - branche eau - branche "
         "eau \"DPL\" a confié à l’I.C. Groupement HYDROSTRUCTURES – ICM l’Étude de faisabilité de "
         "renforcement et de sécurisation de l’AEP des localités urbaines et rurales de l’axe Azrou - M’Rirt. La zone "
         "d’étude définie par l’ONEE - branche eau - branche eau comprend : "
         "Milieu Urbain : Province d’Ifrane : ville d’Azrou et centres d’Aïn Leuh, Sidi Addi et Had Oued Ifrane ; "
         "Province de Khénifra Milieu Rural : Province d’Ifrane : municipalité de M’rirt et centre de Tighza. "
         ": communes rurales d’Aïn Leuh, Ben Smim, Sidi El Makhfi, Oued Ifrane "
         "et Tigrigra ; - Province de Khénifra : communes rurales d’Oum Rabia et El Hammam. "
         "L’étude se compose des trois (03) missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – "
         "ressources et besoins – capacité de production et de transport. "
         "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
         "Mission III : Évaluation Environnementale. "
         "Le présent mémoire constitue la note de synthèse de la mission I.",
         {
             "entities": [
                 (27, 41, "LABEL_MARCHE"),             # 930/E/DPL/2012
                 (143, 158, "LABEL_ORG"),              # HYDROSTRUCTURES
                 (161, 164, "LABEL_ORG"),              # ICM
                 (275, 280, "LABEL_LOC"),              # Azrou
                 (281, 289, "LABEL_LOC"),              # M’Rirt
             ]
         }
    ),

    (
        "Dans le cadre du marché N° 930/E/DPL/2012, la Direction Planification de l'ONEE - branche eau - branche "
        "eau \"DPL\" a confié à l’I.C. Groupement HYDROSTRUCTURES – ICM l’Étude de faisabilité de "
        "renforcement et de sécurisation de l’AEP des localités urbaines et rurales de l’axe Azrou - M’Rirt. La zone "
        "d’étude définie par l’ONEE - branche eau - branche eau comprend : "
        "Milieu Urbain : - Province d’Ifrane : ville d’Azrou et centres d’Aïn Leuh, Sidi Addi et Had Oued Ifrane ; "
        "- Province de Khénifra : municipalité de M’rirt et centre de Tighza. "
        "Milieu Rural : - Province d’Ifrane : communes rurales d’Aïn Leuh, Ben Smim, Sidi El Makhfi, Oued Ifrane "
        "et Tigrigra ; - Province de Khénifra : communes rurales d’Oum Rabia et El Hammam. "
        "L’étude se compose des trois (03) missions suivantes : "
        "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – "
        "ressources et besoins – capacité de production et de transport. "
        "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
        "Mission III : Évaluation Environnementale. "
        "Le présent dossier constitue le rapport définitif de la mission I  et il traite des principaux aspects "
        "suivants : - Généralités sur l’aire d’étude ; - Description des systèmes d’AEP existants ; - Analyse de la situation actuelle de l’assainissement liquide ; - Projection de la demande en eau ; - Analyse de la situation actuelle en matière des ressources en eau souterraines et "
        "superficielles ; - Établissement des bilans besoins – ressources ; - Établissement des bilans besoins – capacités de transport.",
        {
            "entities": [
                (27, 41, "LABEL_MARCHE"),               # 930/E/DPL/2012
                (143, 158, "LABEL_ORG"),                # HYDROSTRUCTURES
                (161, 164, "LABEL_ORG"),                # ICM
                (275, 280, "LABEL_LOC"),                # Azrou
                (283, 289, "LABEL_LOC"),                # M’Rirt
                (1080, 1089, "LABEL_VERSION")           # définitif
            ]
        }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable – Branche "
         "Eau (ONEE-BO) – Direction Planification, au bureau d’études ADI, dans le cadre du "
         "marché n°1081/E/DPL/2015, a pour objet l’établissement du Schéma Directeur de "
         "renforcement de la production d’eau potable de la ville de Dakhla. Cette étude est "
         "prévue selon les trois missions suivantes : "
         " Mission I : Analyse de la situation actuelle de l’AEP et actualisation du bilan besoins – ressources ; "
         " Mission II : Etudes des schémas de renforcement et de sécurisation de la production "
         "de l’eau potable de la ville de Dakhla ; "
         " Mission III : Evaluation environnementale. "
         "Le présent rapport constitue la note de synthèse de la Mission II, relative à l’étude des "
         "Schémas de renforcement et de sécurisation de la production de l’eau potable de la ville de "
         "Dakhla et zones liées. "
         "La zone, concernée par la présente étude, inclut la ville de Dakhla, le village de pêche de "
         "Lassarga et le centre de Tawrta, relevant de la commune d’El Argoub, et qui est susceptible "
         "d’être alimenté, à partir du système d’AEP de la ville de Dakhla. "
         "La ville de Dakhla est le chef-lieu de la région de Dakhla - Oued Eddahab, selon le nouveau "
         "découpage régional du Royaume, et de la province d'Oued Ed-Dahab. La figure 1, ci-après, "
         "illustre la situation géographique de la zone d’étude. "
         "Selon le RGPH 2014, la population de la ville de Dakhla s’élève à 106 277 habitants, soit "
         "environ 85% de la population de la province d’Oued Ed-Dahab. Cette population est répartie "
         "sur 25 469 ménages. La population du centre de Tawrta, selon le rapport justificatif du plan "
         "d’aménagement de ce centre, est estimée à 300 habitants en 2013.",
         {
             "entities": [
                 (156, 159, "LABEL_ORG"),             # ADI
                 (187, 202, "LABEL_MARCHE"),          # 1081/E/DPL/2015
                 (315, 321, "LABEL_LOC"),             # Dakhla
             ]
         }
    ),

    (
        "Dans le cadre du marché N° 930/E/DPL/2012, la Direction Planification de l'ONEE - branche eau - "
        "branche eau \"DPL\" a confié à l’I.C. Groupement HYDROSTRUCTURES – ICM l’Étude de faisabilité de "
        "renforcement et de sécurisation de l’AEP des localités urbaines et rurales de l’axe Azrou - M’Rirt. La zone "
        "d’étude définie par l’ONEE - branche eau - branche eau comprend : "
        "Milieu Urbain : - - "
        "Province d’Ifrane : ville d’Azrou et centres d’Aïn Leuh, Sidi Addi et Had Oued Ifrane ; "
        "Province de Khénifra : municipalité de M’rirt et centre de Tighza. "
        "Milieu Rural : - - "
        "Province d’Ifrane : communes rurales d’Aïn Leuh, Ben Smim, Sidi El Makhfi, Oued Ifrane "
        "et Tigrigra ; "
        "Province de Khénifra : communes rurales d’Oum Rabia et El Hammam. "
        "L’étude se compose des trois (03) missions suivantes : "
        "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – "
        "ressources et besoins – capacité de production et de transport. "
        "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
        "Mission III : Évaluation Environnementale. "
        "Le présent mémoire constitue le rapport définitif de la mission III.",
        {
            "entities": [
                (27, 41, "LABEL_MARCHE"),               # 930/E/DPL/2012
                (143, 158, "LABEL_ORG"),                # HYDROSTRUCTURES
                (161, 164, "LABEL_ORG"),                # ICM
                (275, 280, "LABEL_LOC"),                # Azrou
                (283, 289, "LABEL_LOC"),                # M’Rirt
                (1080, 1089, "LABEL_VERSION")           # définitif
            ]
        }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable- Branche "
         "Eau (ONEE-BO) - Direction Planification, au bureau d’études ADI, dans le cadre du marché "
         "n°1081/E/DPL/2015, a pour objet la réalisation de l’étude du Schéma Directeur de "
         "renforcement de la production d’eau potable de la ville de Dakhla.  "
         "Cette étude sera réalisée selon les trois missions suivantes : - - - "
         "Mission 1 : Analyse de la situation actuelle de l’AEP et actualisation du bilan besoins- "
         "ressources ;  "
         "Mission 2 : Etudes des schémas de renforcement et de sécurisation de la production de "
         "l’eau potable de la ville de Dakhla ; "
         "Mission 3 : Evaluation environnementale "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le "
         "rapport de synthèse de la Mission III, relative à l’étude d’évaluation environnementale du "
         "projet de renforcement de la production d’eau potable de la ville de Dakhla.",
         {
             "entities": [
                 (155, 158, "LABEL_ORG"),             # ADI
                 (186, 201, "LABEL_MARCHE"),          # 1081/E/DPL/2015
                 (324, 330, "LABEL_LOC"),             # Dakhla
             ]
         }
    ),

    (
        "Dans le cadre du marché N° 821/E/DPL/2010, la Direction Planification de l'ONEE - branche eau \"DPL\" a "
         "confié à l’I.C. Groupement GIECO - HYDROSTRUCTURES l’Étude de Faisabilité pour le Renforcement de "
         "l’Alimentation en Eau Potable de la Région de Guercif - Taourirt. La zone d’étude telle que définie par "
         "l’ONEE - branche eau comprend : "
         "Milieu Urbain : - Province de Guercif : ville de Guercif ; - Province de Taourirt : ville de Taourirt, centres d’El Aioun Sidi Mellouk et de Debdou ; "
         "- Province de Boulemane : centre d’Outat El Haj. "
         "Milieu Rural : - Province de Guercif : Communes rurales d’Assebbab, Barkine, Houara Ouled Raho, "
         "Lamrija, Saka, Mazguitam, Ouled Bourima, Ras Laksar et Taddart. - Province de Taourirt : Communes rurales d’Ahl Oued Za, Melg El Ouidane, Gteter, El Atef, "
         "Oulad M’hammed, Sidi Ali Belkacem, Sidi Lahsen, Tancherfi, Ain lehjer, Mestegmer et "
         "Mechraa Hammadi. - Province de Boulemane : Communes rurales de Fritissa, Tissaf, El Orjane, Ermila et "
         "Oulad Ali Youssef. "
         "L’étude se compose des trois (03) missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – "
         "ressources et besoins – capacité de production et de transport à l’horizon 2035. "
         "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
         "Mission III : Évaluation Environnementale. "
         "Le présent document constitue le note de synthèse de la mission I.",
         {
             "entities": [
                 (27, 41, "LABEL_MARCHE"),                  # 821/E/DPL/2010
                 (129, 134, "LABEL_ORG"),                   # GIECO
                 (137, 152, "LABEL_ORG"),                   # HYDROSTRUCTURES
                 (246, 253, "LABEL_LOC"),                   # Guercif
                 (256, 264, "LABEL_LOC"),                   # Taourirt
             ]
         }
    ),

    (
        "Dans le cadre du marché N° 1094/E/DPL/2016, la Direction Planification de l'ONEE - branche eau \"DPL\" a "
        "confié à l’I.C. HYDROSTRUCTURES l’Étude du schéma directeur de renforcement et de sécurisation de "
        "l’AEP de la région d’Errachidia - Tinghir. "
        "L’étude se compose des deux (02) missions suivantes : "
        "Mission I : Analyse de la situation actuelle d’AEP et actualisation du bilan besoins – ressources "
        "/ bilan besoins capacité de transport. "
        "Mission II : Étude des schémas de renforcement et de sécurisation de la production d’eau potable : "
        "Le présent mémoire constitue le rapport définitif de la mission I. Il traite des principaux aspects "
        "suivants : "
        "Généralités sur l’aire d’étude ; "
        "Description des systèmes d’AEP existants ; "
        "Analyse de la situation actuelle de l’assainissement liquide ; "
        "Projection de la demande en eau ; "
        "Analyse de la situation actuelle en matière des ressources en eau souterraines et "
        "superficielles ; "
        "Établissement des bilans besoins - ressources ; "
        "Établissement des bilans besoins - capacités de transport.",
        {
            "entities": [
                (27, 42, "LABEL_MARCHE"),               # 1094/E/DPL/2016
                (119, 134, "LABEL_ORG"),                # HYDROSTRUCTURES
                (222, 232, "LABEL_LOC"),                # Errachidia
                (235, 242, "LABEL_LOC"),                # Tinghir
                (574, 583, "LABEL_VERSION")             # définitif
            ]
        }
    ),

    (
        "La présente étude, confiée par l’ONEP/DPL, au bureau d’études ADI, dans le cadre du "
         "marché n°18/E/DPL/2010, a pour objet la réalisation de l'étude de faisabilité pour le "
         "renforcement d’alimentation en eau potable de la ville de Laayoune par dessalement "
         "d’eau de mer. Cette étude sera réalisée selon les quatre missions suivantes : - - - - "
         "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins  – ressources ;  "
         "Mission II : Identification des sites d’implantation de l’usine de dessalement et "
         "définition des schémas d’adduction ; "
         "Mission III : Evaluation environnementale ; "
         "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque "
         "site, évaluation économique et synthèse des résultats. "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue la "
         "note de synthèse du rapport définitif de la Mission I, relative à l’analyse de la "
         "situation actuelle d'AEP et l’actualisation du bilan besoins – ressources.",
         {
             "entities": [
                 (62, 65, "LABEL_ORG"),                 # ADI
                 (93, 106, "LABEL_MARCHE"),             # 18/E/DPL/2010
                 (228, 236, "LABEL_LOC"),               # Laayoune
                 (851, 860, "LABEL_VERSION")            # définitif
             ]
         }
    ),

    (
        "Le contexte général des ressources en eau de la région de Laayoune est caractérisé par la "
         "rareté et la dégradation de la qualité (niveau de salinité élevé dépassant généralement 4 g/l).  "
         "En effet, le climat de la région est de type aride saharien, tempéré par l'humidité marine, "
         "marqué par la rareté des précipitations, avec des écarts importants dans le temps. La région "
         "est dépourvue de ressources en eau de surface (aucun cours d’eau pérenne) ; les eaux "
         "souterraines constituent la seule ressource en eau potable de la région. "
         "Face à cette situation de pénurie et pour assurer l’AEP de la zone d’études avec une eau "
         "répondant aux normes de qualité et en quantité suffisante, l’ONEE-Branche Eau s’est "
         "engagé, depuis 1995, dans la réalisation des installations de production de l’eau potable par "
         "dessalement d’eau de mer. Ainsi, la région dispose actuellement d’une station de "
         "dessalement de l’eau de mer permettant de contribuer d’une façon significative dans la "
         "satisfaction des besoins d’AEPI. Une infrastructure importante, d’adduction et de distribution "
         "de l’eau potable, a été mise en place. "
         "Pour faire face aux besoins croissants en eau potable de la zone d’études, et en tenant "
         "compte des conditions difficiles d’exploitation des eaux conventionnelles (succession des "
         "années de sécheresse…), l’ONEE-Branche Eau s’est lancé dans de nouveaux projets qui "
         "visent à : "
         "Renforcer  les capacités des ouvrages de production de l’eau potable existants, à partir "
         "de dessalement des eaux de mer ; "
         "Réhabiliter les anciennes installations de production de l’eau potable. "
         "Dans cette optique, l’ONEE-Branche Eau/DPL a confié au bureau d’études ADI, dans le "
         "cadre du marché n°18/E/DPL/2010, la présente étude relative à l'étude de faisabilité pour le "
         "renforcement d’alimentation en eau potable de la ville de Laayoune, par dessalement d’eau "
         "de mer. "
         "Elle est prévue selon les quatre missions suivantes : - - - - "
         "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins  – "
         "ressources ;  "
         "Mission II : Identification des sites d’implantation de l’usine de dessalement et définition "
         "des schémas d’adduction ; "
         "Mission III : Evaluation environnementale ; "
         "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque site, "
         "évaluation économique et synthèse des résultats. "
         "Ce rapport constitue la note de synthèse de la mission II.",
         {
             "entities": [
                 (1637, 1640, "LABEL_ORG"),             # ADI
                 (1668, 1681, "LABEL_MARCHE"),          # 18/E/DPL/2010
                 (1801, 1809, "LABEL_LOC"),             # Laayoune
             ]
         }
    ),

    (
        "Dans le cadre du marché N° 1094/E/DPL/2016, la Direction Planification de l'ONEE - branche eau \"DPL\" a "
        "confié à l’I.C. HYDROSTRUCTURES l’Étude du schéma directeur de renforcement et de sécurisation de "
        "l’AEP de la région d’Errachidia - Tinghir. "
        "L’étude se compose des deux (02) missions suivantes : "
        "Mission I : Analyse de la situation actuelle d’AEP et actualisation du bilan besoins – ressources "
        "/ bilan besoins capacité de transport. "
        "Mission II : Étude des schémas de renforcement et de sécurisation de la production d’eau potable : "
        "Le présent mémoire constitue le rapport définitif de la mission II.",
        {
            "entities": [
                (27, 42, "LABEL_MARCHE"),           # 1094/E/DPL/2016
                (119, 91, "LABEL_ORG"),             # HYDROSTRUCTURES
                (222, 232, "LABEL_LOC"),            # Errachidia
                (235, 242, "LABEL_LOC"),            # Tinghir
                (574, 583, "LABEL_VERSION")         # définitif
            ]
        }
    ),

    (
        "Dans le cadre du marché N° 821/E/DPL/2010, la Direction Planification de l'ONEE - branche eau \"DPL\" a "
        "confié à l’I.C. Groupement GIECO - HYDROSTRUCTURES l’Étude de Faisabilité pour le Renforcement de "
        "l’Alimentation en Eau Potable de la Région de Guercif - Taourirt. La zone d’étude telle que définie par "
        "l’ONEE - branche eau comprend : "
        "Milieu Urbain : - Province de Guercif : ville de Guercif ; - Province de Taourirt : ville de Taourirt, centres d’El Aioun Sidi Mellouk et de Debdou ; "
        "Province de Boulemane : centre d’Outat El Haj. "
        "Milieu Rural : - Province de Guercif : Communes rurales d’Assebbab, Barkine, Houara Ouled Raho, "
        "Lamrija, Saka, Mazguitam, Ouled Bourima, Ras Laksar et Taddart. - Province de Taourirt : Communes rurales d’Ahl Oued Za, Melg El Ouidane, Gteter, El "
        "Atef, Oulad M’hammed, Sidi Ali Belkacem, Sidi Lahsen, Tancherfi, Ain lehjer, Mestegmer et Mechraa Hammadi. "
        "Province de Boulemane : Communes rurales de Fritissa, Tissaf, El Orjane, Ermila et Oulad Ali Youssef. "
        "L’étude se compose des trois (03) missions suivantes : "
        "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – "
        "ressources et besoins – capacité de production et de transport à l’horizon 2035. "
        "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
        "Mission III : Évaluation Environnementale. "
        "Le présent mémoire constitue le rapport définitif de la mission III.",
        {
            "entities": [
                (27, 41, "LABEL_MARCHE"),               # 821/E/DPL/2010
                (129, 134, "LABEL_ORG"),                # GIECO
                (137, 152, "LABEL_ORG"),                # HYDROSTRUCTURES
                (246, 253, "LABEL_LOC"),                # Guercif
                (256, 264, "LABEL_LOC"),                # Taourirt
                (1358, 1367, "LABEL_VERSION")           # définitif
            ]
        }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable (ONEE BRANCHE EAU) – "
         "Direction de la planification (DPL), au bureau d’études NOVEC, dans le cadre du marché "
         "n°184/E/DPL/2011, a pour objet la réalisation de l'étude de faisabilité de renforcement pour l’AEP de la "
         "ville de Meknés, des centres et des douars limitrophes à partir du futur barrage d’Ouljat Soltane. "
         "L’étude est organisée en trois missions comme suit : "
         " Mission I : Analyse de la situation actuelle d’AEP et établissement des bilans besoins-ressources et "
         "besoins-capacités de production et de transport. "
         " Mission II : Etude des schémas d’alimentation en eau potable. "
         " Mission III : Evaluation environnementale "
         "Le présent rapport est relatif à la note de synthèse de la mission II.",
         {
             "entities": [
                 (163, 168, "LABEL_ORG"),             # NOVEC
                 (196, 210, "LABEL_MARCHE"),          # 184/E/DPL/2011
                 (308, 314, "LABEL_LOC"),             # Meknés
             ]
         }
    ),

    (
        "Contexte de l’étude Le contexte général des ressources en eau de la région de Laayoune est caractérisé par la rareté et la dégradation de la qualité (niveau de salinité élevé dépassant généralement 4 g/l). "
         "En effet, le climat de la région est de type aride, marqué par la rareté des précipitations, avec des écarts importants dans le temps. La région est dépourvue de ressources en eau de surface (aucun cours d’eau pérenne) ; "
         "les eaux souterraines constituent la seule ressource en eau potable de la région. "
         "Face à cette situation de pénurie et pour assurer l’AEP de la zone d’études avec une eau répondant aux normes de qualité et en quantité suffisante, l’ONEE-BE1 s’est engagé, depuis 1995, dans la réalisation des installations de production de l’eau potable par dessalement d’eau de mer. "
         "Ainsi, la région dispose actuellement d’une station de dessalement de l’eau de mer permettant de contribuer d’une façon significative dans la satisfaction des besoins d’AEPI. Une infrastructure importante, d’adduction et de distribution de l’eau potable, a été mise en place. "
         "Pour faire face aux besoins croissants en eau potable de la zone d’études, et en tenant compte des conditions difficiles d’exploitation des eaux conventionnelles (succession des années de sécheresse…), l’ONEE-BE s’est lancé dans de nouveaux projets qui visent à : "
         "Renforcer les capacités des ouvrages de production de l’eau potable existants, à partir de dessalement des eaux de mer ; "
         "Réhabiliter les anciennes installations de production de l’eau potable. "
         "Dans cette optique, l’ONEE-Branche Eau/DPL a confié au bureau d’études ADI, dans le cadre du marché n°18/E/DPL/2010, la présente étude relative à l'étude de faisabilité pour le renforcement d’alimentation en eau potable de la ville de Laayoune, par dessalement d’eau de mer. "
         "Consistance de l’étude Cette étude sera réalisée selon les quatre missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins – ressources ; "
         "Mission II : Identification des sites d’implantation de l’usine de dessalement et définition des schémas d’adduction ; "
         "Mission III : Evaluation environnementale ; "
         "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque site, évaluation économique et synthèse des résultats. "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le rapport définitif de la Mission II, relative à l’Identification des sites d’implantation de l’usine de dessalement et la définition des schémas d’adduction. "
         "Il comprend les chapitres suivants : Chapitre I : Rappel des principaux résultats de la mission I ; Chapitre II : Description technique des installations de dessalement d’eau de mer ; Chapitre III : Identification, analyse et choix des sites potentiels ; Chapitre IV : Définition et étude technico-économique des schémas d’adduction.",

         {"entities": [(1598, 1601, "LABEL_ORG"),           # ADI
                       (1629, 1642, "LABEL_MARCHE"),        # 18/E/DPL/2010
                       (1762, 1770, "LABEL_LOC"),           # Laayoune
                       (2379, 2388, "LABEL_VERSION")]       # définitif
         }
    ),

    (
        "Le contexte général des ressources en eau de la région de Laayoune est caractérisé par la rareté et la dégradation de la qualité (niveau de salinité élevé dépassant généralement 4 g/l). "
         "En effet, le climat de la région est de type aride, marqué par la rareté des précipitations, avec des écarts importants dans le temps. La région est dépourvue de ressources en eau de surface (aucun cours d’eau pérenne) ; "
         "les eaux souterraines constituent la seule ressource en eau potable de la région. "
         "Face à cette situation de pénurie et pour assuer l’AEP de la zone d’études avec une eau répondant aux normes de qualité et en quantité suffisante, l’ONEP s’est engagé, depuis 1995, dans la réalisation des installations de production de l’eau potable par dessalement d’eau de mer. "
         "Ainsi, la région dispose actuellement d’une station de dessalement de l’eau de mer permettant de contribuer d’une façon significative dans la satisfaction des besoins d’AEPI. Une infrastructure importante, d’adduction et de distribution de l’eau potable, a été mise en place. "
         "Pour faire face aux besoins croissants en eau potable de la zone d’études, et en tenant compte des conditions difficiles d’exploitation des eaux conventionnelles (succession des années de sécheresse…), l’ONEP s’est lancé dans de nouveaux projets qui visent à : "
         "Renforcer les capacités des ouvrages de production de l’eau potable existants, à partir de dessalement des eaux de mer ; "
         "Réhabiliter les anciennes installations de production de l’eau potable. "
         "Dans cette optique, l’ONEP/DPL a confié au bureau d’études ADI, dans le cadre du marché n°18/E/DPL/2010, la présente étude relative à l'étude de faisabilité pour le renforcement d’alimentaton en eau potable de la ville de Laayoune, par dessalement d’eau de mer. "
         "Consistance de l’étude Cette étude sera réalisée selon les quatre missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins – ressources ; "
         "Mission II : Identification des sites d’implantation de l’usine de dessalement et définition des schémas d’adduction ; "
         "Mission III : Evaluation environnementale ; "
         "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque site, évaluation économique et synthèse des résultats. "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le rapport définitif de la Mission I, relative à l’Analyse de la Situation Actuelle d'AEP et à l’Actualisation du Bilan Besoins – Ressources. "
         "Il comprend les chapitres suivants : Chapitre I : Données générales sur la zone d’étude ; Chapitre II : Situation actuelle de l’AEP dans la zone d’étude ; Chapitre III : Situation des ressources en eau ; Chapitre IV : Etude de la demande en eau de la zone du projet ; Chapitre V : Bilans besoins-ressources et besoins-capacité de transit ; Chapitre VI : Conclusion.",

        {"entities": [(1558, 1561, "LABEL_ORG"),                # ADI
                      (1589, 1602, "LABEL_MARCHE"),             # 18/E/DPL/2010
                      (1721, 1729, "LABEL_LOC"),                # Laayoune
                      (2338, 2347, "LABEL_VERSION")]            # définitif
         }
    ),

    (
        "Dans le cadre du marché N° 183/E/DPL/2011, la Direction Planification de l'ONEE-branche eau \"DPL\" a "
        "confié à l’I.C. Groupement GIECO - HYDROSTRUCTURES l’Étude de Renforcement de l’a Production d’Eau "
        "Potable de la ville de Laattaouia, des centres et douars avoisinants. La zone d’étude définie par l’ONEE "
        "branche eau comprend : "
        "Milieu Urbain : - Province d’El Kelaâ des Sraghna : Municipalités de Laattaouia, Sidi Rahhal et Tamallalt. "
        "Milieu Rural : - Province d’El Kelaâ des Sraghna : Communes rurales de : Bouya Omar, Choara, Dzouz, "
        "Fraita, Laatamna, Laattaouia Ech-chaibia, Ouargui, Oulad Aarrad, Jouala, Jbiel,  Zemrane "
        "et Zemrane Charqia. - - Province de Rhamna: Communes rurales de Ras Ain Rhamna, Jaidate, Tlauh et Akarma "
        "Province d’Al Haouz: Communes rurales de Tazart et Touama. "
        "L’étude se compose des trois (03) missions suivantes : "
        "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – "
        "ressources et besoins – capacité de production et de transport. "
        "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
        "Mission III : Évaluation Environnementale. "
        "Le présent mémoire constitue le rapport définitif de la mission III.",
        {
            "entities": [
                (27, 41, "LABEL_MARCHE"),               # 183/E/DPL/2011
                (127, 132, "LABEL_ORG"),                # GIECO
                (135, 150, "LABEL_ORG"),                # HYDROSTRUCTURES
                (222, 232, "LABEL_LOC"),                # Laattaouia
                (1141, 1150, "LABEL_VERSION")           # définitif
            ]
        }
    ),

    (
        "Contexte de l’étude Le contexte général des ressources en eau de la région de Laayoune est caractérisé par la rareté et la dégradation de la qualité (niveau de salinité élevé, dépassant généralement 4 g/l). "
         "En effet, le climat de la région est de type aride, marqué par la rareté des précipitations, avec des écarts importants dans le temps. La région est dépourvue de ressources en eau de surface (aucun cours d’eau pérenne) ; "
         "les eaux souterraines constituent la seule ressource en eau potable de la région. "
         "Face à cette situation de pénurie et pour assurer l’AEP de la zone d’études avec une eau répondant aux normes de qualité et en quantité suffisante, l’ONEE-Branche Eau s’est engagé, depuis 1995, dans la réalisation des installations de production de l’eau potable par dessalement d’eau de mer. "
         "Ainsi, la région dispose actuellement d’une station de dessalement de l’eau de mer permettant de contribuer, d’une façon significative, dans la satisfaction des besoins d’AEPI. Une infrastructure importante, d’adduction et de distribution de l’eau potable, a été mise en place. "
         "Pour faire face aux besoins croissants en eau potable de la zone d’études, et en tenant compte des conditions difficiles d’exploitation des eaux conventionnelles (succession des années de sécheresse…), l’ONEE-Branche Eau s’est lancé dans de nouveaux projets qui visent à : "
         "Renforcer les capacités des ouvrages existants de production de l’eau potable, à partir de dessalement des eaux de mer ; "
         "Réhabiliter les anciennes installations de production de l’eau potable. "
         "Dans cette optique, l’ONEE-Branche Eau/DPL a confié au bureau d’études ADI, dans le cadre du marché n°18/E/DPL/2010, la présente étude relative à l'étude de faisabilité pour le renforcement d’alimentation en eau potable de la ville de Laayoune, par dessalement d’eau de mer. "
         "Cette étude est prévue selon les quatre missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d'AEP et actualisation du bilan besoins – ressources ; "
         "Mission II : Identification des sites d’implantation de l’usine de dessalement et définition des schémas d’adduction ; "
         "Mission III : Evaluation environnementale ; "
         "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque site, évaluation économique et synthèse des résultats. "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le rapport définitif de la Mission III, relative à l’évaluation environnementale du projet de renforcement de la production d’eau potable de la zone d’étude. "
         "Il comprend les chapitres suivants : Chapitre I : Cadre juridique et institutionnel ; Chapitre II : Description du projet ; Chapitre III : Description du milieu ; Chapitre IV : Comparaison environnementale des variantes des sites de la station de dessalement ; Chapitre V : Identification et évaluation des impacts potentiels du projet ; Chapitre VI : Identification des mesures d’atténuation et de compensation des impacts négatifs ; Chapitre VII : Programme de surveillance et de suivi environnemental.",

         {"entities": [(1618, 1621, "LABEL_ORG"),                 # ADI
                       (1649, 1662, "LABEL_MARCHE"),              # 18/E/DPL/2010
                       (1782, 1790, "LABEL_LOC"),                 # Laayoune
                       (2373, 2382, "LABEL_VERSION"),]            # définitif
         }
    ),
    (
        "Dans le cadre du marché n°1165/E/DPL/2008, l’Office National de L’électricité et de "
        "l’eau Potable (ONEE Branche Eau) a confié au groupement d’Ingénieurs Conseils "
        "CID/AYESA, l’étude de faisabilité pour le renforcement de l’alimentation en eau potable "
        "par ressources conventionnelles ou dessalement d’eau de mer des villes, centres et "
        "communes rurales de la côte atlantique situés entre Kénitra et Safi. "
        "L’aire de l’étude s’étend sur une grande partie de la côte atlantique et comprend en "
        "particulier les principales villes de Kénitra, Salé, Rabat, Casablanca, Mohammedia, "
        "Settat, Berrechid, El Jadida et Safi ainsi que les villes, centres et douars dont "
        "l’alimentation en eau potable est liée ou susceptible d’être liée aux systèmes existants "
        "ou projetés dans cette zone.  "
        "Les principales prestations à réaliser dans le cadre de cette étude sont : "
        "• Actualisation du bilan besoins-ressources et du bilan besoins-capacité de "
        "production et de transport; "
        "• Identification et étude des différents scénarios de renforcement et de "
        "sécurisation d’AEP dans la zone d’étude jusqu’à l’horizon 2035; "
        "• Évaluation environnementale des projets proposés.  "
        "L’étude comprend les quatre missions suivantes : "
        "• Mission I : Actualisation des bilans besoins-ressources et besoins-capacités "
        "de production et de transport ; "
        "• Mission III : Étude des schémas de renforcement et de sécurisation de l’AEPI "
        "de la zone de la Côte Atlantique située entre les villes de Kénitra et "
        "Safi ; "
        "• Mission III : Évaluation environnementale ; "
        "• Mission IV : Synthèse.  "
        "Le dossier de la Mission II a été scindé en deux volumes : "
        "Volume   1 : Mobilisation des ressources en eau  "
        "Volume 2 : Renforcement des capacités de production et de transport des "
        "installations existantes ; "
        "Le présent document constitue la version définitive du volume 1 de la mission II.",
        {
            "entities": [
                (26, 41, "LABEL_MARCHE"),               # 1165/E/DPL/2008
                (162, 165, "LABEL_ORG"),                # CID
                (166, 171, "LABEL_ORG"),                # AYESA
                (385, 392, "LABEL_LOC"),                # Kénitra
                (396, 400, "LABEL_LOC"),                # Safi
                (1778, 1788, "LABEL_VERSION"),          # définitive
            ]
        }
    ),

    (
         "Dans le cadre du Marché n°625/E/DPS/2007, l’Office National de l’Eau Potable (ONEP) a confié au groupement SCET-SCOM et HIDROPROJECTO l’étude d’Alimentation en Eau Potable de la ville de MARRAKECH, des centres et douars limitrophes a partir de barrage AL MASSIRA. "
         "La présente étude se déroulera en cinq missions : "
         "MISSION I : ETUDE DE FACTIBILITE- Sous -Mission I-1 : Description des systèmes d'AEP actuels et actualisation des Bilans Ressources Besoins - Sous -Mission I.2 : Etude des Schémas d’Alimentation en Eau Potable "
         "MISSION II – EVALUATION ENVIRONNEMENTALE "
         "MISSION III : ETUDE D’AVANT PROJET SOMMAIRE  \"APS\"- APS Prise d’eau - APS Adduction "
         "MISSION IV : ETUDE D’AVANT PROJET DETAILLE  \"APD\"- APD de la prise d’eau brute  - APD de la station de traitement - APD des stations de pompage - APD des conduites d’adduction - APD de télégestion "
         "MISSION V – DOSSIERS DE CONSULTATION DES ENTREPRISES "
         "Le présent rapport constitue le rapport définitif de la sous- mission I.2.",

         {"entities": [(26, 40, "LABEL_MARCHE"),                 # 625/E/DPS/2007
                       (107, 116, "LABEL_ORG"),                  # SCET-SCOM
                       (120, 133, "LABEL_ORG"),                  # HIDROPROJECTO
                       (187, 196, "LABEL_LOC"),                  # MARRAKECH
                       (939, 948, "LABEL_VERSION"),]             # définitif
        }
    ),

        ("Dans le cadre du Marché n.° 625/E/DPS/2007, l’Office National de l’Eau Potable (ONEP) a confié au groupement SCET-SCOM et HIDROPROJECTO l’étude d’Alimentation en Eau Potable de la ville de MARRAKECH, des centres et douars limitrophes a partir du barrage AL MASSIRA. "
         "La présente étude se déroulera en cinq missions : "
         "MISSION I : ETUDE DE FACTIBILITE "
         "Sous-Mission I.1 : Description des systèmes d'AEP actuels et actualisation des Bilans Ressources Besoins. "
         "Sous-mission I.2 : Etude des Schémas d’Alimentation en Eau Potable. "
         "MISSION II – EVALUATION ENVIRONNEMENTALE "
         "MISSION III : ETUDE D’AVANT PROJET SOMMAIRE  \"APS\" "
         "Sous-Mission III.1 : APS Prise d’eau. "
         "Sous-Mission III.2 : APS Adduction. "
         "MISSION IV : ETUDE D’AVANT PROJET DETAILLE  \"APD\" "
         "APD de la prise d’eau brute. "
         "APD de la station de traitement. "
         "APD des stations de pompage. "
         "APD des conduites d’adduction "
         "APD de télégestion "
         "MISSION V – DOSSIERS DE CONSULTATION DES ENTREPRISES "
         "Le présent rapport constitue le rapport préliminaire de la Sous-Mission I.2, concernant le volet de la prise d’eau.",

         {"entities": [(28, 42, "LABEL_MARCHE"),                # 625/E/DPS/2007
                       (109, 118, "LABEL_ORG"),                 # SCET-SCOM
                       (122, 135, "LABEL_ORG"),                 # HIDROPROJECTO
                       (189, 198, "LABEL_LOC"),                 # MARRAKECH
                       (974, 220, "LABEL_VERSION")]             # préliminaire
         }
    ),

    (
        "Dans le cadre du marché N° 820/E/DPL/2008, la Direction Planification de l'ONEP \"DPL\" a confié à l’I.C. Groupement GIECO - HYDROSTRUCTURES l’Étude de faisabilité du renforcement et de sécurisation de l’AEP de la région de Ouezzane-Jorf El Melha. "
         "La zone d’étude définie par l’ONEP comprend : "
         "Milieu Urbain : - Province de Ouezzane : ville de Ouezzane et centres de Brikcha, Zoumi et Moqrisset ; - Province de Sidi Kacem : municipalités de Jorf El Melha et Had Kourt et centre d’Aïn Dorij. "
         "Milieu Rural : - Système d’AEP de Jorf El Melha : Lamrabih ; - Système d’AEP Adductions Bouagba et Oued El Makhazine : CR d’Aïn Beida, Aïn Dfali, Arbaoua, Asjen, Bni Oual, Bni Qolla, Brikcha, Kariat Ben Aouda, Masmouda, Moulay Abdelkader, Mzefroune, Oued El Makhazine, Sidi Ahmed Ben Aissa, Sidi Ameur El Hadi et Sidi Redouane ; "
         "Système d’AEP Adduction Barrage Al Wahda : CR de Bni Ahmed Cherkia, Bni Ahmed Gharbia, Bni Faghloum, Kallat Bouqorra, Lamjaara, Mansoura, Moqrisset, Ounnana, Sidi Ahmed Cherif, Sidi Bousber, Teroual, Zghira, Zoumi. "
         "Système d’AEP de Had Kourt : CR de Nouirat, Ouled Nouel, Sidi Azzouz et Sidi Mohamed Chelh. "
         "L’étude se compose des trois (03) missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – ressources et besoins – capacité de production et de transport. "
         "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
         "Mission III : Évaluation Environnementale. "
         "Le présent mémoire constitue le rapport provisoire de la mission I, il traite des principaux aspects suivants : "
         "Généralités sur l’aire d’étude ; Description des systèmes d’AEP existants ; Analyse de la situation actuelle de l’assainissement liquide ; Projection de la demande en eau ; Analyse de la situation actuelle en matière des ressources en eau souterraines et superficielles ; Établissement des bilans besoins – ressources ; Établissement des bilans besoins – capacités de transport.",

         {"entities": [(27, 41, "LABEL_MARCHE"),                # 820/E/DPL/2008
                       (115, 120, "LABEL_ORG"),                 # GIECO
                       (123, 138, "LABEL_ORG"),                 # HYDROSTRUCTURES
                       (222, 244, "LABEL_LOC"),                 # Ouezzane-Jorf El Melha
                       (1479, 1489, "LABEL_VERSION")]           # provisoire
    }
    ),

    (
        "Dans le cadre du marché N° 820/E/DPL/2010, la Direction Planification de l'ONEE - branche eau \"DPL\" a confié à l’I.C. Groupement GIECO - HYDROSTRUCTURES l’Étude de faisabilité du renforcement et de sécurisation de l’AEP de la région d’Ouezzane-Jorf El Melha. "
         "La zone d’étude définie par l’ONEE - branche eau comprend : "
         "Milieu Urbain : - Province d’Ouezzane : ville d’Ouezzane et centres d’Aïn Dorij, Brikcha, Zoumi et Moqrisset ; - Province de Sidi Kacem : municipalités de Jorf El Melha et Had Kourt et le centre d’Aïn Dfali. "
         "Milieu Rural : - Système d’AEP de Jorf El Melha : CR Lamrabih et Taoughilt. - Système d’AEP Adductions Bouagba et Oued El Makhazine : CR de Aïn Beida, Aïn Dfali, Arbaoua, Asjen, Bni Oual, Bni Qolla, Brikcha, Kariat Ben Aouda, Masmouda, Moulay Abdelkader, Mzefroune, Oued El Makhazine, Sidi Ahmed Ben Aissa, Sidi Ameur El Hadi et Sidi Redouane. "
         "- Système d’AEP Adduction Barrage Al Wahda : CR de Bni Ahmed Cherkia, Bni Ahmed Gharbia, Bni Faghloum, Kalaat Bouqorra, Lamjaara, Mansoura, Moqrisset, Ounnana, Sidi Ahmed Cherif, Sidi Bousber, Teroual, Zghira, Zoumi, Bab Berred, Tamorot et Oued Malha. "
         "- Système d’AEP de Had Kourt : CR de Nouirate, Oulad Nouel, Sidi Azzouz, My Abdelkader et Sidi M’Hamed Chelh. "
         "- Système d’AEP de Aïn Dfali :CR de Aïn Dfali, Bni Oual et Sidi Azzouz. "
         "L’étude se compose des trois (03) missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – ressources et besoins – capacité de production et de transport. "
         "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
         "Mission III : Évaluation Environnementale. "
         "Le présent dossier constitue le rapport définitif de la mission II.",

         {"entities": [(27, 41, "LABEL_MARCHE"),                    # 820/E/DPL/2010
                       (129, 134, "LABEL_ORG"),                     # GIECO
                       (137, 152, "LABEL_ORG"),                     # HYDROSTRUCTURES
                       (235, 257, "LABEL_LOC"),                     # Ouezzane-Jorf El Melha
                       (1659, 1668, "LABEL_VERSION")]               # définitif
    }
    ),

    (
        "Dans le cadre du Marché n°625/E/DPS/2007, l’Office National de l’Eau Potable (ONEP) a confié au groupement SCET-SCOM et HIDROPROJECTO l’étude d’Alimentation en Eau Potable de la ville de MARRAKECH, des centres et douars limitrophes a partir de barrage AL MASSIRA. "
         "La présente étude se déroulera en cinq missions : "
         "MISSION I : ETUDE DE FACTIBILITE- Sous -Mission I-1 : Description des systèmes d'AEP actuels et actualisation des Bilans Ressources Besoins - Sous -Mission I.2 : Etude des Schémas d’Alimentation en Eau Potable "
         "MISSION II – EVALUATION ENVIRONNEMENTALE "
         "MISSION III : ETUDE D’AVANT PROJET SOMMAIRE  \"APS\"- APS Prise d’eau - APS Adduction "
         "MISSION IV : ETUDE D’AVANT PROJET DETAILLE  \"APD\"- APD de la prise d’eau brute  - APD de la station de traitement - APD des stations de pompage - APD des conduites d’adduction - APD de télégestion "
         "MISSION V – DOSSIERS DE CONSULTATION DES ENTREPRISES "
         "Le présent rapport constitue le rapport définitif de la sous- mission I.2.",

         {"entities": [(26, 40, "LABEL_MARCHE"),                    # 625/E/DPS/2007
                       (107, 116, "LABEL_ORG"),                     # SCET-SCOM
                       (120, 133, "LABEL_ORG"),                     # HIDROPROJECTO
                       (187, 196, "LABEL_LOC"),                     # MARRAKECH
                       (939, 948, "LABEL_VERSION")]                 # définitif
          }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et l’Eau Potable – Branche "
         "Eau (ONEE-BO), au bureau d’études ADI, dans le cadre du marché n°1129 /E/DPL/2014, a "
         "pour objet la réalisation de l'étude du Plan Directeur d’AEP des Populations Urbaines et "
         "Rurales de la zone Nord du Bassin hydraulique de la Moulouya. Cette étude est prévue "
         "selon les trois  missions suivantes : "
         " Mission I : Etude des besoins en eau potable jusqu’à l’Horizon 2035 ; "
         " Mission II : Recensement et analyse des ressources utilisées et/ou affectées à "
         "l’eau potable et Bilan besoins ressources ; "
         " Mission III : Plan directeur d’alimentation en eau potable de la zone d’étude. "
         "Le présent rapport constitue la note de synthèse de la mission II.",
         {
             "entities": [
                 (127, 130, "LABEL_ORG"),                # ADI
                 (158, 174, "LABEL_MARCHE"),             # 1129 /E/DPL/2014
                 (319, 327, "LABEL_LOC"),                # Moulouya
             ]
         }
    ),

    (
        "Dans le cadre du marché N° 820/E/DPL/2010, la Direction Planification de l'ONEE - branche eau \"DPL\" a confié à l’I.C. Groupement GIECO - HYDROSTRUCTURES l’Étude de faisabilité du renforcement et de sécurisation de l’AEP de la région d’Ouezzane-Jorf El Melha. "
         "La zone d’étude définie par l’ONEE - branche eau comprend : "
         "Milieu Urbain : - Province d’Ouezzane : ville d’Ouezzane et centres d’Aïn Dorij, Brikcha, Zoumi et Moqrisset ; "
         "Province de Sidi Kacem : municipalités de Jorf El Melha et Had Kourt et le centre d’Aïn Dfali. "
         "Milieu Rural : - Système d’AEP de Jorf El Melha : CR Lamrabih et Taoughilt. "
         "Système d’AEP Adductions Bouagba et Oued El Makhazine : CR de Aïn Beida, Aïn Dfali, Arbaoua, Asjen, Bni Oual, Bni Qolla, Brikcha, Kariat Ben Aouda, Masmouda, Moulay Abdelkader, Mzefroune, Oued El Makhazine, Sidi Ahmed Ben Aissa, Sidi Ameur El Hadi et Sidi Redouane. "
         "Système d’AEP Adduction Barrage Al Wahda : CR de Bni Ahmed Cherkia, Bni Ahmed Gharbia, Bni Faghloum, Kalaat Bouqorra, Lamjaara, Mansoura, Moqrisset, Ounnana, Sidi Ahmed Cherif, Sidi Bousber, Teroual, Zghira, Zoumi, Bab Berred, Tamorot et Oued Malha. "
         "Système d’AEP de Had Kourt : CR de Nouirate, Oulad Nouel, Sidi Azzouz, My Abdelkader et Sidi M’Hamed Chelh. "
         "Système d’AEP de Aïn Dfali : CR de Aïn Dfali, Bni Oual et Sidi Azzouz. "
         "L’étude se compose des trois (03) missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – ressources et besoins – capacité de production et de transport. "
         "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
         "Mission III : Évaluation Environnementale. "
         "Le présent mémoire constitue le rapport définitif de la mission III.",

         {"entities": [(27, 41, "LABEL_MARCHE"),                # 820/E/DPL/2010
                       (129, 134, "LABEL_ORG"),                 # GIECO
                       (137, 152, "LABEL_ORG"),                 # HYDROSTRUCTURES
                       (235, 257, "LABEL_LOC"),                 # Ouezzane-Jorf El Melha
                       (1650, 1659, "LABEL_VERSION")]           # définitif
          }
    ),

    (
        "Dans le cadre du marché N° 820/E/DPL/2010, la Direction Planification de l'ONEE - branche eau "
        "\"DPL\" a confié à l’I.C. Groupement GIECO - HYDROSTRUCTURES l’Étude de faisabilité du "
        "renforcement et de sécurisation de l’AEP de la région d’Ouezzane-Jorf El Melha. La zone d’étude "
        "définie par l’ONEE - branche eau comprend : "
        "Milieu Urbain : - Province d’Ouezzane : ville d’Ouezzane et centres d’Aïn Dorij, Brikcha, Zoumi et "
        "Moqrisset ; - Province de Sidi Kacem : municipalités de Jorf El Melha et Had Kourt et le centre d’Aïn "
        "Dfali. "
        "Milieu Rural : - Système d’AEP de Jorf El Melha : CR Lamrabih et Taoughilt. - Système d’AEP "
        "Adductions Bouagba et Oued El Makhazine : CR de Aïn Beida, Aïn Dfali, Arbaoua, Asjen, Bni Oual, "
        "Bni Qolla, Brikcha, Kariat Ben Aouda, Masmouda, Moulay Abdelkader, Mzefroune, Oued El Makhazine, "
        "Sidi Ahmed Ben Aissa, Sidi Ameur El Hadi et Sidi Redouane. - Système d’AEP Adduction Barrage "
        "Al Wahda : CR de Bni Ahmed Cherkia, Bni Ahmed Gharbia, Bni Faghloum, Kalaat Bouqorra, Lamjaara, "
        "Mansoura, Moqrisset, Ounnana, Sidi Ahmed Cherif, Sidi Bousber, Teroual, Zghira, Zoumi, Bab Berred, "
        "Tamorot et Oued Malha. - Système d’AEP de Had Kourt : CR de Nouirate, Oulad Nouel, Sidi Azzouz, "
        "My Abdelkader et Sidi M’Hamed Chelh. - Système d’AEP de  Aïn Dfali :CR de Aïn Dfali,  Bni Oual et "
        "Sidi Azzouz. "
        "L’étude se compose des trois (03) missions suivantes : "
        "Mission I : Analyse de la Situation Actuelle d’AEP et Établissement des bilans besoins – ressources "
        "et besoins – capacité de production et de transport. "
        "Mission II : Étude des Schémas d'Alimentation en eau Potable : "
        "Mission III : Évaluation Environnementale. "
        "Le présent mémoire constitue la note de synthèse relative à la mission II.",
        {
            "entities": [
                (27, 41, "LABEL_MARCHE"),               # 820/E/DPL/2010
                (129, 134, "LABEL_ORG"),                # GIECO
                (137, 152, "LABEL_ORG"),                # HYDROSTRUCTURES
                (235, 257, "LABEL_LOC"),                # Ouezzane-Jorf El Melha
            ]
        }
    ),

    (
        "Dans le cadre du marché n°270/E/DPL/2019, la Direction de Planification (DPL), de l’Office National de l’Electricité et de l’Eau Potable- Branche Eau (ONEE-BO), a confié au bureau d’Etudes ADI, la réalisation de l’étude du schéma directeur de renforcement et de sécurisation de l’AEP de la ville de Safi et sa région. "
         "Cette étude est prévue selon les trois missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d’AEP et actualisation du Bilan Besoins Ressources ; "
         "Mission II : Etude des Schémas d’Alimentation en Eau Potable ; "
         "Mission III : Evaluation Environnementale. "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le rapport provisoire de la mission III, relative à l’Evaluation Environnementale du projet de renforcement et de sécurisation de l’AEP de la ville de Safi et sa région. "
         "Il comprend les 6 chapitres suivants : "
         "Chapitre 1 : Cadre juridique et institutionnel ; "
         "Chapitre 2 : Justification et description du projet ; "
         "Chapitre 3 : Description des milieux physique, biologique et humain ; "
         "Chapitre 4 : Identification et évaluation des impacts potentiels du projet ; "
         "Chapitre 5 : Identification des mesures d’atténuation et de compensation des impacts négatifs ; "
         "Chapitre 6 : Programme de surveillance et de suivi environnemental.",

         {"entities": [(26, 14, "LABEL_MARCHE"),                # 270/E/DPL/2019
                       (189, 192, "LABEL_ORG"),                 # ADI
                       (299, 303, "LABEL_LOC"),                 # Safi
                       (674, 684, "LABEL_VERSION")]             # provisoire
         }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable – Branche Eau (ONEE-BO) – Direction Planification, au bureau d’études ADI, dans le cadre du marché n°270/E/DPL/2019, a pour objet la réalisation de l'étude du schéma directeur de renforcement et de sécurisation de l’AEP de la ville de Safi et sa région. "
         "Cette étude est prévue selon les trois missions suivantes : "
         "Mission I : besoins ressources ; "
         "Mission II : Analyse de la Situation Actuelle d'AEP et actualisation du bilan Etude des Schémas d'Alimentation en Eau Potable ; "
         "Mission III : Evaluation environnementale. "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le rapport définitif de la Mission I ; il comprend les chapitres suivants : "
         "Chapitre I : Présentation générale de la zone d’études ; "
         "Chapitre II : Description des systèmes actuels d'AEP de la zone d’études ; "
         "Chapitre III : Recensement et analyse des ressources en eau affectées à l'AEPI ; "
         "Chapitre IV : Etude de la demande en eau ; "
         "Chapitre V : Bilan Besoins - ressources et bilan besoins – capacité de production et de transport.",

         {"entities": [(156, 159, "LABEL_ORG"),                     # ADI
                       (187, 201, "LABEL_MARCHE"),                  # 270/E/DPL/2019
                       (321, 325, "LABEL_LOC"),                     # Safi
                       (696, 705, "LABEL_VERSION")]                 # définitif
          }
    ),

    (
        "Dans le cadre du marché n°985/E/DPL/2017, l’Office National de l’Electricité et de l’Eau "
        "Potable – Branche Eau (ONEE-BO) a confié à l’Ingénieur Conseil CID, l’étude de faisabilité pour "
        "le renforcement et la sécurisation d’AEP des localités urbaines et rurales de la région "
        "d’Oulmes-Rommani à partir du futur barrage de Tiddas. "
        "La zone d’étude se situe dans la région de Rabat – Salé – Kénitra et constitue particulièrement "
        "la partie sud de la province de Khémisset. Elle comprend la Municipalité de Rommani, les "
        "centres urbains de Maaziz, Oulmes, Tiddas et Ezzhiliga ainsi que 15 communes rurales relevant "
        "des cercles Khémisset, Oulmes et Rommani. "
        "L’étude devra aboutir à la définition des schémas d’adduction et de production d’eau potable "
        "en vue de satisfaire les besoins en eau potable de la zone d’étude à court, moyen et long "
        "termes tout en tenant compte des aspects liés à la sécurisation moyennant des solutions "
        "d’interconnexion entre les systèmes d’AEP existants ou projetés à partir des ressources en eau "
        "mobilisées et mobilisables superficielles et souterraines. "
        "Les principales prestations à réaliser dans le cadre de cette étude sont : - - - - "
        "Analyse de la situation actuelle d’AEP ; "
        "Bilan besoins – ressources ; "
        "Bilan besoins – capacité de production et de transport des ouvrages d’AEP ; "
        "Identification et étude des différentes variantes de renforcement et/ou de "
        "sécurisation de l’AEP. "
        "L’étude sera réalisée selon les deux missions suivantes : - - "
        "Mission I :   Analyse de la situation actuelle d’AEP et établissement des bilans besoins – ressources et besoins – capacité de production et de transport à "
        "l’horizon de 2040 ; "
        "Mission II :      "
        "Etude des schémas d’alimentation en eau potable. "
        "Le présent document concerne la note de synthèse de la mission I.",
        {
            "entities": [
                (26, 40, "LABEL_MARCHE"),               # 985/E/DPL/2017
                (152, 155, "LABEL_ORG"),                # CID
                (275, 281, "LABEL_LOC"),                # Oulmes
                (282, 289, "LABEL_LOC"),                # Rommani

            ]
        }
    ),

    (
        "Dans le cadre du marché N° 386/E/DPL/2019, la Direction Planification de l'ONEE - branche eau \"DPL\" a confié à l’I.C. CID l’Étude du Schéma Directeur de Production d’eau Potable des Localités Urbaines et Rurales de la Province de Sefrou. "
         "L’étude se compose des deux (02) missions suivantes : "
         "Mission I : Analyse de la situation actuelle d’AEP et actualisation du bilan besoins – ressources. "
         "Mission II : Étude des schémas d’alimentation en eau potable : "
         "Le présent mémoire constitue le rapport définitif de la mission I. Il traite des principaux aspects suivants : "
         "Données Générales sur l’aire d’étude ; "
         "Description des systèmes d’AEP existants ; "
         "Projection démographiques et de la demande en eau ; "
         "Analyse de la situation actuelle en matière des ressources en eau souterraines et superficielles ; "
         "Établissement des bilans besoins - ressources ; "
         "Établissement des bilans besoins – capacité de production ; "
         "Établissement des bilans besoins - capacité de transport.",

         {"entities": [(27, 41, "LABEL_MARCHE"),                   # 386/E/DPL/2019
                       (118, 121, "LABEL_ORG"),                    # CID
                       (230, 236, "LABEL_LOC"),                    # Sefrou
                       (494, 503, "LABEL_VERSION")]                # définitif
          }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable – Branche Eau "
        "(ONEE-BO) – Direction Planification, au bureau d’études ADI, dans le cadre du marché "
        "n°270/E/DPL/2019, a pour objet la réalisation de l'étude du schéma directeur de "
        "renforcement et de sécurisation de l’AEP de la ville de Safi et sa région. Cette étude est "
        "prévue selon les trois missions suivantes : "
        "Mission I : besoins ressources ; "
        "Mission II : Analyse de la Situation Actuelle d'AEP et actualisation du bilan "
        "Etude des Schémas d'Alimentation en Eau Potable ; "
        "Mission III : Evaluation environnementale. "
        "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le rapport de "
        "synthèse de la mission I.",
        {
            "entities": [
                (156, 159, "LABEL_ORG"),                # ADI
                (187, 201, "LABEL_MARCHE"),             # 270/E/DPL/2019
                (321, 325, "LABEL_LOC"),                # Safi
            ]
        }
    ),

    (
        "Dans le cadre du marché N° 386/E/DPL/2019, la Direction Planification de l'ONEE - branche eau "
        "\"DPL\" a confié à l’I.C. CID l’Étude du Schéma Directeur de Production d’eau Potable des Localités "
        "Urbaines et Rurales de la Province de Sefrou.  "
        "L’étude se compose des deux (02) missions suivantes : "
        "Mission I : Analyse de la situation actuelle d’AEP et actualisation du bilan besoins – ressources ;  "
        "Mission II :    Étude des schémas d’alimentation en eau potable. "
        "Le présent rapport constitue la note de synthèse de la mission I.",
        {
            "entities": [
                (27, 41, "LABEL_MARCHE"),                   # 386/E/DPL/2019
                (118, 121, "LABEL_ORG"),                    # CID
                (230, 236, "LABEL_LOC"),                    # Sefrou
            ]
        }
    ),

    (
        "Dans le cadre du marché N° 386/E/DPL/2019, la Direction Planification de l'ONEE - branche eau \"DPL\" a confié à l’I.C. CID l’Étude du Schéma Directeur de Production d’eau Potable des Localités Urbaines et Rurales de la Province de Sefrou. "
         "L’étude se compose des deux (02) missions suivantes : "
         "Mission I : Analyse de la situation actuelle d’AEP et actualisation du bilan besoins – ressources. "
         "Mission II : Étude des schémas d’alimentation en eau potable. "
         "Le présent mémoire constitue le rapport définitif de la mission II. Il traite des principaux aspects suivants : "
         "Données générales sur l’aire d’étude ; "
         "Description des systèmes d’AEP existants ; "
         "Projection démographiques et de la demande en eau ; "
         "Analyse de la situation actuelle en matière des ressources en eau souterraines et superficielles ; "
         "Bilans besoins – ressources ; "
         "Schémas d’alimentation en eau potable ; "
         "Conception et dimensionnement des ouvrages ; "
         "Coût d’investissement et comparaison technico-économique des variantes.",

         {"entities": [(27, 41, "LABEL_MARCHE"),                    # 386/E/DPL/2019
                       (118, 121, "LABEL_ORG"),                     # CID
                       (230, 236, "LABEL_LOC"),                     # Sefrou
                       (493, 502, "LABEL_VERSION")]                 # définitif
          }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable – Branche Eau (ONEE-BO) – Direction Planification, au bureau d’études ADI, dans le cadre du marché n°986/E/DPL/2014, a pour objet la réalisation de l'étude de faisabilité de renforcement et de sécurisation de l’AEP des localités urbaines et rurales de la région de Sidi Kacem – Sidi Slimane. "
         "Cette étude est prévue selon les deux missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d'AEP et établissement du bilan besoins ressources à l’horizon 2040 et besoins – capacités de production et de transport ; "
         "Mission II : Etude des Schémas d'Alimentation en Eau Potable ; "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le rapport définitif de la Mission I ; il comprend les chapitres suivants : "
         "Chapitre I : Présentation générale de la zone d’études ; "
         "Chapitre II : Description des systèmes actuels d'AEP de la zone d’études ; "
         "Chapitre III : Recensement et analyse des ressources en eau affectées à l'AEPI ; "
         "Chapitre IV : Etude de la demande en eau ; "
         "Chapitre V : Bilan Besoins - ressources et bilan besoins – capacité de production et de transport.",

         {"entities": [(156, 159, "LABEL_ORG"),                 # ADI
                       (187, 201, "LABEL_MARCHE"),              # 986/E/DPL/2014
                       (351, 361, "LABEL_LOC"),                 # Sidi Kacem
                       (364, 376, "LABEL_LOC"),                 # Sidi Slimane
                       (760, 769, "LABEL_VERSION")]             # définitif
          }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable – Branche Eau (ONEE "
        "BO) – Direction Planification, au bureau d’études ADI, dans le cadre du marché n°986/E/DPL/2014, a "
        "pour objet la réalisation de l'étude de faisabilité de renforcement et de sécurisation de l’AEP des localités "
        "urbaines et rurales de la région de Sidi Kacem – Sidi Slimane. Cette étude est prévue selon les deux "
        "missions suivantes : "
        "Mission I : Analyse de la Situation Actuelle d'AEP et établissement du bilan besoins "
        "ressources à l’horizon 2040 et besoins – capacités de production et de transport ; "
        "Mission II : Etude des Schémas d'Alimentation en Eau Potable. "
        "La présente note constitue la synthèse de la mission II.",
        {
            "entities": [
                (156, 159, "LABEL_ORG"),                    # ADI
                (187, 201, "LABEL_MARCHE"),                 # 986/E/DPL/2014
                (351, 361, "LABEL_LOC"),                    # Sidi Kacem
                (364, 376, "LABEL_LOC"),                    # Sidi Slimane
            ]
        }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable – Branche "
        "Eau (ONEE-BO) – Direction Planification, au bureau d’études ADI, dans le cadre du marché "
        "n°850/E/DPL/2017, a pour objet la réalisation de l'étude de faisabilité de renforcement et de "
        "sécurisation de l’AEP de la ville d’El Kelâa Sraghna , centres et douars avoisinants. Cette "
        "étude est prévue selon les deux missions suivantes : "
        "Mission I : Analyse de la Situation Actuelle d'AEP et établissement du bilan besoins "
        "ressources à l’horizon 2040 et besoins – capacités de production et de "
        "transport ; "
        "Mission II : Etude des Schémas d'Alimentation en Eau Potable. "
        "Le présent rapport constitue la note de synthèse de la mission I.",
        {
            "entities": [
                (156, 159, "LABEL_ORG"),            # ADI
                (187, 201, "LABEL_MARCHE"),         # 850/E/DPL/2017
                (315, 264, "LABEL_LOC"),            # El Kelâa Sraghna
            ]
        }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable – Branche "
        "Eau (ONEE-BO) – Direction Planification, au bureau d’études ADI, dans le cadre du marché "
        "n°850/E/DPL/2017, a pour objet la réalisation de l'étude de faisabilité de renforcement et de "
        "sécurisation de l’AEP de la ville d’El Kelâa Sraghna, centres et douars avoisinants. Cette "
        "étude est prévue, selon les deux missions suivantes : - - "
        "Mission I : Analyse de la Situation Actuelle d'AEP et établissement du "
        "bilan besoins ressources à l’horizon 2040 et besoins – capacités de production et de "
        "transport ; "
        "Mission II : Etude des Schémas d'Alimentation en Eau Potable. "
        "Le présent rapport constitue la note de synthèse de la Mission II, relative à l’étude des "
        "Schémas d’Alimentation en Eau Potable.  "
        "La zone d’étude concerne une partie de la province d’El Kelâa des Sraghna. Elle comprend "
        "la municipalité d’EL kelâa des Sraghna, et les communes de Chtaiba, El Marbouh, "
        "Lounasda, Mayate, Oulad Cherki, Oulad El Garne, Oulad Msabbel, Oulad Sbih, Oulad "
        "Yaacoub, Sidi El Hattab, Taouzint et Znada, relevant toutes du cercle d’El Kelâa des "
        "Sraghna. Leur situation géographique est montrée sur la figure n°1, ci-après. "
        "Cette zone fait partie de la région administrative de Marrakech-Safi. La figure 2, ci-après, "
        "donne le découpage administratif de la zone d’études",
        {
            "entities": [
                (156, 159, "LABEL_ORG"),            # ADI
                (187, 201, "LABEL_MARCHE"),         # 850/E/DPL/2017
                (315, 264, "LABEL_LOC"),            # El Kelâa Sraghna
            ]
        }
    ),

    (
        "Dans le cadre du marché n°465/E/DPS/2007, l’Office National de l’Eau Potable "
        "(ONEP) a confié à l’Ingénieur Conseil CID, l’étude de schéma directeur d’alimentation "
        "en eau potable à long terme du complexe Tanger Tétouan. "
        "L’aire de l’étude s’étend sur une grande partie de la région du nord et comprend en "
        "particulier les provinces de Tanger – Assilah, Fahs - Anjra, Mdiq – Fnideq et Tétouan "
        "ainsi que les villes, centres et douars dont l’alimentation en eau potable est liée ou "
        "susceptibles d’être liée aux systèmes existants ou projetés dans cette zone.  "
        "Les principales prestations à réaliser dans le cadre de cette étude sont : "
        "Analyse de la situation actuelle d’AEP ; "
        "Etablissement du bilan besoins ressources ; "
        "Vérification du bilan besoins – capacité de production et du bilan besoins – "
        "capacité de transit ; "
        "Identification et étude des variantes plausibles de renforcement et/ou de "
        "sécurisation d’AEP dans la zone d’étude ; "
        "Evaluation environnementale des projets proposés.  "
        "L’étude sera réalisée selon les trois missions suivantes : "
        "Mission 1 : Analyse de la situation actuelle d’AEP et établissement des bilans "
        "besoins – ressources et besoins – capacité de production et de transport ; "
        "Mission 2 : Etude des schémas d’alimentation en eau potable ; "
        "Mission 3 : Evaluation environnementale. "
        "Le dossier de la Mission I a été scindé en 3 volumes : "
        "Volume 1 : Données de base et Situation actuelle d’AEP ; "
        "Volume 2 : Ressources en eau ; "
        "Volume 3 : Besoins en eau ; "
        "Note de synthèse. "
        "Le présent rapport constitue la version définitive de la note de synthèse de la mission "
        "1.",
        {
            "entities": [
                (26, 40, "LABEL_MARCHE"),                   # 465/E/DPS/2007
                (115, 118, "LABEL_ORG"),                    # CID
                (203, 209, "LABEL_LOC"),                    # Tanger
                (210, 217, "LABEL_LOC"),                    # Tétouan
                (1525, 1535, "LABEL_VERSION")               # définitive
            ]
        }
    ),

    (
        "La Direction Planification de l’Office National de l’Electricité et de l’Eau Potable – Branche Eau (ONEE – DPL) "
        "a confié au bureau d’études NOVEC dans le cadre du marché N°987/E/DPL/2014, l’étude du "
        "schéma directeur d’AEP des localités relevant des provinces de Tata et d’Assa-Zag. "
        "Les objectifs assignés à cette étude s’articulent autour des points fondamentaux suivants : "
        "Evaluation de la situation actuelle de la desserte en eau, "
        "Etude démographique et Evaluation des besoins en eau : "
        "Recensement des ressources en eau souterraine et superficielle affectées à l'AEP "
        "Synthèse hydrogéologique, "
        "Evaluation des ressources en eau de la zone d'étude, "
        "Bilan besoins ressources. "
        "Bilan besoins – capacité de production et de transport des ouvrages d’AEP ; "
        "Etude du plan directeur d'AEP des populations urbaines et rurales de la zone d'étude. "
        "L’étude comporte à cet effet 2 missions présentées comme suit : "
        "Mission I : Analyse de la situation actuelle d’AEP et établissement des bilans besoins – "
        "ressources et besoins capacités de production et de transport ; "
        "Mission II : Etude des schémas d’alimentation en eau potable ; "
        "La présente note de synthèse, concerne la Mission I (Analyse de la situation actuelle d’AEP et "
        "établissement du bilan besoins-ressources et besoins-capacités de production et de transport), en "
        "édition définitive.",
        {
            "entities": [
                (140, 145, "LABEL_ORG"),                     # NOVEC
                (172, 186, "LABEL_MARCHE"),                  # 987/E/DPL/2014
                (262, 266, "LABEL_LOC"),                     # Tata
                (272, 280, "LABEL_LOC"),                     # Assa-Zag
                (1317, 1327, "LABEL_VERSION")                # définitive
            ]
        }
    ),

    (
        "La Direction Planification de l’Office National de l’Electricité et de l’Eau Potable – Branche Eau "
        "(ONEE/BO – DPL) a confié au bureau d’études NOVEC dans le cadre du marché N°987/E/DPL/2014, "
        "l’étude du schéma directeur d’AEP des localités relevant des provinces de Tata et d’Assa-Zag. "
        "Les objectifs assignés à cette étude s’articulent autour des points fondamentaux suivants : "
        "Evaluation de la situation actuelle de la desserte en eau, "
        "Etude démographique et évaluation des besoins en eau : "
        "Recensement des ressources en eau souterraine et superficielle affectées à l'AEP "
        "Synthèse hydrogéologique, "
        "Evaluation des ressources en eau de la zone d'étude, "
        "Bilan besoins ressources. "
        "Bilan besoins – capacité de production et de transport des ouvrages d’AEP ; "
        "Etude du plan directeur d'AEP des populations urbaines et rurales de la zone d'étude. "
        "L’étude comporte à cet effet 2 missions présentées comme suit : "
        "Mission I : Analyse de la situation actuelle d’AEP et établissement des bilans besoins – "
        "ressources et besoins capacités de production et de transport ; "
        "Mission II : Etude des schémas d’alimentation en eau potable ; "
        "Le présent document, concerne la note de synthèse de la Mission II (Etude des schémas "
        "d’alimentation en eau potable), en édition définitive.",
        {
            "entities": [
                (143, 148, "LABEL_ORG"),                # NOVEC
                (175, 189, "LABEL_MARCHE"),             # 987/E/DPL/2014
                (265, 269, "LABEL_LOC"),                # Tata
                (275, 283, "LABEL_LOC"),                # Assa-Zag
                (1248, 1258, "LABEL_VERSION")           # définitive
            ]
        }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Electricité et de l’Eau Potable – Branche Eau (ONEE-BO) – Direction Planification, au bureau d’études ADI, dans le cadre du marché n°850/E/DPL/2017, a pour objet la réalisation de l'étude de faisabilité de renforcement et de sécurisation de l’AEP de la ville d’El Kelâa Sraghna, Centre et douars avoisinants. "
         "Cette étude est prévue selon les deux missions suivantes : "
         "Mission I : Analyse de la Situation Actuelle d'AEP et établissement du bilan besoins ressources à l’horizon 2040 et besoins – capacités de production et de transport ; "
         "Mission II : Etude des Schémas d'Alimentation en Eau Potable ; "
         "Le présent rapport, établi sur la base des Termes De Références (TDR), constitue le rapport définitif de la Mission I ; "
         "il comprend les chapitres suivants : "
         "Chapitre I : Présentation générale de la zone d’études ; "
         "Chapitre II : Description des systèmes actuels d'AEP de la zone d’études ; "
         "Chapitre III : Recensement et analyse des ressources en eau affectées à l'AEPI ; "
         "Chapitre IV : Etude de la demande en eau ; "
         "Chapitre V : Bilan Besoins - ressources et bilan besoins – capacité de production et de transport.",

         {"entities": [(156, 159, "LABEL_ORG"),             # ADI
                       (187, 201, "LABEL_MARCHE"),          # 850/E/DPL/2017
                       (315, 331, "LABEL_LOC"),             # El Kelâa Sraghna
                       (745, 754, "LABEL_VERSION")]         # définitif
          }
    ),

    (
        "Dans le cadre du marché N° 426/E/DPL/2016, la Direction Planification de l'ONEE - branche eau \"DPL\" a "
        "confié à l’I.C. HYDROSTRUCTURES l’Étude de faisabilité pour le renforcement et la sécurisation de l’AEP "
        "de la ville de Taza, des centres et du rural limitrophes.  "
        "L’étude se compose des deux (02) missions suivantes : "
        "Mission I : Analyse de la situation actuelle d’AEP et actualisation du bilan besoins – "
        "ressources. "
        "Mission II : Étude des schémas de renforcement et de sécurisation de la production d’eau "
        "potable : "
        "La présente note constitue la synthèse de la mission I.",
        {
            "entities": [
                (27, 41, "LABEL_MARCHE"),                   # 426/E/DPL/2016
                (118, 133, "LABEL_ORG"),                    # HYDROSTRUCTURES
                (221, 225, "LABEL_LOC"),                    # Taza
            ]
        }
    ),

    (
        "Dans le cadre du marché N° 426/E/DPL/2016, la Direction Planification de l'ONEE - branche eau \"DPL\" a "
        "confié à l’I.C. HYDROSTRUCTURES l’Étude de faisabilité pour le renforcement et la sécurisation de l’AEP "
        "de la ville de Taza, des centres et du rural limitrophes.  "
        "L’étude se compose des deux (02) missions suivantes : "
        "Mission I : Analyse de la situation actuelle d’AEP et actualisation du bilan besoins – "
        "ressources. "
        "Mission II : Étude des schémas de renforcement et de sécurisation de la production d’eau "
        "potable : "
        "La présente note constitue la synthèse de la mission II.",
        {
            "entities": [
                (27, 41, "LABEL_MARCHE"),           # 426/E/DPL/2016
                (118, 133, "LABEL_ORG"),            # HYDROSTRUCTURES
                (221, 225, "LABEL_LOC"),            # Taza
            ]
        }
    ),

    (
        "Dans le cadre du marché N° 426/E/DPL/2016, la Direction Planification de l'ONEE - branche eau \"DPL\" a confié à l’I.C. HYDROSTRUCTURES l’Étude de faisabilité pour le renforcement et la sécurisation de l’AEP de la ville de Taza, des centres et du rural limitrophes. "
         "L’étude se compose des deux (02) missions suivantes : "
         "Mission I : Analyse de la situation actuelle d’AEP et actualisation du bilan besoins – ressources. "
         "Mission II : Étude des schémas de renforcement et de sécurisation de la production d’eau potable : "
         "Le présent mémoire constitue le rapport définitif de la mission II.",

         {"entities": [(27, 41, "LABEL_MARCHE"),                # 426/E/DPL/2016
                       (118, 133, "LABEL_ORG"),                 # HYDROSTRUCTURES
                       (221, 225, "LABEL_LOC"),                 # Taza
                       (556, 565, "LABEL_VERSION")]             # définitif
          }
    ),

    (
        "La présente étude, confiée par l’Office National de l’Eau Potable (ONEP) – Direction de la "
        "planification (DPL), au bureau d’études SCET-SCOM, dans le cadre du marché n°673/E/DPL/2008, "
        "a pour objet la réalisation de l'étude de faisabilité du dessalement d’eau de mer pour le "
        "renforcement de l’alimentation en eau potable des villes de Tiznit et Sidi Ifni et des "
        "centres et douars avoisinants. "
        "L’étude est organisée en quatre missions comme suit : "
        "Mission I : analyse de la situation actuelle d’AEP et actualisation du bilan besoins "
        "ressources; "
        "Mission II : Identification des sites d’implantation de l’usine de dessalement et définition des "
        "schémas d’adduction ; "
        "Mission III : Evaluation environnementale ; "
        "Mission IV : Définition du procédé de dessalement le plus approprié pour chaque site, "
        "évaluation économique et synthèse des résultats. "
        "La présente note de synthèse récapitule les grandes lignes du rapport définitif de la mission I.",
        {
            "entities": [
                (131, 140, "LABEL_ORG"),                 # SCET-SCOM
                (168, 182, "LABEL_MARCHE"),              # 673/E/DPL/2008
                (334, 340, "LABEL_LOC"),                 # Tiznit
                (344, 353, "LABEL_LOC"),                 # Sidi Ifni
                (911, 920, "LABEL_VERSION")              # définitif
            ]
        }
    ),

    (
        "Dans le cadre du marché N° 426/E/DPL/2016, la Direction Planification de l'ONEE - branche eau \"DPL\" a confié à l’I.C. HYDROSTRUCTURES l’Étude de faisabilité pour le renforcement et la sécurisation de l’AEP de la ville de Taza, des centres et du rural limitrophes. "
         "L’étude se compose des deux (02) missions suivantes : "
         "Mission I : Analyse de la situation actuelle d’AEP et actualisation du bilan besoins – ressources. "
         "Mission II : Étude des schémas de renforcement et de sécurisation de la production d’eau potable : "
         "Le présent mémoire constitue le rapport définitif de la mission I. Il traite des principaux aspects suivants : "
         "Généralités sur l’aire d’étude ; "
         "Description des systèmes d’AEP existants ; "
         "Analyse de la situation actuelle de l’assainissement liquide ; "
         "Projection de la demande en eau ; "
         "Analyse de la situation actuelle en matière des ressources en eau souterraines et superficielles ; "
         "Établissement des bilans besoins - ressources ; "
         "Établissement des bilans besoins - capacités de transport.",

         {"entities": [(27, 41, "LABEL_MARCHE"),                # 426/E/DPL/2016
                       (118, 133, "LABEL_ORG"),                 # HYDROSTRUCTURES
                       (221, 225, "LABEL_LOC"),                 # Taza
                       (556, 565, "LABEL_VERSION")]             # définitif
          }
    ),
]

random.shuffle(TRAIN_DATA)
split = int(len(TRAIN_DATA) * 0.8)
train_data = TRAIN_DATA[:split]
valid_data = TRAIN_DATA[split:]

pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

def evaluate_loss(nlp, data):
    losses = {}
    for text, annotation in data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotation)
        nlp.update([example], losses=losses, drop=0.0, sgd=None)  # Pas de mise à jour réelle
    return losses.get("ner", 0.0)

optimizer = nlp.resume_training()
best_loss = float('inf')
patience = 5
no_improve = 0
output_dir = Path("./modele_ner_doc")
output_dir.mkdir(exist_ok=True)

with nlp.disable_pipes(*other_pipes):
    sizes = compounding(1.0, 4.0, 1.001)
    for iteration in range(30):
        random.shuffle(train_data)
        batches = minibatch(train_data, size=sizes)
        losses = {}
        for batch in batches:
            for text, annotation in batch:
                try:
                    doc_tmp = nlp.make_doc(text)
                    biluo = offsets_to_biluo_tags(doc_tmp, annotation["entities"])
                    if any(t == "-" for t in biluo):
                        continue
                except Exception:
                    continue
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotation)
                nlp.update([example], sgd=optimizer, drop=0.35, losses=losses)
        print(f"Iteration {iteration+1}, train losses: {losses}")

        val_loss = evaluate_loss(nlp, valid_data)
        print(f"  Validation loss: {val_loss:.3f}")

        if val_loss < best_loss:
            best_loss = val_loss
            no_improve = 0
            nlp.to_disk(output_dir)
            print(f"  ▶ Nouveau meilleur modèle sauvegardé (loss={best_loss:.3f})")
        else:
            no_improve += 1
            print(f"  Pas d'amélioration ({no_improve}/{patience})")
            if no_improve >= patience:
                print("Early stopping déclenché.")
                break

print("\nChargement du meilleur modèle pour test:")
nlp_best = spacy.load(output_dir)

test_samples = [
    (
    "La présente étude, confiée par l’Office National de l’Electricité et l’Eau Potable – Branche Eau (ONEE-BO), "
    "au bureau d’études ADI, dans le cadre du marché n°1129 /E/DPL/2014, a pour objet la réalisation de l'étude "
    "du Plan Directeur d’AEP des Populations Urbaines et Rurales de la zone Nord du Bassin hydraulique de la Moulouya. "
    "Cette étude est prévue selon les trois  missions suivantes : "
    "Mission I : Etude des besoins en eau potable jusqu’à l’Horizon 2035 ; "
    "Mission II : Recensement et analyse des ressources utilisées et/ou affectées à l’eau potable et Bilan besoins ressources ; "
    "Mission III : Plan directeur d’alimentation en eau potable de la zone d’étude. "
    "Le présent rapport constitue la note de synthèse définitive de la mission I."
)]


for text in test_samples:
    doc = nlp_best(text)
    print(f"\nTexte : {text[:100]}...")
    for ent in doc.ents:
        print(f"  ➤ {ent.label_}: {ent.text}")

print(f"\nModèle sauvegardé dans : {output_dir.resolve()}")
