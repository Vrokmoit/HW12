from collections import UserDict
from datetime import datetime
import json

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value=None):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, phone):
        if phone is not None and not Phone.validate_phone(phone):
            raise ValueError("Phone number must be 10 digits")
        self._value = phone

    @staticmethod
    def validate_phone(phone):
        return len(phone) == 10 and phone.isdigit()

class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, birthday):
        if birthday is not None and not self.validate_birthday(birthday):
            raise ValueError("Invalid birthday format. Use YYYY-MM-DD")
        self._value = birthday

    def validate_birthday(self, birthday):
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            year, month, day = map(int, birthday.split("-"))
            return (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31)
        except ValueError:
            return False

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        if phone is not None:
            if Phone.validate_phone(phone):
                self.phones.append(Phone(phone))
            else:
                raise ValueError("Phone number must be 10 digits")

    def remove_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                self.phones.remove(phone)
                return

    def edit_phone(self, name, new_phone):
        found_contact = None
        for contact in self.phones:
            if contact.value == name:
                found_contact = contact
                break

        if found_contact is None:
            raise ValueError(f"Contact '{name}' not found")

        if new_phone is not None and not Phone.validate_phone(new_phone):
            raise ValueError("Phone number must be 10 digits")

        found_contact.value = new_phone

    def find_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                return phone
        return None

    def days_to_birthday(self):
        if self.birthday.value:
            today = datetime.now()
            birth_date = datetime.strptime(self.birthday.value, "%Y-%m-%d")
            next_birthday = datetime(today.year, birth_date.month, birth_date.day)
            if next_birthday < today:
                next_birthday = datetime(today.year + 1, birth_date.month, birth_date.day)
            days_left = (next_birthday - today).days
            return days_left
        else:
            return None

    def __str__(self):
        phones_str = ", ".join([phone.value for phone in self.phones])
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday.value}"

    def serialize(self):
        return {
            'name': self.name.value,
            'phones': [phone.value for phone in self.phones],
            'birthday': self.birthday.value,
        }  

    @classmethod
    def deserialize(cls, data):
        name = data['name']
        phones = data['phones']
        birthday = data['birthday']
        record = cls(name, birthday)
        for phone in phones:
            record.add_phone(phone)
        return record

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def find(self, name):
        if name in self.data:
            return self.data[name]

    def iterator(self, batch_size=1):
        data_values = list(self.data.values())
        for i in range(0, len(data_values), batch_size):
            yield data_values[i:i + batch_size]
    
    def save_to_file(self, filename):
        with open(filename, 'w') as file:
            data = {
                'contacts': [record.serialize() for record in self.data.values()],
            }
            json.dump(data, file)

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            self.data = {record['name']: Record.deserialize(record) for record in data['contacts']}

    def search_contacts(self, query):
        results = []
        for contact in self.data.values():
            if (query in contact.name.value) or any(query in phone.value for phone in contact.phones):
                results.append(contact)
        return results

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name"
        except ValueError as e:
            return str(e)
        except IndexError as e:
            if "unpack" in str(e):
                return "Give me name and phone please"
            else:
                return "Invalid input"
        except Exception as e:
            return str(e)
    return wrapper

@input_error
def add_contact(name, *phones_and_birthday):
    phones = []
    birthday = None

    for arg in phones_and_birthday:
        if "-" in arg:
            try:
                datetime.strptime(arg, "%Y-%m-%d")
                birthday = arg
            except ValueError:
                pass
        else:
            phones.append(arg)

    record = Record(name, birthday)
    for phone in phones:
        record.add_phone(phone)
    address_book.add_record(record)
    return "Contact added successfully"

@input_error
def change_phone(name, phone):
    if name in address_book.data:
        if not phone:
            raise ValueError("Phone is missing")
        record = address_book[name]
        record.edit_phone(record.phones[0].value, phone)
        return "Phone number updated"
    else:
        raise ValueError(f"Contact '{name}' not found")

@input_error
def find_phone(name):
    if name in address_book.data:
        record = address_book[name]
        phones = [phone.value for phone in record.phones]
        if phones:
            return phones
        else:
            return f"No phones found for contact '{name}'"
    else:
        raise ValueError(f"Contact '{name}' not found")


def show_all_contacts():
    data = address_book.data
    if not data:
        return "No contacts found"
    else:
        result = "\n".join([str(record) for record in data.values()])
        return result

def show_contacts_batch(batch_size=1):
    data = address_book.data
    if not data:
        return "No contacts found"
    else:
        result = [str(record) for record in data.values()]
        for idx, r in enumerate(result):
            print(r)
            if (idx + 1) % batch_size == 0 and idx < len(result) - 1:
                input("Press Enter to continue...")
        return ""


def main():
    print("How can I help you?")
    
    while True:
        command = input("Enter a command: ").lower()
        
        if command == "hello":
            print("How can I help you?")
        elif command.startswith("add "):
            _, *rest = command.split()
            if len(rest) < 2:
                print("Enter at least name and phone")
                continue
            name = rest[0]
            phone = rest[1]
            if len(rest) > 2:
                birthday = rest[2]
                response = add_contact(name, phone, birthday)
            else:
                response = add_contact(name, phone)
            print(response)
        elif command.startswith("change "):
            _, name, *phone = command.split()
            phone = " ".join(phone)
            response = change_phone(name, phone)
            print(response)
        elif command.startswith("phone "):
            _, name = command.split()
            try:
                response = find_phone(name)
                print(response)
            except Exception as e:
                print(e)
        elif command == "show all":
            result = show_all_contacts()
            print(result)
        elif command.startswith("birthday "):
            _, name = command.split()
            try:
                contact = address_book.find(name)
                if contact:
                    response = contact.days_to_birthday()
                    print(response)
                else:
                    print(f"Contact '{name}' not found")
            except Exception as e:
                print(e)
        elif command.startswith("delete "):
            _, name = command.split()
            try:
                address_book.delete(name)
                print(f"Contact '{name}' deleted successfully")
            except KeyError:
                print(f"Contact '{name}' not found")
        elif command.startswith("show batch"):
            parts = command.split()
            if len(parts) == 3 and parts[2].isdigit():
                batch_size = int(parts[2])
                results = show_contacts_batch(batch_size)
                for result in results:
                    print(result)
            else:
                print("Invalid 'show batch' command. Use 'show batch N', where N is the batch size.")
        elif command == "save":
            filename = input("Enter the filename to save the address book: ")
            address_book.save_to_file(filename)
            print(f"Address book saved to {filename}")
        elif command == "load":
            filename = input("Enter the filename to load the address book from: ")
            address_book.load_from_file(filename)
            print("Address book loaded successfully")
        elif command.startswith("search "):
            query = command[7:]
            results = address_book.search_contacts(query)
            if results:
                for result in results:
                    print(result)
            else:
                print(f"No contacts found matching '{query}'")

        elif command in ["good bye", "close", "exit"]:
            print("Good bye!")
            break
        else:
            print("Invalid command. Please try again")

if __name__ == "__main__":
    address_book = AddressBook()
    main()
