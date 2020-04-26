"""
Resize images and add margins

If no files are provided as arguments then all the images in the directory will be processed.
"""

from PIL import Image
from copy import copy
import warnings
import argparse
import os
import logging
import yaml  # PyYaml

# TODO: implement proper logging for trouble shooting
# TODO: offer ability to change default settings through config file
# TODO: installation script that makes it possible to run script through context menu (right click)


def resize(image, size, margins=True, roundmargins=False):
    """Resize image with margins
    
    Only shrinks image if it is larger than the given size. If the image is smaller margins can still be added.
    
    args:
        image: PIL.Image.Image to be resized
        size: tuple, defining the new size (width, height) integers only
        margins: boolean, add margins to the shortest side
        roundmargins: boolean, add margins to all sides if applicable. Has no effect is margins is false
        
    returns:
        PIL.Image.Image: the resized image
    """
    # Validate input
    assert type(size) is tuple
    assert all(type(x) is int for x in size)
    assert len(size) == 2
    assert type(margins) is bool
    assert type(roundmargins) is bool
    if margins is False and roundmargins is True:
        warnings.warn('the roundmargins will not have any effect due the margins option being set to False')
    
    # Resize image, only shrinks if bigger
    image = copy(image)
    image.thumbnail(size)
    
    if margins:
        # if both width and heigth smaller then add margin to most the side diverging most from aspect ratio
        if image.size[0] < size[0] and image.size[1] < size[1] and not roundmargins:
            pass
            # Implement later if such user requirement exists
        else:
            # Create a solid background to put the resized image on, thus creating the margins
            result = Image.new('RGB', size, color=MARGIN_COLOR)
            result.paste(image, ((size[0] - image.size[0]) // 2, (size[1] - image.size[1]) // 2))
            image = result
        
    return image

if __name__ == '__main__':
    ### ARGUMENT PARSING ###
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*',
                        help='the files that need to be resized (or directory containing files)')
    args = parser.parse_args()

    ### CONFIG ###
    appdir = os.path.join(os.environ['APPDATA'], 'image-resize')
    with open(os.path.join(appdir, 'default-config.yml'), 'r') as f:
        config = yaml.load(f.read())
        SIZE = (config["size"]['width'], config["size"]['heigth'])
        MARGIN_COLOR = (config['margin_color']['r'],config['margin_color']['g'],config['margin_color']['b'])
        QUALITY = config['quality']

    ### LOGGING ###
    logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.environ['APPDATA'], "resize.log"))
    
    logging.info(f"path input is {args.paths}")
    workdir = os.path.abspath(os.curdir)
    logging.debug(f'current work directory is {workdir}')

    ### MAIN ###
    if args.paths:
        paths = args.paths
    else:
        # no file paths have been provided, so gather all the files in this directory non-recursively
        with os.scandir() as scan:
            paths = list(entry.path for entry in scan if entry.is_file())

    for path in paths:
        #path = os.path.join(workdir, path)
        if os.path.isfile(path):
            try:
                image = Image.open(path)
            except OSError:
                logging.error(f"{path} cannot be opened")
                continue
            logging.debug(f"resizing: {path} to {SIZE}")
            image = resize(image, SIZE)
            new_path = path[:path.rfind('.')] + ".jpg"
            image.save(new_path, optimize=True, quality=QUALITY)
            logging.info(f'resized and saved image {new_path}')
            if path.lower() != new_path.lower():
                os.remove(path)
                logging.info(f'deleted original from {path}')
            else:
                logging.debug(f'original is overwritten because old path {path} and new path {new_path} are the same')
        elif os.path.isdir(path):
            # TODO: Handle directories
            pass
        else:
            logging.info(f"{path} is neither a file or directory")