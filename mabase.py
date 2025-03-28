import sqlite3
import csv

def insert_into(curseur, fic_csv, nom_table, ind_int):
    with open("quizz_nsi.csv") as fh:
        fh.readline()
        lecteur_ligne = csv.reader(fh, delimiter=";")
        for tab_ligne in lecteur_ligne:
            for indice in ind_int:
                tab_ligne[indice] = int(tab_ligne[indice])
            commSQL = f"INSERT INTO {nom_table} VALUES {tuple(tab_ligne)}"
            try:
                curseur.execute(commSQL)
            except sqlite3.IntegrityError:
                print("clé primaire existante")

def creation_table():
    conn = sqlite3.connect("mabase.db")
    curseur = conn.cursor()
    
    curseur.execute("""
    CREATE TABLE QUIZZ1 (
        id INTEGER PRIMARY KEY, 
        langue TEXT, 
        question TEXT, 
        rep1 TEXT, 
        rep2 TEXT, 
        rep3 TEXT, 
        rep4 TEXT, 
        difficulte TEXT, 
        morale TEXT, 
        source TEXT
    );
    """)

    with open("quizz_nsi.csv", newline='', encoding="utf-8") as fh:
        descripteur = csv.DictReader(fh, delimiter=";")  # Utilisation du bon délimiteur
        for dico in descripteur:
            t = tuple(dico.values())
            try:
                curseur.execute(f"INSERT INTO QUIZZ1 VALUES ({', '.join(['?']*len(t))})", t)
            except sqlite3.IntegrityError:
                print("Clé primaire existante :", t[0])
    
    conn.commit()
    conn.close()


# Exécution du code
creation_table()

# Connexion pour lecture
conn = sqlite3.connect("mabase.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM QUIZZ1 WHERE langue='fr'")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
