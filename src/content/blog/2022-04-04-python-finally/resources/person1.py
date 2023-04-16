class Person:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    def get_id(self):
        """ Maybe we make an API or database call here or something """
        return "abc123"

def process_person(person: Person):
    """ This does something """
    return person.get_id()

