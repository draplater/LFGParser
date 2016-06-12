class UFSet(object):
    def __init__(self):
        self.map = dict()

    def add(self, obj):
        if obj not in self.map.keys():
            self.map[obj] = obj

    def find(self, obj):
        if obj not in self.map.keys():
            raise KeyError
        if self.map[obj] == obj:
            return obj
        self.map[obj] = self.find(self.map[obj])
        return self.map[obj]

    def union(self, obj1, obj2):
        if self.find(obj1) != self.find(obj2):
            self.map[self.find(obj1)] = obj2