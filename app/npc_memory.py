import json
import re
from collections import Counter
from typing import List, Dict
import logging

class NPCKarczmarzMemory:
    def __init__(self, memory_file="npc_memory.json"):
        self.memory_file = memory_file
        self.data = self.load_memory()
        self.current_context = ""
        self.recent_topics = []
        self.priority_keywords = {
            "Temeria", "Emhyr","Nilfgard", "Foltest" "suwerenność", "zniewolenie", "karczma", "Melitele", "Wojna", "Piwo"}
        self.knowledge_base = self.data.get("static_knowledge", {}).get("topics", [])
        self.conversation_memory = self.clean_existing_memory(self.data.get("conversation_memory", []))
        self.compressed_summaries = self.data.get("compressed_summaries", [])
   
    def update_context(self, user_input: str, npc_response: str):
        """Update the current context based on the latest interaction."""
        tags = self.extract_tags(user_input, npc_response)
        if tags:
            self.current_context = tags[0]
            self.recent_topics.append(self.current_context)  
            if len(self.recent_topics) > 5:  # Limit to the last 5 topics
                self.recent_topics.pop(0)
        else:
            self.current_context = ""
    def retrieve_context(self) -> str:
        """Retrieve the current context for use in NPC responses."""
        return self.current_context or "Brak aktywnego tematu rozmowy."
    def load_memory(self) -> Dict:
        try:
            with open(self.memory_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logging.warning(f"Memory file '{self.memory_file}' not found. Initializing empty memory.")
            return {"static_knowledge": {}, "conversation_memory": [], "compressed_summaries": []}

    def save_memory(self):
        self.data["conversation_memory"] = self.conversation_memory
        self.data["compressed_summaries"] = self.compressed_summaries
        with open(self.memory_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def clean_existing_memory(self, conversation_memory: List[Dict]) -> List[Dict]:
        for entry in conversation_memory:
            user_input = entry.get("summary", "").split(".")[0].replace("Gracz pytał: '", "").replace("'.", "")
            npc_response = entry.get("npc_response", "")
            entry["tags"] = self.extract_tags(user_input, npc_response)
        return conversation_memory

    def extract_tags(self, user_input: str, npc_response: str) -> List[str]:
        combined_text = f"{user_input} {npc_response}".lower()
        tokens = re.findall(r'\b\w+\b', combined_text)
        stopwords = {"a", "co", "to", "i", "w", "na", "do", "z", "za", "po", "ze", "o", "się", "czy"}
        filtered_tokens = [word for word in tokens if word not in stopwords and len(word) > 2]
        token_counts = Counter(filtered_tokens)
        scores = {}
        for i, token in enumerate(filtered_tokens):
            base_score = (1 / token_counts[token]) + (1 / (i + 1))
            boost = 2 if token in self.priority_keywords else 1
            scores[token] = scores.get(token, 0) + base_score * boost
        sorted_tokens = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return [token for token, score in sorted_tokens[:5]]

    def add_interaction(self, user_input: str, npc_response: str):
        tags = self.extract_tags(user_input, npc_response)
        summary = {
            "summary": f"Gracz pytał: '{user_input}'. Karczmarz odpowiedział: '{npc_response}'.",
            "tags": tags,
            "topic": tags[0] if tags else "unknown",
            "npc_response": npc_response
        }
        self.conversation_memory.append(summary)
        #self.update_context(user_input, npc_response)
        if len(self.conversation_memory) > 4:
            self.conversation_memory.pop(0)

    def compress_memory(self):
     if len(self.conversation_memory) > 20:
        # Get the oldest 10 interactions
        to_compress = self.conversation_memory[:10]

        # Generate a compressed summary retaining half the information
        summary = self._generate_half_summary(to_compress)
        
        # Append the compressed summary to compressed_summaries
        self.compressed_summaries.append(summary)

        # Remove the oldest 10 interactions
        self.conversation_memory = self.conversation_memory[10:]
    def _generate_half_summary(self, interactions: List[Dict]) -> str:
        """Generate a concise summary retaining half of the information."""
        summary = "Podsumowanie rozmów (skrócone):\n"
        for i, msg in enumerate(interactions):
            # Retain every second message's summary
            if i % 2 == 0:  # Adjust retention ratio as needed
                summary += f"{msg['summary']}\n"
        return summary.strip()

    def _generate_summary(self, interactions: List[Dict]) -> str:
        summary = "Podsumowanie rozmów:\n"
        for msg in interactions:
            summary += f"{msg['summary']}\n"
        return summary.strip()

    def retrieve_context(self, topic: str = "") -> str:
        try:
            static_knowledge = self.data.get("static_knowledge", {})
            description = static_knowledge.get("description", "Nie wiem za wiele...")
            family = static_knowledge.get("family", "Nieznana rodzina")
            return f"Karczmarz: {description}\nRodzina: {family}"
        except Exception as e:
            logging.error(f"Error in retrieve_context: {e}")
            return "Brak danych w pamięci karczmarza."

    def find_relevant_topic(self, user_input: str) -> Dict:
        input_tags = self.extract_tags(user_input, "")
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
    memory = NPCKarczmarzMemory()
    memory.save_memory()