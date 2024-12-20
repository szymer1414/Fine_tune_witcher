import json
import re
from collections import Counter
from typing import List, Dict
import logging

class NPCKarczmarzMemory:
    def __init__(self, memory_file="npc_memory.json"):
        self.memory_file = memory_file
        # Załadowanie danych pamięci z pliku
        self.data = self.load_memory()
        # Pobranie wiedzy statycznej i pamięci rozmów
        self.knowledge_base = self.data.get("static_knowledge", {}).get("topics", [])
        self.conversation_memory = self.clean_existing_memory(self.data.get("conversation_memory", []))
        self.compressed_summaries = self.data.get("compressed_summaries", [])

    def load_memory(self) -> Dict:
        """Ładowanie pamięci z pliku JSON."""
        try:
            with open(self.memory_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Jeśli plik nie istnieje, zwróć pustą strukturę pamięci
            return {"static_knowledge": {}, "conversation_memory": [], "compressed_summaries": []}

    def save_memory(self):
        """Zapisanie aktualnego stanu pamięci do pliku JSON."""
        self.data["conversation_memory"] = self.conversation_memory
        self.data["compressed_summaries"] = self.compressed_summaries
        with open(self.memory_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def clean_existing_memory(self, conversation_memory: List[Dict]) -> List[Dict]:
        """Oczyszczanie istniejącej pamięci rozmów z poprawieniem tagów."""
        for entry in conversation_memory:
            entry["tags"] = self.extract_tags(entry["summary"])
        return conversation_memory

    def extract_tags(self, text: str) -> List[str]:
        """Dynamiczne określanie najbardziej znaczących tagów z tekstu."""
        # Tokenizacja tekstu i usunięcie znaków interpunkcyjnych
        tokens = re.findall(r'\b\w+\b', text.lower())

        # Zliczanie częstotliwości występowania słów
        token_counts = Counter(tokens)

        # Obliczanie dynamicznego znaczenia dla każdego tokena
        scores = {}
        for i, token in enumerate(tokens):
            scores[token] = scores.get(token, 0) + (1 / token_counts[token]) + (1 / (i + 1))

        # Sortowanie tokenów według obliczonych wyników
        sorted_tokens = sorted(scores.items(), key=lambda item: item[1], reverse=True)

        # Zwrot 5 najważniejszych tokenów jako tagi
        return [token for token, score in sorted_tokens[:5]]

    def add_interaction(self, user_input: str, npc_response: str):
        """Dodanie nowej interakcji do pamięci."""
        # Ekstrakcja tagów z wejścia użytkownika
        tags = self.extract_tags(user_input)
        summary = {
            "summary": f"Gracz pytał: '{user_input}'. Karczmarz odpowiedział: '{npc_response}'.",
            "tags": tags,
            "topic": tags[0] if tags else "unknown"
        }
        self.conversation_memory.append(summary)

        # Sprawdzenie, czy należy skompresować pamięć
        if len(self.conversation_memory) > 20:
            self.compress_memory()

    def compress_memory(self):
        """Kompresja starszych interakcji do podsumowania."""
        to_compress = self.conversation_memory[:20]
        summary = self._generate_summary(to_compress)
        self.compressed_summaries.append(summary)
        self.conversation_memory = self.conversation_memory[20:]

    def _generate_summary(self, interactions: List[Dict]) -> str:
        """Generowanie zwięzłego podsumowania kilku interakcji."""
        summary = "Podsumowanie rozmów:\n"
        for msg in interactions:
            summary += f"{msg['summary']}\n"
        return summary.strip()

    def retrieve_context(self, topic: str = "") -> str:
        """Pobieranie kontekstu opartego na wiedzy statycznej."""
        try:
            static_knowledge = self.data.get("static_knowledge", {})
            description = static_knowledge.get("description", "Nie wiem za wiele...")
            family = static_knowledge.get("family", "Nieznana rodzina")
            return f"Karczmarz: {description}\nRodzina: {family}"
        except Exception as e:
            logging.error(f"Error in retrieve_context: {e}")
            return "Brak danych w pamięci karczmarza."

    def find_relevant_topic(self, user_input: str) -> Dict:
        """Znajdowanie najbardziej odpowiedniego tematu na podstawie wejścia użytkownika."""
        input_tags = self.extract_tags(user_input)
        logging.debug(f"Extracted input tags: {input_tags}")

        best_match = None
        highest_overlap = 0

        for topic in self.data.get("static_knowledge", {}).get("topics", []):
            topic_tags = topic.get("tags", [])
            overlap = len(set(input_tags) & set(topic_tags))
            score = overlap * topic.get("importance", 1)
            if score > highest_overlap:
                best_match = topic
                highest_overlap = score

        if best_match:
            logging.debug(f"Found relevant topic: {best_match['topic']}")
        else:
            logging.debug("No relevant topic found.")

        return best_match

if __name__ == "__main__":
    # Przykładowe uruchomienie i zapis pamięci
    memory = NPCKarczmarzMemory()
    memory.save_memory()
