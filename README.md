# image-resize
Resizing images on the fly

As part of a workflow images of several formats and filetypes serve as input. This script aims to reduce manual work in the workflow. The script resizes the images and optionally adds margins to fit to size while keeping the ratios.

## Build
Optionally you can build the script into an exe using pyinstaller.

## Development Planning
### Release 2
| feature | status |
---| ---
everything to JPG | DONE
image compression | DONE
context menu support | DONE
install script for context menu | TODO 
process entire folder through context menu | TODO

### Backlog
- Support multiple presets through context menu (through the use of config files)
- Basic GUI without presistent settings
- Support drag and drop for GUI
- create presets through GUI