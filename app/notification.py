# Standard Library
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, List

class NotificationStrategy(ABC):
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
    
    @abstractmethod
    def send_notification(self, data):
        pass


class LogNotificationStrategy(NotificationStrategy):
    def __init__(self, topic_name: str = "Logging_topic"):
        super().__init__(topic_name)

    def send_notification(self, data: Any):
        # TODO: try to structure the notification in a much better way
        # TODO: shift from print to logging statements
        print(f"Sending Notification: Topic Name: {self.topic_name} Data: {len(data)}")