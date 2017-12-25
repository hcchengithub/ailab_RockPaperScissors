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
chatroom = "AILAB" # "剪刀、石頭、布"

# Anti-Robot delay time , thanks to Rainy's great idea.
nextDelay = 3
nextDelay_msg = 'Next anti-robot delay time: %i seconds\n' % (nextDelay)

# Initialize debugger peforth 
peforth.ok(loc=locals(),cmd='''
    :> [0] value main.locals // ( -- dict ) main locals
    \ Check ffmpeg, ffprobe, the needed 'download' directory, and the neural network model 
    dos ffmpeg -version
    [if] cr ." Fatal error! ffmpeg not found which is used to convert pictures." cr bye [then]
    dos ffprobe -version
    [if] cr ." Fatal error! ffprobe not found which is for pictures' duration." cr bye [then]
    dos dir download 
    [if] cr ." Fatal error! 'download' directory not found." cr bye [then]
    dos dir tf_files\models\mobilenet_v1_1.0_224_frozen.tgz 
    dos dir tf_files\models\mobilenet_v1_0.50_224_frozen.tgz 
    or \ only one model needed but I have them downloaded already so check them all
    [if] cr 
         ." Fatal error! neural network model not found." cr 
         ."   tf_files\models\mobilenet_v1_1.0_224_frozen.tgz " cr
         ."   tf_files\models\mobilenet_v1_0.50_224_frozen.tgz" cr
         bye [then]
    \ define variables
    __main__ :> chatroom constant chatroom // ( -- text ) The working chatroom NickName
    __main__ :> nextDelay constant nextDelay // ( -- int ) Anti-robot delay time
    none value locals
    none value msg
    \ redefine the 'bye' command to logout itchat first
    : bye main.locals :> ['itchat'].logout() bye ; 
    exit \ Don't forget this!!
    ''')  
    
# Sending message to friend or chatroom depends on the given 'send'
# function. It can be itchat.send or msg.user.send up to the caller.
# WeChat text message has a limit at about 2000 utf-8 characters so
# we need to split a bigger string into chunks.
def send_chunk(text, send, pcs=2000):
    s = text
    while True:
        if len(s)>pcs:
            time.sleep(3)  # Anti-Robot delay 
            print(s[:pcs]); 
            send(s[:pcs])
        else:
            time.sleep(3)  # Anti-Robot delay 
            print(s); 
            send(s)
            break
        s = s[pcs:]    

# Console is a peforth robot that listens and talks.
# Used in chatting with both friends and chatrooms.
def console(msg,cmd):
    if cmd:
        print(cmd)  # already on the remote side, don't need to echo. 
        peforth.vm.push(msg); peforth.vm.dictate("to msg")  # Availablize msg in peforth interpreter
        if peforth.vm.debug==11: peforth.ok('11> ',loc=locals(),cmd=":> [0] to locals cr")  # breakpoint
        # re-direct the display to peforth screen-buffer
        peforth.vm.dictate("display-off")  
        try:
            peforth.vm.push((locals(),globals(),'console prompt'))
            peforth.vm.dictate(":> [0] to locals " + cmd)
        except Exception as err:
            errmsg = "Failed! : {}".format(err)
            peforth.vm.dictate("display-on")
            time.sleep(nextDelay)  # Anti-Robot delay 
            send_chunk(errmsg + nextDelay_msg + "\nOK", msg.user.send)
        else:
            # Normal cases 
            peforth.vm.dictate("display-on screen-buffer")
            screen = peforth.vm.pop()[0]
            time.sleep(nextDelay)  # Anti-Robot delay 
            send_chunk(screen + nextDelay_msg + "\nOK", msg.user.send)

#        
# 讓 Inception V3 Transfered Learning 看照片，回答 剪刀、石頭、布
#        
def predict(msg):
    if peforth.vm.debug==22: peforth.ok('22> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    results = time.ctime() + '\n'
    results += 'Google Inception V3 Transfered Learning thinks it is:\n'
    pathname = 'download\\' + msg.fileName # 照片放在 working directory/download 下
    msg.download(pathname)  
    # TensorFlow 的 tf.image.decode_bmp/jpen/png/pcm 很差，改用 ffmpeg 
    peforth.vm.dictate("dos ffmpeg -i {} -y 1.png".format(pathname)+"\ndrop\n")  
    results += ai.predict("1.png")
    peforth.vm.dictate("dos del {}".format(pathname)+"\ndrop\n")
    time.sleep(nextDelay)  # Anti-Robot delay 
    send_chunk(results + nextDelay_msg, msg.user.send)

@itchat.msg_register((ATTACHMENT,VIDEO,VOICE,RECORDING), isGroupChat=True)
def attachment(msg):
    if peforth.vm.debug==33: peforth.ok('33> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        msg.download('download\\' + msg.fileName)
        time.sleep(nextDelay)  # Anti-Robot delay 
        send_chunk('Attachment: %s \nreceived at %s\n' % (msg.fileName,time.ctime()) + nextDelay_msg, msg.user.send)

@itchat.msg_register(TEXT, isGroupChat=True)
def chat(msg):
    if peforth.vm.debug==44: peforth.ok('44> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        if msg.isAt: 
            cmd = msg.text.split("\n",maxsplit=1)[1] # remove the first line: @nickName ...
            console(msg, cmd)                        # 避免帶有空格的 nickName 惹問題
        else:    
            # Shown on the robot computer
            print(time.ctime(msg.CreateTime), end=" ")
            for i in msg.User['MemberList']:
                if i.UserName == msg.ActualUserName:
                    print(i.NickName)
            print(msg.text)

@itchat.msg_register(PICTURE, isGroupChat=True)
def picture(msg):
    if peforth.vm.debug==55: peforth.ok('55> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        predict(msg)

# peforth.vm.debug = 44
if peforth.vm.debug==66: peforth.ok('66> ',loc=locals(),cmd=":> [0] to locals cr")  # breakpoint    
itchat.auto_login(hotReload=False)
itchat.run(debug=True, blockThread=True)
peforth.ok('Examine> ',loc=locals(),cmd=':> [0] to main.locals cr')

'''

# --------------- Playground ---------------------------------------------------
# Setup the playground for testing without itchat (avoid the need to login)

\ 弄出個 msg 來供 function test 測試用，而無須 itchat 連線。

    <accept>
    <py>
    def msg():
        pass
    def _():
        pass
    msg.user = _    
    msg.user.send = str # 吃掉 argument 
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
    </py> to msg
    </accept> dictate
    \ Introduce peforth value msg to peforth global 
    msg __main__ :: peforth.projectk.msg=pop(1)

    \ 應用例
    
    __main__ :> predict(msg) . cr
    __main__ :: console(msg,".s")

    \ 瞭解這個虛擬的 msg 
    
    Examine> msg . cr
    <function compyle_anonymous.<locals>.msg at 0x0000020FADBAF400>
    
    Examine> msg (see)
    {
        "__class__": "function",
        "__module__": "peforth.projectk",
        "__doc__": null,
        "user": {
            "__class__": "function",
            "__module__": "peforth.projectk",
            "__doc__": null,
            "send": {
                "__class__": "builtin_function_or_method",
                "__module__": "builtins",
                "__doc__": "print(value, ..., sep=' ', end='\\n', file=sys.stdout, flush=False)\n\nPrints the values to a stream, or to sys.stdout by default.\nOptional keyword arguments:\nfile:  a file-like object (stream); defaults to the current sys.stdout.\nsep:   string inserted between values, default a space.\nend:   string appended after the last value, default a newline.\nflush: whether to forcibly flush the stream."
            },
            "NickName": "A believer",
            "verify": {
                "__class__": "function",
                "__module__": "peforth.projectk",
                "__doc__": null
            }
        },
        "isAt": true,
        "fileName": "20171222153010.jpg",
        "type": "fil",
        "download": {
            "__class__": "function",
            "__module__": "peforth.projectk",
            "__doc__": null
        },
        "text": "Message text from the WeChat cloud",
        "Text": "Message text from the WeChat cloud"
    }

\ itchat robot toolkit 由遠端灌過來給 robot 執行的程式集
\ Ynote: Itchat Robot Toolkit 在這兒集中管理

    \ 主程式裡要提供以下常數與變數的 placeholder
    \ __main__ :> chatroom constant chatroom // ( -- text ) The working chatroom NickName
    \ __main__ :> nextDelay constant nextDelay // ( -- int ) Anti-robot delay time
    \ none value msg

    import time constant time // ( -- module )
    cr time :> ctime() . cr \ print recent time on Robot PC when making this setting
    
    \ 到了 runtime 憑 msg.user.NickName 才知道 focused chatroom 是那個，因此 msg
    \ 動態地要用到。FORTH value msg 在 console() 臨時準備好，到了這裡時已經
    \ available 了。
    
    \ get itchat module object
    py> sys.modules['itchat'] constant itchat // ( -- module ) WeChat automation
    
    \ get PIL graph tool
    import PIL.ImageGrab constant im // ( -- module ) PIL.ImageGrab

    \ @Damion
    \ itchat :> search_chatrooms(pop())[0].nickName . cr
    \ 
    \ __main__ :> chatroom ( NickName of the focused chatroom  )
    \ itchat :> search_chatrooms(pop()) constant chatrooms 
    \ chatrooms count ?dup [if] dup [for] 
    \     dup t@ - ( COUNT i ) . space ( COUNT ) 
    \ [next] drop [then]
    \ 
    \ itchat :> search_chatrooms(pop())[0] constant focusedChatroom // ( -- obj ) focused chatroom object
    
    : check // ( -- ) Get robot pc desktop screenshot
        cr time :> ctime() . cr \ print the recent time on the robot pc
        im :: grab().save("1.jpg") \ capture screenshot 
        nextDelay time :: sleep(pop()) \ anti-robot delay before every send()
        msg :> user.send("@img@1.jpg") \ send to chatroom 
        . cr ; \ shows the responsed message

    : getfile // ( "pathname" -- ) Get source code for debugging
        py> str(pop()).strip() \ trim pathname 
        s" @fil@" swap + \ command string 
        cr time :> ctime() . space s" getfile: " . dup . cr
        nextDelay time :: sleep(pop()) \ anti-robot delay before every send()
        msg :> user.send(pop()) \ send to chatroom so everybody gets it
        . cr ; \ shows the responsed message
        /// In case source code were modified on the robot pc.
'''
