class LinkPaginatorConfiguration:
    def __init__(self, next_pointer=None, result_pointer=None):
        self.next_pointer = next_pointer
        self.result_pointer = result_pointer

    def set_next_pointer(self, next_pointer):
        self.next_pointer = next_pointer
        return self

    def set_result_pointer(self, result_pointer):
        self.result_pointer = result_pointer
        return self
