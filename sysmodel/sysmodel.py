from nicegui import ui
from os import listdir
from os.path import isfile, join
from pathlib import Path

class Demo:
    def __init__(self):
        self.number = 1

demo = Demo()
#v = ui.checkbox('visible', value=True)
#with ui.column().bind_visibility_from(v, 'value'):
    #ui.slider(min=1, max=3).bind_value(demo, 'number')
    #ui.toggle({1: 'A', 2: 'B', 3: 'C'}).bind_value(demo, 'number')
    #ui.number().bind_value(demo, 'number')

def update_cursor(image):
    pass


image_dir_path = Path("./images/")

files = [f for f in image_dir_path.iterdir() if f.is_file()]
select = ui.select([f.stem for f in files], on_change=update_cursor())

ui.run()
