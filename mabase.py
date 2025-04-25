import sqlite3
import csv

def creation_table():
    """créer la base de donnée à l'aide d'un csv
    Précondition :
    fichier non vide

    Paramètres:
    aucuns

    Renvoi :
    pas de return

    creer la datbase"""
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

    with open("quizz_nsi_linux.csv", newline='', encoding="utf-8") as fh:
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
