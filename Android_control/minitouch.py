import pdb
import subprocess
import time
import socket
import os
from typing import Tuple
import warnings
#warnings.filterwarnings("ignore", message=".*sBIT.*") #I don't know how to fix this, there is no way I click 
#warnings.filterwarnings('ignore', category=UserWarning)#images again. Will worry later
import cv2
# adb shell monkey -p com.gof.global -c android.intent.category.LAUNCHER 1

from contextlib import contextmanager
import sys
import io

#@contextmanager
#def suppress_stderr():
#    stderr = sys.stderr
#    stderr_redirector = io.StringIO()
#    sys.stderr = stderr_redirector
#    try:
#        yield stderr_redirector
#    finally:
#        sys.stderr = stderr
@contextmanager
def suppress_stderr():
    # Save the current stderr
    old_stderr = sys.stderr
    # Open null device
    null = os.open(os.devnull, os.O_WRONLY)
    # Replace stderr with null device
    os.dup2(null, sys.stderr.fileno())
    
    try:
        yield
    finally:
        # Restore stderr
        sys.stderr = old_stderr
        os.close(null)

ADB_PATH = os.path.join(os.path.abspath(''),     #Assuming scrcpy will be in that path, convenient. Maybe should
    'Android_control',
    'scrcpy-win64-v2.4',                       #allow a default path too
    'adb.exe')
class AndroidTouchControl:
    def __init__(self, ID:str,adb_path: str =ADB_PATH, minitouch_dir: str = "./prebuilt/"):
        self.adb_path = adb_path
        self.minitouch_dir = minitouch_dir
        self.device_id = ID
        self.device_arch = None
        self.minitouch_process = None
        self.socket = None
        self.pressure_max = None
        self.max_x, self.max_y = self._get_device_dimensions()
        # if self._is_emulator():
            

    @classmethod
    def find_devices(cls):
        start = subprocess.run ([ADB_PATH,'start-server'],capture_output=True)
        time.sleep(10)
        result = subprocess.run([ADB_PATH,'devices'],capture_output=True)
        # pdb.set_trace()
        if result.stdout:
            if (n:=result.stdout.decode().splitlines()[1:-1]):
                return [i.split() for i in n]
            else:
                return 'ADB connected, but no devices found'
        else:
            return result
    @classmethod
    def connect_to_first_device(cls, verify=True):
        result = AndroidTouchControl.find_devices()
        if type(result) is str:
            print(result)
            input('Press enter to close this window')
            exit()
        if type(result) is not list:
            print(result)
            print('Something went wrong')
            input('Press enter to close this window')
            exit()
        for device in result:
            if device[1].lower() =='device':
                x = AndroidTouchControl(device[0])
                if verify:
                    print(f'Testing device {device[0]}')
                    print('Attempting to swipe on device, please open something that will let you verify the swipe')
                    input('Press enter to initiate swipe...')
                    x.swipe(200,900,200,300)
                    check = input('Did it swipe? Press y for yes:')
                    if check.lower().startswith('y'):
                        return x
                return x           #returning just x here, needs better solution. 
        print('Looks like could not connect')
        return None

    def _run_adb(self, *args):
        """Adds the 'adb' and the device id by default, add other stuff"""
        cmd = [self.adb_path]
        if self.device_id:
            cmd.extend(['-s', self.device_id])
        cmd.extend(args)
        #print(cmd)
        return subprocess.run(cmd, capture_output=True)
    def _is_emulator(self):
        """Check if the device is an emulator"""
        result = self._run_adb('shell', 'getprop', 'ro.product.model')
        model = result.stdout.decode('utf-8').strip()
        return 'sdk' in model.lower() or 'emulator' in model.lower()
    def take_screenshot(self, output_path='screen.png'):
        """Take a screenshot of the device"""
        # Take screenshot and save to device
        self._run_adb('shell', 'screencap', '-p', '/sdcard/screen.png')
        # Pull screenshot from device
        self._run_adb('pull', '/sdcard/screen.png', output_path)
        # Clean up
        self._run_adb('shell', 'rm', '/sdcard/screen.png')
        
        # Verify screenshot resolution
        img = cv2.imread(output_path)
        if img is not None:
            height, width = img.shape[:2]
            if (width, height) != (self.max_x, self.max_y):
                raise Exception(f"Screenshot resolution mismatch. Expected {self.max_x}x{self.max_y}, got {width}x{height}")
        
        return output_path

    def find_template(self, template_path, screenshot_path=None, threshold=0.8):
        """
        Find template image in screenshot
        Returns: (x, y) center coordinates of best match, or None if not found
        """
        # Take screenshot if not provided
        if screenshot_path is None:
            screenshot_path = self.take_screenshot()

        # Read images
        screenshot = cv2.imread(screenshot_path)
        with suppress_stderr():                                         #Till I find a better fix
            template = cv2.imread(template_path)
        
        # Verify template resolution is compatible
        template_height, template_width = template.shape[:2]
        if template_width > self.max_x or template_height > self.max_y:
            raise Exception(f"Template image is larger than target resolution: {template_width}x{template_height}")

        # Perform template matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # Get center point of match
            center_x = max_loc[0] + template_width//2
            center_y = max_loc[1] + template_height//2
            return (center_x, center_y)
        return None

    def tap(self, x, y):
        """Tap at specific coordinates"""
        if 0 <= x <= self.max_x and 0 <= y <= self.max_y:
            self._run_adb('shell', 'input', 'tap', str(x), str(y))
        else:
            raise Exception(f"Tap coordinates ({x}, {y}) out of bounds for resolution {self.target_width}x{self.target_height}")
    def swipe(self, x1, y1, x2, y2):
        """Tap at specific coordinates"""
        if 0 <= x1 <= self.max_x and 0 <= y1 <= self.max_y:
            self._run_adb('shell', 'input', 'swipe', str(x1), str(y1),str(x2), str(y2))
        else:
            raise Exception(f"Tap coordinates ({x1}, {y1}) out of bounds for resolution {self.max_x}x{self.max_y}")

    def click_on_image(self, template_path, max_attempts=3, threshold=0.8):
        """
        Find and click on an image template
        Returns: True if successful, False if not found
        """
        for attempt in range(max_attempts):
            coords = self.find_template(template_path, threshold=threshold)
            if coords:
                x, y = coords
                self.tap(x, y)
                return True
            time.sleep(1)
        return False

    def wait_for_image(self, template_path, timeout=30, threshold=0.8):
        """
        Wait for an image to appear on screen
        Returns: (x, y) coordinates if found, None if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            coords = self.find_template(template_path, threshold=threshold)
            if coords:
                return coords
            time.sleep(1)
        return None

    def _get_device_dimensions(self):
        """Get the device screen dimensions using adb."""
        result = subprocess.run(
            [self.adb_path, "shell", "wm size"],
            capture_output=True,
            text=True
        )
        # Parse "Physical size: 1080x2400" format
        # size = result.stdout.strip().split(': ')[1].split('x')
        # adb gives me Override size and physical size. So as o comes before p, I sort and take the first one. This will break
        size = sorted(result.stdout.splitlines())[0].split(': ')[1].split('x')
        return int(size[0]), int(size[1])

    def _initialize_minitouch_params(self, socket_connection):
        """Initialize minitouch parameters from its output."""
        # Read parameters from minitouch
        params = socket_connection.recv(1024).decode('utf-8').split('\n')
        for line in params:
            if line.startswith('$'):
                _, width, height, pressure = map(int, line.split(' ')[1:])
                self.max_x = width
                self.max_y = height
                self.pressure_max = pressure
                break

    def _scale_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """Scale screen coordinates to minitouch coordinates."""
        if not (self.max_x and self.max_y):
            device_width, device_height = self._get_device_dimensions()
            # Use a default max if not initialized
            self.max_x = self.max_x or device_width
            self.max_y = self.max_y or device_height

        # Scale coordinates
        scaled_x = int((x * self.max_x) / device_width)
        scaled_y = int((y * self.max_y) / device_height)
        return scaled_x, scaled_y

    def get_device_architecture(self) -> str:
        """Get the CPU architecture of the connected Android device."""
        result = subprocess.run(
            [f'"{self.adb_path}"', "shell", "getprop", "ro.product.cpu.abi"],
            capture_output=True,
            text=True
        )
        arch = result.stdout.strip()
        
        # Map Android architectures to minitouch binary names
        arch_map = {
            'arm64-v8a': 'arm64',
            'armeabi-v7a': 'arm',
            'x86_64': 'x86_64',
            'x86': 'x86'
        }
        self.device_arch = arch
        # self.device_arch = arch_map.get(arch, arch)
        return self.device_arch

    def push_minitouch(self) -> None:
        """Push the appropriate minitouch binary to the device."""
        if not self.device_arch:
            self.get_device_architecture()
            
        # Construct path to the minitouch binary
        minitouch_path = os.path.join(
            self.minitouch_dir,
            self.device_arch,
            "bin",
            "minitouch"
        )
        
        # First try with regular minitouch
        push_result = subprocess.run([
            self.adb_path, "push",
            minitouch_path,
            "/data/local/tmp/minitouch"
        ])
        
        # If regular minitouch fails, try minitouch-nopie
        if push_result.returncode != 0:
            minitouch_nopie_path = os.path.join(
                self.minitouch_dir,
                self.device_arch,
                "bin",
                "minitouch-nopie"
            )
            subprocess.run([
                self.adb_path, "push",
                minitouch_nopie_path,
                "/data/local/tmp/minitouch"
            ])
        
        # Set executable permissions
        subprocess.run([
            self.adb_path, "shell",
            "chmod 755 /data/local/tmp/minitouch"
        ])

    def start_minitouch(self) -> None:
        """Start the minitouch service on the device."""
        # Kill any existing minitouch process
        subprocess.run([
            self.adb_path, "shell",
            "pkill", "minitouch"
        ])
        
        # Start minitouch in background
        self.minitouch_process = subprocess.Popen([
            self.adb_path, "shell",
            "/data/local/tmp/minitouch"
        ])
        
        # Forward the minitouch socket
        subprocess.run([
            self.adb_path, "forward",
            "tcp:1111", "localabstract:minitouch"
        ])
        
        # Give it time to start
        time.sleep(1)

    def perform_pinch(self, start_points: Tuple[Tuple[int, int], Tuple[int, int]], 
                     end_points: Tuple[Tuple[int, int], Tuple[int, int]], 
                     duration: float = 0.5) -> None:
        """
        Perform a pinch gesture (zoom in/out).
        
        Args:
            start_points: ((x1, y1), (x2, y2)) starting coordinates for both fingers
            end_points: ((x1, y1), (x2, y2)) ending coordinates for both fingers
            duration: Time in seconds for the gesture
        """
        import socket
        
        # Connect to minitouch socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 1111))
        
        # Get initial info from minitouch
        s.recv(1024).decode('utf-8')
        
        try:
            # Start tracking two fingers
            s.send(f"d 0 {start_points[0][0]} {start_points[0][1]} 50\n".encode())
            s.send(f"d 1 {start_points[1][0]} {start_points[1][1]} 50\n".encode())
            s.send(b"c\n")
            
            # Calculate intermediate points
            steps = int(duration * 60)  # 60 updates per second
            for i in range(steps):
                t = i / steps
                x1 = int(start_points[0][0] + (end_points[0][0] - start_points[0][0]) * t)
                y1 = int(start_points[0][1] + (end_points[0][1] - start_points[0][1]) * t)
                x2 = int(start_points[1][0] + (end_points[1][0] - start_points[1][0]) * t)
                y2 = int(start_points[1][1] + (end_points[1][1] - start_points[1][1]) * t)
                
                s.send(f"m 0 {x1} {y1} 50\n".encode())
                s.send(f"m 1 {x2} {y2} 50\n".encode())
                s.send(b"c\n")
                time.sleep(1/60)
            
            # Release both fingers
            s.send(b"u 0\n")
            s.send(b"u 1\n")
            s.send(b"c\n")
            
        finally:
            s.close()
    def perform_pinch(self, start_points: Tuple[Tuple[int, int], Tuple[int, int]], 
                     end_points: Tuple[Tuple[int, int], Tuple[int, int]], 
                     duration: float = 0.5) -> None:
        """
        Perform a pinch gesture with coordinate scaling.
        
        Args:
            start_points: ((x1, y1), (x2, y2)) starting coordinates in screen pixels
            end_points: ((x1, y1), (x2, y2)) ending coordinates in screen pixels
            duration: Time in seconds for the gesture
        """
        # Create socket connection if not exists
        if not hasattr(self, 'socket') or not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('127.0.0.1', 1111))
            self._initialize_minitouch_params(self.socket)

        try:
            # Scale all coordinates
            start_p1_scaled = self._scale_coordinates(*start_points[0])
            start_p2_scaled = self._scale_coordinates(*start_points[1])
            end_p1_scaled = self._scale_coordinates(*end_points[0])
            end_p2_scaled = self._scale_coordinates(*end_points[1])

            # Start tracking two fingers
            self.socket.send(f"d 0 {start_p1_scaled[0]} {start_p1_scaled[1]} 50\n".encode())
            self.socket.send(f"d 1 {start_p2_scaled[0]} {start_p2_scaled[1]} 50\n".encode())
            self.socket.send(b"c\n")
            
            steps = int(duration * 60)  # 60 updates per second
            for i in range(steps):
                t = i / steps
                x1 = int(start_p1_scaled[0] + (end_p1_scaled[0] - start_p1_scaled[0]) * t)
                y1 = int(start_p1_scaled[1] + (end_p1_scaled[1] - start_p1_scaled[1]) * t)
                x2 = int(start_p2_scaled[0] + (end_p2_scaled[0] - start_p2_scaled[0]) * t)
                y2 = int(start_p2_scaled[1] + (end_p2_scaled[1] - start_p2_scaled[1]) * t)
                
                self.socket.send(f"m 0 {x1} {y1} 50\n".encode())
                self.socket.send(f"m 1 {x2} {y2} 50\n".encode())
                self.socket.send(b"c\n")
                time.sleep(1/60)
            
            # Release both fingers
            self.socket.send(b"u 0\n")
            self.socket.send(b"u 1\n")
            self.socket.send(b"c\n")

        except Exception as e:
            print(f"Error during pinch: {e}")
            # Close socket on error to force reconnect next time
            self.socket.close()
            self.socket = None
            raise

    def cleanup(self) -> None:
        """Clean up resources and stop minitouch."""
        if self.minitouch_process:
            self.minitouch_process.terminate()
            subprocess.run([self.adb_path, "shell", "pkill", "minitouch"])
            subprocess.run([self.adb_path, "forward", "--remove", "tcp:1111"])



if __name__ =='__main__':
    # Initialize the controller
    # pdb.set_trace()
    controller = AndroidTouchControl(
        adb_path=ADB_PATH,  # Path to your adb executable
        minitouch_dir="./prebuilt/"  # Directory containing minitouch binaries
    )

    # Setup minitouch
    controller.get_device_architecture()  # Automatically detects device architecture
    controller.push_minitouch()  # Pushes the appropriate binary to the device
    controller.start_minitouch()  # Starts the minitouch service

    try:
        # Perform a pinch-out (zoom in)
        controller.perform_pinch(
            start_points=((300, 1000), (400, 700)),  # Starting points for two fingers
            end_points=((300, 1000), (400, 500)),    # End points (moving apart)
            duration=1.5                            # Duration of the gesture
        )
        time.sleep(3)
        
        # Perform a pinch-in (zoom out)
        controller.perform_pinch(
            start_points=((300, 1000), (400, 500)),  # Starting points for two fingers
            end_points=((300, 1000), (400, 700)),    # End points (moving together)
            duration=0.5                            # Duration of the gesture
        )

    finally:
        # Clean up when done
        controller.cleanup()
