from .state_text import state_text
from .option_text import option_text
from string import ascii_uppercase

def call_func_with_str(obj,text,par=None):
    func = getattr(obj, text)
    if(par==None):
        result=func()
    else:
        result = func(par)
    return result

def print_state_text(state):
    print(state_text[state])

def get_options(triggers):
    result=''
    for char,option in zip(ascii_uppercase,triggers):
        result+=f'{char}:{option_text[option]}\n'
    return result[:-1]

