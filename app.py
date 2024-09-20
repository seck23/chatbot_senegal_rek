from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
from langdetect import detect
import torch

app = Flask(__name__)

# Charger le modèle DialoGPT et le tokenizer
model_name = "microsoft/DialoGPT-medium"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Base de connaissances sur le tourisme au Sénégal
tourism_knowledge_base = {
      "saly": {
        "fr": "Saly est une station balnéaire prisée sur la Petite Côte, avec des plages de sable doré, des hôtels de luxe, des clubs de golf et une vie nocturne animée. C’est aussi une destination idéale pour les amateurs de sports nautiques comme le jet-ski, la planche à voile, et la pêche en haute mer.",
        "en": "Saly is a popular seaside resort on the Petite Côte, featuring golden sandy beaches, luxury hotels, golf clubs, and a vibrant nightlife. It is also a perfect destination for water sports enthusiasts like jet skiing, windsurfing, and deep-sea fishing."
    },
    "lac rose": {
        "fr": "Le Lac Rose, aussi appelé Lac Retba, est célèbre pour sa teinte rosée due à la présence d’algues microscopiques et sa forte concentration en sel. Ce site est également une étape finale du célèbre Rallye Dakar, et l’exploitation du sel y est une activité économique clé.",
        "en": "The Pink Lake, also known as Lake Retba, is famous for its pink hue caused by microscopic algae and its high salt concentration. The site is also the final stage of the famous Dakar Rally, and salt extraction is a key economic activity here."
    },
    "cap skirring": {
        "fr": "Cap Skirring, en Casamance, est un paradis tropical avec des plages bordées de cocotiers, des eaux cristallines et des villages de pêcheurs. C’est une destination idéale pour la détente, le tourisme balnéaire, ainsi que pour découvrir la culture Diola à travers ses traditions et sa gastronomie.",
        "en": "Cap Skirring, in Casamance, is a tropical paradise with palm-lined beaches, crystal-clear waters, and fishing villages. It’s an ideal destination for relaxation, beach tourism, and discovering Diola culture through its traditions and gastronomy."
    },
    "kafountine": {
        "fr": "Kafountine est un village côtier paisible en Casamance, avec des plages sauvages et une riche biodiversité. Ce village est aussi réputé pour son festival de musique traditionnel et ses initiatives écotouristiques.",
        "en": "Kafountine is a peaceful coastal village in Casamance with wild beaches and rich biodiversity. This village is also known for its traditional music festival and ecotourism initiatives."
    },
    "king fahd palace": {
        "fr": "Situé à Dakar, cet hôtel de luxe offre des vues sur l'océan Atlantique, un service haut de gamme et des installations modernes.",
        "en": "Located in Dakar, this luxury hotel offers views of the Atlantic Ocean, top-notch service, and modern facilities."
    },
    "lamantin beach": {
        "fr": "À Saly, cet hôtel 5 étoiles propose des chambres luxueuses, un spa, et une plage privée, idéal pour des vacances de détente.",
        "en": "In Saly, this 5-star hotel offers luxurious rooms, a spa, and a private beach, perfect for a relaxing vacation."
    },
    "les alizés": {
        "fr": "Un hôtel de luxe à Cap Skirring avec des bungalows confortables, une vue sur l'océan, et un spa pour une relaxation totale.",
        "en": "A luxury hotel in Cap Skirring with comfortable bungalows, ocean views, and a spa for total relaxation."
    },
    "ecolodge de sédhiou": {
        "fr": "Un écolodge respectueux de l'environnement, situé au bord du fleuve Casamance, offrant des activités écotouristiques.",
        "en": "An eco-friendly lodge on the banks of the Casamance River, offering ecotourism activities."
    },
    "goree": {
        "fr": "L'Île de Gorée est un site historique où l'on peut visiter la Maison des Esclaves, symbole puissant de la traite des esclaves.",
        "en": "Gorée Island is a historical site where you can visit the House of Slaves, a powerful symbol of the slave trade."
    },
    "monument de la renaissance africaine": {
        "fr": "Cette statue de 49 mètres à Dakar célèbre la renaissance africaine et offre une vue panoramique sur la ville.",
        "en": "This 49-meter statue in Dakar celebrates African renaissance and offers a panoramic view of the city."
    },
    "pont faidherbe": {
        "fr": "Le Pont Faidherbe est un symbole emblématique de Saint-Louis, reliant l'île au continent.",
        "en": "The Faidherbe Bridge is an iconic symbol of Saint-Louis, connecting the island to the mainland."
    },
    "ziguinchor": {
        "fr": "Capitale de la Casamance, Ziguinchor est riche en histoire coloniale, avec des marchés animés et une culture vibrante.",
        "en": "The capital of Casamance, Ziguinchor, is rich in colonial history, with bustling markets and vibrant culture."
    },
    "lac rose": {
        "fr": "Le Lac Rose, également appelé Lac Retba, est célèbre pour sa couleur rose unique due à la forte concentration de sel.",
        "en": "The Pink Lake, also known as Lake Retba, is famous for its unique pink color due to its high salt concentration."
    },
    "parc national du niokolo-koba": {
        "fr": "Un des plus grands parcs nationaux d'Afrique de l'Ouest, abritant des lions, des éléphants, et une grande diversité de faune.",
        "en": "One of the largest national parks in West Africa, home to lions, elephants, and a wide variety of wildlife."
    },
    "delta du saloum": {
        "fr": "Un labyrinthe de mangroves, lagunes et îles, idéal pour l'observation des oiseaux, la pêche, et les excursions en pirogue.",
        "en": "A maze of mangroves, lagoons, and islands, perfect for birdwatching, fishing, and pirogue excursions."
    },
    "parc national de la langue de barbarie": {
        "fr": "Un site naturel spectaculaire avec une biodiversité riche, parfait pour observer les oiseaux migrateurs.",
        "en": "A spectacular natural site with rich biodiversity, perfect for observing migratory birds."
    },
    "forêt de diola": {
        "fr": "Les forêts tropicales de Casamance offrent des randonnées guidées pour découvrir une biodiversité unique.",
        "en": "The tropical forests of Casamance offer guided hikes to discover unique biodiversity."
    },
    "touba": {
        "fr": "Touba est le centre du Mouridisme, avec la Grande Mosquée et le Grand Magal, un pèlerinage annuel attirant des millions de fidèles.",
        "en": "Touba is the center of Mouridism, with the Grand Mosque and the Grand Magal, an annual pilgrimage attracting millions of devotees."
    },
    "tivaouane": {
        "fr": "Tivaouane est le centre de la confrérie Tijaniyya au Sénégal, célèbre pour le Gamou, célébrant la naissance du prophète Mahomet.",
        "en": "Tivaouane is the center of the Tijaniyya brotherhood in Senegal, famous for the Gamou, celebrating the birth of Prophet Muhammad."
    },
    "popenguine": {
        "fr": "Popenguine est un lieu de pèlerinage catholique important, connu pour sa basilique Notre-Dame de la Délivrance.",
        "en": "Popenguine is an important Catholic pilgrimage site, known for its Notre-Dame de la Délivrance basilica."
    },
    "musique et danse": {
        "fr": "Le Sénégal est célèbre pour le Mbalax, popularisé par Youssou N'Dour, et les danses traditionnelles comme le Sabar.",
        "en": "Senegal is famous for Mbalax, popularized by Youssou N'Dour, and traditional dances like the Sabar."
    },
    "artisanat": {
        "fr": "Le village artisanal de Soumbédioune à Dakar est un lieu incontournable pour découvrir les sculptures en bois, les peintures sous-verre, et les bijoux traditionnels.",
        "en": "The Soumbédioune craft village in Dakar is a must-visit for wooden sculptures, glass paintings, and traditional jewelry."
    },
    "thiéboudienne": {
        "fr": "Plat national du Sénégal, composé de poisson mariné, de riz et de légumes, cuit dans une sauce tomate épicée.",
        "en": "The national dish of Senegal, consisting of marinated fish, rice, and vegetables, cooked in a spicy tomato sauce."
    },
    "yassa": {
        "fr": "Un plat mariné à base de citron, d'oignons et de moutarde, souvent préparé avec du poulet ou du poisson.",
        "en": "A marinated dish with lemon, onions, and mustard, often made with chicken or fish."
    },
    "mafé": {
        "fr": "Ragoût à base de pâte d'arachide, généralement accompagné de riz et servi avec du poulet, du bœuf ou de l'agneau.",
        "en": "A stew made from peanut paste, usually served with rice and chicken, beef, or lamb."
    },
    "bissap": {
        "fr": "Le Bissap (jus d'hibiscus) est une boisson populaire et rafraîchissante au Sénégal.",
        "en": "Bissap (hibiscus juice) is a popular and refreshing drink in Senegal."
    },
    "bouye": {
        "fr": "Le Bouye (jus de baobab) est une autre boisson traditionnelle très appréciée au Sénégal.",
        "en": "Bouye (baobab juice) is another traditional drink widely enjoyed in Senegal."
    },
    "lutte sénégalaise": {
        "fr": "La lutte sénégalaise est le sport national, avec des combats accompagnés de chants et de danses traditionnelles.",
        "en": "Senegalese wrestling is the national sport, with matches accompanied by traditional songs and dances."
    },
    "football": {
        "fr": "Le football est très populaire au Sénégal, avec des joueurs comme Sadio Mané. Le Stade Léopold Sédar Senghor est le principal stade du pays.",
        "en": "Football is very popular in Senegal, with players like Sadio Mané. The Léopold Sédar Senghor Stadium is the country's main stadium."
    },
    "courses de pirogues": {
        "fr": "Compétitions traditionnelles spectaculaires dans les villages de pêcheurs comme Saint-Louis et Ziguinchor.",
        "en": "Spectacular traditional competitions in fishing villages like Saint-Louis and Ziguinchor."
    },
     
    "plages": {
        "fr": "Les plages populaires du Sénégal incluent la plage de Saly, la plage de Ngor, la plage de Yoff, et la plage de Cap Skiring.",
        "en": "Popular beaches in Senegal include Saly beach, Ngor beach, Yoff beach, and Cap Skiring beach."
    },
     "sites": {
        "fr": "Les sites touristiques au Sénégal incluent l'Île de Gorée, le Lac Rose, le Parc National du Niokolo-Koba, les Îles de la Madeleine, Saint-Louis, et la Casamance.",
        "en": "Tourist sites in Senegal include Gorée Island, the Pink Lake, Niokolo-Koba National Park, the Madeleine Islands, Saint-Louis, and Casamance."
    },
    "endroits chic": {
        "fr": "Les endroits chics au Sénégal incluent l'Hôtel Radisson Blu et La Villa à Dakar, le Lamantin Beach Hotel et Royal Saly à Saly, l'Hôtel Les Alizés et Le Bougainvillier à Cap Skiring, l'Hôtel La Residence et Le Quai des Artistes à Saint-Louis, et le Ngor Diarama et Le Ciel d'Afrique à Ngor.",
        "en": "Chic places in Senegal include Radisson Blu Hotel and La Villa in Dakar, Lamantin Beach Hotel and Royal Saly in Saly, Hotel Les Alizés and Le Bougainvillier in Cap Skiring, Hotel La Residence and Le Quai des Artistes in Saint-Louis, and Ngor Diarama and Le Ciel d'Afrique in Ngor."
    },
    "rallye du sénégal": {
        "fr": "Course de voitures tout-terrain à travers les paysages variés du pays, incluant des dunes de sable et des savanes.",
        "en": "An off-road car race across the country's varied landscapes, including sand dunes and savannahs."
    }
}

# Réponses pré-programmées pour les salutations et questions générales
general_responses = {
    "bonjour": {
        "fr": "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
        "en": "Hello! How can I assist you today?"
    },
    "hi": {
        "fr": "Salut ! Comment puis-je vous aider aujourd'hui ?",
        "en": "Hi! How can I assist you today?"
    },
    "comment ça va": {
        "fr": "Je suis un chatbot, donc je n'ai pas de sentiments, mais je suis prêt à vous aider !",
        "en": "I'm a chatbot, so I don't have feelings, but I'm here to help!"
    },
    "how are you": {
        "fr": "Je suis un chatbot, donc je n'ai pas de sentiments, mais je suis prêt à vous aider !",
        "en": "I'm a chatbot, so I don't have feelings, but I'm here to help!"
    }
}


# Fonction de détection de langue
def detect_language(text):
    try:
        lang = detect(text)
        if lang == "fr":
            return "fr"
        elif lang == "en":
            return "en"
        else:
            return "fr"  # Par défaut
    except:
        return "fr"  # Si la détection échoue

# Générer des réponses
def generate_response(prompt, language):
    for key, responses in general_responses.items():
        if key in prompt.lower():
            return responses[language]
    
    for keyword, response in tourism_knowledge_base.items():
        if keyword in prompt.lower():
            return response[language]
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    if inputs["input_ids"].size(1) == 0:
        return "Désolé, je n'ai pas compris."
    
    outputs = model.generate(inputs["input_ids"], max_length=100, pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(outputs[:, inputs["input_ids"].shape[-1]:][0], skip_special_tokens=True)

# Route pour le chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")
    language = detect_language(user_input)
    response = generate_response(user_input, language)
    return jsonify({"response": response})

# Route pour l'interface
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
