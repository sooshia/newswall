import feedparser

from re     import sub
from math   import log
from tile   import TileBox
from random import choice
from time   import asctime, localtime, time
from feeder import GoogleNews

class TileView(object):
    CANVAS = (1080, 720)
    BORDER = 1

    CONF = {
            'border'        : 1, 
            'maxFontSize'   : {'ko' : 300, 'us' : 400, 'zh-CN' : 250 },
            'minFontSize'   : {'ko' :  13, 'us' :  10, 'zh-CN' :  10 },
            'padding'       : 5,
            'marginTop'     : 24,
           }

    TEMPLATE = {
                'title'     : '<DIV class="box" id="tile%(id)s" onmouseover="showDetail(this);" onmouseout="hideDetail(this);" '
                              'style="background-color: %(color)s;font-size:%(font)spx;width:%(width)spx;height:%(height)spx;left:%(left)spx;top:%(top)spx;">'
                              '<A onclick=\'showArticle("%(link)s"); resizeIF();\'>%(title)s</a>'
                              '</DIV>\n',
                'detail'    : '<DIV id="tile%(id)s_detail" class="box_detail" style="display:none; width:600px; height:300px; background-color:white">'
                              '%(summary)s'
                              '</DIV>\n',
                'header'    : '<!DOCTYPE html>\n'
                              '<HTML>\n'
                              '<HEAD>\n'
                              '<META http-equiv="Content-Type" content="text/html; utf-8">\n'
                              '<LINK rel="stylesheet" type="text/css" href="/site_media/css/common.css"/>\n'
                              '<SCRIPT type="text/javascript" src="/site_media/js/effects.js"></SCRIPT>\n'
                              '<SCRIPT type="text/javascript" src="/site_media/js/clock.js"></SCRIPT>\n'
                              '</HEAD>\n'
                              '<TITLE>NewsMap</TITLE>\n'
                              '<BODY style="margin:0" onLoad="worldClockZone()")>\n'
                              '<IFRAME id="articleContainer" onmouseout="hideArticle();" class="newsReader"></IFRAME>\n'
                              '<IMG id="rectangle" src="/site_media/images/rectangle.png" style="display:none; position:absolute;" />\n',
                'body'      : '<DIV style="width:1280px; height:720px; overflow:hidden; background-color:black">%(contents)s</DIV>\n',
                'navi'      : '<DIV class="navi">%(topics)s</DIV>\n',
                'topic'     : '<A href=%(link)s><DIV class="nitem" style="top:%(top)spx; background-color:%(color)s;">%(topic)s</DIV></A>\n',
                'selected'  : '<DIV class="nitem" style="top:%(top)spx; width:5px; background-color:rgba(255,255,255,0.85);"></DIV>\n',
                'language'  : '<DIV class="logo" id="small" style="top:540px; font-size:14px">%(lang)s</DIV>\n',
                'logo'      : '<DIV class="logo" id="big">%(logo)s</DIV>\n',
                'time'      : '<DIV class="logo" id="GMT" style="top:634px; font-size:16px">%(time)s</DIV>\n',
                'footer'    : '</BODY>\n' 
                              '</HTML>\n'
                }

    COLORS = {
               'BLUE'    : ['#154669', '#144365', '#1A5782', '#103650', '#123D5B', '#113854'], 
               'BROWN'   : ['#7B6C19', '#84741A', '#524810', '#5E5313', '#6F6116', '#7F7019'],
               'RED'     : ['#6D1616', '#671515', '#470E0E', '#801A1A', '#621414', '#541111'], 
               'GREEN'   : ['#265511', '#367C19', '#306C16', '#2F6C16', '#1F480E', '#41941E'],
               'CYAN'    : ['#1A8053', '#0B3925', '#1B8557', '#0D432C', '#13613F', '#17754C'],
               'PURPLE'  : ['#180B38', '#3C1C8D', '#200F4C', '#21104E', '#231153', '#401E95'],
               'PINK'    : ['#9C1F8B', '#420D3B', '#741767', '#8C1C7D', '#54114B', '#7F1971'],
               'GRAY'    : ['#7A7A7A', '#272727', '#5F5F5F', '#AAAAAA', '#666666', '#3C3C3C'],
               'ORANGE'  : ['#8B5927', '#D77D32', '#D2954F', '#EF904C', '#CDA27D', '#C29F6D'],
              }

    COLOR_MAP = {
               'BLUE'    : ['w'],
               'BROWN'   : ['b'],
               'RED'     : ['y', 'm'],
               'GREEN'   : ['l'],
               'ORANGE'  : ['p'],
               'PINK'    : ['e'],
               'PURPLE'  : ['s'],
               'GRAY'    : ['t', 'tc', 'snc'],
               'CYAN'    : ['po', 'ir'],
               }

    def __init__(self, locale):
        box = TileBox()

        while not box.checkDone():
            newTile = box.getTile()
            if box.checkAvailable(newTile):
                box.fill(newTile)
            box.move()

        self.locale = locale
        self.trace  = box.getTrace()
        self.unitX, self.unitY = box.getUnitSize(self.CANVAS)

    def getFontSize(self, tileSize, textLength):
        maxFontSize, minFontSize = self.CONF['maxFontSize'][self.locale], self.CONF['minFontSize'][self.locale]
        return (float((maxFontSize - minFontSize)) / textLength) * log(tileSize) + minFontSize
    
    def manipulate(self, summary):
        return sub('valign="top"', 'valign="center"', summary)

    def removeTail(self, title):
        return sub(' -.*', '', title)

    def getContents(self, feed, topic):
        contents   = ''
        feedCount  = len(feed)
        themeColor = self.getTopicColor(topic)

        for i, ((left, top), (width, height)) in enumerate(self.trace):
            contents += self.TEMPLATE['title'] % {'id'   : i,
                                                'color'  : choice(self.COLORS[themeColor]),
                                                'font'   : self.getFontSize(width * height, len(self.removeTail(feed[i % feedCount].title))),
                                                'width'  : width  * self.unitX - (self.CONF['padding'] + self.CONF['border']) * 2,
                                                'height' : height * self.unitY - (self.CONF['padding'] + self.CONF['border']) * 2,
                                                'left'   : left   * self.unitX,
                                                'top'    : top    * self.unitY,
                                                'title'  : self.removeTail(feed[i % feedCount].title),
                                                'link'   : feed[i % feedCount].link}
            contents += self.TEMPLATE['detail'] % {'id' : i, 'summary' : self.manipulate(feed[i % feedCount].summary)}

        return self.TEMPLATE['body'] % {'contents' : contents}

    def getTopics(self, topicDic, topicSel):
        topicMenu = '' 
        for index, topic in enumerate(topicDic):
            topicMenu += self.TEMPLATE['topic'] % {'link'   : '/%(locale)s/%(topic)s' % {'locale' : self.locale, 'topic' : topic},
                                                   'top'    : self.CONF['marginTop'] + index * 40,
                                                   'color'  : self.COLORS[self.getTopicColor(topic)][0],
                                                   'topic'  : topicDic[topic] } 
            if topic == topicSel:
                topicMenu += self.TEMPLATE['selected'] % {'top' : self.CONF['marginTop'] + index * 40} 

        return self.TEMPLATE['navi'] % {'topics' : topicMenu} 

    def getLanguage(self, locales):
        language = ['<A href="/%(locale)s/%(topic)s" style="color:%(color)s;">%(lang)s' % {
                                'locale' : locale, 
                                'topic'  : 'w', 
                                'color'  : locale == self.locale and '#BAFF1A' or '#FFFFFF',
                                'lang'   : GoogleNews.getLangFromLocale(locale)}  + '</A>'
                    for locale in locales]

        return self.TEMPLATE['language'] % {'lang' : ' | '.join(language)}

    def getTopicColor(self, topic):
        for color in self.COLOR_MAP:
            if topic in self.COLOR_MAP[color]:
                return color

    def getTemplate(self, key):
        return self.TEMPLATE.get(key, '')

    def getLogos(self):
        return self.TEMPLATE['logo'] % {'logo' : 'News'} + self.TEMPLATE['time'] % {'time'   : asctime(localtime(time()))}
