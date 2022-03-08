from pynput import mouse
import pyautogui
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, ImageClip
from moviepy.editor import concatenate_videoclips
import moviepy.video.fx.all as vfx


# record screen for a selected region
def record_screen(fileformat="mp4", region=(0, 0, 1920, 1080), filename="Recording.mp4", fps=20.0, display=False):
    # specify output format, avi or mp4, by default mp4
    if fileformat == "avi":
        codec = cv2.VideoWriter_fourcc(*"XVID")
    else:
        codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    # create a VideoWriter object
    w, h = region[2], region[3]
    video_writer = cv2.VideoWriter(filename, codec, fps, (w, h))
    # create an empty window and update window size
    cv2.namedWindow("Recording", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Recording", int(w/2), int(h/2))

    while True:
        # grab screen using PyAutoGUI
        img = pyautogui.screenshot(region=region)
        # convert image to a numpy array
        frame = np.array(img)
        # convert it from BGR to RGB(Red, Green, Blue)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # write it to the output file
        video_writer.write(frame)
        # display recording when necessary
        if display:
            cv2.imshow('Recording', frame)
        # quit recording when pressing 'q' or esc
        if cv2.waitKey(1) in [ord('q'), 27]:
            break
    # release the Video writer
    video_writer.release()
    # destroy all windows
    cv2.destroyAllWindows()


# create video by concatenate a list of images
def create_video_by_images(images=[], fps=5, out_filename="joint_images.gif", video_format="gif"):
    clips = [ImageClip(m).set_duration(1/fps) for m in images]
    concat_clip = concatenate_videoclips(clips, method="compose")
    if video_format == "gif":
        concat_clip.write_gif(out_filename, fps=fps)
    else:
        concat_clip.write_videofile(out_filename, fps=fps)


# trim, crop, or convert a video
def trim_and_convert_video(filename="Recording.mp4", clips=None, cropping_rectangle=None,
                           out_format=".mp4", out_filename="clipped.mp4", fps=1):
    video = VideoFileClip(filename)
    if cropping_rectangle:
        x1, y1, x2, y2 = cropping_rectangle
        video = vfx.crop(video, x1=x1, y1=y1, x2=x2, y2=y2)
    if clips:
        clipped = [video.subclip(*clip) for clip in clips]
        final_clip = concatenate_videoclips(clipped)
    else:
        # no clips
        final_clip = video
    if out_format == "gif":
        final_clip.write_gif(out_filename, fps=fps)
    else:
        final_clip.write_videofile(out_filename, fps=fps)


mouse_location = {
    "pressed": [],
    "released": []
}


# display selected region for screen recorder
def display_region(region=None):
    if not region:
        return False
    img = pyautogui.screenshot(region=region)
    # create an empty window to show captured area
    cv2.namedWindow("Selected Region", cv2.WINDOW_KEEPRATIO)
    # make it the same size as capture screen
    w, h = region[2], region[3]
    cv2.resizeWindow("Selected Region", w, h)
    # convert image to a numpy array
    frame = np.array(img)
    # convert it from BGR to RGB(Red, Green, Blue)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cv2.imshow('Selected Region', frame)
    is_ok = pyautogui.confirm(text='Is the selected region ok?', title='Check Region', buttons=['Yes', 'No'])
    # destroy all windows
    cv2.destroyAllWindows()
    return True if is_ok == "Yes" else False


# capture mouse click events
def on_click(x, y, button, pressed):
    # get mouse location on left button press and release events
    if button == mouse.Button.left:
        if pressed:
            print('{0} at {1}'.format('Pressed', (x, y)))
            # get pressed location
            mouse_location["pressed"] = [x, y]
        else:
            print('{0} at {1}'.format('Released', (x, y)))
            # get released location
            mouse_location["released"] = [x, y]
            # make sure the pressed location was capture
            if mouse_location["pressed"]:
                x0, y0 = mouse_location["pressed"]
                # stop listener when the captured region is bigger than the 5*5 area
                if abs(x - x0) > 5 and abs(y - y0) > 5:
                    return False


# select region by mouse
def select_region_by_mouse():
    # collect events until released
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    # get selected region
    x1, y1 = mouse_location["pressed"]
    x2, y2 = mouse_location["released"]
    x0, y0 = (min(x1, x2), min(y1, y2))
    w, h = (max(x1, x2) - x0, max(y1, y2) - y0)
    return [x0, y0, w, h]


# select and verify the region
def select_region_and_verify(capture_full_screen=False):
    if capture_full_screen:
        wh = pyautogui.size()
        region = [0, 0, wh.width, wh.height]
        return region
    max_tries = 3
    for i in range(max_tries):
        pyautogui.alert(text='Please Select Region', title='Select Region', button='OK')
        region = select_region_by_mouse()
        print(region)
        ok = display_region(region=region)
        if ok:
            return region
    else:
        pyautogui.alert(text='Exceed max retries', title='Exceeding max retries', button='OK')
    pyautogui.alert(text='Selected Region is not valid!', title='Invalid Region', button='OK')
    # if region is not valid, exit the program
    exit(0)


if __name__ == "__main__":
    """below is select to a region and record screen activities as a video"""
    # selected_region = select_region_and_verify(capture_full_screen=False)
    # video_format = "avi"  # mp4 or avi
    # output_file = "data/Recording.avi"
    # frame_per_second = 30.0
    # record_screen(filename=output_file, fileformat=video_format, region=selected_region,
    #               fps=frame_per_second, display=True)

    """below is to trim, crop or convert a video"""
    # clips to keep in the video
    clips = [
        [(0, 0), (0, 8)],      # clip between [0 min 1 sec, 0 min 4 sec]
        [(0, 24), (0, 32)],    # clip between [0 min 6 sec, 0 min 10 sec]
    ]
    # rectangle area to crop:  upper left x, upper left y, lower right x, lower right y
    rectangle = [10, 240, 610, 680]
    # call video editor
    # set rectangle as None if cropping is not needed
    trim_and_convert_video(filename="data/test_recording.mp4",
                           clips=clips, cropping_rectangle=rectangle,
                           out_format="gif", out_filename="data/test_recording_trimmed.gif", fps=1)
    # set clips=None, cropping_rectangle=None when only format converting is needed
    trim_and_convert_video(filename="data/test_recording.mp4",
                           clips=None, cropping_rectangle=None,
                           out_format="gif", out_filename="data/test_recording.gif", fps=1)

    """below is to join a list of images to create gif picture"""
    test_images = ["images/img_{}.png".format(i) for i in range(30)]
    create_video_by_images(images=test_images, fps=4, video_format="gif", out_filename="data/joined_images.gif")