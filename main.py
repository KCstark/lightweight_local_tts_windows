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
import threading
import emoji
import queue
from twitch_chat_irc import twitch_chat_irc
from datetime import datetime 
from pathlib import Path


class mainApp:
    def __init__(self):
        timetamp=datetime.now().strftime("%d-%m-%Y T %H:%M:%S")     
        self.log_file = open(f"ttsApp.log", "w")
        self.log_file.write(f"Logs for {timetamp}, Format as: dd-mm-yyyy T hh:mm:ss \n")
        self.script_directory = Path(__file__).parent.resolve()
        self.server_url="http://localhost:5000"
        self.twitch_token_generator_url="https://twitchtokengenerator.com/"
        self.twitch_irc_url="irc://irc.chat.twitch.tv:6667"
        self.currvoice="default_voice"
        self.chatDelay=0.69
        self.blacklistWords=["http"]
        self.blacklistUsers=["StreamElements"]
        self.readCommands=False
        
        print(f"Current directory : {self.script_directory}")
        self.log_file.write(f"Current directory : {self.script_directory}")
        print("Press ctrl+c to exit")
        self.log_file.write(f"Press ctrl+c to exit")

        self.check_python()
        self.install_piper()
        self.handle_voices() #add a download more open voice later here
        def testvo():
            print("Wating 4sec to test..")
            time.sleep(4)
            self.test_server()
        testvoT=threading.Thread(target=testvo,daemon=True)
        testvoT.start()
        self.connect_app()
        
        
        
    def check_python(self):
        ver = sys.version_info
        print(f"Python version {ver.major}.{ver.minor} found")        
        self.log_file.write(f"Python version {ver.major}.{ver.minor} found")
        

        if ver < (3, 10):
            print("Need Python version >= 3.10, please install!")
            self.log_file.write(f"Need Python version >= 3.10, please install!")
            sys.exit(1)

    def install_piper(self):
        package_name = "piper-tts"
        self.installation_checker(package_name)

    def handle_voices(self):
        voices_folder = self.script_directory / "voices"

        if not voices_folder.exists():
            print("No voices folder found, creating 'voices' folder")
            self.log_file.write(f"No voices folder found, creating 'voices' folder")
            voices_folder.mkdir(exist_ok=True)
            # add a download voice prompt later from here: https://huggingface.co/rhasspy/piper-voices/tree/main
            return

        if not any(voices_folder.iterdir()):
            print("Voices folder is empty. Please add .onnx files.")
            self.log_file.write(f"Voices folder is empty. Please add .onnx files.")
            return

        print("Retrieving voices...")
        self.log_file.write(f"Retrieving voices...")
        voice_files =[]
        for p in voices_folder.iterdir():
            if p.is_dir():
                voice_files.append(p)
        voice_files.sort()

        if not voice_files:
            print("No voices found! Please add .onnx files in 'voices' folder under there name.")
            self.log_file.write(f"No voices found! Please add .onnx files in 'voices' folder under there name.")
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
        self.log_file.write(f"You have selected {selected_folder.name}")
        self.piperServer(selected_folder, voices_folder)

    def test_server(self):
        print("Confirming server working, generating test output..")
        self.log_file.write(f"Confirming server working, generating test output..")
        out_dirr=self.script_directory/"output"
        if not out_dirr.exists():
            print("output folder dont exists, creating..")
            self.log_file.write(f"output folder dont exists, creating..")
            self.script_directory.mkdir(exist_ok=True)
        payload = {
        "text": f"Hello! I'm {self.currvoice}, happy to meet you!"
        }
        output_file = out_dirr / "testserver.wav"
        
        #testing the server & then playing sound
        if self.apiCall(output_file,payload):
            self.playWav(output_file)
        else:
            return
    
    def connect_app(self):
        appMap={1:'Twitch',2:'YouTube'}
        print(f"Avaiable apps... \n{appMap}")
    
        while True:
            try:
                choice = int(input("Enter the app you want to connect to: #"))
                appMap[choice]
                break
            except (ValueError, KeyError):
                print("Invalid selection, try again.")
        print(f"Selected: {appMap[choice]}")
        self.log_file.write(f"Selected: {appMap[choice]}")
        
        match (choice):
            case 1: 
                self.twitch_setup()
            case _:
                print(f"Some error in selection: {appMap[choice]}, or not implementaion in progress..")
                self.log_file.write(f"Some error in selection: {appMap[choice]}, or not implementaion in progress..")
        
        
        
    def twitch_setup(self):
        print("Running Twitch setup...")
        self.log_file.write(f"Running Twitch setup...")
        #  pip install twitch-chat-irc
        self.installation_checker("twitch-chat-irc")
        
        # either login or just type the channel name to acccess chat
        loginOptions={1:'annon(only read access)',2:'token (full access to chat)'}
        print(loginOptions)
        while True:
            try:
                choose=int(input("login choice: #"))
                loginOptions[choose]
                break
            except (ValueError, KeyError):
                print("Invalid selection, try again.")
        # https://pypi.org/project/twitch-chat-irc/
        connection=self.twitchLogin(choose,loginOptions)
        self.log_file.write(f"Connection created to twitch")
        ##########################                           ###########################################
        # #impl reentery logic here for 
        # 3 cases-> stopping-end, stopping-new_channel, stopping-restarting with same channel
        while True:
            channel_name=input("Enter the channel name you want to connect to: ")
            try:
                self.twitch_message_handler(connection,channel_name,choose)
            except KeyboardInterrupt:
                print(f"\nDetected Ctrl+C, stopping...")
                break
            # choiceChannel=input(f"Disconnecting...! Want to change channels? y/n: ")
            # if choiceChannel.lower()!= "y":                
            #     break

        # Close connection
        print(f"Closing twitch connection...")
        self.log_file.write(f"Closing twitch connection...")
        connection.close_connection()
        
    def twitch_message_handler(self,connection,channel_name,choice):
        print(f"Starting new socket, listenting to all the new messages now, \n(ctrl+c to stop socket)")
        self.log_file.write(f"Starting new socket, listenting to all the new messages now, \n(ctrl+c to stop socket)")
        
        stopping_event=threading.Event()
        message_queue=queue.Queue(maxsize=50)
        # message_queue=queue.Queue()
        
        def listener():
            # Receiving messages
            # creates a socket to listen message will break on ctrl+c only
            try:            
                print(f"listener on............")
                connection.listen(channel_name,
                                on_message=lambda msg: message_queue.put(("Twitch",msg)))                
            except Exception as e:
                # this will end with an error & thats fine
                stopping_event.set()
                print(f"Listner socket breaking... \n{e}")
        
        def processor():
            while not stopping_event.is_set():
                try:
                    #working & cehcking message queue every 2 sec
                    source, msg=message_queue.get(timeout=1)
                    self.process_message(msg,source)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Error processing message: {e}")
                    self.log_file.write(f"Error processing message: {e}\n")
                    
        def writer():
            # Send a message
            while True:
                message=input("('+stop-' to disconnect) \nEnter message to send: ")
                if message=="+stop-":
                    stopping_event.set()
                    connection.send(channel_name,"/part")
                    # connection.close_connection()
                    break
                connection.send(channel_name,message)
        
        listenerT=threading.Thread(target=listener,daemon=True)
        messProcessorT=threading.Thread(target=processor,daemon=True)
        
        def startListen():
            listenerT.start()
            messProcessorT.start()
            if choice!=1:
                writer()
            else:
                message=input("'+stop-' to disconnect: ")
                if message=="+stop-":
                    stopping_event.set()
                    # connection.close_connection()
                    return
                elif message=="+ref-":
                    stopping_event.set()
                    # connection.close_connection()
                    print(f"Refreshing the socket...")
                    self.log_file.write(f"Refreshing the socket...")

        startListen()
        #waiting for processor to finish current message
        messProcessorT.join(timeout=5)
            
        
    def  process_message(self,message,source):
        print(f"\nFrom {source}:{message['message']}")
        mess=message['message']
        usrr=message['display-name']
        mess=self.resloveEmojis(mess)
        self.log_file.write(f"\nFrom {source}:{mess}")
        # below filter to ignore links, !commands & some accounts dont read them ###############################
        if not self.readCommands and mess.startswith('!'): return
        for word in self.blacklistWords:
            if mess.find(word)!=-1: return
        #blackleinst users
        for usr in self.blacklistUsers:
            if usrr==usr: return
        
        self.playmessage(message['message'],source)
        
    def resloveEmojis(self, message):
        self.log_file.write("Resolving emoji")
        return emoji.demojize(message,delimiters=(" ", " "))
        
        
    def playmessage(self,message,source):
        out_dirr=self.script_directory/"output"
        # print(f"simulating palying messsahge........ {message}")
        if not out_dirr.exists():
            print("output folder dont exists, creating..")
            self.log_file.write(f"output folder dont exists, creating..")
            self.script_directory.mkdir(exist_ok=True)
        payload = {
        "text": message
        }
        output_file = out_dirr / f"{source}-chat.wav"
        
        #playing on the server
        if self.apiCall(output_file,payload):
            self.playWav(output_file)
        else:
            return
        
        
    
    def twitchLogin(self,choice,loginOptions):
        print(f"login mode: {loginOptions[choice]}")
        self.log_file.write(f"login mode: {loginOptions[choice]}")
        outh_token= "random_string_hehe" 
        refresh_token= "random_string_hehe"
        nickname= "justinfan123456"
        if choice!=1:
            print(f"Go {self.twitch_token_generator_url} & get your tokens with 'chat:read' and 'chat:edit' access minimum!")
            outh_token=input("Enter ACCESS TOKEN: ")
            refresh_token=input("Enter REFRESH TOKEN: ")
            nickname=input("Enter Your nickname(make sure its same as the account you used to get the token): ")
        
        # connect to twitch irc chat now
        print(f"Connecting to twitch...")
        connection = twitch_chat_irc.TwitchChatIRC()
        connection = twitch_chat_irc.TwitchChatIRC(nickname,outh_token)
        
        print(f"Twitch connection created!")
        return connection
        
        
    def installation_checker(self,package_name):
        try:
            print(f"Checking if {package_name} is installed...")
            self.log_file.write(f"Checking if {package_name} is installed...")
            subprocess.check_output(
                [sys.executable, "-m", "pip", "show", package_name],
                stderr=subprocess.STDOUT
            )
            print(f"{package_name} is already installed")
            self.log_file.write(f"{package_name} is already installed")            
        except subprocess.CalledProcessError:
            print(f"{package_name} is NOT installed, installing...")
            self.log_file.write(f"{package_name} is NOT installed, installing...")
            try:
                subprocess.check_output(
                    # [sys.executable, "-m", "pip", "install", "--user", package_name],
                    # stderr=subprocess.STDOUT
                    [sys.executable, "-m", "pip", "install", package_name],
                    stderr=subprocess.STDOUT #for venv version
                )
                print(f"{package_name} installed successfully")
                self.log_file.write(f"{package_name} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error installing {package_name}:\n{e.output.decode()}")
                self.log_file.write(f"Error installing {package_name}:\n{e.output.decode()}")
                sys.exit(1)
        
        
    def apiCall(self,output_file_path,payload):
        # print(f"Calling server api...")
        self.log_file.write(f"Calling server api...")        
        response = requests.post(
            self.server_url,
            json=payload,# automatically sets Content-Type: application/json
            timeout=30
        )

        if response.status_code == 200:
            output_file_path.write_bytes(response.content)
            # print(f"Saved the response: {output_file_path}")
            return True
        else:
            print(f"Request failed (restart the app!!): {response.status_code}\n{response.text}")
            self.log_file.write(f"Request failed (restart the app!!): {response.status_code}\n{response.text}")
            return False
        
        
    def playWav(self, output_file_path):
        # print(f"Playing sound from {output_file_path}")
        self.log_file.write(f"Playing sound from {output_file_path}")
        # reading the file saved
        wave_obj = sa.WaveObject.from_wave_file(str(output_file_path))
        play_obj = wave_obj.play()
        play_obj.wait_done()  #optional, waits until finished playing
        
    
    def piperServer(self, selected_voice_folder, voices_folder):
        print("Starting piper server with:")
        print(f"Voice: {selected_voice_folder.name}")
        self.currvoice={selected_voice_folder.name}
        print(f"Folder: {voices_folder}")
        #start piper server here
        # python -m piper.http_server -m lisa
        voiceName=selected_voice_folder.name
        # Format as: dd-mm-yyyy T hh:mm:ss
        timetamp=datetime.now().strftime("%d-%m-%Y T %H:%M:%S")
        # log_file = open(f"piper_server.log", "w")    
        self.log_file.write(f"Below are logs for {timetamp}, Format as: dd-mm-yyyy T hh:mm:ss \n")
        try:
                self.piperProcess=subprocess.Popen(
                    [sys.executable, "-m", "piper.http_server", "-m", voiceName],
                    cwd=selected_voice_folder,
                    # below to see server logs in console
                    stdout=self.log_file,
                    stderr=self.log_file
                )
                print("piper-tts server running..")
        except Exception as e:
                print(f"Error starting piper-tts server:\n{e}")
                self.log_file.write(f"Error starting piper-tts server:\n{e}")
                sys.exit(1)
        
    def stop_piperServer(self):
        if hasattr(self,'piperProcess') and self.piperProcess.poll() is None:
            print("Stopping piper-tts server...")
            self.log_file.write(f"Stopping piper-tts server...")
            self.piperProcess.terminate()
            try:
                self.piperProcess.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing piper server...")
                self.log_file.write(f"Force killing piper server...")
                self.piperProcess.kill()
        


if __name__ == "__main__":
    app=mainApp()
    try:
        while True:
            pass #keeps main thread runnnig
    except KeyboardInterrupt:
        print("\nExiting piper script and server!!")    
        app.stop_piperServer()

