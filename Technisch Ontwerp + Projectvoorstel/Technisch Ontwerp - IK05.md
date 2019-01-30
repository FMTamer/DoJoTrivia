# **Technisch Ontwerp - IK05**

## Routes
****
##### Index:
###### @app.route("/"):
Als de bezoeker niet is ingelogd, wordt onze "introductiepagina", index.html, geladen, waar er een mogelijkheid is om in te loggen. Ook heeft de bezoeker toegang tot de registreerpagina en (via de sidebar) nogmaals Register, Contact en About Us. Als de gebruiker wel ingelogd is, krijgt hij zijn persoonlijke pagina, "personal-page.html" te zien.

##### Personal Page:
###### @app.route("/personal"):
Vanaf hier kan de gebruiker ervoor kiezenom zijn eigen quiz te maken, een nieuwe game te maken, of om een game te joinen. Via de sidebar heeft de gebruiker toegang tot deze zelfde opties, naast opnieuw zijn persoonlijke pagina, Contact en About Us. Ook staat er in dit geval een optie om uit te loggen.

##### Register:
###### @app.route("/register", methods=["GET", "POST"]):
Als de route een request method van GET krijgt, wordt de registratiepagina (register.html) geladen, met een veld voor een gebruikersnaam, wachtwoord, bevestiging van het wachtwoord en een e-mailadres.
Als de request method naar POST verandert, kijkt de route of alles is ingevuld en of de gebruikersnaam en e-mailadres uniek zijn. Als dit het geval is, wordt de gebruiker automatisch ingelogd en wordt hij naar zijn persoonlijke pagina gebracht.

##### Login:
###### @app.route("/login", methods=["GET", "POST"]):
Als de request method GET is, wordt de homepagina (index.html) geladen.
Als deze naar POST verandert, wordt allereerst gekeken of de gebruikersnaam en het wachtwoord zijn ingevuld. Dan wordt gekeken of de gebruikersnaam en het wachtwoord overeenkomen met de database, en als dit het geval is wordt de gebruiker ingelogd (ook wordt er onthouden wie is ingelogd) en komt hij op zijn persoonlijke pagina terecht. Als dit niet het geval is, krijgt hij hier melding van.

##### Logout:
###### @app.route("/logout", methods=["GET"]):
Hier wordt de user id vergeten van de voorheen ingelogde gebruiker. Daarna wordt logout.html geladen, die zal redirecten naar de homepagina na vijf seconden.

##### Contact:
###### @app.route("/contact", methods=["GET", "POST"]):
Als de request method GET is, wordt de template contact.html gerendered met hierop een selectie voor de soort contactform, de gebruikersnaam en e-mail van de contact zoekende. Ook is er ruimte voor een (optioneel) bericht.
Als de request method POST is, dus als het formulier is ingevuld, wordt de gebruiker naar contacted.html verstuurd, wat de gebruiker bedankt voor de gegeven feedback en hem na vijf seconden terugbrengt naar de homepagina. Ook wordt er een mail verstuurd naar het ingevulde e-mailadres ter bevestiging van het ontvangst.

##### About Us:
###### @app.route("/about-us"):
Hier staat een klein verhaaltje over het ontstaan van de website, samen met het logo van de website. Verder heeft het niet echt een functie behalve de template about-us.html renderen.

##### Custom Quiz:
###### @app.route("/customquiz", methods = ['GET', 'POST']):
Als de request method GET is, wordt customquiz_title.html geladen, waar de gebruiker een titel aan zijn zelfgemaakte quiz kan geven. Als de request method POST wordt, wordt gekeken of er een titel is gegeven en of deze al in gebruik is. Als wel, of als er geen titel gegeven is, dan wordt de gebruiker hierover gewaarschuwd en moet hij een (andere) titel kiezen, anders wordt hij doorgestuurd naar app route custom question.

##### Custom Question:
###### @app.route("/custom_question", methods = ['GET', 'POST']):
Als de request method GET is wordt custom_question.html geladen, waar de titel van de quiz ook wordt weergegeven. Hier kan de gebruiker een vraag opstellen met vier mogelijke antwoorden, een juiste en drie onjuiste.
Als de request method verandert naar POST, door te drukken op "Add Question", wordt er eerst gekeken of alle velden zijn ingevuld. Als dit niet het geval is, wordt de gebruiker hiervoor gewaarschuwd. Anders worden de gegeven titel en antwoorden toegevoegd in de database. Als de gebruiker klaar is met de quiz, drukt hij op "Done" en wordt de quiz toegevoegd aan de database.

##### Create Game:
###### @app.route("/creategame", methods=["GET", "POST"]):
Als de request method GET is, wordt creategame.html gerendered, met daarop een dropdown menu met een keuze van mogelijke quizzes en een knop om het spel te beginnen.
Als de request method POST is, wordt als eerst de game aangemaakt en een kamernummer gegenereerd. Daarna wordt, indien een random quiz is gekozen, een willekeurige volgorde van willekeurige vragen met de antwoorden uit de database gegeven. Als er een specifieke quiz is gekozen wordt deze uit de database gehaald.

##### Join Game:
###### @app.route("/joingame",  methods=["GET", "POST"]):
Als de request method GET is, wordt joining.html gerendered als de speler niet in een game is. Als dit echter wel het geval is, wordt de speler hiervoor gewaarschuwd.
Als de request method POST is, wordt er gekeken of het gegeven kamernummer bestaat nadat de gebruiker op "Join Game" drukt. Als dit het geval is, wordt de speler toegevoegd aan de gegeven kamer. Dan worden de geselecteerde vragen met antwoorden opgehaald, waarna de antwoorden worden gehusseld. Dan wordt answer.html gerendered met de huidige vraag en antwoorden.

##### Scorebord:
###### @app.route("/results"):
Als eerst worden de spelers en het kamernummer ingelezen, waarna de bijbehorende scores en tijd van afloop van de quiz worden weergegeven op results.html. Dan wordt de winnaar bepaald op basis van een vergelijking van de scores, de speler met de hoogste score wint, wat wordt meegegeven aan de template. Als het gelijkspel is, wordt dit ook meegegeven aan de template. Ten slotte wordt de "completed" variabele voor de game in de database naar 1 gezet.

##### Juist antwoord:
###### app.route('/quizC', methods=['GET', 'POST']):
Als een speler de huidige vraag heeft beantwoord, wordt gekeken of de andere speler deze vraag ook heeft beantwoord. Als niet, wordt er gewacht tot dit het geval is. Vervolgens wordt er een punt bij de score van de speler(s) die de vraag juist heeft/hebben beantwoordt gerekend. Dan wordt er gekeken of er nog vragen over zijn voor de huidige game, als wel dan wordt de volgende vraag opgehaald met de antwoorden, die dan worden gehusseld. Als dit niet het geval is, wordt de tijd van afloop genoteerd en worden de spelers naar het scorebord gebracht.

##### Onjuist antwoord:
###### @app.route('/quizW', methods=['GET', 'POST']):
Als een speler de huidige vraag heeft beantwoord, wordt gekeken of de andere speler deze vraag ook heeft beantwoord. Als niet, wordt er gewacht tot dit het geval is. Dan wordt er gekeken of er nog vragen over zijn voor de huidige game, als wel dan wordt de volgende vraag opgehaald met de antwoorden, die dan worden gehusseld. Als dit niet het geval is, wordt de tijd van afloop genoteerd en worden de spelers naar het scorebord gebracht.

##### Opgeven:
###### @app.route("/retreat", methods=['POST']):
Als eerst wordt de huidige tijd genoteerd. Dan wordt de score van de speler die op heeft gegeven naar 0 gezet en die van de andere speler naar 10. Ten slotte wordt results.html gerendered met de tijd van afloop en scores meegegeven.


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

##### Passlib:
https://passlib.readthedocs.io/en/stable/narr/quickstart.html

##### Tempfile:
https://docs.python.org/2/library/tempfile.html

##### SMTPlib:
https://docs.python.org/3/library/smtplib.html

##### JSON:
https://docs.python.org/3/library/json.html

