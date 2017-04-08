from xml.dom.minidom import parse
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import sys
import math
from traceback import format_exc

ADDON_ID = "script.module.colorpicker"
ADDON = xbmcaddon.Addon(ADDON_ID)
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
COLORFILES_PATH = xbmc.translatePath("special://profile/addon_data/%s/colors/" % ADDON_ID).decode("utf-8")
SKINCOLORFILES_PATH = xbmc.translatePath("special://profile/addon_data/%s/colors/" % xbmc.getSkinDir()).decode("utf-8")
SKINCOLORFILE = xbmc.translatePath("special://skin/extras/colors/colors.xml").decode("utf-8")
WINDOW = xbmcgui.Window(10000)
SUPPORTS_PIL = False

# HELPERS ###########################################


def log_msg(msg, level=xbmc.LOGDEBUG):
    '''log message to kodi log'''
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    xbmc.log("Skin Helper Service ColorPicker --> %s" % msg, level=level)


def log_exception(modulename, exceptiondetails):
    '''helper to properly log an exception'''
    log_msg(format_exc(sys.exc_info()), xbmc.LOGWARNING)
    log_msg("Exception in %s ! --> %s" % (modulename, exceptiondetails), xbmc.LOGERROR)


def try_encode(text, encoding="utf-8"):
    '''helper method'''
    try:
        return text.encode(encoding, "ignore")
    except Exception:
        return text

# IMPORT PIL/PILLOW ###################################

try:
    # prefer Pillow
    from PIL import Image
    img = Image.new("RGB", (1, 1))
    del img
    SUPPORTS_PIL = True
except Exception as exc:
    log_exception(__name__, exc)
    try:
        # fallback to traditional PIL
        import Image
        img = Image.new("RGB", (1, 1))
        del img
        SUPPORTS_PIL = True
    except Exception as exc:
        log_exception(__name__, exc)


class ColorPicker(xbmcgui.WindowXMLDialog):
    '''
        Provides a simple ColorPicker in Kodi by filling a list/container
        with listitems for each available color.
        The thumb for each listitem is set to a PNG image in the right color,
        generated by PIL. The skinner can save the user-selected color to either a
        skin string, window property or pass it to the skinshortcuts script.
    '''

    colors_list = None
    skinstring = None
    win_property = None
    shortcut_property = None
    colors_path = None
    saved_color = None
    current_window = None
    header_label = None
    colors_file = None
    all_colors = {}
    all_palettes = []
    active_palette = None

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.action_exitkeys_id = [10, 13]
        self.win = xbmcgui.Window(10000)
        self.build_colors_list()
        self.result = -1

        self.addon_id = kwargs.get('addon_id', ADDON_ID)
        self.addon = kwargs.get('addon', ADDON)
        self.addon_path = kwargs.get('addon_path', ADDON_PATH)

        self.skin_color_file = kwargs.get('skin_color_file', SKINCOLORFILE)
        self.skin_color_files_path = kwargs('skin_color_files_path', SKINCOLORFILES_PATH)
        self.color_files_path = kwargs('color_files_path', COLORFILES_PATH)




        # check paths
        if xbmcvfs.exists(self.skin_color_file) and not xbmcvfs.exists(self.skin_color_files_path):
            xbmcvfs.mkdirs(self.skin_color_files_path)
        if not xbmcvfs.exists(self.color_files_path):
            xbmcvfs.mkdirs(self.color_files_path)

    def add_color_to_list(self, colorname, colorstring):
        '''adds the coloroption as listitem to the list'''
        color_image_file = self.create_color_swatch_image(colorstring)
        listitem = xbmcgui.ListItem(label=colorname, iconImage=color_image_file)
        listitem.setProperty("colorstring", colorstring)
        self.colors_list.addItem(listitem)

    def build_colors_list(self):
        '''
            build the list of colorswatches we want to display, check if skinner
            overrides the default provided colorsfile and pick the right colorpalette
        '''

        # prefer skin colors file
        if xbmcvfs.exists(self.skin_color_file):
            colors_file = self.skin_color_file
            self.colors_path = self.skin_color_files_path
        else:
            colors_file = os.path.join(self.addon_path, 'resources', 'colors', 'colors.xml').decode("utf-8")
            self.colors_path = self.color_files_path

        doc = parse(colors_file)
        palette_listing = doc.documentElement.getElementsByTagName('palette')
        if palette_listing:
            # we have multiple palettes specified
            for item in palette_listing:
                palette_name = item.attributes['name'].nodeValue
                self.all_colors[palette_name] = self.get_colors_from_xml(item)
                self.all_palettes.append(palette_name)
        else:
            # we do not have multiple palettes
            self.all_colors["all"] = self.get_colors_from_xml(doc.documentElement)
            self.all_palettes.append("all")

    def load_colors_palette(self, palette_name=""):
        '''load preferred color palette'''
        self.colors_list.reset()
        if not palette_name:
            # just grab the first palette if none specified
            palette_name = self.all_palettes[0]
        # set window prop with active palette
        if palette_name != "all":
            self.current_window.setProperty("palettename", palette_name)
        if not self.all_colors.get(palette_name):
            log_msg("No palette exists with name %s" % palette_name, xbmc.LOGERROR)
            return
        for item in self.all_colors[palette_name]:
            self.add_color_to_list(item[0], item[1])

    def onInit(self):
        '''Called after initialization, get all colors and build the listing'''
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        self.current_window = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        self.colors_list = self.getControl(3110)
        # set header_label
        try:
            self.getControl(1).setLabel(self.header_label)
        except Exception:
            pass

        # get current color that is stored in the skin setting
        curvalue = ""
        curvalue_name = ""
        if self.skinstring:
            curvalue = xbmc.getInfoLabel("Skin.String(%s)" % self.skinstring)
            curvalue_name = xbmc.getInfoLabel("Skin.String(%s.name)" % self.skinstring)
        if self.win_property:
            curvalue = WINDOW.getProperty(self.win_property)
            curvalue_name = xbmc.getInfoLabel('%s.name)' % self.win_property)
        if curvalue:
            self.current_window.setProperty("colorstring", curvalue)
            if curvalue != curvalue_name:
                self.current_window.setProperty("colorname", curvalue_name)
            self.current_window.setProperty("current.colorstring", curvalue)
            if curvalue != curvalue_name:
                self.current_window.setProperty("current.colorname", curvalue_name)

        # load colors in the list
        self.load_colors_palette(self.active_palette)

        # focus the current color
        if self.current_window.getProperty("colorstring"):
            self.current_window.setFocusId(3010)
        else:
            # no color setup so we just focus the colorslist
            self.current_window.setFocusId(3110)
            self.colors_list.selectItem(0)
            self.current_window.setProperty("colorstring",
                                            self.colors_list.getSelectedItem().getProperty("colorstring"))
            self.current_window.setProperty("colorname",
                                            self.colors_list.getSelectedItem().getLabel())

        # set opacity slider
        if self.current_window.getProperty("colorstring"):
            self.set_opacity_slider()

        xbmc.executebuiltin("Dialog.Close(busydialog)")

    def onFocus(self, controlId):
        '''builtin kodi event'''
        pass

    def onAction(self, action):
        '''builtin kodi event'''
        if action.getId() in (9, 10, 92, 216, 247, 257, 275, 61467, 61448, ):
            # exit or back called from kodi
            self.save_color_setting(restoreprevious=True)
            self.close_dialog()

    def close_dialog(self):
        '''close our xml window'''
        self.close()

    def set_opacity_slider(self):
        '''set the opacity slider based on the alpha channel in the ARGB colorstring'''
        colorstring = self.current_window.getProperty("colorstring")
        try:
            if colorstring != "" and colorstring is not None and colorstring.lower() != "none":
                a, r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:6], colorstring[6:]
                a, r, g, b = [int(n, 16) for n in (a, r, g, b)]
                a = 100.0 * a / 255
                self.getControl(3015).setPercent(float(a))
        except Exception:
            pass

    def save_color_setting(self, restoreprevious=False):
        '''save the selected color to the skin setting or window property'''
        if restoreprevious:
            colorname = self.current_window.getProperty("current.colorname")
            colorstring = self.current_window.getProperty("current.colorstring")
        else:
            colorname = self.current_window.getProperty("colorname")
            colorstring = self.current_window.getProperty("colorstring")
        if not colorname:
            colorname = colorstring
        self.create_color_swatch_image(colorstring)
        if self.skinstring and (not colorstring or colorstring == "None"):
            xbmc.executebuiltin("Skin.SetString(%s.name, %s)"
                                % (try_encode(self.skinstring), try_encode(self.addon.getLocalizedString(32013))))
            xbmc.executebuiltin("Skin.SetString(%s, None)"
                                % try_encode(self.skinstring))
            xbmc.executebuiltin("Skin.Reset(%s.base)"
                                % try_encode(self.skinstring))
        elif self.skinstring and colorstring:
            xbmc.executebuiltin("Skin.SetString(%s.name, %s)"
                                % (try_encode(self.skinstring), try_encode(colorname)))
            colorbase = "ff" + colorstring[2:]
            xbmc.executebuiltin("Skin.SetString(%s, %s)"
                                % (try_encode(self.skinstring), try_encode(colorstring)))
            xbmc.executebuiltin("Skin.SetString(%s.base, %s)"
                                % (try_encode(self.skinstring), try_encode(colorbase)))
        elif self.win_property:
            WINDOW.setProperty(self.win_property, colorstring)
            WINDOW.setProperty(self.win_property + ".name", colorname)

    def onClick(self, controlID):
        '''builtin kodi event - handle onclick and execute correct action'''
        if controlID == 3110:
            # color clicked
            item = self.colors_list.getSelectedItem()
            colorstring = item.getProperty("colorstring")
            self.current_window.setProperty("colorstring", colorstring)
            self.current_window.setProperty("colorname", item.getLabel())
            self.set_opacity_slider()
            self.current_window.setFocusId(3012)
            self.current_window.setProperty("color_chosen", "true")
            self.save_color_setting()
        elif controlID == 3010:
            # manual input
            dialog = xbmcgui.Dialog()
            colorstring = dialog.input(self.addon.getLocalizedString(32012),
                                       self.current_window.getProperty("colorstring"), type=xbmcgui.INPUT_ALPHANUM)
            self.current_window.setProperty("colorname", self.addon.getLocalizedString(32050))
            self.current_window.setProperty("colorstring", colorstring)
            self.set_opacity_slider()
            self.save_color_setting()
        elif controlID == 3011:
            # none button
            self.current_window.setProperty("colorstring", "")
            self.save_color_setting()

        if controlID == 3012 or controlID == 3011:
            # save button clicked or none
            if self.skinstring or self.win_property:
                self.close_dialog()
            elif self.shortcut_property:
                self.result = (self.current_window.getProperty("colorstring"),
                               self.current_window.getProperty("colorname"))
                self.close_dialog()

        elif controlID == 3015:
            try:
                # opacity slider
                colorstring = self.current_window.getProperty("colorstring")
                opacity = self.getControl(3015).getPercent()
                num = opacity / 100.0 * 255
                e = num - math.floor(num)
                a = e < 0.5 and int(math.floor(num)) or int(math.ceil(num))
                colorstring = colorstring.strip()
                r, g, b = colorstring[2:4], colorstring[4:6], colorstring[6:]
                r, g, b = [int(n, 16) for n in (r, g, b)]
                color = (a, r, g, b)
                colorstringvalue = '%02x%02x%02x%02x' % color
                self.current_window.setProperty("colorstring", colorstringvalue)
                self.save_color_setting()
            except Exception:
                pass

        elif controlID == 3030:
            # change color palette
            ret = xbmcgui.Dialog().select(self.addon.getLocalizedString(32141), self.all_palettes)
            self.load_colors_palette(self.all_palettes[ret])

    def create_color_swatch_image(self, colorstring):
        '''helper method to generate a colorized image using PIL'''
        color_image_file = None
        if colorstring:
            paths = []
            paths.append(u"%s%s.png" % (self.color_files_path, colorstring))
            if xbmcvfs.exists(self.skin_color_file):
                paths.append(u"%s%s.png" % (self.skin_color_files_path, colorstring))
            for color_image_file in paths:
                if not xbmcvfs.exists(color_image_file):
                    if SUPPORTS_PIL:
                        # create image with PIL
                        try:
                            colorstring = colorstring.strip()
                            if colorstring[0] == '#':
                                colorstring = colorstring[1:]
                            a, r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:6], colorstring[6:]
                            a, r, g, b = [int(n, 16) for n in (a, r, g, b)]
                            color = (r, g, b, a)
                            img = Image.new("RGBA", (16, 16), color)
                            img.save(color_image_file)
                            del img
                        except Exception as exc:
                            log_exception(__name__, exc)
                    else:
                        # create image with online service if no pil support
                        xbmcvfs.copy( "https://dummyimage.com/16/%s/%s.png" % (colorstring[2:],colorstring[2:]), color_image_file )
                        log_msg("Local PIL module not available, generating color swatch image with online service", xbmc.LOGWARNING)
        return color_image_file

    @staticmethod
    def get_colors_from_xml(xmlelement):
        '''get all colors from xml file'''
        items = []
        listing = xmlelement.getElementsByTagName('color')
        for color in listing:
            name = color.attributes['name'].nodeValue.lower()
            colorstring = color.childNodes[0].nodeValue.lower()
            items.append((name, colorstring))
        return items
