from upload_client import *
from download_client import *
from showfiles_client import *

def run():
    userId = input("Enter your username baliz ")
        
    while True:
        action = input("Enter an action number from 1: upload, 2: showfiles, 3: download, 4: Exit ")
        
        if (int(action) == 1): #upload
            filename = input("Enter video name baliz ")
            path = input("Enter video path baliz " )
            upload_client.run(userId, filename, path) # to do
        
        elif (int(action) == 2): #showfiles
            showfiles_client.run(userId)
        
        elif (int(action) == 3): #download
            filename = input("Enter video name baliz ")
            path = input("Enter video path baliz " )
            d = download(userId, filename)  # should pass the path to download too
            d.run()
        
        elif (int(action) == 4):
            print("goodbye khawsatiko\n")
            break


if __name__ == "__main__": 
    run()