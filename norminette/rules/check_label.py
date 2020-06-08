from rules import Rule
from scope import *


class CheckLabel(Rule):
    def __init__(self):
        super().__init__()
        self.depends_on = ["IsLabel"]

    def run(self, context):
        context.new_error("LABEL_FBIDDEN", context.peek_token(0))
        return False, 0