from flask import Flask, render_template, redirect, url_for, request, flash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Nécessaire pour utiliser les messages flash

# Fonction pour récupérer une question
def get_question(numero_question):
    conn = sqlite3.connect("mabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM QUIZZ1 WHERE id=? AND langue='fr'", (numero_question,))
    question = cursor.fetchone()
    conn.close()
    return question

# Fonction pour récupérer les réponses
def get_reponses(numero_question):
    conn = sqlite3.connect("mabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT rep1, rep2, rep3, rep4 FROM QUIZZ1 WHERE id=? AND langue='fr'", (numero_question,))
    reponses = cursor.fetchone()
    conn.close()
    return reponses

# Fonction pour mélanger les réponses
def melanger_reponses(reponses):
    bonne_reponse = reponses[0]
    liste_reponse = list(reponses)
    random.shuffle(liste_reponse)
    return liste_reponse, bonne_reponse

@app.route("/")
def index():
    return redirect(url_for('question_page', numero=1))

@app.route("/question/<int:numero>/")
def question_page(numero):
    question = get_question(numero)
    if question is None:
        return print("Aucune question trouvée")

    reponses = get_reponses(numero)
    if reponses is None:
        return print("Aucune réponse trouvée")

    reponses, bonne_reponse = melanger_reponses(reponses)
    return render_template("index.html", question=question[0], reponses=reponses, numero=numero)

@app.route("/verifier/<int:numero>/", methods=["POST"])
def verifier_reponse(numero):
    # Vérifier si la question existe
    question = get_question(numero)
    if question is None:
        return f"Aucune question trouvée pour l'ID {numero}", 404

    reponses = get_reponses(numero)
    if reponses is None:
        return f"Aucune réponse trouvée pour l'ID {numero}", 404

    _, bonne_reponse = melanger_reponses(reponses)
    
    # Récupérer la réponse soumise par l'utilisateur
    reponse_utilisateur = request.form.get('choix')
    
    # Vérifier si c'est la bonne réponse
    if reponse_utilisateur == bonne_reponse:
        flash("Bravo ! C'était la bonne réponse.", "success")
    else:
        flash(f"Dommage ! La bonne réponse était {bonne_reponse}.", "error")

    # Passer à la question suivante
    prochaine_question = numero + 1
    question_suivante = get_question(prochaine_question)

    # Si la prochaine question existe, rediriger vers elle
    if question_suivante:
        return redirect(url_for('question_page', numero=prochaine_question))
    else:
        return render_template("fin_quiz.html", message="Fin du quiz !")

if __name__ == "__main__":
    app.run(debug=True)
