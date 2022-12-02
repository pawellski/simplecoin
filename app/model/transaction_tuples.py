from collections import namedtuple

InputTuple = namedtuple("InputTuple", "previous_id current_owner amount")
OutputTuple = namedtuple("OutputTuple", "new_owner current_owner new_amount current_amount")
