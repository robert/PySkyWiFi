def b26_encode(input_string):
    # Convert input string to a base-256 integer
    base256_int = 0
    for char in input_string:
        base256_int = base256_int * 256 + ord(char)
    
    # Convert base-256 integer to base26 string
    if base256_int == 0:
        return 'A'  # Special case for empty input or input that equals zero
    
    base26_str = ""
    while base256_int > 0:
        base26_str = chr(base256_int % 26 + 65) + base26_str
        base256_int //= 26
    
    return base26_str

def b26_decode(input_string):
    # Convert base26 string to a base-256 integer
    base26_int = 0
    for char in input_string:
        base26_int = base26_int * 26 + (ord(char) - 65)
    
    # Convert base-256 integer to string
    bytes_list = []
    while base26_int > 0:
        bytes_list.insert(0, base26_int % 256)
        base26_int //= 256
    
    return ''.join(chr(byte) for byte in bytes_list)
