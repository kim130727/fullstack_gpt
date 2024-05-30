from pydub import AudioSegment

f1 =AudioSegment.from_mp3("C:\download\yang\\240508_yang_0002.mp3")
f2 =AudioSegment.from_mp3("C:\download\yang\\240508_yang_0003.mp3")

f3 = f1+f2

f3.export("C:\download\yang\\240508_yang_0002_2.mp3", format="mp3")