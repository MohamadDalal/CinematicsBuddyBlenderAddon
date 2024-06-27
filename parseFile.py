import re

class RecordingMetadata:
    def __init__(self, Version, Camera, Average_FPS, Frames, Duration, num_cars = 0):
        self.version = Version
        self.cameraName = Camera
        self.avgFPS = float(Average_FPS)
        self.numFrames = int(Frames)
        self.duration = float(Duration)
        self.numCars = int(num_cars)
    
    def __str__(self):
        return f"Version: {self.version}\nCamera Name: {self.cameraName}\nAverage FPS: {self.avgFPS}\nNumber of Frames: {self.numFrames}\nDuration: {self.duration}\nNumber of Cars: {self.numCars}"

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
    carData = [{"L": [], "R": [], "ID": ""} for i in range(num_cars)]
    timeData = {"RF": 0, "T": 0}
    ballVals = frame.split("B:")[1].split("CM")[0].split("\n")
    cameraVals = frame.split("CM:")[1].split("CR")[0].split("\n")
    timeVals = frame.split("T:{")[1].split("\n")
    

    ballLoc = ballVals[1].split("L:")[1].split(",")
    ballRot = ballVals[2].split("R:")[1].split(",")
    cameraFOV = cameraVals[1].split("F:")[1]
    cameraLoc = cameraVals[2].split("L:")[1].split(",")
    cameraRot = cameraVals[3].split("R:")[1].split(",")
    timeReplayFrame = timeVals[1].split("RF:")[1]
    timeTotal = timeVals[2].split("T:")[1]
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
    timeData["RF"] = int(timeReplayFrame)
    timeData["T"] = float(timeTotal)
    
    carVals = frame.split("CR:")[1]
    carLines:list = carVals.splitlines()
    carPattern = re.compile("\t\t[0-9]+:{")
    carStrings = {}
    for i in range(1,len(carLines)):
        #print(carLines[i])
        if carPattern.match(carLines[i]):
            s = carLines[i].split(":")
            carIndex = s[0].strip()
            carStrings[carIndex] = ""
        else:
            carStrings[carIndex] += carLines[i].rstrip()+"\n"
        
    for i, k in enumerate(carStrings.keys()):
        #print(carStrings[k])
        #print(i, k)
        carLoc = carStrings[k].split("L:")[1].split("\n")[0].split(",")
        carRot = carStrings[k].split("R:")[1].split("\n")[0].split(",")
        carData[i]["L"] = [float(i)/100 for i in carLoc]
        carData[i]["L"][1] *= -1
        carData[i]["R"] = [float(ballRot[0]),
                           -float(ballRot[1]),
                           float(ballRot[2]),
                           -float(ballRot[3])]
        carData[i]["ID"] = k

    return ballData, cameraData, carData, timeData

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
        while line != "CARS SEEN":
            line = f.readline().strip()
        pattern = re.compile("\t[0-9]+:{")
        num_cars = 0
        while line != "EXAMPLE FRAME FORMAT":
            #print(line)
            if pattern.match(line):
                num_cars += 1
            line = f.readline().rstrip()
        recordingMetadata["num_cars"] = num_cars
        while line != "BEGIN ANIMATION":
            line = f.readline().rstrip()
        line = f.readline().rstrip()
        pattern = re.compile("[0-9]+:{")
        for i in range(int(recordingMetadata["Frames"])):
            s = line.split(":")
            current_frame = s[1]+"\n"
            line = f.readline().rstrip()
            while not (pattern.match(line) or line == ""):
                current_frame += line+"\n"
                line = f.readline().rstrip()
            ballData, cameraData, carData, timeData = parseFrames(current_frame, num_cars)
            frames.append({"B": ballData, "CM": cameraData, "CR": carData, "T": timeData})
    return RecordingMetadata(**recordingMetadata), frames

if __name__ == "__main__":
    metadata, frames = readCinematicsBuddyFile("test_file.txt")
    print(metadata)
    print(frames[0])