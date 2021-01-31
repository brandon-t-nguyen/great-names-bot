class Message:
    def __init__(self, content="", file_path=None):
        self.content = content
        if file_path is None:
            self.multipart = False
        else:
            self.multipart = True
            self.file_path = file_path
