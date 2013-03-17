def make_json_diff(obj):
    if isinstance(obj, dict):
        return JsonDiffDict(obj)
    elif isinstance(obj, list):
        return JsonDiffList(obj)

class JsonDiff(object):
    pass

class JsonDiffDict(dict, JsonDiff):
    def __init__(self, adict):
        super(JsonDiffDict, self).__init__(adict)
        self.make_sub_diffs()

    def make_sub_diffs(self):
        for k,v in self.items():
            if not isinstance(v, basestring)\
               and not isinstance(v, int)\
            and not isinstance(v, float):
                self[k] = make_json_diff(v)

class JsonDiffList(list, JsonDiff):
    def __init__(self, alist):
        super(JsonDiffList, self).__init__(alist)
        self.make_sub_diffs()

    def make_sub_diffs(self):
        for i,v in enumerate(self):
            if not isinstance(v, basestring)\
               and not isinstance(v, int)\
            and not isinstance(v, float):
                self[i] = make_json_diff(v)

