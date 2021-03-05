class InvalidProductException(Exception):
    """
    Raised when an Invalid Product is given
    """
    def __init__(self, message="Invalid Product"):
        self.message = message
        super().__init__(self.message)
