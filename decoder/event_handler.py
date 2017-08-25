class event(object):
    def __init__(self):
        self.handlers = set();

    def add_handler(self, handler):
        self.handlers.add(handler);
        return self;

    def rm_handler(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self;

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)
