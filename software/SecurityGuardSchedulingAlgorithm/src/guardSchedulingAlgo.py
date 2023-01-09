
class GuardEntry:
    # Identifier for the guard that owns this time
    id = 0

    # The start time of this entry
    startTime = 0

    # The end time of this entry
    endTime = 0

    # The duration of this entry
    duration = 0

def getEmptyTimeSlots(numTimeSlots):
    """ EmptyTimeSlots can be a simple list where each
    index is 30min block of time in a day.
    So start times would look like [8am, 8:30am, 9am,...]
    14*2 = 28 slots would be 14hrs (8am to 2am) """
    emptySlots = []
    for x in range(0, numTimeSlots):
         emptySlots.insert(0, None)
    return emptySlots

def getGuardEntries():
    """ Returns the list of guard availabilities"""
    None

def compareGuardEntry(entryA, entryB):
    """ Compares A to B. 
        If A has starts earlier: A > B
        If A.start == B.start, largest duration wins
         """
    if(entryA.duration >= entryB.duration):
        greaterDuration = True
    else:
        greaterDuration = False

    if(entryA.startTime < entryB.startTime):
        return True
    elif(entryA.startTime == entryB.startTime):
        return greaterDuration
    else: # entryA.duration < entryB.duration
        return False

def sortGuardEntries(guardEntriesList):
    """ Returns a sorted version of the list given. """
    finalList = []
    # Insertion sort
    for entry in guardEntriesList:
        for i in range(0, len(finalList)):
            if(len(finalList) == 0):
                break
            if(compareGuardEntry(entry, finalList[i])):
                # Current entry is larger than the position
                break
        finalList.insert(i, entry)
    return finalList

def createSchedule(guardEntriesList, emptyTimeSlots):
    """ Main function that executes the schedule """

    # Get the available slots
    emptyTimeSlots = getEmptyTimeSlots()
    

    # Sort Guard Entries from earliest start 


    None

if __name__ == "__main__":
    print("Running Scheduling Algorithm")

    # Print details of schedules
    # 