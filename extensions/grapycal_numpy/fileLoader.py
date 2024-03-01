import tkinter as tk
from tkinter import filedialog

import json,numpy,pickle
from grapycal import Node
from objectsync.sobject import SObjectSerialized
import os
from grapycal import Node
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.port import InputPort
import numpy as np

class FileLoader(Node):
    '''
    To load file from your local storage
    Support File format is JSON, NPM, PKL, TXT
    Input : file data format 
    Output : file data format
    '''
    category = "numpy/dataloader"
    def create(self):
        super().build_node()
        self.shape.set("simple")
        self.label.set("File Loader")

        self.output_port = self.add_out_port("File Outputs")
        self.text = self.add_text_control("0")
        self.button = self.add_button_control("Load")
        self.file_num = 0
        self.files_path = []
        self.button.on_click += self.button_clicked
        self.option_control = self.add_option_control(options=['JSON','NPM','PKL','TXT'],value='JSON',name='opt')

    def button_clicked(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-alpha", 0.0)
        root.attributes("-topmost", True)
        root.focus_force()
        selected_files = None
        match self.option_control.get_value():
            case 'JSON': 
                selected_files = filedialog.askopenfilenames(parent=root, initialdir="./", filetypes=[("json files", "*.json")])
            case 'NPY':
                selected_files = filedialog.askopenfilenames(parent=root, initialdir="./", filetypes=[("numpy files", "*.npy")])
            case 'PKL':
                selected_files = filedialog.askopenfilenames(parent=root, initialdir="./", filetypes=[("pickle files", "*.pkl")])
            case 'TXT':
                selected_files = filedialog.askopenfilenames(parent=root, initialdir="./", filetypes=[("text files", "*.txt")])
        
        root.destroy()
        if len(selected_files) == 0:
            return
        self.files_path = selected_files
        self.file_num = len(self.files_path)
        self.text.set(str(self.file_num))

    def double_click(self):
        self.run(self.task)

    def task(self):
        files = []
        for file in self.files_path:
            f = open(file)
            match self.option_control.get_value():
                case 'JSON':
                    file = json.load(f)
                    self.output_port.set_data_type('json')
                case 'NPY':
                    file = numpy.load(f)
                    self.output_port.set_data_type('numpy')
                case 'PKL':
                    file = pickle.load(f)
                    self.output_port.set_data_type('pickle')
                case 'TXT':
                    file = f.read()
                    self.output_port.set_data_type('text')
            files.append(file)
        self.output_port.push_data(files)

    def destroy(self) -> SObjectSerialized:
        return super().destroy()
    
class FileFilter(Node):
    '''
    input : list of files

    text : index (1 -> number of files) / number of files

    output : index of file in the list

    previous : previous file in the list
    next : next file in the list
    '''
    category = "file"

    def create(self):
        self.label.set("File Filter")
        self.shape.set("simple")
        self.text = self.add_text_control("0")
        self.prev_button = self.add_button_control("Previous")
        self.next_button = self.add_button_control("Next")
        self.output_port = self.add_out_port("File Output")
        self.input_port = self.add_in_port("Files Input")
        self.index = 0
        self.file_num = 0
        self.files = None
        self.prev_button.on_click += self.prev_button_clicked
        self.next_button.on_click += self.next_button_clicked
        self.file_type = None

    def prev_button_clicked(self):
        if self.index == 0:
            self.index = self.file_num - 1
        else :
            self.index -= 1
        self.text.set(str(self.index + 1) + " / " + str(self.file_num))
        self.run(self.push_file)

    def next_button_clicked(self):
        if self.index == self.file_num - 1:
            self.index = 0
        else :
            self.index += 1
        self.text.set(str(self.index + 1) + " / " + str(self.file_num))
        self.run(self.push_file)

    def edge_activated(self, edge: Edge, port: InputPort):
        self.files = self.input_port.get_one_data()
        self.file_type = self.input_port.get_data_type()
        self.file_num = len(self.files)
        self.index = 0
        self.text.set(str(self.index + 1) + " / " + str(self.file_num))
        self.run(self.init_file)

    def init_file(self):
        match self.file_type:
            case 'jpg':
                file = np.array(self.files[0]).astype(np.float32).transpose(2, 0, 1) / 255 #channels, height, width
                file = file[::-1, :, :]
                if image.shape[0] == 4:
                    image = image[:3]
                self.output_port.push_data(image)
            case 'png':
                file = np.array(self.files[0]).astype(np.float32).transpose(2, 0, 1) / 255 #channels, height, width
                file = file[::-1, :, :]
                if image.shape[0] == 4:
                    image = image[:3]
                self.output_port.push_data(image)
            case 'json':
            
            case 'npy':
        

    def push_image(self):
        print(self.images[self.index].shape)
        image = np.array(self.images[self.index]).astype(np.float32).transpose(2, 0, 1) / 255
        image = image[::-1, :, :]
        if image.shape[0] == 4:
            image = image[:3]
        self.output_port.push_data(image)