class Signal(object):
    
    def __init__(self):
        self._listeners = []
        
    def register(self, listener, prio=None):
        if listener in self._listeners:
            self.unregister(listener)
        if prio and prio < len(self._listeners):
            self._listeners.insert(prio, listener)
        else:
            self._listeners.append(listener)
        
    def unregister(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)
            
    def emit(self, *args, **kwargs):
        [listener(*args, **kwargs) for listener in self._listeners]



