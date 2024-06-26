import re

class RecordingMetadata:
    def __init__(self, Version, Camera, Average_FPS, Frames, Duration):
        self.version = Version
        self.cameraName = Camera
        self.avgFPS = float(Average_FPS)
        self.numFrames = int(Frames)
        self.duration = float(Duration)
    
    def __str__(self):
        return f"Version: {self.version}\nCamera Name: {self.cameraName}\nAverage FPS: {self.avgFPS}\nNumber of Frames: {self.numFrames}\nDuration: {self.duration}"

def parseLine(line:str):
    key = ""
    value = ""
    if line.isspace() or line == "":
        return None
    else:
        s = line.split(":")
        key = s[0].rstrip().replace(" ", "_")
        value = s[1].lstrip()
        return key, value

def parseFrames(frame:str, num_cars = 0):
    ballData = {"L": [], "R": []}
    cameraData = {"F": 90, "L": [], "R": []}
    ballVals = frame.split("B:")[1].split("CM")[0].split("\n")
    cameraVals = frame.split("CM:")[1].split("CR")[0].split("\n")

    ballLoc = ballVals[1].split("L:")[1].split(",")
    ballRot = ballVals[2].split("R:")[1].split(",")
    cameraFOV = cameraVals[1].split("F:")[1]
    cameraLoc = cameraVals[2].split("L:")[1].split(",")
    cameraRot = cameraVals[3].split("R:")[1].split(",")
    # Blender works in meters, but unreal units are centimeters so we divide location by 100
    ballData["L"] = [float(i)/100 for i in ballLoc]
    ballData["L"][1] *= -1
    ballData["R"] = [float(ballRot[0]),
                     -float(ballRot[1]),
                     float(ballRot[2]),
                     -float(ballRot[3])]
    cameraData["F"] = float(cameraFOV)
    cameraData["L"] = [float(i)/100 for i in cameraLoc]
    cameraData["L"][1] *= -1
    cameraData["R"] = [float(cameraRot[0]),
                       -float(cameraRot[2]),
                       -float(cameraRot[1]),
                       -float(cameraRot[3])]
    return ballData, cameraData, {}

    # TODO: parse car data
    


def readCinematicsBuddyFile(filename:str):
    recordingMetadata = {}
    frames = []
    frame_num = 0
    current_frame = ""
    with open(filename, "r") as f:
        line = f.readline().strip()
        while line != "RECORDING METADATA":
            line = f.readline().strip()
        line = f.readline().strip()
        while line != "REPLAY METADATA":
            ret = parseLine(line)
            if ret is not None:
                recordingMetadata[ret[0]] = ret[1]
            line = f.readline().strip()
        while line != "BEGIN ANIMATION":
            line = f.readline().strip()
        line = f.readline().rstrip()
        pattern = re.compile("[0-9]+:{")
        for i in range(int(recordingMetadata["Frames"])):
            s = line.split(":")
            current_frame = s[1]+"\n"
            line = f.readline().rstrip()
            while not (pattern.match(line) or line == ""):
                current_frame += line+"\n"
                line = f.readline().rstrip()
            ballData, cameraData, carData = parseFrames(current_frame)
            frames.append({"B": ballData, "CM": cameraData, "CR": carData})
    return RecordingMetadata(**recordingMetadata), frames