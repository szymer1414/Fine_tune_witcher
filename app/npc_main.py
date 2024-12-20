from npc_character import NPCKarczmarz

def main():
    npc = NPCKarczmarz()

    print("Karczmarz: Witaj w mojej karczmie! Co cię tu sprowadza?")
    while True:
        try:
            user_input = input("Ty: ")
            if user_input.lower() in ["koniec", "wyjdz"]:
                print("Karczmarz: Do zobaczenia, wędrowcze!")
                npc.memory.save_memory()  # Save memory on exit
                break
            elif user_input.lower() in ["zapisz", "zapisz i wyjdź"]:
                npc.memory.save_memory()
                print("Karczmarz: Pamięć zapisana. Do zobaczenia, wędrowcze!")
                break

            npc_response = npc.respond(user_input)
            print(f"Karczmarz: {npc_response}")

        except KeyboardInterrupt:
            print("\nKarczmarz: Wygląda na to, że musisz iść. Do zobaczenia!")
            npc.memory.save_memory()  # Save memory on forced exit
            break
        except Exception as e:
            print("Karczmarz: Coś poszło nie tak. Spróbuj ponownie.")
            npc.memory.save_memory()  # Save memory to ensure no data loss

if __name__ == "__main__":
    main()
