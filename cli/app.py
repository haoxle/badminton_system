from core.player import PlayerRegistry
from cli.prompts import prompt_choice
from cli.registry_flows import register_player_flow, list_players_flow
from cli.session_flows import (
    SessionState,
    add_attendee_flow,
    show_attendees_flow,
    remove_attendee_flow,
    start_session_flow,
    show_courts_flow,
    complete_court_flow,
    show_games_played_flow,
    pause_attendee_flow,
    unpause_attendee_flow,
)


def session_menu(registry: PlayerRegistry) -> None:
    state = SessionState()
    print("\n=== Session (lobby) ===")

    while True:
        if state.phase == "lobby":
            print("\nSession Lobby:")
            print("1) Add attendee from database")
            print("2) Show attendees")
            print("3) Remove attendee")
            print("4) Register new player (mid-session)")
            print("5) Start session (auto-allocate courts)")
            print("0) End session and return to main menu")

            choice = prompt_choice("Choose an option: ", {"1", "2", "3", "4", "5", "0"})

            if choice == "1":
                add_attendee_flow(registry, state)
            elif choice == "2":
                show_attendees_flow(registry, state)
            elif choice == "3":
                remove_attendee_flow(registry, state)
            elif choice == "4":
                register_player_flow(registry)
            elif choice == "5":
                start_session_flow(registry, state)
                if state.phase == "running":
                    print("\n=== Session (running) ===")
                    show_courts_flow(state)
                    input("\nPress Enter to return to the menu...")
            elif choice == "0":
                print("Ending session.")
                break

        else:
            print("\nSession Running:")
            print("1) Show courts")
            print("2) Mark court finished (rotate players)")
            print("3) Show games played")
            print("4) Add attendee (late arrival)")
            print("5) Remove attendee (leaving)")
            print("6) Pause attendee")
            print("7) Unpause attendee")
            print("0) End session and return to main menu")

            choice = prompt_choice("Choose an option: ", {"1", "2", "3", "4", "5", "6", "7", "0"})

            if choice == "1":
                show_courts_flow(state)
                input("\nPress Enter to return to the menu...")
            elif choice == "2":
                complete_court_flow(registry, state)
                input("\nPress Enter to return to the menu...")
            elif choice == "3":
                show_games_played_flow(registry, state)
                input("\nPress Enter to return to the menu...")
            elif choice == "4":
                add_attendee_flow(registry, state)
                input("\nPress Enter to return to the menu...")
            elif choice == "5":
                remove_attendee_flow(registry, state)
                input("\nPress Enter to return to the menu...")
            elif choice == "6":
                pause_attendee_flow(state)
                input("\nPress Enter to return to the menu...")
            elif choice == "7":
                unpause_attendee_flow(state)
                input("\nPress Enter to return to the menu...")
            elif choice == "0":
                print("Ending session.")
                break


def run(registry: PlayerRegistry) -> None:
    print("Welcome to the Badminton System")

    while True:
        print("\nMain Menu:")
        print("1) Register player")
        print("2) List players")
        print("3) Start / Enter session")
        print("0) Exit")

        choice = prompt_choice("Choose an option: ", {"1", "2", "3", "0"})

        if choice == "1":
            register_player_flow(registry)
        elif choice == "2":
            list_players_flow(registry)
        elif choice == "3":
            session_menu(registry)
        elif choice == "0":
            print("Goodbye.")
            break
