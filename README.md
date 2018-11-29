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

# config.txt
```
######################################################
# PLEASE CHANGE FOLLOWING CONFIGS ####################
Twitch_Channel          = xxx_target_channel_name_xxx

Trans_Username          = xxx_trans_user_name_xxx
Trans_OAUTH             = xxxx_oauth_for_trans_user_xxxx

#######################################################
# OPTIONAL CONFIGS ####################################
lang_TransToHome        = ja
lang_HomeToOther        = en

Ignore_Users            = Nightbot, BikuBikuTest
Ignore_Line             = http, BikuBikuTest
Delete_Words            = saatanNooBow, BikuBikuTest

# Any emvironment, set it to `True`, then text will be read by TTS voice!
gTTS                    = True
```

| Option| Description |
| -- | -- |
| Twitch_Channel | The target chat room for translation. |
| Trans_Username | username for translation |
| Trans_OAUTH | Get key for Trans_Username at https://twitchapps.com/tmi/ |
| lang_TransToHome | If set it to [`ja`], all texts will be translated to the JAPANESE! |
| lang_HomeToOther | If set it to [`en`], the language in [`lang_TransToHome`] is trans to [`en`]. |
| Ignore_Users | You can set some users : [Nightbot, BikuBikuTest, someotheruser, ...] |
| Ignore_Line | If the words are in message, the message will be ignored.|
| Delete_Words | The words will be removed from message. |
| gTTS | Any emvironment, text will be read by TTS voice! |

# memo
## support language (google translator)
https://cloud.google.com/translate/docs/languages

# Developer Info.
|Title | Automatic Translator for Twitch Chat (Next Generation) |
|Developer | husband_sayonari_omega
|github | https://github.com/sayonari/twitchTransFreeNext |
| mail | sayonari@gmail.com |