import cPickle
from copy import deepcopy


class AJsonDiffBase(object):
    def __init__(self, current=None, original=None):
        self.original = original
        self.current = current

    # an empty diff
    def added(self):
        return set()

    def removed(self):
        return set()

    def changed(self):
        return set()

    def unchanged(self):
        return set()


class AJsonDictDiff(AJsonDiffBase):
    """
    A dictionary difference calculator
    The contents of this class was originally posted here:
    http://stackoverflow.com/questions/1165352/fast-comparison-between-two-python-dictionary/1165552#1165552
    """

    def __init__(self, current, original):
        super(AJsonDictDiff, self).__init__(current, original)
        self.current_dict, self.past_dict = self.current, self.original
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (self.current, self.original)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        return set(self.current_keys) - self.intersect

    def removed(self):
        return set(self.past_keys) - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


class AJsonListDiff(AJsonDiffBase):
    """
    A list difference calculator.
    Lists may give importance to order, so we return diff like this:
        - unchanged: Index and Value are the same in both lists
        - added: Indexes not present in original list but present in current list
        - removed: Indexes present in original and not in current list
        - changed: Any changed value in indexes present in both lists.
                    Note that we DO consider indexes here:
                    If a value is present in both lists but in different indexes,
                    it will be caught as changed.
    """

    def __init__(self, current, original):
        super(AJsonListDiff, self).__init__(current, original)
        # we need to make all list entries hashable to convert them to sets
        self._hashed_current = [cPickle.dumps(o) for o in self.current]
        self._hashed_original = [cPickle.dumps(o) for o in self.original]

    def added(self):
        return set(i for i, o in enumerate(self.current)
                   if i >= len(self.original))

    def removed(self):
        return set(i for i, o in enumerate(self.original)
                   if i >= len(self.current))

    def changed(self):
        """
            Returns changed items, considering index preservation,
            i.e.: value present in both lists but on different index
            will be returned as changed.
        """
        changed = []
        # we'll loop over the smaller list
        if len(self._hashed_current) < len(self._hashed_original):
            base_list = self._hashed_current
        else:
            base_list = self._hashed_original
        for i, o in enumerate(base_list):
            if self._hashed_original[i] != self._hashed_current[i]:
                changed.append(i)
        return set(changed)

    def unchanged(self):
        """
        Both index and value must be the same
        """
        unchanged = []
        # we'll loop over the smaller list
        if len(self._hashed_current) < len(self._hashed_original):
            base_list = self._hashed_current
        else:
            base_list = self._hashed_original
        for i, o in enumerate(base_list):
            if self._hashed_original[i] == self._hashed_current[i]:
                unchanged.append(i)
        return set(unchanged)


class AJsonLock():
    LOCKS = ('MODIFICATION', 'ADDITION', 'REMOVAL')
    _current_locks = set()

    def __init__(self, lock=None):
        if lock and lock.upper() in self.LOCKS:
            self._locks.union(set(lock))

    def __unicode__(self):
        return self.get_current_locks()

    def get_current_locks(self):
        return self._locks

    def clear_locks(self):
        self._locks = set()

    def add_lock(self, lock):
        if lock.upper() in self.LOCKS:
            self._locks.union(set(lock))
        else:
            raise TypeError("The lock %s must be one of %s" % (lock, ",".join(self.LOCKS)))

    def remove_lock(self, lock):
        if lock.upper() in self.LOCKS:
            self._locks.discard(lock)
        else:
            raise TypeError("The lock %s must be one of %s" % (lock, ",".join(self.LOCKS)))


class AJsonBase(object):
    _meta = {
        'instances': list(),
        'original': None,
        'diff': None,
        'lock': AJsonLock(),
        'root': None
    }

    def __call__(self, obj):
        if isinstance(obj, dict):
            instance = AJsonDict(obj, self)
        elif isinstance(obj, list):
            instance = AJsonList(obj, self)
        # self._meta['instances'].append(instance)
        # self._meta['original'] = deepcopy(instance)
        return instance

    def diff(self):
        if not self._cache_valid():
            if isinstance(self._meta['original'], AJsonDict) and isinstance(self, AJsonDict):
                return AJsonDictDiff(self, self._meta['original'])
            elif isinstance(self._meta['original'], AJsonList) and isinstance(self, AJsonList):
                return AJsonListDiff(self, self._meta['original'])
            else:
                return AJsonDiffBase()
        else:
            print "*** USING CACHE ***"
            return self._meta['diff']

    def recursive_diff(self):
        """
            Gathers the diff objects on every AJson instance
            and compiles tuples with the changed keys/indexes:
            >>recursive_diff.change()
            >>set([(0,'a','c'), (0,'d',0, 'e')])
        """
        diffs = []
        # if no changes
        if not self._meta['instances']:
            diffs = set(diffs)
        else:
            for i in self._meta['root']._meta['instances']:
                diffs.append(i.diff())
        return diffs

    def _cache_valid(self):
        if self._meta['diff'] and self._meta['original'] == self:
            return True
        return False

    def get_instances(self):
        return self._meta['root']._meta['instances']


class AJsonDict(dict, AJsonBase):
    def __init__(self, adict, root=None):
        super(AJsonDict, self).__init__(adict)
        self._meta['original'] = deepcopy(self)
        self._meta['root'] = root
        # self._meta['root']._meta['instances'].append(self)

    def diff(self):
        return AJsonDictDiff(self, self._meta['original'])

    def __getitem__(self, k):
        entry = super(AJsonDict, self).__getitem__(k)
        if isinstance(entry, list) and not isinstance(entry, AJsonList):
            entry = AJsonList(entry, self._meta['root'])
            # we are transforming the value, so we need to update it
            super(AJsonDict, self).__setitem__(k, entry)
            entry = super(AJsonDict, self).__getitem__(k)
        elif isinstance(entry, dict) and not isinstance(entry, AJsonDict):
            entry = AJsonDict(entry, self._meta['root'])
            # update it
            super(AJsonDict, self).__setitem__(k, entry)
            entry = super(AJsonDict, self).__getitem__(k)
        return entry

    def __setitem__(self, i, y):
        super(AJsonDict, self).__setitem__(i, y)
        self._meta['root']._meta['instances'].append(self)


class AJsonList(list, AJsonBase):
    def __init__(self, alist, root=None):
        super(AJsonList, self).__init__(alist)
        self._meta['original'] = deepcopy(self)
        self._meta['root'] = root
        # print self._meta['root']._meta['instances']

    def diff(self):
        return AJsonListDiff(self, self._meta['original'])

    def __getitem__(self, i):
        entry = super(AJsonList, self).__getitem__(i)
        if isinstance(entry, list) and not isinstance(entry, AJsonList):
            entry = AJsonList(entry, self._meta['root'])
            # we are transforming the value, so we need to update it
            super(AJsonList, self).__setitem__(i, entry)
            entry = super(AJsonList, self).__getitem__(i)
        elif isinstance(entry, dict) and not isinstance(entry, AJsonDict):
            entry = AJsonDict(entry, self._meta['root'])
            # update it
            super(AJsonList, self).__setitem__(i, entry)
            entry = super(AJsonList, self).__getitem__(i)
        return entry

    def __setitem__(self, key, value):
        super(AJsonList, self).__setitem__(key, value)
        self._meta['root']._meta['instances'].append(self)


SuperJson = AJsonBase