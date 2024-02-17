from __future__ import annotations

from typing import Callable, Optional, Protocol
from dataclasses import dataclass
from nicegui import ui
from constants import *
from functools import partial

import threading
import time
import sys
import signal

def signal_handler(signal, frame):
    print("You pressed Ctrl+C!")
    #sys.exit(0)

#catchable_sigs = set(signal.Signals) - {signal.SIGSTOP}
#catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
#for sig in catchable_sigs:
#    signal.signal(sig, signal_handler)
#signal.signal(signal.SIGINT, signal_handler)

class Item(Protocol):
    title: str

@dataclass
class ToDo:
    title: str


@dataclass
class HTTPGetEvents():
    def __init__(self, num_events, request_size):
        self.num_events = num_events
        self.request_size = request_size

    def get_num_events(self):
        return self.num_events

    def get_request_size(self):
        return self.request_size


class Reg():
    element_registry = {}

    @staticmethod
    def add(element, component):
        Reg.element_registry[element] = component

    @staticmethod
    def get(element):
        return Reg.element_registry[element]


class Attr():
    def __init__(self, name, get_func, set_func, the_type):
        self.name = name
        self.get_func = get_func
        self.set_func = set_func
        self.the_type = the_type


class EditAttrsMenu():
    def __init__(self, component_view):
        self.edits = {}
        self.component_view = component_view
        with self.component_view.element:
            self.element = ui.element('div').classes("absolute p-2 border-dotted border-2 border-indigo-600 top-[10px] left-[60px] w-[150px] bg-grey-1")
            with self.element:
                for a in self.component_view.component.get_attributes():
                    ui.input(a.name, on_change=partial(self.edit_value, a.name)).classes("static")
                    ui.label("[value=%s]" % a.get_func()).classes("static")
                ui.button("Save", on_click=self.component_view.close_edits_menu)

    def edit_value(self, name, edit):
        print("set value: (%s=%s)" % (name, edit.value))
        self.edits[name] = edit.value

    def save_and_close(self):
        for a in self.component_view.component.get_attributes():
            value = self.edits.get(a.name)
            if value is not None:
                a.set_func(a.the_type(value))
        self.element.clear()
        self.element.delete()
        #self.element = None


class Counter():
    def __init__(self, component_view):
        self.component_view = component_view
        with self.component_view.element:
            self.element = ui.element('div').classes("absolute m-0 p-0 border-solid border-2 border-black top-[-25px] left-[90px] w-[50px] bg-grey-1")
            with self.element:
                failed_events = ui.label("").classes("static bg-red text-white")
                failed_events.bind_text_from(component_view.component, "failed_events")
                succeeded_events = ui.label("").classes("static bg-green text-white")
                succeeded_events.bind_text_from(component_view.component, "succeeded_events")


class GlobalState():
    def __init__(self):
        self.global_events_state = True
        self.active_workflow = None
        self.parent_container = None

    def disable_events(self):
        self.global_events_state = False

    def enable_events(self):
        self.global_events_state = True

    def is_events_enabled(self):
        return self.global_events_state

    def set_active_workflow(self, workflow):
        print("set active workflow: %s" % workflow)
        self.active_workflow = workflow

    def get_active_workflow(self):
        return self.active_workflow

    def set_parent_container(self, container):
        self.parent_container = container

    def get_parent_container(self):
        return self.parent_container


global_state = GlobalState()


def global_on_click(callback, event_props):
    print("global_on_click")
    #print(dir(event_props.client))
    #print(dir(event_props.sender))
    print(event_props)
    if global_state.is_events_enabled() and global_state.get_active_workflow() is None:
        callback(event_props)


def body_on_click(event_props):
    print("body_on_click")
    if global_state.get_active_workflow() is not None:
        global_state.get_active_workflow().end_workflow(event_props)


class Workflow():
    def __init__(self, component):
        self.temp_div = None

    def start_workflow(self, event_props):
        global global_state
        with global_state.get_parent_container():
            self.temp_div = ui.element('div').classes("static bg-light-grey-1 relative w-full h-[800px]")
            self.temp_div.on('click', self.end_workflow)
        global_state.set_active_workflow(self)

    def end_workflow(self, event_props):
        global global_state
        global_state.set_active_workflow(None)
        self.temp_div.clear()
        self.temp_div.delete()


class AttachWorkflow(Workflow):
    def __init__(self, component):
        super().__init__(component)

    def start_workflow(self, event_props):
        super().start_workflow(event_props)
        #if global_state.get_active_workflow() is not None:
        #    return
        print("Starting workflow")
        #ui.query('body').on_click('click', self.end_workflow())
        ui.query('body').style("cursor: pointer")
        #global_state.get_parent_container().on('click', self.end_workflow)
        #ui.query('body').

    def end_workflow(self, event_props):
        super().end_workflow(event_props)
        print("Ending workflow")
        ui.query('body').style("cursor: default")
        #global_state.get_parent_container().on('click', None)
        #print(dir(event_props))

        #print(dir(event_props.client))
        #print(dir(event_props.sender))
        #print(event_props.client)
        #print(event_props.sender)
        #print(event_props)
        #print(event_props.target)
        #print(Reg.get(event_props.sender))


class ComponentView():
    def __init__(self, component, parent):
        self.component = component
        self.parent = parent
        self.image = None
        self.element = None
        self.edits_menu = None
        self.is_menu_active = False

    def set_image(self, image):
        self.image = image

    def set_parent(self, parent):
        self.parent = parent

    def add_to_view(self, top, left):
        with self.parent:
            self.element = ui.element('div')
            with self.element:
                ui.image(self.image)
                with ui.element('div').classes("m-1 border-solid border-2 w-100%"):
                    ai = ui.image(IMAGE_DIR_PATH / "attach.png")
                    ai.classes("m-1 w-[20px] h-[20px]")
                    flow = AttachWorkflow(self.component)
                    ai.on('click', partial(global_on_click, flow.start_workflow))

                    gear = ui.image(IMAGE_DIR_PATH / "gear.png")
                    gear.classes("m-1 w-[20px] h-[20px]")
                    gear.on('click', partial(global_on_click, self.show_edit_menu), ['offsetX', 'offsetY'])

        self.element.on('dragstart', pickup_card, ['offsetX', 'offsetY'])
        self.element.props('draggable').classes("w-[90px] top-[%dpx] left-[%dpx] absolute cursor-pointer" % (top, left))
        Reg.add(self.element, self)

    def show_edit_menu(self, event_props):
        if self.is_menu_active:
            return
        self.edits_menu = EditAttrsMenu(self)
        self.is_menu_active = True
        return True

    def close_edits_menu(self):
        self.edits_menu.save_and_close()
        self.is_menu_active = False

    #def component(self):
    #    return Reg.get(self.element)


class WebClientView(ComponentView):
    def __init__(self, component, parent):
        super().__init__(component, parent)
        self.image = IMAGE_DIR_PATH / "clients.png"


class WebServerView(ComponentView):
    def __init__(self, component, parent):
        super().__init__(component, parent)
        self.image = IMAGE_DIR_PATH / "server.png"

    def add_to_view(self, top, left):
        super().add_to_view(top, left)
        Counter(self)


class Component():
    def __init__(self):
        self.image = None
        self.element = None
        self.parent = None
        self.consumers = []

    def add_consumer(self, consumer):
        self.consumers.append(consumer)


class WebClient(Component):
    def __init__(self):
        super().__init__()
        self.request_rate = 10
        self.num_clients = 10

    def get_attributes(self):
        return [Attr("request_rate", self.get_request_rate, self.set_request_rate, int),
               Attr("num_clients", self.get_num_clients, self.set_num_clients, int)]

    def get_request_rate(self):
        return self.request_rate

    def get_num_clients(self):
        return self.num_clients

    def set_request_rate(self, request_rate: int):
        self.request_rate = request_rate

    def set_num_clients(self, num_clients: int):
        self.num_clients = num_clients

    def send_to_consumers(self, duration_secs=1):
        events = HTTPGetEvents(self.request_rate * duration_secs, 100)
        for consumer in self.consumers:
            consumer.consume(events, duration_secs)


class WebServer(Component):
    def __init__(self):
        super().__init__()
        self.num_threads = 1
        self.op_latency_ms = 1000
        self.failed_events = 0
        self.succeeded_events = 0

    def get_attributes(self):
        return [Attr("num_threads", self.get_num_threads, self.set_num_threads, int),
               Attr("op_latency_ms", self.get_op_latency_ms, self.set_op_latency_ms, int)]

    def get_num_threads(self):
        return self.num_threads

    def get_op_latency_ms(self):
        return self.op_latency_ms

    def set_num_threads(self, num_threads: int):
        self.num_threads = num_threads

    def set_op_latency_ms(self, op_latency_ms: int):
        self.op_latency_ms = op_latency_ms

    def consume(self, events, duration):
        ops_per_sec = self.num_threads * (1000 / self.op_latency_ms)
        ops_per_duration = ops_per_sec * duration
        if isinstance(events, HTTPGetEvents):
            failed_events = events.get_num_events() - ops_per_duration
            self.failed_events += failed_events
            self.succeeded_events += ops_per_duration
            if failed_events > 0:
                #ui.notify("Failed to process %d events" % failed_events, color='red')
                pass
            else:
                #ui.notify("GOOD JOB! You processed all events", color='green')
                pass

the_card = None
selected_file = IMAGE_DIR_PATH / "default.png"
click_offset = (0, 0)

def create_image_div(image, top, left, height, width):
    print("create a div with image: %s" % image)
    the_card = ui.element('div')
    with the_card:
        ui.image(image)
    the_card.on('dragstart', pickup_card, ['offsetX', 'offsetY'])
    the_card.props('draggable').classes("top-[%dpx] left-[%dpx] h-[%dpx] w-[%dpx] absolute cursor-pointer bg-grey-1" % (top, left, height, width))

def update_cursor(image):
    global selected_file
    global parent_div
    print("Updating cursor: %s" % image)
    selected_file =  IMAGE_DIR_PATH / ("%s.%s" % (image.value, "png"))
    with parent_div:
        create_image_div(selected_file)

files = [f for f in IMAGE_DIR_PATH.iterdir() if f.is_file()]
select = ui.select([f.stem for f in files], on_change=None)
#select = ui.select([f.stem for f in files], on_change=update_cursor)

def move_card(event_props) -> None:
    print(event_props)
    global the_card
    offset = (event_props.args['offsetY'], event_props.args['offsetX'])
    new_card_loc = (offset[0]-click_offset[0], offset[1]-click_offset[1])
    the_card.classes("top-[%dpx] left-[%dpx]" % (new_card_loc[0], new_card_loc[1]))

def pickup_card(event_props):
    global the_card
    global click_offset
    print(event_props)
    the_card = event_props.sender
    click_offset = (event_props.args['offsetY'], event_props.args['offsetX'])

def dop():
    pass

def dl():
    pass

def loop_me(client_view):
    #print("Looping")
    duration_secs = 5
    client = client_view.component
    while True:
        time.sleep(duration_secs)
        with client_view.element:
            client.send_to_consumers(duration_secs)

parent_div = ui.element('div').classes("bg-light-grey-1 relative w-full h-[800px]")
global_state.set_parent_container(parent_div)
parent_div.on('drop', move_card, ['offsetX', 'offsetY', 'target', 'relatedTarget'])
parent_div.on('dragover.prevent', dop)
parent_div.on('dragleave', dl)
with parent_div:
    server = WebServer()
    client = WebClient()
    client.add_consumer(server)

    cv = WebClientView(client, parent_div)
    cv.add_to_view(400, 300)
    WebServerView(server, parent_div).add_to_view(400, 750)
    #create_image_div(IMAGE_DIR_PATH / "html.png", 450, 500, 50, 150)
    #create_image_div(selected_file)

    #loop_me()
    t = threading.Thread(target=loop_me, args=(cv,), daemon=True)
    t.start()
    #t.join()

ui.run()
