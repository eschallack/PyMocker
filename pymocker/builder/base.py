# first, we need to scan the names of the columns from the datatype
# the challenge is that the only real entrypoint is the providers map, which only gives us access to catch custom data types
# we need to do one of the following:
    # 1. modify the library itself, and insert our own custom logic that can be toggled on and off that 
    # discovers which functions relate to our columns. 
    # 2. create custom types for each field to fuffil the override condition (seems obtuse, but maybe could work)
    # 3. just write my own library and use polyfaker as a solid fallback. I'm leaning towards this decision.
from pymocker.builder.rank import rank

def scan_field_type():
    pass
def decide_function_to_add():
    pass
def attach_method_to_class():
    pass
