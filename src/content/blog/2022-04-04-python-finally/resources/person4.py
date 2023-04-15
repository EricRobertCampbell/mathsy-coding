class Person:
    def __init__(self, name: str):
        self.name = name

    def get_id(self):
        """ Maybe we make an API or database call here or something """
        return "abc123"

def process_person(person: Person):
    """ This does something """
    try:
        return person.get_id()
    except Exception as e:
        print(f"Error calling do_something for Person {person.first_name} {person.last_name}:", e)
    finally:
        return None

