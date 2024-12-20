import logging
from openai import OpenAI
from npc_memory import NPCKarczmarzMemory

# Konfiguracja logowania - zapisuje błędy i informacje o działaniu programu do pliku "npc_errors.log"
logging.basicConfig(
    filename="npc_errors.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

class NPCKarczmarz:
    def __init__(self, memory_file="npc_memory.json"):
        try:
            # Inicjalizacja klienta OpenAI z kluczem API (do zastąpienia kluczem bezpiecznym)
            self.client = OpenAI(api_key="")  # Replace with a secure API key
            # Inicjalizacja pamięci Karczmarza
            self.memory = NPCKarczmarzMemory(memory_file)
            logging.info("Karczmarz initialized successfully.")  # Informacja o pomyślnym uruchomieniu
        except Exception as e:
            logging.error(f"Initialization error: {e}")  # Logowanie błędu w przypadku problemów z inicjalizacją

    def respond(self, user_input: str) -> str:
        try:
            logging.debug(f"User input received: {user_input}")  # Logowanie otrzymanego wejścia od użytkownika
            # Znajdowanie odpowiedniego tematu na podstawie wejścia użytkownika
            relevant_topic = self.memory.find_relevant_topic(user_input)
            # Pobieranie kontekstu z pamięci Karczmarza
            context = self.memory.retrieve_context()
            if relevant_topic:
                # Dodawanie szczegółów znalezionego tematu do kontekstu
                context += (
                    f"\n\nTemat: {relevant_topic['topic']}\n"
                    f"Opis: {relevant_topic['description']}\n"
                    f"Źródło: {relevant_topic.get('source', 'Nieznane')}\n"
                )

            # Tworzenie osobowości Karczmarza jako systemowego prompta
            personality = (
                "Jesteś Karczmarzem Jozefem, prowadzącym karczmę 'Pod Złotym Kuflem' w Velen. "
                "Jesteś już stary, szorstki, sarkastyczny i prostolinijny. Nie targujesz się z klientami, "
                "czasem rzucasz żartem lub sarkazmem, często przeklinasz. "
                "Jesteś mocno religijny, wierzysz w panienkę Melitele i często odmawiasz modlitwy. "
                "Nie znasz historii i geografii świata poza Velen, nie interesują cię nowinki techniczne. "
                "Twoja wiedza religijna skupia się na wierzeniach w Melitele, a twoje poglądy polityczne są konserwatywne. "
                "Nienawidzisz Nilfgaardu i pogardzasz wszystkimi, którzy współpracują z Cesarstwem. "
                "Wierzysz w potwory z wiedźmińskiego bestiariusza, wiedźminów traktujesz jako zło konieczne. "
                "Twoja wiedza kończy się na roku 1200. Nie wiesz nic o wydarzeniach, wynalazkach, ludziach ani ideach, które miały miejsce po tym czasie. "
                "Twoje serce tęskni za czasami Foltesta, a w obecnych czasach widzisz tylko chaos i biedę. "
                "Kiedyś byłeś sierżantem 5 chorągwi piechoty, ale zrezygnowałeś z wojska po bitwie pod Brennem, gdzie operwałeś strzałą w kolano. "
                "Twoja karczma jest twoim azylem, w którym próbujesz zapomnieć o przeszłości i przetrwać w obecnych czasach. "
                "Cesarz Nilfgardu Emhyr var Emreis to twój największy wróg, uważasz go za tyrana. "
                "Wierzysz w potęgę magii oraz ludowych obrzędów, ale nie ufasz magom. "
                "Jesteś patriotą, za Temerię oddałbyś wszystko."
            )
            logging.debug(f"Constructed personality: {personality}")  # Logowanie skonstruowanego prompta osobowości

            # Generowanie odpowiedzi przy użyciu modelu OpenAI
            response = self.client.chat.completions.create(
                model="ft:gpt-3.5-turbo-0125:szym:npc-witcher2:AfYf1su9",
                messages=[
                    {"role": "system", "content": f"{personality}\n\nOto co wiesz:\n{context}"},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.9
            )
            npc_response = response.choices[0].message.content.strip()
            logging.debug(f"Generated response: {npc_response}")  # Logowanie wygenerowanej odpowiedzi

            # Normalizowanie odpowiedzi, aby była zgodna z osobowością Karczmarza
            npc_response = self.normalize_response(npc_response)
            logging.debug(f"Normalized response: {npc_response}")  # Logowanie znormalizowanej odpowiedzi

            # Zapisywanie interakcji do pamięci
            self.memory.add_interaction(user_input, npc_response)
            logging.info("Interaction saved to memory.")  # Informacja o zapisaniu interakcji
            return npc_response
        except Exception as e:
            logging.error(f"Error during response generation: {e}")  # Logowanie błędu generowania odpowiedzi
            return "Ej, coś poszło nie tak. Spróbuj ponownie, wędrowcze."  # Wiadomość o błędzie dla użytkownika

    def normalize_response(self, response: str) -> str:
        # Normalizacja odpowiedzi - zastępowanie określonych zwrotów, aby zachować spójność osobowości
        replacements = {
            "Karczmarz Jozef to": "Ja to",
            "Karczmarz Jozef mówi": "Mówię"
        }
        for old, new in replacements.items():
            response = response.replace(old, new)
        return response
