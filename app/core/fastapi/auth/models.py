from starlette.authentication import BaseUser


class CustomUser(BaseUser):  # noqa
    def __init__(self, pk: str, first_name: str, last_name: str) -> None:
        self.pk = pk
        self.first_name = first_name
        self.last_name = last_name

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
