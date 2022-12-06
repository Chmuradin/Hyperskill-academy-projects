from db import Task


class ToDoList:
    def __init__(self) -> None:
        self.menu = {
            0: self.quit,
            1: self.tasks_for_today,
            2: self.tasks_for_week,
            3: self.all_tasks,
            4: self.missed_tasks,
            5: self.add_task,
            6: self.delete_task
        }
        self.is_running = True
        self.tasks = []

    def quit(self) -> None:
        self.is_running = False
        print("\nBye!")

    def tasks_for_today(self) -> None:
        self.tasks = Task.find_day(long=False, short=True)
        if not self.tasks:
            print("Nothing to do!")
        else:
            for index, task in enumerate(self.tasks):
                print(f"{index + 1}. {task}")
        print()  # required for test

    def tasks_for_week(self) -> None:
        for i in range(7):
            self.tasks = Task.find_day(td=i)
            if not self.tasks:
                print("Nothing to do!")
            else:
                for index, task in enumerate(self.tasks):
                    print(f"{index + 1}. {task}")
            print()

    def all_tasks(self) -> None:
        self.tasks = Task.find_all()
        for index, task in enumerate(self.tasks):
            print(f'{index + 1}. {task[0]}. {task[1].strftime("%#d %b")}')

    def missed_tasks(self) -> None:
        self.tasks = Task.missed()
        print("Missed tasks:")
        if not self.tasks:
            print("All tasks have been completed!")
        else:
            for index, task in enumerate(self.tasks):
                print(f'{index + 1}. {task[0]}. {task[1].strftime("%#d %b")}')
        print()

    def delete_task(self) -> None:
        self.tasks = Task.find_all()
        print("Choose the number of the task you want to delete:")
        i = 1
        for index, task in enumerate(self.tasks):
            print(f'{index + 1}. {task[0]}. {task[1].strftime("%#d %b")}')
            i += 1
        index = int(input())
        if index in range(i):
            Task.delete_task(index)
            print("The task has been deleted!")
        else:
            print("Wrong input")

    @staticmethod
    def add_task() -> None:
        Task.add_task()
        print("The task has been added!\n")

    def run(self) -> None:
        while self.is_running:
            self.print_menu()
            selection = self.get_menu_selection()
            self.menu[selection]()

    def get_menu_selection(self) -> int:
        while True:
            try:
                user_input = int(input())
                if 0 <= user_input <= len(self.menu) - 1:
                    return user_input
                print("That is not a valid selection.")
            except ValueError:
                print("Error.")

    @staticmethod
    def print_menu() -> None:
        print(("1) Today's tasks\n"
               "2) Week's tasks\n"
               "3) All tasks\n"
               "4) Missed tasks\n"
               "5) Add a task\n"
               "6) Delete a task\n"
               "0) Exit"))


def main() -> None:
    app = ToDoList()
    app.run()


if __name__ == "__main__":
    main()
