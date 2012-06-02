#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, pango

from config import *

def Banner(class_id, image):
    box = gtk.HBox(homogeneous, spacing)
    box.set_border_width(borderwidth/3)

    banner = gtk.Image()
    banner.set_from_file(image)
    banner.show()

    box.pack_start(banner, expand, fill, padding)

    return box

def Title(class_id, text):
    box = gtk.HBox(homogeneous, spacing)
    box.set_border_width(borderwidth)

    title = gtk.Label()
    title.set_markup(text)
    title.set_line_wrap(True)
    title.set_size_request(window_width - (borderwidth*10), -1)
    title.show()

    box.pack_start(title, expand, fill, padding)

    return box

def Description(class_id, text):
    box = gtk.HBox(homogeneous, spacing)
    box.set_border_width(borderwidth/3)

    style = pango.AttrList()
    size = pango.AttrSize(8000, 0, -1)
    style.insert(size)

    description = gtk.Label()
    description.set_markup(text)
    description.set_line_wrap(True)
    description.set_size_request(window_width - (borderwidth*10), -1)
    description.set_attributes(style)
    description.show()

    box.pack_start(description, expand, fill, padding)

    return box

def TextEntry(class_id, maxlength, length, text, regex, flimit, fclear, ffill):
    box = gtk.HBox(homogeneous, spacing)
    box.set_border_width(borderwidth/3)

    textentry = gtk.Entry()
    textentry.set_width_chars(length)
    textentry.set_max_length(maxlength)
    textentry.set_text(text)
    textentry.set_sensitive(True)
    textentry.set_editable(True)
    textentry.set_visibility(True)
    textentry.connect('insert-text', flimit, regex)
    textentry.connect('focus-in-event', fclear, text)
    textentry.connect('focus-out-event', ffill, text)
    textentry.show()

    box.pack_start(textentry, expand, fill, padding)

    return box, textentry

def Combo(class_id, combolist, combodefault, entry, f_1, p_1, f_2, p_2, f_3, p_3):
    box = gtk.HBox(homogeneous, spacing)
    box.set_border_width(borderwidth/3)

    if entry:
        combo = gtk.combo_box_entry_new_text()
    else:
        combo = gtk.combo_box_new_text()

    for item in combolist:
        combo.append_text(item)

    combo.set_active(combodefault)
    combo.connect('changed', f_1, p_1)
    combo.connect('changed', f_2, p_2)
    combo.connect('changed', f_3, p_3)
    combo.show()

    box.pack_start(combo, expand, fill, padding)

    return box, combo

def CheckList(class_id, checklist, checkdefault):
    box = gtk.HBox(homogeneous, spacing)
    box.set_border_width(borderwidth/3)

    space = gtk.HSeparator()
    box.pack_start(space, expand, fill, 30)

    items = gtk.VBox(homogeneous, spacing)
    items.set_border_width(borderwidth/3)

    for item in checklist:
        check = gtk.CheckButton(item)
        if checkdefault != '' and item == checkdefault:
            check.set_active(True)
            check.set_sensitive(False)
        check.show()
        items.pack_start(check, expand, fill, padding)

    box.pack_start(items, expand, fill, padding)

    return box, items

def ScrolledFrame(class_id):
    frame = gtk.Frame()
    frame.set_border_width(borderwidth/3)

    scrolledwindow = gtk.ScrolledWindow()
    scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

    textview = gtk.TextView()
    textview.set_wrap_mode(gtk.WRAP_WORD)
    textview.set_editable(False)
    text = textview.get_buffer()

    scrolledwindow.add(textview)
    frame.add(scrolledwindow)

    return frame, text

def ActiveButton(class_id, text, f_1, p_1, f_2, p_2, f_3, p_3):
    box = gtk.HBox(homogeneous, spacing)
    box.set_border_width(borderwidth*0)

    button = gtk.Button(stock = text)
    button.set_border_width(borderwidth*0)
    button.connect('clicked', f_1, p_1)
    button.connect('clicked', f_2, p_2)
    button.connect('clicked', f_3, p_3)
    button.show()

    box.pack_start(button, expand, fill, padding)

    return box, button

def ActiveCheck(class_id, text, active, f_1, p_1, f_2, p_2, f_3, p_3):
    box = gtk.HBox(homogeneous, spacing)
    box.set_border_width(borderwidth/3)

    check = gtk.CheckButton(text)
    check.set_border_width(borderwidth)
    if active:
        check.set_active(True)
    check.connect('toggled', f_1, p_1)
    check.connect('toggled', f_2, p_2)
    check.connect('toggled', f_3, p_3)
    check.show()

    box.pack_start(check, expand, fill, padding)

    return box, check

def UserMessage(message, title):
    gtk.gdk.threads_enter()
    md = gtk.MessageDialog( parent = None,
                            flags = 0,
                            type = gtk.MESSAGE_ERROR,
                            buttons = gtk.BUTTONS_CLOSE,
                            message_format = message)
    md.set_title(title)
    md.run()
    md.destroy()
    gtk.gdk.threads_leave()

def ProgressWindow(text, title, q_window, q_bar, q_msg):
    gtk.gdk.threads_enter()
    dialog = gtk.Dialog()
    dialog.set_title(title)
    dialogarea = dialog.get_content_area()
    dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    dialog.set_size_request(window_width*2/3, window_height/8)
    dialog.set_resizable(False)

    box = gtk.VBox(homogeneous, spacing)
    box.set_border_width(borderwidth)

    label = gtk.Label()
    label.set_markup(text)
    progress = gtk.ProgressBar()

    box.pack_start(label, expand, fill, padding)
    box.pack_start(progress, expand, fill, padding)
    dialogarea.add(box)
    dialog.show_all()

    q_window.put(dialog)
    q_bar.put(progress)
    q_msg.put(label)
    gtk.gdk.threads_leave()
