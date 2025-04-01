from flask import Flask, render_template, redirect, url_for, request, flash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"  

def get_question(numero_question):
    conn = sqlite3.connect("mabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM QUIZZ1 WHERE id=? AND langue='fr'", (numero_question,))
    question = cursor.fetchone()
    conn.close()
    return question[0] if question else None

def get_reponses(numero_question):
    conn = sqlite3.connect("mabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT rep1, rep2, rep3, rep4 FROM QUIZZ1 WHERE id=? AND langue='fr'", (numero_question,))
    reponses = cursor.fetchone()
    conn.close()
    return list(reponses) if reponses else None

@app.route("/")
def index():
    return redirect(url_for('question_page', numero=1))

@app.route("/question/<int:numero>/")
def question_page(numero):
    question = get_question(numero)
    reponses = get_reponses(numero)
    bonne_reponse = reponses[0]
    reponses_melangees = reponses.copy()
    random.shuffle(reponses_melangees)
    return render_template("index.html", question=question, reponses=reponses_melangees, numero=numero, bonne_reponse=bonne_reponse)

@app.route("/verifier/<int:numero>/", methods=["POST"])
def verifier_reponse(numero):
    question = get_question(numero)
    reponses = get_reponses(numero)

    if question is None or reponses is None:
        flash("Fin du quiz !", "info")
        return redirect(url_for('fin_quiz')) 
    
    bonne_reponse = reponses[0]
    reponse_utilisateur = request.form.get('choix')


    if reponse_utilisateur == bonne_reponse:
        flash(f"Bravo ! {bonne_reponse} était la bonne réponse.", "success")
    else:
        flash(f"Dommage ! La bonne réponse était {bonne_reponse}.", "error")

    # Redirection vers la page de réponse
    return redirect(url_for('afficher_reponse', numero=numero, question=question, reponse=bonne_reponse))


@app.route("/reponse/<int:numero>/")
def afficher_reponse(numero):
    return render_template("reponse.html", numero=numero, question=request.args.get('question'), reponse=request.args.get('reponse'))


if __name__ == "__main__":
    app.run(debug=True)
