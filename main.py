# 1
# need to make a script that can start piper tts server

#check python version needs to be >= 3.10
#check pipertts server is installed-- how?
#-> install if not then start server else just start the server

# start piper-tts server at current location tho need to add voice pack here hmm..
# check if voices older present if yes go in it & run server at that location, then
# list all voices present in it, select on & run server with that(might need to check
# if there is a way change voice adhocly in piper-tts for now just select one use picks)
# after user selects voice run server 
# test creating a dummy ------- create a test wav file then play it to confirm 

# python3 -m pip install piper-tts[http]

import sys
import subprocess
import requests 
import time
import simpleaudio as sa
from datetime import datetime 
from pathlib import Path


class PiperScript:
    def __init__(self):
        self.script_directory = Path(__file__).parent.resolve()
        self.server_url="http://localhost:5000"
        print(f"Current directory : {self.script_directory}")
        print("Press ctrl+c to exit")

        self.check_python()
        self.install_piper()
        self.handle_voices() #add a download more open voice later here
        print("Wating 5sec to test..")
        time.sleep(5)
        self.test_server()
        
        

    def check_python(self):
        ver = sys.version_info
        print(f"Python version {ver.major}.{ver.minor} found")

        if ver < (3, 10):
            print("Need Python version >= 3.10, please install!")
            sys.exit(1)

    def install_piper(self):
        package_name = "piper-tts"

        try:
            print("Checking if piper-tts is installed...")
            subprocess.check_output(
                [sys.executable, "-m", "pip", "show", package_name],
                stderr=subprocess.STDOUT
            )
            print("piper-tts is already installed")
        except subprocess.CalledProcessError:
            print(f"{package_name} is NOT installed, installing...")
            try:
                subprocess.check_output(
                    # [sys.executable, "-m", "pip", "install", "--user", package_name],
                    # stderr=subprocess.STDOUT
                    [sys.executable, "-m", "pip", "install", package_name],
                    stderr=subprocess.STDOUT #for venv version
                )
                print("piper-tts installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error installing piper-tts:\n{e.output.decode()}")
                sys.exit(1)

    def handle_voices(self):
        voices_folder = self.script_directory / "voices"

        if not voices_folder.exists():
            print("No voices folder found, creating 'voices' folder")
            voices_folder.mkdir(exist_ok=True)
            # add a download voice prompt later from here: https://huggingface.co/rhasspy/piper-voices/tree/main
            return

        if not any(voices_folder.iterdir()):
            print("Voices folder is empty. Please add .onnx files.")
            return

        print("Retrieving voices...")
        voice_files =[]
        for p in voices_folder.iterdir():
            if p.is_dir():
                voice_files.append(p)
        voice_files.sort()

        if not voice_files:
            print("No voices found! Please put .onnx files in 'voices' folder under there name.")
            return

        for idx, file in enumerate(voice_files, start=1):
            print(f"{idx}. {file.name}")

        while True:
            try:
                v_choice = int(input("Enter the voice you want to load: #"))
                selected_folder = voice_files[v_choice - 1]
                break
            except (ValueError, IndexError):
                print("Invalid selection, try again.")

        print(f"You have selected {selected_folder.name}")
        self.piperServer(selected_folder, voices_folder)

    def test_server(self):
        print("Confirming server working, generating test output..")
        out_dirr=self.script_directory/"output"
        if not out_dirr.exists():
            print("output folder dont exists, creating..")
            self.script_directory.mkdir(exist_ok=True)
        payload = {
        "text": "This is a testttttttttt-1 2 3 4 5 6 7 8 hehehe. I'd rather you just say the words instead, Oh yes why not :)"
        }
        output_file = out_dirr / "testserver.wav"
        
        #testing the server & then playing sound
        if self.apiCall(output_file,payload):
            self.playWav(output_file)
        else:
            return
        
    def apiCall(self,output_file_path,payload):
        print(f"Calling server api...")
        response = requests.post(
            self.server_url,
            json=payload,# automatically sets Content-Type: application/json
            timeout=30
        )

        if response.status_code == 200:
            output_file_path.write_bytes(response.content)
            print(f"Saved the response: {output_file_path}")
            return True
        else:
            print(f"Request failed (restart the app!!): {response.status_code}\n{response.text}")
            return False
        
        
    def playWav(self, output_file_path):
        print(f"Playing sound from {output_file_path}")
        # reading the file saved
        wave_obj = sa.WaveObject.from_wave_file(str(output_file_path))
        play_obj = wave_obj.play()
        play_obj.wait_done()  #optional, waits until finished playing
        
    
    def piperServer(self, selected_voice_folder, voices_folder):
        print("Starting piper server with:")
        print(f"Voice: {selected_voice_folder.name}")
        print(f"Folder: {voices_folder}")
        #start piper server here
        # python -m piper.http_server -m lisa
        voiceName=selected_voice_folder.name
        # Format as: dd-mm-yyyy T hh:mm:ss
        timetamp=datetime.now().strftime("%d-%m-%Y T %H:%M:%S")
        log_file = open(f"piper_server.log", "w")
        log_file.write(f"Below are logs for {timetamp}, Format as: dd-mm-yyyy T hh:mm:ss \n")
        try:
                self.piperProcess=subprocess.Popen(
                    [sys.executable, "-m", "piper.http_server", "-m", voiceName],
                    cwd=selected_voice_folder,
                    # below to see server logs in console
                    stdout=log_file,
                    stderr=log_file
                )
                print("piper-tts server running..")
        except Exception as e:
                print(f"Error starting piper-tts server:\n{e}")
                sys.exit(1)
        
    def stop_piperServer(self):
        if hasattr(self,'piperProcess') and self.piperProcess.poll() is None:
            print("Stopping piper-tts server...")
            self.piperProcess.terminate()
            try:
                self.piperProcess.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing piper server...")
                self.piperProcess.kill()
        


if __name__ == "__main__":
    app=PiperScript()
    try:
        while True:
            pass #keeps main thread runnnig
    except KeyboardInterrupt:
        print("\nExiting piper script and server!!")
        app.stop_piperServer()

