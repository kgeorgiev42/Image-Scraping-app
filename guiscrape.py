from tkinter import *
from tkinter import ttk, filedialog, messagebox, PhotoImage, Label
import base64
import os
import json
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen

config = {}

    
def fetch_url():
    url = _url.get()
    config['images'] = []
    _images.set(())

    try:
        page = requests.get(url)
    except requests.RequestException as rex:
        _sb(str(rex))
    else:
        soup = BeautifulSoup(page.content, 'html.parser')
        images = fetch_images(soup, url)
        if images:
            _images.set(tuple(img['name'] for img in images))
            _sb('Images found: {}'.format(len(images)))
        else:
            _sb('No images found.')
        config['images'] = images

def fetch_images(soup, base_url):
    images = []
    for img in soup.findAll('img'):
        src = img.get('src')
        img_url = ('{base_url}/{src}'.format(base_url=base_url, src=src))
        name = img_url.split('/')[-1]
        images.append(dict(name=name, url=img_url))
    return images

def fetch_selected_images(event):
    widget = event.widget
    selected_idx = widget.curselection()
    selected_items = [widget.get(int(item)) for item in selected_idx]
    selected_images = []
    url = _url.get() + '/img'

    for img in selected_items:
        img_url = ('{base_url}/{src}'.format(base_url=url, src=img))
        name = img_url.split('/')[-1]
        if name in selected_items:
            selected_images.append(dict(name=name, url=img_url))
        for idx in selected_idx:
            widget.itemconfig(idx, fg='red')
                
    config['images'] = selected_images

def rec_from_json():
    filename = filedialog.askopenfilename(
        filetypes=[('JSON', '.json')]
    )
    if filename:
        with open(filename, 'r') as f:
            data = json.loads(f.read())
        dir_name = filedialog.askdirectory(mustexist=True)
        for (name, b64val) in data.items():
            path_name = os.path.join(dir_name, name)
            with open(path_name, 'wb') as f:
                f.write(base64.b64decode(b64val))

        _alert('Successfully reconstructed the images.')
 
def preview_images(event):
    widget = event.widget
    selected_idx = widget.curselection()
    selected_items = [widget.get(int(item)) for item in selected_idx]
    url = _url.get() + '/img'
    selected_images = []

    if len(selected_items) == 1:
        for img in selected_items:
            img_url = ('{base_url}/{src}'.format(base_url=url, src=img))
            image_byt = urlopen(img_url).read()
            image_b64 = base64.encodestring(image_byt)
            selected_images.append(image_b64)

        if img_url.endswith('.png'):
            p_wnd = Toplevel()
            p_wnd.title('Preview: '+ img)
            photo = PhotoImage(data=image_b64)
            photo_label = Label(p_wnd, image=photo)
            photo_label.pack()
            p_wnd.mainloop()
        else:
            _alert('Only .png format images can be previewed at this time.')
        
        
    else:
        _alert('Incorrect number of items selected for preview.')


def save():
    if not config.get('images'):
        _alert('No images to save')
        return

    if _save_method.get() == 'img':
        dirname = filedialog.askdirectory(mustexist=True)
        _save_images(dirname)
    else:
        filename = filedialog.asksaveasfilename(
            initialfile='images.json',
            filetypes=[('JSON', '.json')])
        _save_json(filename)

def _save_images(dirname):
    if dirname and config.get('images'):
        for img in config['images']:
            img_data = requests.get(img['url']).content
            filename = os.path.join(dirname, img['name'])
            with open(filename, 'wb') as f:
                f.write(img_data)
        _alert('Done')

def _save_json(filename):
    if filename and config.get('images'):
        data = {}
        for img in config['images']:
            img_data = requests.get(img['url']).content
            b64_img_data = base64.b64encode(img_data)
            str_img_data = b64_img_data.decode('utf-8')
            data[img['name']] = str_img_data

        with open(filename, 'w') as ijson:
            ijson.write(json.dumps(data))
        _alert('Done')



def _sb(msg):
    _status_msg.set(msg)

def _alert(msg):
    messagebox.showinfo(message=msg)
    

if __name__ == "__main__":

    _root = Tk()
    _root.title('Image Scraping app')
    _root.resizable(width = False, height = False)

    _mainframe = ttk.Frame(_root, padding = '5 5 5 5')
    _mainframe.grid(row = 0, column = 0, sticky = (E,W,N,S))

    _url_frame = ttk.LabelFrame(_mainframe, text = 'URL', padding = '5 5 5 5')
    _url_frame.grid(row=0, column=0, sticky=(E,W))
    _url_frame.columnconfigure(0, weight=1)
    _url_frame.rowconfigure(0, weight=1)

    _url = StringVar()
    _url.set('http://localhost:8000')
    _url_entry = ttk.Entry(_url_frame, width=40, textvariable=_url)
    _url_entry.grid(row=0, column=0, sticky=(E, W, S, N), padx=5)
    _fetch_btn = ttk.Button(_url_frame, text='Fetch info from URL', command=fetch_url)
    _fetch_btn.grid(row=0, column=1, sticky=W, padx = 5)
    

    _img_frame = ttk.LabelFrame(
        _mainframe, text='Content', padding='9 0 0 0'
    )
    _img_frame.grid(row=1, column=0, sticky=(N,S,E,W))
    _images = StringVar()
    _img_listbox = Listbox(
        _img_frame, listvariable=_images, height=6, width=25, selectmode='multiple'
    )
    _img_listbox.grid(row=0, column=0, sticky=(E,W), pady=5)
    _img_listbox.bind('<<ListboxSelect>>', fetch_selected_images)
    _img_listbox.bind('<Button-3>',preview_images)

    _scrollbar = ttk.Scrollbar(
        _img_frame, orient=VERTICAL, command=_img_listbox.yview
    )
    _scrollbar.grid(row=0, column=1, sticky=(S,N), pady=6)
    _img_listbox.configure(yscrollcommand=_scrollbar.set)

    _radio_frame = ttk.Frame(_img_frame)
    _radio_frame.grid(row=0, column=2, sticky = (N, S, W, E))

    _choice_lbl = ttk.Label(_radio_frame, text = 'Choose how to save images')
    _choice_lbl.grid(row = 0, column = 0, padx = 5, pady = 5 )
    _save_method = StringVar()
    _save_method.set('img')

    _img_only_radio = ttk.Radiobutton(
        _radio_frame, text='As Images', variable=_save_method, value='img'
    )
    _img_only_radio.grid(row=1, column=0, padx=5, pady=2, sticky=W)
    _img_only_radio.configure(state='normal')
    _json_radio = ttk.Radiobutton(
        _radio_frame, text='As JSON', variable=_save_method, value='json'
    )
    _json_radio.grid(row=2, column=0, padx=5, pady=2, sticky=W)

    _scrape_btn = ttk.Button(
        _mainframe, text='Scrape!', command=save
    )
    _scrape_btn.grid(row=2, column=0, sticky=W, pady=5)

    _rec_json_btn = ttk.Button(
        _mainframe, text='Reconstruct from JSON', command=rec_from_json
    )
    _rec_json_btn.grid(row = 2, column = 0,sticky=E, pady = 5)
    
    

    _status_frame = ttk.Frame(
        _root, relief='sunken', padding='2 2 2 2'
    )
    _status_frame.grid(row=1, column=0, sticky=(E, W, S))
    _status_msg = StringVar()
    _status_msg.set('Type a URL to start scraping...')
    _status = ttk.Label(
        _status_frame, textvariable=_status_msg, anchor=W
    )
    _status.grid(row=0, column=0, sticky=(E, W))

    #context menu

    _menubar = Menu(_root)
    filemenu = Menu(_menubar, tearoff=0)
    filemenu.add_command(label='Fetch images from URL', command=fetch_url)
    filemenu.add_command(label='Scrape images', command=save)
    filemenu.add_command(label='Reconstruct images', command=rec_from_json)
    filemenu.add_separator()

    def reset():
        _url.set('http://localhost:8000')
        _img_listbox.delete(0,'end')
        _save_method.set('img')
        _status_msg.set('Type a URL to start scraping...')

    def about():
        ab_wnd = Toplevel()
        ab_wnd.title('About')
        string = 'Simple Image Scraping app made with Python 3 and tkinter.\n\nThis app is an improved version of an image scraping app created\n by Fabrizio Romano and published in Packt.\nYou can also check out some other great Python examples at www.packtpub.com.'
        ab_lbl = Label(ab_wnd, text=string, justify=CENTER, anchor=W)
        ab_lbl.pack()
        ab_wnd.mainloop()
    
    def help():
        hp_wnd = Toplevel()
        hp_wnd.title('Help')
        text = 'App Info:\n'
        hp_head = Label(hp_wnd, text=text, justify=CENTER, font=('Courier',12))
        hp_head.pack()
        text = ' - Fetch info from URL: Downloads all images from the selected URL and places their filenames in the listbox.\n - Scrape: Saves the selected images in a directory, chosen by the user either as images or in JSON format.\n - Reconstruct: Creates a batch of images from a selected .json file and saves them in a selected directory.\n - Right-clicking on a listbox element shows a preview of the image. (Only .png formats have this feature and only 1 image can be selected at a time).'
        hp_text = Label(hp_wnd, text=text, justify=LEFT, font=('Times New Roman',10))
        hp_text.pack()
        hp_wnd.mainloop()


    filemenu.add_command(label='Reset content', command=reset)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=_root.quit)
    _menubar.add_cascade(label="File", menu=filemenu)
    _menubar.add_command(label = 'Help', command=help)
    _menubar.add_command(label = 'About the app', command=about)

    

    _root.config(menu = _menubar)

    _root.mainloop()