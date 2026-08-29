from flask import Flask, request, session, redirect
from twilio.rest import Client
from dotenv import load_dotenv
import os
from supabase import create_client
from functools import wraps

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "swiftsystems2026")

MOT_DE_PASSE = os.getenv("ADMIN_PASSWORD", "admin123")

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

def envoyer_sms(numero, nom, ticket_id):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    msg = f"Envoyer par SwiftSystems\nBonjour {nom}, votre service #{ticket_id} est termine.\nComment avez vous trouve le service ? 1=Excellent 2=Correct 3=Mauvais"
    client.messages.create(body=msg, from_=TWILIO_NUMBER, to=numero)
    print(f"SMS envoye a {numero}")

@app.route("/")
def accueil():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Prise de Rendez-vous</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: 'Georgia', serif; background: #f9f9f9; color: #333; }
            .container { max-width: 600px; margin: 40px auto; background: white; padding: 40px; box-shadow: 0 2px 20px rgba(0,0,0,0.08); }
            h1 { text-align: center; font-size: 24px; color: #2c3e50; margin-bottom: 10px; letter-spacing: 2px; }
            p.sub { text-align: center; color: #999; margin-bottom: 30px; font-size: 13px; }
            label { display: block; font-size: 11px; letter-spacing: 1px; color: #666; margin-bottom: 5px; margin-top: 15px; text-transform: uppercase; }
            input, textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; font-family: Georgia; }
            textarea { height: 100px; resize: vertical; }
            button { width: 100%; padding: 15px; background: #2c3e50; color: white; border: none; margin-top: 25px; font-size: 14px; letter-spacing: 2px; cursor: pointer; text-transform: uppercase; }
            button:hover { background: #1a252f; }
            .success { text-align: center; margin-top: 15px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PRISE DE RENDEZ-VOUS</h1>
            <p class="sub">Remplissez le formulaire ci-dessous</p>
            <label>NOM COMPLET *</label>
            <input type="text" id="nom" placeholder="Jean Dupont" />
            <label>COURRIEL *</label>
            <input type="email" id="email" placeholder="jean@email.com" />
            <label>NUMÉRO DE TÉLÉPHONE *</label>
            <input type="text" id="telephone" placeholder="+15141234567" />
            <label>DATE DU RENDEZ-VOUS *</label>
            <input type="date" id="date_rdv" />
            <label>TYPE DE SERVICE *</label>
            <input type="text" id="type_service" placeholder="Ex: Mariage, Portrait, Consultation..." />
            <label>LOCALISATION</label>
            <input type="text" id="localisation" placeholder="Ville ou adresse" />
            <label>MESSAGE</label>
            <textarea id="message" placeholder="Informations supplémentaires..."></textarea>
            <button onclick="soumettre()">ENVOYER LA DEMANDE</button>
            <div class="success" id="msg"></div>
        </div>
        <script>
            function soumettre() {
                const nom = document.getElementById('nom').value;
                const email = document.getElementById('email').value;
                const telephone = document.getElementById('telephone').value;
                const date_rdv = document.getElementById('date_rdv').value;
                const type_service = document.getElementById('type_service').value;
                const localisation = document.getElementById('localisation').value;
                const message = document.getElementById('message').value;
                if (!nom || !email || !telephone || !date_rdv || !type_service) {
                    document.getElementById('msg').innerText = 'Veuillez remplir tous les champs obligatoires.';
                    document.getElementById('msg').style.color = 'red';
                    return;
                }
                fetch('/ajouter-client', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({nom, email, telephone, date_rdv, type_service, localisation, message})
                })
                .then(r => r.json())
                .then(() => {
                    document.getElementById('msg').innerText = 'Demande envoyee avec succes !';
                    document.getElementById('msg').style.color = 'green';
                    ['nom','email','telephone','date_rdv','type_service','localisation','message'].forEach(id => document.getElementById(id).value = '');
                });
            }
        </script>
    </body>
    </html>
    """
    return html, 200

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == MOT_DE_PASSE:
            session["logged_in"] = True
            return redirect("/clients")
        return """
        <div style="text-align:center;margin-top:100px;font-family:Arial">
            <h2>Mot de passe incorrect</h2>
            <a href="/login">Reessayer</a>
        </div>
        """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connexion</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Georgia; background: #f9f9f9; }
            .container { max-width: 400px; margin: 100px auto; background: white; padding: 40px; box-shadow: 0 2px 20px rgba(0,0,0,0.08); text-align: center; }
            h1 { color: #2c3e50; margin-bottom: 20px; font-size: 20px; letter-spacing: 2px; }
            input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; margin-bottom: 15px; box-sizing: border-box; }
            button { width: 100%; padding: 12px; background: #2c3e50; color: white; border: none; font-size: 14px; cursor: pointer; letter-spacing: 1px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESPACE ADMIN</h1>
            <form method="POST">
                <input type="password" name="password" placeholder="Mot de passe" />
                <button type="submit">CONNEXION</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.route("/ajouter-client", methods=["POST"])
def ajouter_client():
    data = request.get_json()
    supabase.table("clients").insert({
        "nom": data.get("nom"),
        "email": data.get("email"),
        "telephone": data.get("telephone"),
        "date_rdv": data.get("date_rdv"),
        "type_service": data.get("type_service"),
        "localisation": data.get("localisation"),
        "message": data.get("message")
    }).execute()
    return {"success": True}, 200

@app.route("/clients")
@login_required
def liste_clients():
    data = supabase.table("clients").select("*").order("created_at", desc=True).execute().data
    rows = ""
    for c in data:
        couleur = "#999" if c["sms_envoye"] else "#27ae60"
        texte = "SMS Envoye" if c["sms_envoye"] else "Envoyer SMS"
        rows += f"""
        <tr>
            <td>{c['nom']}</td>
            <td>{c['telephone']}</td>
            <td>{c['type_service']}</td>
            <td>{c['date_rdv']}</td>
            <td><button onclick="envoyerSMS({c['id']}, '{c['nom']}', '{c['telephone']}')" style="background:{couleur};color:white;border:none;padding:8px 15px;cursor:pointer;border-radius:3px;">{texte}</button></td>
        </tr>
        """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Liste des Clients</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial; padding: 30px; background: #f9f9f9; }}
            h1 {{ color: #2c3e50; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
            th {{ background: #2c3e50; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 12px; border-bottom: 1px solid #eee; }}
            tr:hover {{ background: #f5f5f5; }}
            .btn {{ background: #2c3e50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px; display: inline-block; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>Liste des Clients</h1>
        <a href="/" class="btn">+ Nouveau rendez-vous</a>
        <table>
            <tr>
                <th>Nom</th>
                <th>Telephone</th>
                <th>Service</th>
                <th>Date</th>
                <th>SMS</th>
            </tr>
            {rows}
        </table>
        <script>
            function envoyerSMS(id, nom, telephone) {{
                fetch(`/envoyer?nom=${{nom}}&numero=${{encodeURIComponent(telephone)}}&ticket=${{id}}`)
                .then(() => {{
                    fetch(`/marquer-sms/${{id}}`, {{method: 'POST'}});
                    location.reload();
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html, 200

@app.route("/envoyer")
def envoyer():
    nom = request.args.get("nom", "client")
    numero = request.args.get("numero")
    ticket = request.args.get("ticket", "0000")
    if not numero:
        return "Numero manquant!", 400
    envoyer_sms(numero, nom, ticket)
    return "SMS envoye!", 200

@app.route("/marquer-sms/<int:client_id>", methods=["POST"])
def marquer_sms(client_id):
    supabase.table("clients").update({"sms_envoye": True}).eq("id", client_id).execute()
    return {"success": True}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))