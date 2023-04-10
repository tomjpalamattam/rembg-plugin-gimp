#!/usr/bin/env python
# -*- coding: utf-8 -*-

# James Huang <elastic192@gmail.com>
# https://elastic192.blogspot.com/

from gimpfu import *
import os, sys, string, tempfile
import platform

tupleModel = ("u2net","u2net_human_seg", "u2net_cloth_seg", "isnet-general-use") # A tuple 'tuplemodel' is declared to give options (also selctable in drop down menu in gimp) to argument 'selModel'.
def python_fu_RemoveBG(image, drawable, asMask, selModel, AlphaMatting, aeValue):
	removeTmpFile = True
	osName = platform.system() # Get os name
	exportSep = str(os.sep)
	tdir = tempfile.gettempdir() # get tempdir of the os . Here "/tmp"
	print(tdir)
	jpgFile = "%s%sTemp-gimp-0000.jpg" % (tdir, exportSep)
	pngFile = "%s%sTemp-gimp-0000.png" % (tdir, exportSep)
	x1 = 0
	y1 = 0
	option = ""

	image.undo_group_start() # its a gimp function from gimpfu
	curLayer = pdb.gimp_image_get_active_layer(image) # its a gimp function from gimpfu

	if pdb.gimp_selection_is_empty(image):
		pdb.file_jpeg_save(image, drawable, jpgFile, jpgFile, 0.95, 0, 1, 0, "", 0, 1, 0, 0)
	else:
		pdb.gimp_edit_copy(drawable)
		non_empty, x1, y1, x2, y2 = pdb.gimp_selection_bounds(image)
		tmpImage = gimp.Image(x2-x1, y2-y1, 0)
		tmpDrawable = gimp.Layer(tmpImage, "Temp", tmpImage.width, tmpImage.height, RGB_IMAGE, 100, NORMAL_MODE)
		pdb.gimp_image_add_layer(tmpImage, tmpDrawable, 0)
		pat = pdb.gimp_context_get_pattern()
		pdb.gimp_context_set_pattern("Leopard")
		pdb.gimp_drawable_fill(tmpDrawable, 4)
		pdb.gimp_context_set_pattern(pat)
		pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(tmpDrawable,TRUE))
		pdb.file_jpeg_save(tmpImage, tmpDrawable, jpgFile, jpgFile, 0.95, 0, 1, 0, "", 0, 1, 0, 0)
		pdb.gimp_image_delete(tmpImage)
	
	aiExe = "/home/tom/.local/bin/rembg" # path for rembg
	if AlphaMatting:
		option = "-a -ae %d" % (aeValue)
	#cmd = '""%s" i %s "%s" "%s""' % (aiExe, option, jpgFile, pngFile)
	cmd = '"%s" i -m %s %s "%s" "%s"' % (aiExe, tupleModel[selModel], option, jpgFile, pngFile)  # the plugin will display these parameters and below line executes it.  
	os.system(cmd)

	file_exists = os.path.exists(pngFile)
	if file_exists:
		newlayer = pdb.gimp_file_load_layer(image, pngFile)
		image.add_layer(newlayer, -1)
		pdb.gimp_layer_set_offsets(newlayer, x1, y1)
		if asMask:
			pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, newlayer)
			image.remove_layer(newlayer)
			copyLayer = pdb.gimp_layer_copy(curLayer, TRUE)
			image.add_layer(copyLayer, -1)
			mask=copyLayer.create_mask(ADD_SELECTION_MASK)
			copyLayer.add_mask(mask)
			pdb.gimp_selection_none(image)

	image.undo_group_end()
	gimp.displays_flush()

	if removeTmpFile:
		if osName == "Windows":
			del_command = "del \"%s%sTemp-gimp-0000.*\"" % (tdir, exportSep)
		else:
			del_command = "rm \"%s%sTemp-gimp-0000.*\"" % (tdir, exportSep)
		os.system(del_command)

register(
    "python_fu_RemoveBG",
    "AI移除影像背景, AI Remove image background",
    "AI移除影像背景, AI Remove image background",
    "JamesH, <elastic192@gmail.com>",
    "JamesH, https://elastic192.blogspot.com",
    "2022/6/4",
    "<Image>/Python-Fu/AI移除影像背景(AI Remove background) ...",
    "RGB*",
    [
       (PF_TOGGLE, "asMask", ("當作圖層遮罩(as Mask)"), True),
       (PF_TOGGLE, "AlphaMatting", ("alpha matting"), False),
       (PF_OPTION,"selModel","模型(Model)", 0, tupleModel),
       (PF_SPINNER,"aeValue", ("ALPHA_MATTING_ERODE_SIZE"), 15, (15,100,1))
    ],
    [],
    python_fu_RemoveBG,
    domain=("gimp20-python", gimp.locale_directory))

main()
