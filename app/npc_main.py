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
            npc_response = npc.respond(user_input)
            print(f"Karczmarz: {npc_response}")

        except KeyboardInterrupt:
            print("\nKarczmarz: Wygląda na to, że musisz iść. Do zobaczenia!")
            break
        except Exception as e:
            print("Karczmarz: Coś poszło nie tak. Spróbuj ponownie.")
             

if __name__ == "__main__":
    main()
