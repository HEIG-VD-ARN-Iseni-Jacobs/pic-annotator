# Dataset generator

This tool was built to manually but quickly generate a dataset of images for training a CNN model.

It is composed of four main parts :
- The first part is a simple image categorizer, that allows you to quickly categorize images based on a list of categories (the categories are defined in the code).
- The second part is a picture cropper to make sure the object of interest takes enough space in the picture. TODO, not implemented yet.
- The third part is a multi-picture cropper for data augmentation. It takes the cropped images and crops them into multiple randomly-positioned and randomly-sized images. The user can then click on the pictures to select them or not. This allows for a quick and easy data augmentation.
- The fourth part is a picture rotator for data augmentation. It takes the multi-cropped images and rotates them into multiple versions. For now, it creates black borders, but we plan on zooming in on the picture to prevent this.

There are some other parts coming soon with various tools : another dataset augmentation tool by rotation, ...

> [!CAUTION]
> It is **purely vibe-coded** and no human wrote a single line of code : don't hope for a fully fonctionnal and pretty tool, I guarantee you'll be disappointed.

## Components description

### 1. Image Categorizer

Add the pictures you want to categorize in the `./images/0_to_process` folder.
Run the script, use the GUI or your keybord to navigate and categorize the pictures. You can stop at any moment and resume later, the increments won't broke (hopefully). The categorized images will be moved to the `./images/1_categorized` folder and renamed to `<category>_<index>.jpg`

Keybindings :
- `ENTER` : keep the picture (must have been categorized before)
- `DELETE` : delete the picture
- `0`-`9` : select the category

### 2. Picture cropper

TODO, not implemented yet.

### 3. Multi-picture cropper

When you're finished with the categorizer, you can run the picture cropper. You may have to restart the app for you to see pictures in the widget. Don't start this before you're finished with the categorizer : the cropper doesn't rember wich pictures it has already cropped or not. 
Cropped images will be saved in the `./images/2_cropped` folder and renamed to `<categorized_picture_name>_crop_<crop_index>.jpg`

Keybindings :
- `ENTER` : Validate crop selection and go to next picture
- `R` : reinitialize the crop selection

### 4. Picture rotator

Just click on the damn button and wait for the magic to happen.

### How to run the app

Figure it out yourself, Poetry is well documented. Or use [this link](https://letmegooglethat.com/?q=python+poetry). Also, have I told you it's vibe-coded and you should expect bugs and crashes? Yeahhh, so don't use it for anything serious. Or don't use it at all.
