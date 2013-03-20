from copy import copy

class AJsonDiff(object):
    def __init__(self, original, current):
        self.original = original
        self.current = current

    def changed(self):
        return set()
    def unchanged(self):
        return set()
    def added(self):
        return set()
    def removed(self):
        return set()


class AJson(object):
    _instances = list()
    _original = _current = _diff = None # for cache

    def diff(self):
        return self._get_diff()

    def _get_diff(self):
        if not self._cache_valid():
            return AJsonDiff(self._original, self)
        else:
            return self._diff

    def _cache_valid(self):
        if self._diff and self._current and self._original == self:
            return self._diff
        else:
            self._current = self
            self._diff = AJsonDiff(self._original, self)
            return self._diff

    def get_instance(self, obj):
        if isinstance(obj, dict):
            instance = AJsonDict(obj)
        elif isinstance(obj, list):
            instance = AJsonList(obj)
        self._instances.append(instance)
        return instance


class AJsonDict(dict, AJson):
    def __init__(self, adict):
        super(AJsonDict, self).__init__(adict)
        self._original = copy(self)
        self.make_sub_diffs()

    def make_sub_diffs(self):
        for k,v in self.items():
            if not isinstance(v, basestring)\
               and not isinstance(v, int)\
            and not isinstance(v, float):
                self[k] = self.get_instance(v)


class AJsonList(list, AJson):
    def __init__(self, alist):
        super(AJsonList, self).__init__(alist)
        self._original = copy(self)
        self.make_sub_diffs()

    def make_sub_diffs(self):
        for i,v in enumerate(self):
            if not isinstance(v, basestring)\
               and not isinstance(v, int)\
            and not isinstance(v, float):
                self[i] = self.get_instance(v)

