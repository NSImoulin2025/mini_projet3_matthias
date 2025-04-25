from flask import Flask, render_template, redirect, url_for, request, flash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"  

def get_question(numero_question):from flask import Flask, render_template, redirect, url_for, request, flash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

score = 0
max_score = 0
streak = 0

def get_morale(numero_question):
    """Récupère la morale d'une question donnée.

    Précondition :
    La question avec cet ID doit exister dans la base et être en langue
      française.

    Paramètres :
    numero_question : int — Identifiant de la question

    Renvoi :
    str — Morale de la question

    >>> isinstance(get_morale(1), str)
    True
    """
    conn = sqlite3.connect("mabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT morale FROM QUIZZ1 WHERE id=? AND langue='fr'",
                    (numero_question,))
    morale = cursor.fetchone()
    conn.close()
    return morale[0]

def get_question(numero_question):
    """Récupère le texte d'une question à partir de son identifiant.

    Précondition :
    L'identifiant doit correspondre à une question existante.

    Paramètres :
    numero_question : int — Identifiant de la question

    Renvoi :
    str|None — Texte de la question ou None si elle n'existe pas

    >>> q = get_question(1)
    >>> isinstance(q, str) or q is None
    True
    """
    conn = sqlite3.connect("mabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM QUIZZ1 WHERE id=? AND langue='fr'",
                    (numero_question,))
    question = cursor.fetchone()
    conn.close()
    return question[0] if question else None

def get_reponses(numero_question):
    """Récupère les 4 réponses possibles à une question.

    Précondition :
    L'identifiant doit correspondre à une ligne valide avec 4 réponses.

    Paramètres :
    numero_question : int — Identifiant de la question

    Renvoi :
    list[str] — Liste des réponses (la première est correcte)

    >>> r = get_reponses(1)
    >>> isinstance(r, list) and len(r) == 4
    True
    """
    conn = sqlite3.connect("mabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT rep1, rep2, rep3, rep4 FROM QUIZZ1 WHERE id=?" \
    " AND langue='fr'", (numero_question,))
    reponses = cursor.fetchone()
    conn.close()
    return list(reponses) if reponses else []

def get_nb():
    """Retourne le nombre total de questions dans la base (en français).

    Précondition :
    La table QUIZZ1 doit contenir des questions en langue 'fr'.

    Paramètres :
    Aucun

    Renvoi :
    int — Nombre total de questions

    >>> isinstance(get_nb(), int)
    True
    """
    conn = sqlite3.connect("mabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(question) FROM QUIZZ1 WHERE langue='fr'")
    nb = cursor.fetchone()
    conn.close()
    return nb[0] if nb else 0

def winning_streak(winning):
    """Met à jour la série de bonnes réponses consécutives.

    Précondition :
    Aucune

    Paramètres :
    winning : bool — True si la réponse était correcte, False sinon

    Renvoi :
    Aucun (modifie la variable globale streak)

    >>> global streak
    >>> streak = 0
    >>> winning_streak(True)
    >>> winning_streak(True)
    >>> streak
    2
    >>> winning_streak(False)
    >>> streak
    0
    """
    global streak
    if winning:
        streak += 1
    else:
        streak = 0

@app.route("/")
def index():
    """Redirige vers la première question du quiz."""
    return redirect(url_for('question_page', numero=1))

@app.route("/fin_quiz/")
def fin_quiz():
    """Affiche la page de fin de quiz avec le score final."""
    global score
    score_actu = score
    score = 0
    nb_questions = get_nb()
    return render_template("fin_quiz.html", score=score_actu,
                            nb_questions=nb_questions)

@app.route("/derniere_question/")
def derniere_question():
    """Affiche la dernière morale du quiz."""
    numero = get_nb()
    morale = get_morale(numero)
    return render_template("reponse.html", morale=morale, numero=numero)

@app.route("/question/<int:numero>/")
def question_page(numero):
    """Affiche une question et ses réponses mélangées.

    Paramètres :
    numero : int — numéro de la question

    Renvoi :
    Page HTML avec la question et les réponses
    """
    global streak
    question = get_question(numero)
    reponses = get_reponses(numero)

    if not question or not reponses:
        return redirect(url_for('fin_quiz'))

    bonne_reponse = reponses[0]
    reponses_melangees = reponses.copy()
    random.shuffle(reponses_melangees)

    return render_template("index.html", question=question,
                            reponses=reponses_melangees, numero=numero,
                              bonne_reponse=bonne_reponse, streak=streak)

@app.route("/verifier/<int:numero>/", methods=["POST"])
def verifier_reponse(numero):
    """Vérifie si la réponse envoyée est correcte et redirige vers la
      page suivante.

    Paramètres :
    numero : int — numéro de la question actuelle

    Renvoi :
    Redirection vers la page de réponse ou de fin
    """
    global score, streak
    question = get_question(numero)
    reponses = get_reponses(numero)
    morale = get_morale(numero)

    if question is None or reponses is None:
        flash("Fin du quiz !", "info")
        return redirect(url_for('fin_quiz'))

    bonne_reponse = reponses[0]
    reponse_utilisateur = request.form.get('choix')

    if reponse_utilisateur == bonne_reponse:
        flash(f"Bravo ! {bonne_reponse} était la bonne réponse.", "success")
        score += 1
        winning_streak(True)
    else:
        flash(f"Dommage ! La bonne réponse était {bonne_reponse}.", "error")
        winning_streak(False)

    if get_question(numero + 1) is None:
        return redirect(url_for('derniere_question', question=question,
                                 reponse=bonne_reponse, morale=morale,
                                   score=score))

    return redirect(url_for('afficher_reponse', numero=numero,
                             question=question, reponse=bonne_reponse,
                               morale=morale, score=score))

@app.route("/reponse/<int:numero>/")
def afficher_reponse(numero):
    """Affiche la morale et la réponse correcte après une question.

    Paramètres :
    numero : int — numéro de la question

    Renvoi :
    Page HTML de réponse
    """
    return render_template("reponse.html", numero=numero,
                           question=request.args.get('question'),
                           reponse=request.args.get('reponse'),
                           morale=request.args.get('morale'),
                           score=score,
                           streak=streak)

if __name__ == "__main__":
    app.run(debug=True)

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
