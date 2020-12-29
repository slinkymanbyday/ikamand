"""Example usage of ikamand."""
import time
from ikamand.ikamand import Ikamand


def example():
    """Get ikamand status."""
    ikamand = Ikamand("10.0.0.48")
    data = ikamand.get_data()
    print("Data:", data)


def start_stop_cook():
    """Start and stop a cook on the iKamand."""
    ikamand = Ikamand("10.0.0.48")
    ikamand.start_cook(50, 26, 1)
    data = ikamand.get_data()
    print("Data:", data)
    time.sleep(5)
    ikamand.stop_cook()
    data = ikamand.get_data()
    print("Data:", data)


example()
start_stop_cook()
