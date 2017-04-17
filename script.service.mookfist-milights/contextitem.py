import sys
import xbmc

print 'ListItem::VideoInfoTag::getFile() - %s' % sys.listitem.getVideoInfoTag().getFile()
print 'ListItem::GetPath() - %s' % sys.listitem.getPath()
print 'Label: %s' % xbmc.getInfoLabel('ListItem.FilenameAndPath')


player = xbmc.Player()
player.play(item=xbmc.getInfoLabel('ListItem.FilenameAndPath'))

# xbmc.Player.play(sys.listitem)

