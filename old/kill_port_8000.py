import os
import signal
import subprocess
import sys

def kill_process_on_port(port):
    try:
        # Find process using the port
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            shell=True
        )
        
        lines = result.stdout.split('\n')
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                pid = parts[-1]
                print(f"Found process {pid} using port {port}")
                
                # Kill the process
                try:
                    subprocess.run(['taskkill', '/F', '/PID', pid], shell=True, check=True)
                    print(f"Successfully killed process {pid}")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"Failed to kill process {pid}: {e}")
                    return False
        
        print(f"No process found using port {port}")
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Killing process on port 8000...")
    kill_process_on_port(8000)
