# Stores data about classroom
class Room:
    # ID counter used to assign IDs automatically
    _next_room_id = 0

    # Initializes room data and assign ID to room
    def __init__(self, name, lab, number_of_seats):
        # Returns room ID - automatically assigned
        self.Id = Room._next_room_id
        Room._next_room_id += 1
        # Returns name        
        self.Name = name
        # Returns TRUE if room has computers otherwise it returns FALSE
        self.Lab = lab
        # Returns number of seats in room
        self.NumberOfSeats = number_of_seats

    # Restarts ID assigments
    @staticmethod
    def restartIDs() -> None:
        Room._next_room_id = 0
