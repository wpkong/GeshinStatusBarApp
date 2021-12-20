class GenshinNotifier(object):
    NOTIFY_TYPE_MOD = 1
    NOTIFY_TYPE_UNTIL = 2
    
    def __init__(self, notify_capacity, notify_type=NOTIFY_TYPE_MOD):
        self._notify_type = notify_type
        self._notify_capacity = notify_capacity
        self._has_notified = False
        self._notified_value = 0
    
    def trigger(self, v) -> bool:
        if v == self._notified_value: return False
        
        if self._is_value_trigger(v):
            self._has_notified = True
            self._notified_value = v
            return True
        else:
            self._has_notified = False
            return False
    
    def _is_value_trigger(self, v) -> bool:
        if self._notify_type == self.NOTIFY_TYPE_MOD:
            return (v % self._notify_capacity == 0)
        elif self._notify_type == self.NOTIFY_TYPE_UNTIL:
            return (self._notify_capacity == v)
        else:
            return False
