# Projectvoorstel
Door Musa Karim, Vedran Marinovic & Frank Tamer
## Samenvatting
Voor ons project gaan we een webapplicatie, genaamd DoJoTrivia, bouwen waarmee mensen triviavragen kunnen beantwoorden. Deze vragen zullen om en om beantwoord worde, en aan het einde is er een scorebord te zien.

## Features
- Registratie en login
- Quizzes
- Multiplayer
- Scoreboard aan het eind van een game
- Contactpagina (voor het rapporteren van bugs, geven van suggesties, etc.)
- Mail ter bevestiging van verwerking van registratie en feedback

### Extra features
- Notificaties voor wanneer je voor een quiz wordt uitgenodigd en wanneer een quiz naar de volgende vraag springt.
- Een geschiedenis van quizzes per gebruiker.
- Zelf quizzes maken
- Geschiedenis van winsten en verliezen per gebruiker

## Afhankelijkheden

### Databronnen
- Open Trivia Database (van https://opentdb.com/api_config.php)
### Externe componenten
- Bootstrap
- Flask
- Flask-Mail
- Flask-User

### Concurrerende  websites
- Socrative (https://b.socrative.com/login/student/). Met socrative kunnen docenten gemakkelijk hun eigen quizzes maken.
- Kahoot ([https://kahoot.it/](https://kahoot.it/ "https://kahoot.it/"). Kahoot heeft een zeer simpel en kleurrijk design.

### Moeilijkheden
- Multiplayer implementeren
- Waarden krijgen voor scoreboard
- (Gebruikers eigen quizzes laten maken, indien mogelijk)