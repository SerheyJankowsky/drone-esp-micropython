import time
from fc import FlightController

def run():
    """
    Direct motor control - bypassing FC safety checks.
    """
    try:
        fc = FlightController()
        print("Flight Controller connected successfully!")
    except Exception as e:
        print("Could not initialize Flight Controller. Halting.")
        return

    print("\n=== Direct Motor Control Mode ===")
    print("This mode bypasses FC safety checks and controls motors directly.")
    print("Make sure propellers are REMOVED!")
    
    # Test direct motor control
    fc.bypass_safety_checks()
    
    print("\n=== Ready for manual control ===")
    print("You can now add custom motor control logic here.")

if __name__ == "__main__":
    run()