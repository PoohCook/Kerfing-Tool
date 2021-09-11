
class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        val_str = "Namespace("
        for key, val in self.__dict__.items():
            val_str += "%s=%s," % (key, val)

        if val_str[-1] == ',':
            val_str = val_str[:-1]
        return val_str + ")"

    def __repr__(self):
        return self.__str__()
