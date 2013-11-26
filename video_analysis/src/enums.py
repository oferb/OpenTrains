

def enum(**enums):
    return type('Enum', (), enums)

Directions = enum(NORTH=1, SOUTH=2, EAST=3, WEST=4)