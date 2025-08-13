# dvge/models/quest.py

"""Quest model for tracking player objectives and journal entries."""


class Quest:
    """Represents a single quest or journal entry."""
    
    def __init__(self, quest_id, name="New Quest", description="", state="inactive"):
        self.id = quest_id
        self.name = name
        self.description = description
        self.state = state  # inactive, active, completed, failed
    
    def to_dict(self):
        """Serializes the quest data into a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "state": self.state
        }
    
    @staticmethod
    def from_dict(data):
        """Creates a Quest instance from a dictionary."""
        return Quest(
            quest_id=data.get('id', ''),
            name=data.get('name', 'New Quest'),
            description=data.get('description', ''),
            state=data.get('state', 'inactive')
        )
    
    def activate(self):
        """Sets the quest state to active."""
        self.state = "active"
    
    def complete(self):
        """Sets the quest state to completed."""
        self.state = "completed"
    
    def fail(self):
        """Sets the quest state to failed."""
        self.state = "failed"
    
    def is_active(self):
        """Returns True if the quest is active."""
        return self.state == "active"
    
    def is_completed(self):
        """Returns True if the quest is completed."""
        return self.state == "completed"
    
    def is_failed(self):
        """Returns True if the quest is failed."""
        return self.state == "failed"