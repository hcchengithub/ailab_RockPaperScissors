import sys
import itchat
from itchat.content import * # TEXT PICTURE 等 constant 的定義
import peforth
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import time
import random
import scripts.label_image2 as ai

# WeChat chatroom name 
chatroom = "剪刀、石頭、布"

# Anti-Robot delay time , thanks to Rainy's great idea.
nextDelay = random.choice(range(3,18)) 

# import inception
# inception.maybe_download()
# model = inception.Inception() # The Inception v3 model 

# Inhibit 'bye' command, it terminates DOSBox session immediately 
# and leaves 'bye' in msg! Only a re-login can resolve it. To avoid this,
# decorator must return instead of doing the 'bye' command directly.
peforth.ok(loc=locals(),cmd='''
    :> [0] constant main.locals // ( -- dict ) main locals
    none value console.locals // ( -- dict ) console() locals 
    : bye main.locals :> ['itchat'].logout() bye ; 
    exit
    ''')  
    
# Send message to friend or chatroom depends on the given 'send'
# function. It can be itchat.send or msg.user.send up to the caller.
# WeChat text message has a limit at about 2000 utf-8 characters so
# we need to split a bigger string into chunks.
def send_chunk(text, send, pcs=2000):
    s = text
    while True:
        if len(s)>pcs:
            print(s[:pcs]); send(s[:pcs])
        else:
            print(s); send(s)
            break
        s = s[pcs:]    

# Console is a peforth robot that listens and talks.
# Used in chatting with friends and in a chatroom.
def console(msg,cmd):
    if cmd:
        print(cmd)  # already on the remote side, don't need to echo 
        global nextDelay
        nextDelay_msg = '\nNext anti-robot delay time: %i seconds\n' % (nextDelay)
        if peforth.vm.debug==11: peforth.ok('11> ',loc=locals(),cmd=":> [0] constant loc11 cr")  # breakpoint    
        
        # re-direct the display to peforth screen-buffer
        peforth.vm.dictate("display-off")  
        try:
            peforth.vm.push((locals(),globals(),'console prompt'))
            peforth.vm.dictate(":> [0] to console.locals " + cmd)
            # peforth.ok('OK ', loc=locals(),
            #     cmd=":> [0] to console.locals " + cmd + "\n exit")
        except Exception as err:
            errmsg = "Failed! : {}".format(err)
            peforth.vm.dictate("display-on")
            send_chunk(errmsg + nextDelay_msg, msg.user.send)
        else:
            peforth.vm.dictate("display-on screen-buffer")
            screen = peforth.vm.pop()[0]
            send_chunk(screen + nextDelay_msg, msg.user.send)

#        
# 讓 Inception V3 Transfered Learning 看照片，回答 剪刀、石頭、布
#        
def predict(msg):
    results = time.ctime() + '\n'
    results += 'Google Inception V3 Transfered Learning thinks it is:\n'
    pathname = 'download\\' + msg.fileName # 照片放在 working directory/download 下
    msg.download(pathname)  
    if peforth.vm.debug==22: peforth.ok('22a> ',loc=locals(),cmd=":> [0] constant loc22a cr")  # breakpoint    
    peforth.vm.dictate("dos ffmpeg -i {} -y 1.png".format(pathname)+"\ndrop")  
    # if msg.fileName.strip().lower().endswith((".jpeg",'.jpg','.png')):
    #     results += ai.predict(('download\\'+ msg.fileName).strip())
    # else:
    #     results += 'Ooops! jpeg pictures only, please. {} is not one.\n'.format(msg.fileName)
    results += ai.predict("1.png")
    if peforth.vm.debug==22: peforth.ok('22b> ',loc=locals(),cmd=":> [0] constant loc22b cr")  # breakpoint    
    return results

@itchat.msg_register(ATTACHMENT, isGroupChat=True)
def _a(msg):
    global nextDelay
    time.sleep(nextDelay)  # Anti-Robot delay 
    nextDelay = random.choice(range(3,18))
    nextDelay_msg = '\nNext anti-robot delay time: %i seconds\n' % (nextDelay)
    if peforth.vm.debug==33: peforth.ok('33> ',loc=locals(),cmd=":> [0] constant loc33 cr")  # breakpoint    
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        msg.download('download\\' + msg.fileName)
        send_chunk('Attachment: %s \nreceived at %s\n' % (msg.fileName,time.ctime()) + nextDelay_msg, msg.user.send)

@itchat.msg_register(TEXT, isGroupChat=True)
def _b(msg):
    if peforth.vm.debug==44: peforth.ok('44> ',loc=locals(),cmd=":> [0] constant loc44 cr")  # breakpoint    
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        if msg.isAt: 
            time.sleep(nextDelay)  # Anti-Robot delay 
            cmd = msg.text.split("\n",maxsplit=1)[1] # remove the first line: @nickName ...
            console(msg, cmd)                        # 避免帶有空格的 nickName 惹問題

@itchat.msg_register(PICTURE, isGroupChat=True)
def _c(msg):
    global nextDelay
    time.sleep(nextDelay)  # Anti-Robot delay 
    nextDelay = random.choice(range(3,18))
    nextDelay_msg = '\nNext anti-robot delay time: %i seconds\n' % (nextDelay)
    if peforth.vm.debug==55: peforth.ok('55> ',loc=locals(),cmd=":> [0] constant loc55 cr")  # breakpoint    
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        send_chunk(predict(msg) + nextDelay_msg, msg.user.send)

peforth.vm.debug = 22
peforth.ok('Examine> ',loc=locals(),cmd=':> [0] value locals')
if peforth.vm.debug==66: peforth.ok('66> ',loc=locals(),cmd=":> [0] constant loc66 cr")  # breakpoint    
itchat.auto_login(hotReload=False)
itchat.run(debug=False, blockThread=True)

# Bug list
# [x] 正常對話不需 delay --> FP @ v6
# [x] "Next anti-robot delay time" 往上合併好再發，
#     否則中間時間極短又被認出來是個 Bot。
#     --> FP @ v6
# [ ] 檢查 download/ folder 在不在? 不在要警告。
#
#

'''

# --------------- Playground ---------------------------------------------------
# Setup the playground for testing without itchat (avoid the need to login)

<py>
def msg():
    pass
def _():
    pass
msg.user = _    
msg.user.send = print
msg.user.NickName = 'A believer'    
msg.isAt = True
def _():
    print('msg.user.verify() ... pass')
msg.user.verify = _
msg.fileName = '20171222153010.jpg'
msg.type = 'fil' # also 'img'(image), 'vid'(video)
def _(fileName):
    print('Downloaded %s from WeChat cloud' % fileName)
msg.download = _
msg.text = "Message text from the WeChat cloud"
msg.Text = msg.text
push(msg)
</py> constant msg
 __main__ :> predict(v('msg')) . cr


\ 完整設定過程，讓 UUT 回覆它的畫面經由 itchat bot 傳給 AILAB Chatroom.
\ 讓遠端可以來監看執行狀況。這段程式是由遠端灌過來給 UUT 的。
    @秀。。 This line will be ignored 
    \ get itchat module object
    py> sys.modules['itchat'] constant itchat // ( -- module ) WeChat automation
    \ get PIL graph tool
    import PIL.ImageGrab constant im // ( -- module ) PIL.ImageGrab
    \ get AILAB chatroom object through partial nickName 
    itchat :> search_chatrooms('AILAB')[0] constant ailab // ( -- obj ) AILAB chatroom object
    \ Define check command that checks the UUT desktop screenshot
    import time constant time // ( -- module )
    cr time :> ctime() . cr \ print recent time on UUT when making this setting
    : check ( -- ) // check UUT
        time :: sleep(7) \ anti-robot delay time be always 7 seconds
        cr time :> ctime() . cr \ print the recent time on UUT 
        im :: grab().save("1.jpg") \ capture screenshot 
        ailab :> send("@img@1.jpg") \ send to AILAB chatroom 
        . cr \ shows the responsed message
        ;
    \ Define getfile command in case source code were modified on the UUT
    : getfile ( "pathname" -- ) // Get source code for debugging
        time :: sleep(7) py> str(pop()).strip() \ trim pathname 
        s" @fil@" swap + \ command string 
        cr time :> ctime() . space s" getfile: " . dup . cr
        ailab :> send(pop()) \ send to AILAB chatroom so everybody gets it
        . cr \ shows the responsed message
        ;
'''
