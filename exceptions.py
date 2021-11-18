class TargetNotFoundError(Exception):
    """Target not found (is not a file and is not described)"""

    def __init__(self, target, *args):
        super().__init__("Не существует правила для " + target, *args)


class MakefileNotFoundError(Exception):
    """Make file not found"""

    def __init__(self, *args):
        super().__init__("Make file doesn't exist", *args)