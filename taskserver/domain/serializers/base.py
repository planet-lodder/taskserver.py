from abc import ABC, abstractmethod


class Serializer(ABC):
    data = None
    errors = []

    @abstractmethod
    def parse(self): ...

    def validate(self):
        # Clear previous validation result
        self.errors = []
        self.data = self.parse()
        return self.data and len(self.errors) == 0
