require("dotenv").config();
console.log("clé API openAI", process.env.OPEN_API_KEY ? "OK" : "Manquante !");

const express = require("express");
const fetch = require("node-fetch");

const app = express();
app.use(express.json());

const apiKey = "uNvGufUo6OPY9g6i6US8uaTHrfh4Sf4q";
const mistralURL = "https://api.mistral.ai/v1/chat/completions";

app.post("/api/chat", async (req, res) => {
    const userMessage = req.body.message;

    if (!userMessage) {
        return res.status(400).json({ error: "Message vide !" });
    }

    try {
        const response = await fetch(mistralURL, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${apiKey}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                model: "mistral-small-latest",
                messages: [{ role: "user", content: userMessage }]
            })
        });

        const data = await response.json();

        if (!data.choices || data.choices.length === 0) {
            throw new Error("Réponse vide de Mistral");
        }

        res.json({ response: data.choices[0].message.content });
    } catch (error) {
        console.error("Erreur API :", error);
        res.status(500).json({ error: "Problème de connexion avec l'IA. Réessaie plus tard." });
    }
});

app.listen(3000, () => console.log("Serveur actif sur http://localhost:3000"));