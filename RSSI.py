import subprocess
import re
import platform
import time
import math

def calculate_distance_cm(rssi, tx_power=-59):
    """
    Calculate distance using the Free-Space Path Loss (FSPL) model.
    The formula relates RSSI and the distance:
    
    d = 10^((txPower - RSSI) / (10 * n))

    - tx_power: Transmit power of the router (in dBm). The default is -59 dBm.
    - n: Path-loss exponent (usually between 2 and 4 in indoor environments). Default is 2 for line-of-sight.
    
    Returns distance in centimeters with higher precision.
    """
    # Path-loss exponent (n) for typical indoor environment (could be adjusted)
    n = 2.0
    
    # Calculate the distance in meters using the FSPL model
    distance_m = 10 ** ((tx_power - rssi) / (10 * n))
    
    # Convert meters to centimeters for better accuracy in cm
    distance_cm = distance_m * 100
    
    return distance_cm

def get_wifi_rssi():
    os_type = platform.system()
    
    if os_type == "Windows":
        command = "netsh wlan show interfaces"
        rssi_values = []
        num_measurements = 10  # Number of samples for accuracy
        
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
            
            time.sleep(0.5)  # Small delay between measurements

        if rssi_values:
            avg_rssi = sum(rssi_values) / len(rssi_values)  # Average the RSSI values
            print(f"Average RSSI after {num_measurements} samples: {avg_rssi:.2f} dBm")

            # Calculate the precise distance in centimeters
            distance_cm = calculate_distance_cm(avg_rssi)
            print(f"Estimated Distance: {distance_cm:.2f} cm")
        else:
            print("No networks found or connected")
    
    else:
        print("Unsupported operating system")

get_wifi_rssi()