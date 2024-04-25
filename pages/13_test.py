from pydub import AudioSegment  
from pydub.playback import play


def mp3ToWav(src_file, dest_file):  
    sound = AudioSegment.from_mp3(src_file)

    #play(sound)  
    sound.export(dest_file, format="wav")  
    pass  

def wavToMp3(src_file, dest_file):  
    sound = AudioSegment.from_wav(src_file)  
    sound.export(dest_file, format="mp3")

    #play(sound)  
    pass  

if __name__ == '__main__':  
    wavToMp3(src_file="C:\download\yang\\240424_yang 0002.wav",dest_file="C:\download\yang\\240424_yang 0002.mp3")
    wavToMp3(src_file="C:\download\yang\\240424_yang 0003.wav",dest_file="C:\download\yang\\240424_yang 0003.mp3")  
    wavToMp3(src_file="C:\download\yang\\240424_yang 0004.wav",dest_file="C:\download\yang\\240424_yang 0004.mp3")  
    wavToMp3(src_file="C:\download\yang\\240424_yang 0005.wav",dest_file="C:\download\yang\\240424_yang 0005.mp3")  
    wavToMp3(src_file="C:\download\yang\\240424_yang 0006.wav",dest_file="C:\download\yang\\240424_yang 0006.mp3")  
    wavToMp3(src_file="C:\download\yang\\240424_yang 0007.wav",dest_file="C:\download\yang\\240424_yang 0007.mp3")  
    wavToMp3(src_file="C:\download\yang\\240424_yang 0008.wav",dest_file="C:\download\yang\\240424_yang 0008.mp3")  
    pass