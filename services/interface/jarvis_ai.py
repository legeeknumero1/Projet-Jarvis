#!/usr/bin/env python3
"""
Jarvis AI Logic - Simple but intelligent responses
Logique IA simple mais intelligente pour Jarvis
"""

import re
import random
from datetime import datetime
import json
import logging
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class JarvisAI:
    def __init__(self):
        self.context = {}
        self.conversation_history = []
        # SUPPRESSION TOTALE DES RÉPONSES PRÉ-DÉFINIES
        # Selon CLAUDE_PARAMS.md règle 13 : INTERDICTION RÉPONSES PRÉ-DÉFINIES
        
    def analyze_intent(self, message: str) -> dict:
        """Analyse l'intention du message utilisateur"""
        message_lower = message.lower()
        
        # Patterns d'intention
        patterns = {
            "greeting": r"(bonjour|salut|hello|hi|slt|coucou|bonsoir)",
            "question_state": r"(comment vas-tu|comment ça va|ça va|comment allez-vous)",
            "question_time": r"(quelle heure|il est quelle heure|heure)",
            "question_date": r"(quelle date|quel jour|on est quel|aujourd'hui)",
            "question_weather": r"(météo|temps|température|pluie|soleil|neige)",
            "question_identity": r"(qui es-tu|qui êtes-vous|tu es qui|c'est quoi)",
            "question_capabilities": r"(que peux-tu|tes capacités|que sais-tu|aide|help)",
            "thanks": r"(merci|thanks|thank you)",
            "goodbye": r"(au revoir|bye|goodbye|à bientôt|tchao)",
            "calculation": r"(calcul|calculer|\+|\-|\*|\/|=)",
            "question_general": r"(pourquoi|comment|quoi|que|qui|où|quand)",
        }
        
        matched_intents = []
        for intent, pattern in patterns.items():
            if re.search(pattern, message_lower):
                matched_intents.append(intent)
        
        return {
            "intents": matched_intents,
            "confidence": len(matched_intents) / len(patterns),
            "message": message,
            "message_lower": message_lower
        }
    
    def generate_contextual_response(self, intent_analysis: dict) -> str:
        """Génère une réponse contextuelle basée sur l'analyse d'intention"""
        intents = intent_analysis["intents"]
        message = intent_analysis["message"]
        message_lower = intent_analysis["message_lower"]
        
        # Salutations
        if "greeting" in intents:
            greetings = [
                "Bonjour ! Je suis J.A.R.V.I.S, votre assistant personnel. Comment puis-je vous aider ?",
                "Salut ! J.A.R.V.I.S à votre service. Que puis-je faire pour vous ?",
                "Bonjour ! Ravi de vous parler. En quoi puis-je vous être utile ?",
                "Hello ! J.A.R.V.I.S est prêt à vous assister. Que souhaitez-vous ?"
            ]
            return random.choice(greetings)
        
        # Questions sur l'état
        if "question_state" in intents:
            states = [
                "Tous mes systèmes sont opérationnels et fonctionnent parfaitement ! Et vous, comment allez-vous ?",
                "Je vais très bien, merci ! Mes circuits sont en parfait état. Comment puis-je vous aider ?",
                "Excellente forme ! Tous mes processeurs tournent à plein régime. Et vous ?",
                "Impeccable ! Mes algorithmes sont optimisés et prêts à vous servir. Comment ça va de votre côté ?"
            ]
            return random.choice(states)
        
        # Questions sur l'heure
        if "question_time" in intents:
            now = datetime.now()
            responses = [
                f"Il est actuellement {now.strftime('%H:%M:%S')}.",
                f"L'heure actuelle est {now.strftime('%H:%M')}.",
                f"Il est {now.strftime('%H:%M:%S')} précisément.",
                f"Selon mes capteurs temporels, il est {now.strftime('%H:%M')}."
            ]
            return random.choice(responses)
        
        # Questions sur la date
        if "question_date" in intents:
            today = datetime.now()
            days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            months = ["janvier", "février", "mars", "avril", "mai", "juin", 
                     "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
            day_name = days[today.weekday()]
            month_name = months[today.month - 1]
            
            responses = [
                f"Nous sommes {day_name} {today.day} {month_name} {today.year}.",
                f"Aujourd'hui, c'est {day_name} {today.strftime('%d/%m/%Y')}.",
                f"Date actuelle : {day_name} {today.day} {month_name} {today.year}.",
                f"Selon mon calendrier, nous sommes {day_name} {today.strftime('%d/%m/%Y')}."
            ]
            return random.choice(responses)
        
        # Questions sur la météo
        if "question_weather" in intents:
            weather_responses = [
                "Je n'ai pas accès aux données météorologiques en temps réel. Je vous recommande de consulter un service météo fiable comme Météo France.",
                "Pour la météo actuelle, je vous suggère de vérifier une application météo ou un site web spécialisé.",
                "Désolé, je ne peux pas vous donner la météo en temps réel. Essayez weather.com ou votre app météo préférée.",
                "Je n'ai pas de capteurs météo intégrés. Consultez un service météorologique pour des informations précises."
            ]
            return random.choice(weather_responses)
        
        # Questions sur l'identité
        if "question_identity" in intents:
            identity_responses = [
                "Je suis J.A.R.V.I.S - Just A Rather Very Intelligent System. Je suis votre assistant personnel IA.",
                "J.A.R.V.I.S, pour vous servir ! Je suis un système d'intelligence artificielle conçu pour vous assister.",
                "Je suis J.A.R.V.I.S, votre assistant IA personnel. Mon rôle est de vous aider dans vos tâches quotidiennes.",
                "J.A.R.V.I.S est mon nom ! Je suis une IA avancée programmée pour être votre assistant personnel."
            ]
            return random.choice(identity_responses)
        
        # Questions sur les capacités
        if "question_capabilities" in intents:
            capability_responses = [
                "Je peux vous aider avec de nombreuses tâches : répondre à vos questions, donner l'heure et la date, discuter avec vous, faire des calculs simples, et bien plus encore !",
                "Mes capacités incluent : assistance conversationnelle, informations temporelles, aide générale, et je suis en constante amélioration !",
                "Je peux discuter avec vous, vous donner l'heure et la date, vous assister dans vos questions, et apprendre de nos conversations !",
                "Je suis capable de : conversation naturelle, calculs, informations temporelles, assistance générale, et je m'améliore constamment !"
            ]
            return random.choice(capability_responses)
        
        # Remerciements
        if "thanks" in intents:
            thanks_responses = [
                "De rien ! C'est un plaisir de vous aider. Y a-t-il autre chose que je puisse faire pour vous ?",
                "Avec plaisir ! Je suis là pour ça. N'hésitez pas si vous avez d'autres questions.",
                "Il n'y a pas de quoi ! Je suis ravi de pouvoir vous être utile.",
                "C'est tout naturel ! Je suis conçu pour vous assister. Que puis-je faire d'autre ?"
            ]
            return random.choice(thanks_responses)
        
        # Au revoir
        if "goodbye" in intents:
            goodbye_responses = [
                "Au revoir ! Ce fut un plaisir de discuter avec vous. À bientôt !",
                "À bientôt ! J'espère que notre conversation vous a été utile.",
                "Au revoir ! J'ai été ravi de vous aider. N'hésitez pas à revenir !",
                "Goodbye ! Passez une excellente journée. J'espère vous revoir bientôt !"
            ]
            return random.choice(goodbye_responses)
        
        # Calculs simples
        if "calculation" in intents:
            try:
                # Recherche d'expressions mathématiques simples
                import re
                math_expr = re.search(r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', message)
                if math_expr:
                    num1, op, num2 = math_expr.groups()
                    num1, num2 = float(num1), float(num2)
                    
                    if op == '+':
                        result = num1 + num2
                    elif op == '-':
                        result = num1 - num2
                    elif op == '*':
                        result = num1 * num2
                    elif op == '/':
                        if num2 != 0:
                            result = num1 / num2
                        else:
                            return "Erreur : division par zéro impossible !"
                    
                    return f"Le résultat de {num1} {op} {num2} est : {result}"
                else:
                    return "Je peux faire des calculs simples ! Essayez quelque chose comme '5 + 3' ou '10 * 2'."
            except:
                return "Je n'ai pas pu effectuer ce calcul. Essayez une expression plus simple comme '2 + 3'."
        
        # Questions générales - réponse intelligente
        if "question_general" in intents:
            question_responses = [
                f"C'est une question intéressante ! Pour '{message}', je pense qu'il faudrait plus de contexte pour vous donner une réponse précise. Pouvez-vous me donner plus de détails ?",
                f"Bonne question ! Concernant '{message}', je vais faire de mon mieux pour vous aider. Pouvez-vous être plus spécifique ?",
                f"Je vois que vous me demandez quelque chose à propos de '{message}'. J'aimerais vous aider davantage - pouvez-vous me donner plus d'informations ?",
                f"Votre question sur '{message}' est pertinente. J'aurais besoin de plus de contexte pour vous donner une réponse complète et utile."
            ]
            return random.choice(question_responses)
        
        # Réponse par défaut intelligente
        default_responses = [
            f"J'ai bien reçu votre message '{message}'. Je suis encore en apprentissage et j'aimerais mieux comprendre ce que vous cherchez. Pouvez-vous me donner plus de détails ?",
            f"Intéressant ! Vous me parlez de '{message}'. Je suis curieux d'en savoir plus. Que souhaitez-vous savoir exactement ?",
            f"Je vois que vous mentionnez '{message}'. J'aimerais vous aider de manière plus précise. Pouvez-vous reformuler votre demande ?",
            f"Votre message '{message}' attire mon attention. J'aimerais vous donner une réponse plus adaptée - pouvez-vous être plus spécifique ?",
            f"Merci pour votre message '{message}'. Je suis là pour vous aider ! Que puis-je faire concrètement pour vous ?",
            f"Je traite votre demande '{message}'. Pour mieux vous assister, pouvez-vous me dire ce que vous attendez de moi ?",
            f"Votre question '{message}' est notée ! J'aimerais vous donner la meilleure réponse possible. Pouvez-vous m'éclairer sur vos attentes ?",
            f"J'analyse votre message '{message}'. Je suis conçu pour vous aider - dites-moi comment je peux vous être utile !",
            f"Votre demande '{message}' me fait réfléchir. Je veux vous donner une réponse pertinente. Pouvez-vous me guider davantage ?",
            f"Je traite l'information '{message}'. J'aimerais être plus précis dans ma réponse. Que cherchez-vous exactement ?"
        ]
        
        return random.choice(default_responses)
    
    def process_message(self, message: str) -> str:
        """SUPPRIMÉ - Seul Ollama avec mémoire autorisé selon CLAUDE_PARAMS.md règle 13"""
        return "Système IA local non disponible. Utilisation d'Ollama requise."
    
    def get_conversation_context(self) -> dict:
        """Retourne le contexte de la conversation"""
        return {
            "history": self.conversation_history,
            "context": self.context,
            "stats": {
                "total_messages": len(self.conversation_history),
                "user_messages": len([m for m in self.conversation_history if m["type"] == "user"]),
                "assistant_messages": len([m for m in self.conversation_history if m["type"] == "assistant"])
            }
        }