import admin
import sys
import os
from tkinter import filedialog
from tkinter import *
from tkinter import ttk
import threading
import requests
from zipfile import ZipFile
import time
import subprocess

def browse_button():
    global folder_path
    filename = filedialog.askdirectory()
    if filename:
        folder_path.set(filename)
        print(filename)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('')
    return os.path.join(base_path, relative_path)

def install():
    global root
    global folder_path
    global tk
    global ttk
    global downloading_text
    global progressbar
    root.quit()
    root.destroy()
    root = Tk()
    root.title('PHP Windows Installer')
    root.geometry('500x100')
    root.resizable(0, 0)
    root.iconbitmap(resource_path('icon.ico'))
    downloading_text = StringVar()
    label_text = Label(master=root, textvariable=downloading_text)
    label_text.grid()
    progressbar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
    progressbar.grid()
    progressbar['value'] = 0
    progressbar['maximum']= 100
    thread = threading.Thread(target = download)
    thread.start()
    root.mainloop()

def download():
    global folder_path
    global downloading_text
    global root
    global progressbar
    path = folder_path.get()
    tempFilePath = path + '\php.zip'
    downloading_text.set('Downloading PHP...')
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(requests.get('https://windows.php.net/download/').text, 'html.parser')
    lenk = 'https://windows.php.net' + soup.find('a', string='Zip').get('href')
    downloading_text.set('Downloading PHP...\n(' + lenk + ')')
    phpini = requests.get('https://raw.githubusercontent.com/peppelg/PHPWindowsInstaller/master/php.ini').text
    if not os.path.exists(path):
        os.mkdir(path)
    with open(tempFilePath, 'wb') as f:
        response = requests.get(lenk, stream=True)
        total_length = response.headers.get('content-length')
        if total_length is None:
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                percentage = int(100 * dl / total_length)
                progressbar['value'] = percentage
    downloading_text.set('Unzipping...')
    with ZipFile(tempFilePath, 'r') as zipObj:
        zipObj.extractall(path)
    os.remove(tempFilePath)
    subprocess.Popen(['powershell.exe', '[Environment]::SetEnvironmentVariable("Path", "' + path + '", "User")'])
    f = open(path + '\php.ini', 'w+')
    f.write(phpini)
    f.close()
    downloading_text.set('Done.\nPls close this window.')



if not admin.isUserAdmin():
    admin.runAsAdmin()
    sys.exit(0)

root = Tk()
root.title('PHP Windows Installer')
root.geometry('300x80')
root.resizable(0, 0)
root.iconbitmap(resource_path('icon.ico'))
folder_path = StringVar()
folder_path.set(os.environ['ProgramFiles']+'\PHP')
label_text = Label(master=root, text='Install PHP in')
label_text.grid(row=0, column=1)
path = Entry(master=root,textvariable=folder_path)
path.grid(row=1, column=1)
browse = Button(text='Browse', command=browse_button)
browse.grid(row=1, column=2)
next = Button(text='Install', command=install)
next.grid(row=3, column=1)
root.mainloop()
