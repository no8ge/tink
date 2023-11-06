class HelmError(Exception):
    def __init__(self, status, reason):
        super().__init__(status, reason)
        self.status = status
        self.reason = reason