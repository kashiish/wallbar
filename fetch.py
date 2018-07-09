#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 24 02:39:51 2018

@author: kashish
"""

import requests
import os
import subprocess
from configparser import ConfigParser 


url = "https://api.unsplash.com/photos/random?orientation=landscape&{0}&client_id={1}"

config = ConfigParser()

config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config/config.cfg")
config.read(config_file)

image_query = config["unsplash"]["query"]
api_key = config["unsplash"]["api_key"]
images_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Downloaded Images")

script = """ /usr/bin/osascript -e 'tell application "Finder" to set desktop picture to "{0}" as POSIX file' """

class APIKeyError(Exception):
    pass

class APIError(Exception):
    pass

def fetch_image():
    """
    Calls the Unsplash API to get a random image from Unsplash.com. 
    
    params:
        api_key: (string)
    
    """

    requestURL = ""
    
    if image_query is None:
        requestURL = url.format("", api_key)
    else:
        requestURL = url.format("query=" + image_query.replace(" ", "%20"), api_key)
    
    try:  

    	response = requests.get(requestURL)

    	if "oauth error" in response.text.lower():
        	raise APIKeyError() 
    	elif not response.ok:
        	raise APIError(response.text)
    
    	return response

    except Exception as e:
    	raise e


        
def download_random_image():
    """

    Gets a random image from the Unsplash API and writes the image into a file.

    return:
        image_path: (string) path to downloaded image

    """
    _create_directory_if_not_exists()
    response = fetch_image().json()
    image_path = os.path.join(images_directory, response["id"]+".jpg")
    image_file = open(image_path,"wb")
    image_file.write(requests.get(response["links"]["download"]).content)
    image_file.close()

    return image_path


def _create_directory_if_not_exists():
    """
    
    Creates a new directory for downloaded images, if it does not exist.

    """
    if not os.path.exists(images_directory):
        os.makedirs(images_directory)

def set_desktop_image(image_path):
    """
    Sets the desktop image for the computer using the image passed in.

    param:
        image_path: (string) path to image

    """
    subprocess.Popen(script.format(image_path), shell=True)

if __name__ == '__main__':
    image_path = download_random_image()
    set_desktop_image(image_path);