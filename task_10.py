from datetime import datetime, date
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y").date()
            if date_obj > date.today():
                raise ValueError("Birthday cannot be in the future.")
            self.value = date_obj
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError("Invalid date format. Use DD.MM.YYYY")
            raise e

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday_date):
        self.birthday = Birthday(birthday_date)
        
    def show_birthday(self):
        return self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "Not set"

    def add_phone(self, phone_number):
        phone_obj = Phone(phone_number)
        self.phones.append(phone_obj)

    def remove_phone(self, phone_number):
        for p in self.phones:
            if p.value == phone_number:
                self.phones.remove(p)  
                break      
    
    def edit_phone(self, old_phone, new_phone):
        phone_found = False
        for phone in self.phones:
            if phone.value == old_phone:
                self.phones[self.phones.index(phone)] = Phone(new_phone)
                phone_found = True
                break
        if not phone_found:
            raise ValueError("Phone number not found.")

    def find_phone(self, phone_number):
        for p in self.phones: 
            if p.value == phone_number:
                return p
        return None
                  
    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.show_birthday()}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        key = record.name.value
        self.data[key] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
    
    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming_birthdays = []
        
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                
                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday <= 7:
                    upcoming_birthdays.append({
                        'name': record.name.value,
                        'congratulation_date': birthday_this_year.strftime("%d.%m.%Y")
                    })
        
        return upcoming_birthdays

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {str(e)}"
        except KeyError:
            return "Error: Contact not found."
        except IndexError:
            return "Error: Please provide all required arguments."
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    return inner

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Error: Please provide name and phone."
    name, phone = args[0], args[1]
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        return "Error: Please provide name, old phone and new phone."
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Phone number updated."
    else:
        return "Contact not found."

@input_error
def show_phone(args, book: AddressBook):
    if len(args) < 1:
        return "Error: Please provide name."
    name = args[0]
    record = book.find(name)
    if record:
        phones = ', '.join(phone.value for phone in record.phones)
        return f"{name}: {phones}" if phones else f"{name}: No phones"
    else:
        return "Contact not found."

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    result = "All contacts:\n"
    for i, record in enumerate(book.data.values(), 1):
        result += f"{i}. {record}\n"
    return result.strip()

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        return "Error: Please provide name and birthday."
    name, birthday = args[0], args[1]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book: AddressBook):
    if len(args) < 1:
        return "Error: Please provide name."
    name = args[0]
    record = book.find(name)
    if record:
        return f"{name}'s birthday: {record.show_birthday()}"
    else:
        return "Contact not found."

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays in the next week."
    
    result = "Upcoming birthdays this week:\n"
    for i, user in enumerate(upcoming, 1):
        result += f"{i}. {user['name']}: {user['congratulation_date']}\n"
    return result.strip()

def parse_input(user_input):
    return user_input.strip().split()

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    print("Available commands:")
    print("- add [name] [phone]")
    print("- change [name] [old_phone] [new_phone]") 
    print("- phone [name]")
    print("- all")
    print("- add-birthday [name] [DD.MM.YYYY]")
    print("- show-birthday [name]")
    print("- birthdays")
    print("- hello")
    print("- close/exit")
    
    while True:
        user_input = input("\nEnter a command: ")
        command, *args = parse_input(user_input)
        command = command.lower()

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()



