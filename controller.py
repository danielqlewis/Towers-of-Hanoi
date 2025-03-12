from models.menu_model import MenuModel
from constants import ProgramState


class ProgramController:
    def __init__(self, model):
        self.model = model
        self.model_updated = False
        self.next_state = None

    def handle_input(self, user_input):
        if user_input.clicked:
            self.next_state = ProgramState.GAME if isinstance(self.model, MenuModel) else ProgramState.MENU
            self.model_updated = True
