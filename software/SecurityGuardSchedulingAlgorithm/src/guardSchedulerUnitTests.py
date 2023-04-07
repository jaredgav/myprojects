import unittest
from guardSchedulingAlgo import *


class TestGuardScheduler(unittest.TestCase):

    def testMainScheduler(self):
        """ Tests the overall scheduler """
        # ARRANGE

        numGuardsToAllocate = 3
        guardsAllocated = []
        
        entries = []
        entries.append(GuardEntry("Mike", 0, 12))
        entries.append(GuardEntry("Ray", 3, 9))
        entries.append(GuardEntry("Dave", 4, 8))

        # 12 slots 8pm to 2am
        numTimeSlots = 12
        
        # ACT

        # Setup the schedule
        (schedule, guardsAllocated) = createSchedule(entries, numTimeSlots)
        timeSlots = schedule.getSchedule()
        
        # ASSERT

        # Print details of the schedule
        timeSlotIdx = 0
        print("Time Slot,Guard ID")
        for slot in timeSlots:
            print(str(timeSlotIdx) + "," + str(slot.guardID))
            timeSlotIdx += 1
        self.assertTrue(len(guardsAllocated) == 3)


if __name__ == '__main__':
    unittest.main()
    