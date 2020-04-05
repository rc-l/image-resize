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

# TODO: offer ability to change default settings through config file
# TODO: install script that makes it possible to run script through context menu (right click)
# TODO: implement logging for trouble shooting
# TODO: package script for running on windows machine without python


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
            if image.mode == 'P':
                # Get the proper background color from the palette, not doing this would result in unexpected
                # background colors appearing
                mcolor = image.getpalette().index(MARGIN_COLOR)
            else:
                mcolor = MARGIN_COLOR

            result = Image.new(image.mode, size, color=tuple(mcolor for x in image.getbands()))
            if result.mode == 'P':
                # Palette mode (P) refers to the use of a color palette for the colors. 
                # If the palette is not set it will turn the image black and white
                # which is not the intention of the resizing. Copying the palette from the original fixes the issue.
                result.putpalette(image.getpalette())
            result.paste(image, ((size[0] - image.size[0]) // 2, (size[1] - image.size[1]) // 2))
            image = result
        
    return image

if __name__ == '__main__':
    ### CONFIG ###
    SIZE = (1000, 1000)
    MARGIN_COLOR = 255  # White

    ### ARGUMENT PARSING ###
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('paths', nargs='*',
                        help='the files that need to be resized (or directory containing files)')
    args = parser.parse_args()

    ### LOGGING ###
    logging.basicConfig(level=logging.DEBUG, filename="./resize.log")
    
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
            image.save(path)
            logging.info(f'resized and saved image {path}')
        elif os.path.isdir(path):
            # TODO: Handle directories
            pass
        else:
            logging.info(f"{path} is neither a file or directory")