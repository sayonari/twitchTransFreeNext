# twitchTransFreeNext
Next Generation of twitchTransFree!!!!

# USAGE
1. rewrite `config.txt`
2. double-click `twitchTransFN.exe`

That's all!

# I support my wife 24/7 :-) 
This software is made for my wife!  
http://twitch.tv/saatan_pion/  
If you are satisfied by this software, please watch my wife's stream! We are waiting for comming you! and subscribe! donation!

# Please link from your page!
プログラム使うときには，twitchページからリンクを張ってくれたら嬉しいです！（強制ではないです）

さぁたんチャンネルと，翻訳ちゃんのページにリンクを貼っていただけると良いですが，紹介文は各自で考えてくださいρ

[example]  
Twitch: saatan  
http://twitch.tv/saatan_pion/ 

Softwware: twitchTransFreeNext  
https://github.com/sayonari/twitchTransFreeNext

紹介用の絵も頂いちゃいました．使ってください．  
![trans_anomon](https://user-images.githubusercontent.com/16011609/49361210-c1f5ef80-f71e-11e8-8cff-6fd760e8738a.png)  
Painted by anomon  
https://www.twitch.tv/anomomm

# config.txt
```
######################################################
# PLEASE CHANGE FOLLOWING CONFIGS ####################
Twitch_Channel          = xxx_target_channel_name_xxx

Trans_Username          = xxx_trans_user_name_xxx
Trans_OAUTH             = xxxx_oauth_for_trans_user_xxxx

#######################################################
# OPTIONAL CONFIGS ####################################
Trans_TextColor         = GoldenRod
# Blue, Coral, DodgerBlue, SpringGreen, YellowGreen, Green, OrangeRed, Red, GoldenRod, HotPink, CadetBlue, SeaGreen, Chocolate, BlueViolet, and Firebrick

lang_TransToHome        = ja
lang_HomeToOther        = en

Ignore_Users            = Nightbot, BikuBikuTest
Ignore_Line             = http, BikuBikuTest
Delete_Words            = saatanNooBow, BikuBikuTest

# Any emvironment, set it to `True`, then text will be read by TTS voice!
gTTS                    = True


#######################################################
# For TLANSLATE ROOM CONFIGS ##########################
##### channelID <- owner_id, roomUUID <- _id ##########
# channelID               = 000000000
# roomUUID                = 00000000-0000-0000-0000-000000000000
```

| Option| Description |
| -- | -- |
| Twitch_Channel | The target chat room for translation. |
| Trans_Username | username for translation |
| Trans_OAUTH | Get key for Trans_Username at https://twitchapps.com/tmi/ |
| Trans_TextColor  | You can change text color of translator. |
| lang_TransToHome | If set it to [`ja`], all texts will be translated to the JAPANESE! |
| lang_HomeToOther | If set it to [`en`], the language in [`lang_TransToHome`] is trans to [`en`]. |
| Ignore_Users | You can set some users : [Nightbot, BikuBikuTest, someotheruser, ...] |
| Ignore_Line | If the words are in message, the message will be ignored.|
| Delete_Words | The words will be removed from message. |
| gTTS | Any emvironment, text will be read by TTS voice! |
| channelID | (with roomUUID) translated text is send to chat-room |
| roomUUID | (with channelID) translated text is send to chat-room |

# memo
## support language (google translator)
https://cloud.google.com/translate/docs/languages

# secret functions
## choose trans destination language (for one text)
At the time of translation, you can select the target language like `en:` at the beginning of the sentence.  
Example) ru: Hello -> привет там

## translated text is send to chat-room
If you want to send the translated text to chat-room in your channel, please read this section.
You can get more information about [chat-room] following blogs.
https://blog.twitch.tv/bring-your-community-together-with-rooms-ad60cab1af0a

1. Make chat-room in your channel.
2. By using `roomUUID_checker.exe`, get `channelID(owner_id)` and `roomUUID(_id)`
3. Set it to config.txt

NOTE: When rewriting config.txt, please delete the `#` mark at the beginning of each setting value!


# Thanks
Thanks to Pioneers!
The developer of ...
- Google
- googletrans by ssut
    - https://github.com/ssut/py-googletrans
- gtts by pndurette
    - https://github.com/pndurette/gTTS
- playsound by TaylorSMarks
    - https://github.com/TaylorSMarks/playsound
- python_twitch_irc by jspaulsen
    - https://github.com/jspaulsen/python-twitch-irc

and Fix some bugs ...
- gTTS-token by Boudewijn26
- googletrans/gtoken by michaeldegroot/cats-blender-plugin

# Developer Info.

| Title | Automatic Translator for Twitch Chat (Next Generation) |
|--|--|
| Developer | husband_sayonari_omega |
|github | https://github.com/sayonari/twitchTransFreeNext |
| mail | sayonari@gmail.com |
| Twitter | [sayonari](https://twitter.com/sayonari) |