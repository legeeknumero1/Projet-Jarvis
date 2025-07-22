#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jeu du Pendu - Créé pour Enzo par Jarvis
"""

import random
import json
from typing import List, Dict, Any

class HangmanGame:
    def __init__(self):
        self.words = [
            "PYTHON", "JARVIS", "INTELLIGENCE", "ORDINATEUR", "PROGRAMMATION",
            "PERPIGNAN", "ASSISTANT", "DOMOTIQUE", "TECHNOLOGIE", "INNOVATION",
            "RIVESALTES", "PYRENEES", "FRANCAIS", "DEVELOPPEUR", "AUTOMATISATION"
        ]
        self.word = ""
        self.guessed_letters = []
        self.wrong_guesses = 0
        self.max_wrong = 6
        self.game_state = "waiting"  # waiting, playing, won, lost
        
    def start_new_game(self) -> Dict[str, Any]:
        """Démarre une nouvelle partie"""
        self.word = random.choice(self.words).upper()
        self.guessed_letters = []
        self.wrong_guesses = 0
        self.game_state = "playing"
        
        return {
            "status": "started",
            "word_length": len(self.word),
            "display": self._get_display_word(),
            "wrong_guesses": self.wrong_guesses,
            "max_wrong": self.max_wrong,
            "guessed_letters": self.guessed_letters,
            "message": f"🎮 Nouveau jeu du pendu commencé ! Mot de {len(self.word)} lettres."
        }
    
    def guess_letter(self, letter: str) -> Dict[str, Any]:
        """Fait une tentative avec une lettre"""
        if self.game_state != "playing":
            return {"error": "Aucun jeu en cours. Tapez 'nouveau jeu' pour commencer."}
        
        letter = letter.upper().strip()
        
        if len(letter) != 1 or not letter.isalpha():
            return {"error": "Veuillez entrer une seule lettre valide."}
        
        if letter in self.guessed_letters:
            return {"error": f"Vous avez déjà essayé la lettre '{letter}'."}
        
        self.guessed_letters.append(letter)
        
        if letter in self.word:
            # Bonne lettre
            if self._is_word_complete():
                self.game_state = "won"
                return {
                    "status": "won",
                    "display": self.word,
                    "message": f"🎉 Félicitations ! Vous avez trouvé le mot '{self.word}' !",
                    "wrong_guesses": self.wrong_guesses,
                    "guessed_letters": self.guessed_letters
                }
            else:
                return {
                    "status": "correct",
                    "display": self._get_display_word(),
                    "message": f"✅ Bonne lettre ! '{letter}' est dans le mot.",
                    "wrong_guesses": self.wrong_guesses,
                    "guessed_letters": self.guessed_letters
                }
        else:
            # Mauvaise lettre
            self.wrong_guesses += 1
            
            if self.wrong_guesses >= self.max_wrong:
                self.game_state = "lost"
                return {
                    "status": "lost",
                    "display": self.word,
                    "message": f"💀 Perdu ! Le mot était '{self.word}'. Essayez encore !",
                    "wrong_guesses": self.wrong_guesses,
                    "guessed_letters": self.guessed_letters
                }
            else:
                remaining = self.max_wrong - self.wrong_guesses
                return {
                    "status": "wrong",
                    "display": self._get_display_word(),
                    "message": f"❌ '{letter}' n'est pas dans le mot. {remaining} essais restants.",
                    "wrong_guesses": self.wrong_guesses,
                    "guessed_letters": self.guessed_letters
                }
    
    def guess_word(self, word_guess: str) -> Dict[str, Any]:
        """Fait une tentative avec un mot complet"""
        if self.game_state != "playing":
            return {"error": "Aucun jeu en cours. Tapez 'nouveau jeu' pour commencer."}
        
        word_guess = word_guess.upper().strip()
        
        if word_guess == self.word:
            self.game_state = "won"
            return {
                "status": "won",
                "display": self.word,
                "message": f"🎉 Excellent ! Vous avez trouvé le mot '{self.word}' !",
                "wrong_guesses": self.wrong_guesses,
                "guessed_letters": self.guessed_letters
            }
        else:
            self.wrong_guesses += 1
            
            if self.wrong_guesses >= self.max_wrong:
                self.game_state = "lost"
                return {
                    "status": "lost",
                    "display": self.word,
                    "message": f"💀 Perdu ! Le mot était '{self.word}', pas '{word_guess}'.",
                    "wrong_guesses": self.wrong_guesses,
                    "guessed_letters": self.guessed_letters
                }
            else:
                remaining = self.max_wrong - self.wrong_guesses
                return {
                    "status": "wrong",
                    "display": self._get_display_word(),
                    "message": f"❌ '{word_guess}' n'est pas le bon mot. {remaining} essais restants.",
                    "wrong_guesses": self.wrong_guesses,
                    "guessed_letters": self.guessed_letters
                }
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne l'état actuel du jeu"""
        if self.game_state == "waiting":
            return {"message": "Aucun jeu en cours. Tapez 'nouveau jeu' pour commencer !"}
        
        return {
            "status": self.game_state,
            "display": self._get_display_word() if self.game_state == "playing" else self.word,
            "wrong_guesses": self.wrong_guesses,
            "max_wrong": self.max_wrong,
            "guessed_letters": self.guessed_letters,
            "hangman": self._get_hangman_drawing()
        }
    
    def _get_display_word(self) -> str:
        """Retourne le mot avec les lettres découvertes"""
        display = ""
        for letter in self.word:
            if letter in self.guessed_letters:
                display += letter + " "
            else:
                display += "_ "
        return display.strip()
    
    def _is_word_complete(self) -> bool:
        """Vérifie si le mot est complètement découvert"""
        for letter in self.word:
            if letter not in self.guessed_letters:
                return False
        return True
    
    def _get_hangman_drawing(self) -> str:
        """Retourne le dessin du pendu selon le nombre d'erreurs"""
        stages = [
            """
            -----
            |   |
                |
                |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
                |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
            |   |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
           /|   |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
           /|\\  |
                |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
           /|\\  |
           /    |
                |
            ========
            """,
            """
            -----
            |   |
            O   |
           /|\\  |
           / \\  |
                |
            ========
            """
        ]
        
        if self.wrong_guesses < len(stages):
            return stages[self.wrong_guesses]
        else:
            return stages[-1]

# Instance globale du jeu
hangman_game = HangmanGame()

def play_hangman(user_input: str) -> str:
    """Interface principale pour jouer au pendu"""
    user_input = user_input.lower().strip()
    
    if "nouveau jeu" in user_input or "commencer" in user_input or "start" in user_input:
        result = hangman_game.start_new_game()
        response = result["message"] + "\n\n"
        response += f"Mot : {result['display']}\n"
        response += f"Erreurs : {result['wrong_guesses']}/{result['max_wrong']}\n\n"
        response += "Tapez une lettre ou un mot complet pour jouer !"
        return response
    
    elif "statut" in user_input or "état" in user_input or "status" in user_input:
        result = hangman_game.get_status()
        if "message" in result:
            return result["message"]
        
        response = f"Mot : {result['display']}\n"
        response += f"Erreurs : {result['wrong_guesses']}/{result['max_wrong']}\n"
        response += f"Lettres essayées : {', '.join(result['guessed_letters'])}\n"
        response += result["hangman"]
        return response
    
    elif len(user_input) == 1 and user_input.isalpha():
        # Tentative avec une lettre
        result = hangman_game.guess_letter(user_input)
        
        if "error" in result:
            return result["error"]
        
        response = result["message"] + "\n\n"
        if result["status"] in ["won", "lost"]:
            response += f"Mot final : {result['display']}\n"
            response += "Tapez 'nouveau jeu' pour rejouer !"
        else:
            response += f"Mot : {result['display']}\n"
            response += f"Erreurs : {result['wrong_guesses']}/{hangman_game.max_wrong}"
        
        return response
    
    elif len(user_input) > 1 and user_input.isalpha():
        # Tentative avec un mot complet
        result = hangman_game.guess_word(user_input)
        
        if "error" in result:
            return result["error"]
        
        response = result["message"] + "\n\n"
        if result["status"] in ["won", "lost"]:
            response += f"Mot final : {result['display']}\n"
            response += "Tapez 'nouveau jeu' pour rejouer !"
        else:
            response += f"Mot : {result['display']}\n"
            response += f"Erreurs : {result['wrong_guesses']}/{hangman_game.max_wrong}"
        
        return response
    
    else:
        return "Instructions du jeu du pendu :\n• 'nouveau jeu' : commencer une partie\n• Tapez une lettre pour deviner\n• Tapez un mot complet pour tenter votre chance\n• 'statut' : voir l'état actuel"

if __name__ == "__main__":
    print("🎮 Jeu du Pendu - Créé par Jarvis pour Enzo")
    print("=" * 40)
    
    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() in ["quitter", "exit", "quit"]:
            print("👋 Au revoir ! Merci d'avoir joué !")
            break
        
        response = play_hangman(user_input)
        print("\n" + response)