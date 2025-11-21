from .level_1 import get_level as get_level_1
from .level_2 import get_level as get_level_2
from .level_3 import get_level as get_level_3
from .level_4 import get_level as get_level_4
from .level_5 import get_level as get_level_5
from .level_6 import get_level as get_level_6
from .level_7 import get_level as get_level_7
from .level_8 import get_level as get_level_8
from .level_9 import get_level as get_level_9
from .level_10 import get_level as get_level_10

def get_level(level_num):
    """Возвращает конфигурацию уровня по номеру"""
    levels = {
        1: get_level_1(),
        2: get_level_2(),
        3: get_level_3(),
        4: get_level_4(),
        5: get_level_5(),
        6: get_level_6(),
        7: get_level_7(),
        8: get_level_8(),
        9: get_level_9(),
        10: get_level_10()
    }
    
    return levels.get(level_num, get_level_1())