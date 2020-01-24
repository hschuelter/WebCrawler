class Author:
    name = ""
    institute = []

    def __init__(self, name="", institute=""):
        self.name = name
        self.institute = institute

    def __str__(self):
        return self.name + " (" + self.institute + ")"