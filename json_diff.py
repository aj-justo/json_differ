from copy import copy

def make_json_diff(obj):
    if isinstance(obj, dict):
        return AJsonDict(obj)
    elif isinstance(obj, list):
        return AJsonList(obj)


class AJsonDiff(object):
    def __init__(self, original, current):
        self.original = original
        self.current = current


class AJson(object):
    original = None

    def changed(self):
        return AJsonDiff(self.original, self)


class AJsonDict(dict, AJson):
    def __init__(self, adict):
        super(AJsonDict, self).__init__(adict)
        self.original = copy(self)
        self.make_sub_diffs()

    def make_sub_diffs(self):
        for k,v in self.items():
            if not isinstance(v, basestring)\
               and not isinstance(v, int)\
            and not isinstance(v, float):
                self[k] = make_json_diff(v)

class AJsonList(list, AJson):
    def __init__(self, alist):
        super(AJsonList, self).__init__(alist)
        self.original = copy(self)
        self.make_sub_diffs()

    def make_sub_diffs(self):
        for i,v in enumerate(self):
            if not isinstance(v, basestring)\
               and not isinstance(v, int)\
            and not isinstance(v, float):
                self[i] = make_json_diff(v)

