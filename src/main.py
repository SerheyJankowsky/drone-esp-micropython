import time
from fc import FlightController

def demo_flight():
    """Demonstration flight sequence."""
    print("🎯 DRONE FLIGHT DEMONSTRATION")
    print("⚠️  Make sure propellers are ON and area is CLEAR!")
    
    try:
        fc = FlightController()
        print("✅ Flight Controller connected!")
        
        # Test motor control first
        fc.bypass_safety_checks()
        
        print("\n🚁 Starting demo flight sequence...")
        
        # Take off
        print("🛫 Taking off...")
        fc.takeoff(1150, 8)
        time.sleep(2)
        
        # Basic movements
        print("📍 Testing movements...")
        fc.move_up(1170, 400)
        time.sleep(1)
        
        fc.move_forward(1190, 500)
        time.sleep(1)
        
        fc.move_left(1190, 500)
        time.sleep(1)
        
        fc.rotate_clockwise(1210, 300)
        time.sleep(1)
        
        # Return to start position
        fc.move_right(1190, 500)
        time.sleep(1)
        
        fc.move_backward(1190, 500)
        time.sleep(1)
        
        # Land
        print("🛬 Landing...")
        fc.land(1150, 12)
        
        print("🎉 Demo flight complete!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        try:
            fc.emergency_stop()
        except:
            pass

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
    
    print("\n🎮 FLIGHT CONTROL SYSTEM READY!")
    print("=" * 50)
    print("⚠️  SAFETY FIRST: Make sure propellers are ON and area is clear!")
    print("🛑 EMERGENCY: Call fc.emergency_stop() if anything goes wrong!")
    print("=" * 50)
    
    print("\n🚁 Available Flight Commands:")
    print("fc.emergency_stop()              - STOP ALL MOTORS NOW!")
    print("fc.hover(throttle)               - Hover at throttle (1100-1300)")
    print("fc.takeoff(target_throttle, steps) - Gradual takeoff")
    print("fc.land(current_throttle, steps)   - Gradual landing")
    print("")
    print("📍 Movement Commands:")
    print("fc.move_up(power, duration_ms)     - Ascend")
    print("fc.move_down(power, duration_ms)   - Descend")
    print("fc.move_forward(power, duration)   - Move forward")
    print("fc.move_backward(power, duration)  - Move backward")
    print("fc.move_left(power, duration)      - Move left")
    print("fc.move_right(power, duration)     - Move right")
    print("")
    print("🔄 Rotation Commands:")
    print("fc.rotate_clockwise(power, duration)     - Yaw right")
    print("fc.rotate_counterclockwise(power, duration) - Yaw left")
    print("")
    print("🧪 Test Sequence:")
    print("fc.flight_test_sequence()         - Run complete automated test")
    
    print("\n💡 QUICK START EXAMPLE:")
    print("#" * 40)
    print("# Take off and hover")
    print("fc.takeoff(1150, 10)  # Gradual takeoff to throttle 1150")
    print("time.sleep(3)         # Hover for 3 seconds")
    print("")
    print("# Simple movement test")
    print("fc.move_forward(1180, 500)  # Forward for 0.5 seconds")
    print("time.sleep(1)")
    print("fc.move_left(1180, 500)     # Left for 0.5 seconds")
    print("time.sleep(1)")
    print("")
    print("# Land safely")
    print("fc.land(1150, 15)    # Gradual landing")
    print("#" * 40)
    
    print("\n🎯 MANUAL CONTROL MODE:")
    print("You can now call any flight commands manually!")
    print("Example: fc.takeoff(1150, 10)")
    
    # Uncomment the line below to run automatic test flight
    # fc.flight_test_sequence()
    
    print("\n" + "="*60)
    print("🎮 INTERACTIVE FLIGHT CONTROL")
    print("="*60)
    print("Commands:")
    print("  takeoff    - Take off and hover")
    print("  test       - Run movement tests")
    print("  manual     - Enter manual control mode")
    print("  land       - Land the drone")
    print("  stop       - Emergency stop")
    print("  quit       - Exit")
    print("="*60)
    
    while True:
        try:
            cmd = input("Flight Control> ").strip().lower()
            
            if cmd == "takeoff":
                print("🛫 Taking off...")
                fc.takeoff(1150, 10)
                print("✅ Hovering - type 'land' to land")
                
            elif cmd == "test":
                print("🧪 Running movement tests...")
                fc.move_up(1180, 300)
                time.sleep(1)
                fc.move_forward(1200, 400)
                time.sleep(1)
                fc.move_left(1200, 400)
                time.sleep(1)
                fc.rotate_clockwise(1220, 300)
                print("✅ Test complete")
                
            elif cmd == "manual":
                print("🎮 Manual control mode - use these commands:")
                print("  w - forward, s - back, a - left, d - right")
                print("  q - rotate left, e - rotate right")
                print("  space - up, x - down")
                print("  l - land, esc - exit manual mode")
                
                while True:
                    manual_cmd = input("Manual> ").strip().lower()
                    if manual_cmd == "w":
                        fc.move_forward(1180, 300)
                    elif manual_cmd == "s":
                        fc.move_backward(1180, 300)
                    elif manual_cmd == "a":
                        fc.move_left(1180, 300)
                    elif manual_cmd == "d":
                        fc.move_right(1180, 300)
                    elif manual_cmd == "q":
                        fc.rotate_counterclockwise(1200, 200)
                    elif manual_cmd == "e":
                        fc.rotate_clockwise(1200, 200)
                    elif manual_cmd == " ":
                        fc.move_up(1170, 200)
                    elif manual_cmd == "x":
                        fc.move_down(1130, 200)
                    elif manual_cmd == "l":
                        break
                    elif manual_cmd == "esc":
                        break
                    else:
                        print("Invalid command")
                        
            elif cmd == "land":
                print("🛬 Landing...")
                fc.land(1150, 15)
                print("✅ Landed safely")
                
            elif cmd == "stop":
                print("🚨 EMERGENCY STOP!")
                fc.emergency_stop()
                print("✅ All motors stopped")
                
            elif cmd == "quit":
                print("👋 Exiting flight control...")
                fc.emergency_stop()
                break
                
            else:
                print("Available commands: takeoff, test, manual, land, stop, quit")
                
        except KeyboardInterrupt:
            print("\n🚨 Keyboard interrupt - emergency stop!")
            fc.emergency_stop()
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            fc.emergency_stop()
            break

if __name__ == "__main__":
    # Uncomment the line below to run demo instead of interactive mode
    # demo_flight()
    run()

if __name__ == "__main__":
    run()