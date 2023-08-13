from typing import List, Tuple, Optional
from .native_modules import _multi_index
from .types import U64, F64

sort_type_u64 = 0
sort_type_f64 = 1

u64_double_index = _multi_index.u64_double_index

class key_u64_value_double_index(object):
    def __init__(self):
        self.idx = u64_double_index(sort_type_u64)
        self.key_dict = {}

    def free(self) -> bool:
        if not self.idx:
            return False
        ret = self.idx.free()
        self.idx = None
        return ret

    def __del__(self):
        self.free()
    
    def create(self, first: U64, second: F64) -> bool:
        if first in self.key_dict:
            raise Exception("first already exists")
        self.key_dict[first] = second
        return self.idx.create(first, second)

    def modify(self, first: U64, new_value: F64) -> bool:
        try:
            old_value = self.key_dict[first]
        except KeyError:
            raise Exception("first not found")
        ret = self.idx.modify(first, old_value, new_value)
        assert ret
        self.key_dict[first] = new_value
        return True

    def remove(self, first: U64) -> bool:
        try:
            second = self.key_dict[first]
            del self.key_dict[first]
            return self.idx.remove(first, second)
        except KeyError:
            return False

    def set(self, first: U64, second: F64) -> bool:
        try:
            old_value = self.key_dict[first]
            if old_value == second:
                return True
            ret = self.idx.modify(first, old_value, second)
            assert ret
            self.key_dict[first] = second
            return True
        except KeyError:
            return self.create(first, second)

    def find(self, first: U64) -> Optional[F64]:
        try:
            second = self.key_dict[first]
            return second
        except KeyError:
            return None

    def lower_bound(self, first: U64, second=0.0) -> bool:
        return self.idx.lower_bound(first, second)

    def upper_bound(self, first: U64, second=0.0) -> bool:
        return self.idx.upper_bound(first, second)

    def first(self):
        return self.idx.first()

    def last(self):
        return self.idx.last()

    def pop_first(self):
        ret = self.idx.pop_first()
        if not ret:
            return None
        first, second = ret
        del self.key_dict[first]
        return ret

    def pop_last(self):
        ret = self.idx.pop_last()
        if not ret:
            return None
        first, second = ret
        del self.key_dict[first]
        return ret

    def row_count(self) -> int:
        return self.idx.row_count()

class secondary_double_index(object):
    def __init__(self):
        self.idx = u64_double_index(sort_type_f64)
        self.key_dict = {}

    def free(self) -> bool:
        if not self.idx:
            return False
        ret = self.idx.free()
        self.idx = None
        return ret

    def __del__(self):
        self.free()
    
    def create(self, first: U64, second: F64) -> bool:
        if first in self.key_dict:
            raise Exception("first already exists")
        self.key_dict[first] = second
        return self.idx.create(first, second)

    def modify(self, first: U64, new_value: F64) -> bool:
        try:
            old_value = self.key_dict[first]
            if old_value == new_value:
                return True
        except KeyError:
            raise Exception("first not found")
        ret = self.idx.modify(first, old_value, new_value)
        assert ret
        self.key_dict[first] = new_value
        return True

    def remove(self, first: U64) -> bool:
        try:
            second = self.key_dict[first]
            del self.key_dict[first]
            return self.idx.remove(first, second)
        except KeyError:
            return False

    def set(self, first: U64, second: F64) -> bool:
        try:
            old_value = self.key_dict[first]
            if old_value == second:
                return True
            ret = self.idx.modify(first, old_value, second)
            assert ret
            self.key_dict[first] = second
            return True
        except KeyError:
            return self.create(first, second)

    def find_by_first(self, first: U64) -> Optional[F64]:
        try:
            second = self.key_dict[first]
            return second
        except KeyError:
            return None

    def find_by_second(self, second: F64) -> Optional[U64]:
        ret = self.idx.lower_bound(0, second)
        if not ret:
            return None
        first, second = ret
        if second != second:
            return None
        return first

    def lower_bound(self, first: U64, second: F64):
        return self.idx.lower_bound(first, second)

    def upper_bound(self, first: U64, second: F64):
        return self.idx.upper_bound(first, second)

    def first(self):
        return self.idx.first()

    def last(self):
        return self.idx.last()

    def pop_first(self):
        ret = self.idx.pop_first()
        if not ret:
            return None
        first, second = ret
        del self.key_dict[first]
        return ret

    def pop_last(self):
        ret = self.idx.pop_last()
        if not ret:
            return None
        first, second = ret
        del self.key_dict[first]
        return ret

    def row_count(self) -> int:
        return self.idx.row_count()
