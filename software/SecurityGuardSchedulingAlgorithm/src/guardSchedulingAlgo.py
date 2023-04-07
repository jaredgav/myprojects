
import timeConversions
class GuardEntry:
    """ Describes the availability of a guard    """
    def __init__(self, id = 0, slotIdx = None, duration = 1):
        # Identifier for the guard that owns this time
        self.id = id

        # The TimeSlot index that this availability is set for
        self.slotIdx = slotIdx

        # The start time of this entry
        self.startTime = 0

        # The end time of this entry
        self.endTime = 0

        # The duration of this entry by number of TimeSlots
        self.duration = duration
    
    def getInfo(self):
        return "ID: %s \nStart Index: %d \nDuration: %d"%(str(self.id), self.slotIdx, self.duration)

class TimeSlot:
    """ Describes a 30min slot in which a guard can work """
    def __init__(self):
        # Indicates if this position is filled
        self.isFilled = False

        # Indicates the Guard that is allocated for this time slot
        self.guardID = None

        # Indicates the granularity in minutes of the slot (future use)
        self.granularity = 30

class SingleDayTimeSlots:
    """ Describes a day of time slots and performs operations and searches on the time slots for a given day"""
    def __init__(self, timeSlots):
        """ params:
                timeSlots = a list of empty TimeSlots 
        """
        # The an ordered list of time slots for this day
        self.timeSlots = timeSlots
        
    def getEarliestEmptySlot(self):
        """ Returns the index of the first empty time slot for this day"""
        for slotIdx in range(0, len(self.timeSlots)):
            slot = self.timeSlots[slotIdx]
            if slot.isFilled == False:
                return slotIdx
    
    def tryFillSlot(self, entry):
        """ Puts a GuardEntry into an available time slot"""
        assignedSlot = False # Indicates if this entry was used in the schedule
        desiredSlot = entry.slotIdx # the starting slot for this entry
        desiredDuration = entry.duration # the number of slots to fill

        # Add as many slots for the desired duration that are not filled
        for idx in range(desiredSlot, desiredSlot + desiredDuration):
            if self.timeSlots[idx].isFilled == False:
                # Fill in the TimeSlot with the GuardEntry information
                self.timeSlots[idx].guardID = entry.id
                self.timeSlots[idx].isFilled = True
                assignedSlot = True
            else:
                # This slot is already filled, so continue to check the next desired
                continue
        
        return assignedSlot
    
    def checkAllSlotsOpen(self):
        """ Checks if all the time slots are open """
        for slot in self.timeSlots:
            if slot.isFilled:
                return False
    
    def getSchedule(self):
        return self.timeSlots


def getEmptyTimeSlots(numTimeSlots):
    """ EmptyTimeSlots is a list where each ordered index is a 30min block of time in a day. 
    For example, the first index is 8am to 8:30am.
    So start times would look like [8am, 8:30am, 9am,...]
    14 * 2 = 28 slots would be 14hrs (8am to 2am | 0800-0200) """
    emptySlots = []
    for x in range(0, numTimeSlots):
        newTimeSlot = TimeSlot()
        emptySlots.insert(0, newTimeSlot)
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
    """ Returns a sorted version of the list given. Insertion Sort"""
    finalList = []
    # Insertion sort
    for entry in guardEntriesList:
        i = 0
        for i in range(0, len(finalList)):
            if(len(finalList) == 0):
                break
            if(compareGuardEntry(entry, finalList[i])):
                # Current entry is larger than the position
                break
        finalList.insert(i, entry)
    return finalList

def createSchedule(guardEntriesList, numTimeSlots):
    """ Main function that executes the schedule """

    # Get the available slots
    emptyTimeSlots = getEmptyTimeSlots(numTimeSlots)
    timeSlots = SingleDayTimeSlots(emptyTimeSlots)

    # Sort Guard Entries from earliest start
    sortedGuardEntries = sortGuardEntries(guardEntriesList)

    # Stores the list of which guards have already been allocated
    guardsInSchedule = []

    # Iterate over the sorted list of availabilities
    for curEntry in sortedGuardEntries:
        
        # Validate that the earliest open time slot can be filled
        #   Check the list index of the time is correct
        if timeSlots.checkAllSlotsOpen():
            earliestEmptySlot = timeSlots.getEarliestEmptySlot()
            if curEntry.slotIdx > earliestEmptySlot:
                # The earliest time for the available guards does not meet the earliest empty time slot
                print("Unable to Schedule: Earliest available guard is after earliest open time slot")
                break

        
        # Skip this entry if the guard was already placed in the schedule
        if curEntry.id not in guardsInSchedule:
            # Expecting no issues in assigning slots at this point
            success = timeSlots.tryFillSlot(curEntry)
            if success:
                # Add the guard to the tracking of who is on schedule
                guardsInSchedule.append(curEntry.id)
                continue
            else:
                # GuardEntry was not able to be put in the schedule
                pass
    
    # Return a tuple of guards in the schedule and the schedule itself
    return timeSlots, guardsInSchedule


if __name__ == "__main__":
    print("Running Scheduling Algorithm")
    # 18hrs in a day (8am - 2am) 18 * 2 = 36 (+ 1) =  slots ()
    numTimeSlots = 36

    # Setup the schedule
    entries = createTestGuardEntries()

    # Run the algo
    (schedule, guardsAllocated) = createSchedule(entries, numTimeSlots)
    timeSlots = schedule.getSchedule()

    # Print details of the schedule
    timeSlotIdx = 0
    print("Time Slot,Guard ID")
    for slot in timeSlots:
        print(str(timeSlotIdx) + "," + str(slot.guardID))
        timeSlotIdx += 1

    print('\n Copy to and file and save as CSV for tabulated schedule')
