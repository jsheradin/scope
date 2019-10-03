def framegen(chunk):
    import contextlib
    with contextlib.redirect_stdout(None):
        import pygame
    size = chunk[0][0][1]
    thick = chunk[0][0][2]
    pygame.init()
    pygame.display.init()
    screen = pygame.display.set_mode([size, size])
    white = pygame.Color(255, 255, 255)
    black = pygame.Color(0, 0, 0)
    for i in range(len(chunk)):
        bite = chunk[i][1]
        pygame.draw.rect(screen, black, [[0, 0], [size, size]])
        for j in range(len(bite) - 1):
            pygame.draw.line(screen, white, [bite[j, 0], bite[j, 1]], [bite[j + 1, 0], bite[j + 1, 1]], thick)
        pygame.image.save(screen, chunk[i][0][0])
    pygame.display.quit()
    # pygame.quit()


def scope(file, fr, size, thick, threads):
    import numpy as np
    from scipy.io.wavfile import read
    import math
    from multiprocessing import Pool
    import wave
    import contextlib
    import os

    print("Setting up")

    abs_path = os.getcwd() + "/scope/"
    with contextlib.closing(wave.open(abs_path+file, 'r')) as f:
        nframes = f.getnframes()
        rate = f.getframerate()
        duration = nframes / float(rate)

    points_file = read(abs_path+file)
    points = points_file[1]  # get just samples
    points = (points / (2 * max(points[:, 0])) + 0.5) * size  # scale to window
    length = len(points)
    points[:, 1] = size - points[:, 1]  # Flip upside down
    pps = len(points) / duration  # Points per second
    ppf = math.floor(pps / fr)  # Points per frame
    total = round(length / ppf)  # Number of frames
    file_len = len(str(total))  # Length of filename number
    frames = []  # Each element is a frame

    for i in range(total):
        frames.append([[abs_path + "out/" + str(i).rjust(file_len, '0') + ".png", size, thick], points[i * ppf:(i + 1) * ppf]])

    print("Rendering frames")
    packets = []
    fpt = math.ceil(total / threads)  # Frames per thread
    for i in range(threads):
        packets.append(frames[i * fpt:(i + 1) * fpt])

    if __name__ == '__main__':
        with Pool(threads) as p:
            p.map(framegen, packets)

    print("Rendering video")
    os.system("ffmpeg -y -framerate {} -i {}out/%0{}d.png -i \"{}\" -shortest \"{}.mp4\"".format(fr, abs_path, file_len, abs_path+file, abs_path+file.split('.')[0].split('/')[1]))
    print("Done")


scope("music/05 Spirals.wav", 48, 1080, 2, 24)
