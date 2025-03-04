def absolute_value_extra_return(x):
    if x < 0:
        return -x
    else:
        return x
    
    return 'This is dead code.'
print(absolute_value_extra_return(-5))
print(absolute_value_extra_return(50))