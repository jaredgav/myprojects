def military_to_12hr(military_time):
    """ This function takes in a string representing military time, such as "1500" 
    (which represents 3:00 PM), and returns a string representing the equivalent 
    12-hour clock time, such as "3:00 PM". 
    """
    hour = int(military_time[:2])
    minute = int(military_time[2:])
    
    if hour == 0:
        return "12:{:02d} AM".format(minute)
    elif hour < 12:
        return "{:d}:{:02d} AM".format(hour, minute)
    elif hour == 12:
        return "12:{:02d} PM".format(minute)
    else:
        return "{:d}:{:02d} PM".format(hour - 12, minute)
