import subprocess
import re
import platform
import time

def calculate_distance(rssi):
    """
    Adjust the distance calculation for stronger RSSI values.
    This is fine-tuned for closer ranges, since real-world conditions
    can make strong signals appear farther than they should.
    """
    if rssi >= -40:
        return 0.1  # Extremely close (less than 0.5 meters)
    elif -50 <= rssi < -40:
        return 0.5  # Close, around 0.5 meters
    elif -55 <= rssi < -50:
        return 1.0  # Within 1 meter
    elif -60 <= rssi < -55:
        return 1.5  # Around 1.5 meters
    elif -65 <= rssi < -60:
        return 2.0  # Around 2 meters
    elif -70 <= rssi < -65:
        return 3.0  # Around 3 meters
    else:
        return 5.0  # More than 5 meters away

def get_wifi_rssi():
    os_type = platform.system()
    
    if os_type == "Windows":
        # Use netsh wlan show interfaces to get the current connection's RSSI
        command = "netsh wlan show interfaces"

        # Take multiple measurements and average the results for accuracy
        rssi_values = []
        num_measurements = 5  # Number of times to sample RSSI
        
        for _ in range(num_measurements):
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Command failed with return code {result.returncode}")
                return
            
            # Debugging - print the raw output
            print(result.stdout)  # Print the raw output to see the exact information returned

            # Regex to capture SSID, BSSID, and RSSI from the output
            networks = re.findall(r"SSID\s+:\s(.*?)\n.*?BSSID\s+:\s([\da-fA-F:]+)\n.*?Signal\s+:\s(\d+)%", result.stdout, re.DOTALL)
            
            if networks:
                for ssid, mac, signal_strength in networks:
                    # Convert signal strength percentage to dBm (approximation)
                    dBm = int(signal_strength) * 0.5 - 100
                    rssi_values.append(dBm)
                    print(f"Sample RSSI for SSID '{ssid}': {dBm} dBm")  # Show each RSSI value
            
            time.sleep(0.5)  # Small delay between measurements to smooth out fluctuations

        if rssi_values:
            avg_rssi = sum(rssi_values) / len(rssi_values)  # Average the RSSI values
            print(f"Average RSSI after {num_measurements} samples: {avg_rssi:.2f} dBm")

            distance = calculate_distance(avg_rssi)
            print(f"Estimated Distance: {distance:.2f} meters")
        else:
            print("No networks found or connected")
    
    else:
        print("Unsupported operating system")

get_wifi_rssi()

