#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, sys, re, threading, Queue, gzip, urllib2, tempfile, fnmatch, gobject

from config import *

def Dummy(signaled, class_id):
    pass

def LimitEntry(editable, new_text, new_text_length, position, regex):
    limit = re.compile(regex)
    if limit.match(new_text) is None:
        editable.stop_emission('insert-text')

def CleanEntry(editable, destination):
    print editable, destination
    textbuffer = destination['destination']
    textbuffer.set_text('')

def ClearEntry(editable, new_text, text):
    content = editable.get_text()
    if content == text:
        editable.set_text('')

def FillEntry(editable, new_text, text):
    content = editable.get_text()
    if content == '':
        editable.set_text(text)

def Toggle(widget, destination):
    widgetcontainer = destination['destination']
    on_off_widgetlist = widgetcontainer.get_children()
    for on_off_widget in on_off_widgetlist:
        new_widgets = on_off_widget.get_children()
        on_off_widgetlist = on_off_widgetlist + new_widgets
    for on_off_widget in on_off_widgetlist:
        if on_off_widget != widget:
            if on_off_widget.get_sensitive() == True:
                on_off_setting = False
            else:
                on_off_setting = True
            on_off_widget.set_sensitive(on_off_setting)

def ChangeCodename(signaled, class_id):
    dist = class_id.metadist
    db = apt_templates
    codenamecombo = class_id.metacodename
    codenamelist, codenameactive = CodenameList(class_id, dist, db)
    codenamecombo.get_model().clear()
    for item in codenamelist:
        codenamecombo.append_text(item)
    codenamecombo.set_active(codenameactive)

def ChangeRepo(signaled, class_id):
    dist = class_id.metadist.get_active_text()
    repoentry = class_id.metarepo
    exec "newrepotext = "+dist+"_repo"
    repoentry.set_text(newrepotext)

def ChangeSections(signaled, class_id):
    sections = class_id.metareposections
    checklist = SectionList(class_id, class_id.metadist)
    checkdefault = section_default
    children = sections.get_children()
    for child in children:
        sections.remove(child)
    for item in checklist:
        check = gtk.CheckButton(item)
        if item == checkdefault:
            check.set_active(True)
            check.set_sensitive(False)
        check.show()
        sections.pack_start(check, expand, fill, padding)

def AddExtraRepos(signaled, params):
    url = params['url'].get_text()
    branch = params['branch'].get_text()
    sections = params['sections'].get_text()
    arch_container = params['arch_container']
    archs = []
    repolist = params['repolist'].get_text(*params['repolist'].get_bounds())
    repolistframe = params['repolist']
    fvalidation = params['fvalidation']
    fok = params['fok']
    ferror = params['ferror']
    fprogresswindow = params['fprogresswindow']
    frequest = params['frequest']
    errormessage = params['errormessage']
    errortitle = params['errortitle']
    progressmessage = params['progressmessage']
    progresstitle = params['progresstitle']
    
    arch_children = arch_container.get_children()
    for child in arch_children:
        if child.get_active():
            archs.append(child.get_label())

    if fvalidation(url) and archs:
        thread = threading.Thread(
            target = fok, args = (
                url, branch, sections, archs, repolist, repolistframe,
                ferror, fprogresswindow, frequest, errormessage,
                errortitle, progressmessage, progresstitle
                )
            )
    else:
        thread = threading.Thread(
            target = ferror,
            args = (errormessage, errortitle)
            )
    thread.start()

def AddExtraReposThread(url, branch, sections, archs, repolist, repolistframe,
                ferror, fprogresswindow, frequest, errormessage,
                errortitle, progressmessage, progresstitle):

    errorcounter = 0
    q_window = Queue.Queue()
    q_bar = Queue.Queue()
    q_msg = Queue.Queue()

    if repolist.find('deb '+url+' '+branch+' '+sections) == -1:

        thread = threading.Thread(
            target = fprogresswindow,
            args = (
                progresstitle, progresstitle,
                q_window, q_bar, q_msg
                )
            )
        thread.start()
        message = q_msg.get()
        window = q_window.get()
        bar = q_bar.get()

        for section in sections.split(' '):
            for arch in archs:
                contentheader = 0
                message.set_markup(progressmessage % (arch, section))
                bar.pulse()
                requesturl = url+'/dists/'+branch+'/'+section+'/binary-'+arch+'/Packages.gz'
                try:
                    response = urllib2.urlopen(frequest(requesturl))
                except urllib2.HTTPError as e:
                    errorcode = str(e.code)
                    errorcounter += 1
                except urllib2.URLError as e:
                    errorcode = str(e.reason)
                    errorcounter += 1
                except IOError as e:
                    errorcode = str(e.errno)+': '+str(e.strerror)
                    errorcounter += 1
                except ValueError as e:
                    errorcode = str(e)
                    errorcounter += 1
                except TypeError as e:
                    errorcode = str(e)
                    errorcounter += 1
                except:
                    errorcode = str(sys.exc_info()[0])
                    errorcounter += 1
                else:
                    headers = response.info()
                    contentheader = int(headers["Content-Length"])
                
                if contentheader == 0:
                    errorcode = ''
                    errorcounter += 1

        if errorcounter > 0:
            thread = threading.Thread(
                target = ferror,
                args = (errormessage+":\n"+errorcode, errortitle)
                )
            thread.start()
        else:
            repolistframe.set_text(repolist+'deb '+url+' '+branch+' '+sections+'\n')

        window.hide_all()

def AddPackages(signaled, params):
    url = params['url'].get_text()
    branch = params['branch'].get_active_text()
    section_container = params['section_container']
    sections = []
    arch_container = params['arch_container']
    archs = []
    extrarepos = params['extrarepos'].get_text(*params['extrarepos'].get_bounds())
    packages = params['packages'].get_text()
    packageslistframe = params['packageslist']
    fok = params['fok']
    ferror = params['ferror']
    fprogresswindow = params['fprogresswindow']
    fprogress = params['fprogress']
    freplace = params['freplace']
    fcleantempdir = params['fcleantempdir']
    m_no_arch_selected = params['m_no_arch_selected']
    errortitle = params['errortitle']
    progressmessage = params['progressmessage']
    progresstitle = params['progresstitle']

    section_children = section_container.get_children()
    for child in section_children:
        if child.get_active():
            sections.append(child.get_label())

    arch_children = arch_container.get_children()
    for child in arch_children:
        if child.get_active():
            archs.append(child.get_label())

    repolist = [[url, branch, sections]]

    for repoline in extrarepos.split('\n'):
        if repoline:
            components = repoline.split(' ')
            xurl = components[1]
            xbranch = components[2]
            del components[0:3]
            repo = [xurl, xbranch, components]
            repolist.append(repo)

    if archs:
        thread = threading.Thread(
            target = fok, args = (
                repolist, packages, archs, packageslistframe,
                ferror, fprogresswindow, fprogress, freplace, fcleantempdir,
                errormessage, errortitle, progressmessage, progresstitle
                )
            )
    else:
        thread = threading.Thread(
            target = ferror,
            args = (m_no_arch_selected, errortitle)
            )
    thread.start()

def AddPackagesThread(repolist, packages, archs, packageslistframe,
            ferror, fprogresswindow, fprogress, freplace, fcleantempdir,
            errormessage, errortitle, progressmessage, progresstitle):

    bs = 16*1024
    errorcounter = 0
    dic = {
            '/':'', ':':'', 'http':'', 'file':'', 'ftp':'', '?':'',
            '=':'', '&':'', '-':'', '(':'', ')':'', '+':'', '-':'',
            '#':'', '$':'', '%':'', '@':'', '|':'', '~':'', '_':'',
            ',':'', ';':'', '!':''
            }

    q_window = Queue.Queue()
    q_bar = Queue.Queue()
    q_msg = Queue.Queue()
    f_cleantempdir = fcleantempdir(tempdir)

    thread = threading.Thread(
        target = fprogresswindow,
        args = (
            progresstitle, progresstitle,
            q_window, q_bar, q_msg
            )
        )
    thread.start()

    message = q_msg.get()
    window = q_window.get()
    bar = q_bar.get()

    for url, branch, sections in repolist:
        for section in sections:
            for arch in archs:
                read = 0
                blocknum = 0
                contentheader = 0
                message.set_markup(progressmessage % (arch, section))
                requesturl = url+'/dists/'+branch+'/'+section+'/binary-'+arch+'/Packages.gz'
                urlname = freplace(url, dic)

                pkgcache = tempfile.NamedTemporaryFile(
                    prefix = urlname+'-'+branch+'-',
                    suffix = '-'+section+'_'+arch+'.gz',
                    dir = tempdir, delete = False
                    )

                try:
                    response = urllib2.urlopen(requesturl)
                except urllib2.HTTPError as e:
                    errorcode = str(e.code)
                    errorcounter += 1
                except urllib2.URLError as e:
                    errorcode = str(e.reason)
                    errorcounter += 1
                except IOError as e:
                    errorcode = str(e.errno)+': '+str(e.strerror)
                    errorcounter += 1
                except ValueError as e:
                    errorcode = str(e)
                    errorcounter += 1
                except TypeError as e:
                    errorcode = str(e)
                    errorcounter += 1
                except:
                    errorcode = str(sys.exc_info()[0])
                    errorcounter += 1
                else:
                    headers = response.info()
                    contentheader = int(headers["Content-Length"])

                if contentheader == 0:
                    errorcode = ''
                    errorcounter += 1

                if errorcounter == 0:
                    while True:
                        block = response.read(bs)
                        if not block:
                            break
                        pkgcache.write(block)
                        pkgcache.flush()
                        os.fsync(pkgcache.fileno())
                        read += len(block)
                        blocknum += 1
                        percent = float(blocknum*bs)/contentheader
                        fprogress(bar, False, percent)

                    pkgcache.close()
                    response.close()

                if read < contentheader:
                    errorcode = ''
                    errorcounter += 1

    if errorcounter > 0:
        thread = threading.Thread(
            target = ferror,
            args = (errormessage+":\n"+errorcode, errortitle)
            )
        thread.start()
    else:
        timer = gobject.timeout_add(100, fprogress, bar, True, 0)
        for package in packages.split(' '):
            found = 0
            message.set_markup(progressmessage % (package, section))
            for path in os.listdir(tempdir):
                if os.path.isfile(tempdir+path) and fnmatch.fnmatch(tempdir+path, '*.gz'):
                    zipfile = gzip.open(tempdir+path)
                    for line in zipfile.readlines():
                        if line == 'Package: '+package+'\n':
                            found += 1
                    zipfile.close()

            if found > 0:
                packageslist = packageslistframe.get_text(*packageslistframe.get_bounds())
                packageslistframe.set_text(packageslist+' '+package)
            else:
                thread = threading.Thread(
                    target = ferror,
                    args = (errormessage+":\n"+package, errortitle)
                    )
                thread.start()
        gobject.source_remove(timer)
    window.destroy()
