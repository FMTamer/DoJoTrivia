# **Technisch Ontwerp - IK05**

## Routes
****
##### Register:
**Hier wordt gecontrolleerd of de username en email uniek zijn en verder worden alle ingevoerde gegevens in de database gezet.**
@app.route("/register", methods=["GET", "POST"])
def register():
db.execute("INSERT INTO users (username, email, hash) VALUES(:username, :email, :hash)", username=request.form.get("username"), hash=pwd_context.encrypt(request.form.get("password", email=request.form.get("email"))))

##### Login:
**Hier wordt gecontroleerd of de username en wachtwoord aan elkaar gekoppeld zijn in de database en wordt de gebruiker doorverwezen naar de index.**
@app.route("/login", methods=["GET", "POST"])
def login():
db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
pwd_context.verify(request.form.get("password"), rows[0]["hash"])

##### Logout:
**Gebruiker wordt hier uitgelogd en de huidige sessie verbroken.**
@app.route("/logout", methods=["GET", "POST"])
def logout():
session.clear()

##### Contact:
**Na het invullen van alle formulier gegevens wordt in deze route de velden verstuurd via de mail naar de developers van de pagina.**
@app.route("/contact", methods=["GET", "POST"])
def contact():

##### Create Game:
**Hier wordt een room code generate zodat andere spelers kunnen joinen.**
@app.route("/creategame", methods="POST")

##### Make Quiz:
**Hier wordt de gebruiker doorverwezen naar een pagina waar de gebruiker zijn of haar eigen quiz kan maken. Na het invullen worden alle gegevens die ingevuld zijn door de gebruiker ingevoerd in de database.**
@app.route("/makequiz", methods=["GET", "POST"])

##### Play Generated Quiz:
**De gebruiker wordt in een room gezet waar andere spelers deze kunnen joinen met de vragen die van te voren zijn generate.**
@app.route("/playquiz", methods=["GET","POST"])

##### Join Game:
**Hier wordt na het invullen van de room code doorverwezen naar de pre-game pagina. De room code wordt vergelen met de dynamische database.**
@app.route("/join", methods=["GET", "POST"])

##### Start Game:
**De moderator van de game krijgt deze optie te zien wanneer hij of zij wil beginnen. Na dat die optie is geklikt kan iedereen beginnen en wordt de quiz gestart.**
@app.route("/play", methods=["GET","POST"])

## Plugins en frameworks
****
##### Bootstrap:
https://getbootstrap.com/

##### GitHub:
https://github.com/

##### Flask-Mail:
https://github.com/mattupstate/flask-mail/

##### Flask-User:
https://flask-user.readthedocs.io/en/latest/

##### Flask-Session:
https://pythonhosted.org/Flask-Session/