# twitchTransFreeNext
Next Generation of twitchTransFree!!!!

# USAGE
1. rewrite `config.py`
2. double-click `twitchTransFN.exe`

That's all!

NOTE: The file type of config was chaged from .txt to .py!

# I support my wife 24/7 :-) 
This software is made for my wife!  
http://twitch.tv/saatan_pion/  
If you are satisfied by this software, please watch my wife's stream! We are waiting for comming you! and subscribe! donation!

# We welcome your DONATE!!!!
Donation is possible from the following link!  
もし便利だなと思ったら．以下からDONATEしてください．開発中に食べるお菓子代にします！！！  
https://twitch.streamlabs.com/saatan_pion#/

# Please link from your page!
プログラム使うときには，twitchページからリンクを張ってくれたら嬉しいです！（強制ではないです）

さぁたんチャンネルと，翻訳ちゃんのページにリンクを貼っていただけると良いですが，紹介文は各自で考えてくださいρ

[example]  
Twitch: saatan  
http://twitch.tv/saatan_pion/ 

Software: twitchTransFreeNext  
https://github.com/sayonari/twitchTransFreeNext

紹介用の絵も頂いちゃいました．使ってください．  
![trans_anomon](https://user-images.githubusercontent.com/16011609/49361210-c1f5ef80-f71e-11e8-8cff-6fd760e8738a.png)  
Painted by anomon  
https://www.twitch.tv/anomomm

# config.py
```python
######################################################
# PLEASE CHANGE FOLLOWING CONFIGS ####################
Twitch_Channel          = 'xxx_target_channel_name_xxx'

Trans_Username          = 'xxx_trans_user_name_xxx'
Trans_OAUTH             = 'xxxx_oauth_for_trans_user_xxxx'

#######################################################
# OPTIONAL CONFIGS ####################################
Trans_TextColor         = 'GoldenRod'
# Blue, Coral, DodgerBlue, SpringGreen, YellowGreen, Green, OrangeRed, Red, GoldenRod, HotPink, CadetBlue, SeaGreen, Chocolate, BlueViolet, and Firebrick

lang_TransToHome        = 'ja'
lang_HomeToOther        = 'en'

Show_ByName             = True
Show_ByLang             = True

Ignore_Lang             = ['']
Ignore_Users            = ['Nightbot', 'BikuBikuTest']
Ignore_Line             = ['http', 'BikuBikuTest', '888', '８８８']
Delete_Words            = ['saatanNooBow', 'BikuBikuTest']

# Any emvironment, set it to `True`, then text will be read by TTS voice!
# gTTS_In:User Input Text, gTTS_Out:Bot Output Text
gTTS_In                 = True
gTTS_Out                = True

# If you meet any bugs, You can check some error message using Debug mode (Debug = True)
Debug                   = False
```

| Option| Description |
| -- | -- |
| Twitch_Channel | The target chat room for translation. |
| Trans_Username | username for translation |
| Trans_OAUTH | Get key for Trans_Username at https://twitchapps.com/tmi/ |
| Trans_TextColor  | You can change text color of translator. |
| lang_TransToHome | If set it to [`ja`], all texts will be translated to the JAPANESE! |
| lang_HomeToOther | If set it to [`en`], the language in [`lang_TransToHome`] is trans to [`en`]. |
| Show_ByName | If it is set to `True`, user name is shown after translated text. |
| Show_ByLang | If it is set to `True`, the source language is shown after translated text. |
| Ignore_Lang | You can set some languages : [ja,en, ...] |
| Ignore_Users | You can set some users : [Nightbot, BikuBikuTest, someotheruser, ...] |
| Ignore_Line | If the words are in message, the message will be ignored.|
| Delete_Words | The words will be removed from message. |
| gTTS_In | Input text will be read by TTS voice! |
| gTTS_Out | Bot output text will be read by TTS voice! |
| Debug | You can check some error message using Debug mode (Debug = True)|


# memo
## support language (google translator)
https://cloud.google.com/translate/docs/languages

# secret functions
## choose trans destination language (for one text)
At the time of translation, you can select the target language like `en:` at the beginning of the sentence.  
Example) ru: Hello -> привет там

NOTE: When rewriting config.txt, please delete the `#` mark at the beginning of each setting value!

## command: (version)
`!ver`: print the software version.

`!sound xxxx`: play sound (xxxx.mp3), if you put sound data at sound folder.

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
- TwitchIO
    - https://github.com/TwitchIO/TwitchIO

# Developer Info.

| Title | Automatic Translator for Twitch Chat (Next Generation) |
|--|--|
| Developer | husband_sayonari_omega |
|github | https://github.com/sayonari/twitchTransFreeNext |
| mail | sayonari@gmail.com |
| Twitter | [sayonari](https://twitter.com/sayonari) |