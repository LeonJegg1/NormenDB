def tests(question, answer):
    with open("Testfragen.txt", "a", encoding="utf-8") as file:
        file.write(f"{question}\n")
        file.write(f"{answer}\n")
        file.write(f"Bewertung 1-5: {input('Bewertung 1-5:')}\n")
        file.write(f"Begründung: {input('Begründung:')}\n")
        file.write("--------------------------------------------------\n\n")