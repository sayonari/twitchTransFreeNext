######################################################
# PLEASE CHANGE FOLLOWING CONFIGS ####################
Twitch_Channel          = 'target_channel_name'

Trans_Username          = 'trans_user_name'
Trans_OAUTH             = 'oauth_for_trans_user'

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
Ignore_WWW              = ['w', 'ｗ', 'W', 'Ｗ', 'ww', 'ｗｗ', 'WW', 'ＷＷ', 'www', 'ｗｗｗ', 'WWW', 'ＷＷＷ', '草']
Delete_Words            = ['saatanNooBow', 'BikuBikuTest']

# Any emvironment, set it to `True`, then text will be read by TTS voice!
# TTS_In:User Input Text, TTS_Out:Bot Output Text
TTS_In                  = True
TTS_Out                 = True
# TTS_Kind options: "gTTS" (Google TTS), "CeVIO" (CeVIO TTS), "EDGE" (Microsoft Edge TTS), "openai" (OpenAI TTS)
TTS_Kind                = "EDGE"
# CeVIO_Cast            = "さとうささら" # When you are using CeVIO, you must set voice cast name.
TTS_TextMaxLength       = 120
TTS_MessageForOmitting  = "以下略"

# TTS Username Settings
TTS_ReadUsername        = True                 # Whether to read username
TTS_SayWord             = " 说"                  # Connecting word between username and content, e.g.: "username says content"
TTS_SayWord_EN          = " says"               # Connecting word in English environment
TTS_SayWord_JA          = " さん、"              # Connecting word in Japanese environment
TTS_UsernameMaxLength   = 20                   # Maximum username length, truncated if exceeded

# Edge TTS Configuration
# You can modify the default voices for each language here, for example:
# EdgeTTS_Voice_ZhCN     = "zh-CN-YunxiNeural" # Chinese male voice
# EdgeTTS_Voice_En       = "en-US-GuyNeural"   # English male voice

# Set to True to display all available Edge TTS voices at startup
Debug_EdgeTTS_Voices    = False

# if you make TTS for only few lang, please add langID in the list
# for example, ['ja'] means Japanese only, ['ko','en'] means Korean and English are TTS!
ReadOnlyTheseLang       = []

# Select the translate engine ('deepl' or 'google' or 'openai')
Translator              = 'openai'

# Use Google Apps Script for tlanslating
# e.g.) GAS_URL         = 'https://script.google.com/macros/s/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/exec'
GAS_URL                 = ''

# Enter the suffix of the Google Translate URL you normally use.
# Example: translate.google.co.jp -> 'co.jp'
#          translate.google.com   -> 'com'
GoogleTranslate_suffix  = 'co.jp'

# If you meet any bugs, You can check some error message using Debug mode (Debug = True)
Debug                   = False

#OpenAI translate, and support custom url
OpenAI_URL = 'https://api.openai.com/v1/'
OpenAI_API_KEY = 'xx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
System_Prompt = 'You are a professional, authentic machine translation engine.'
Model = 'gpt-4o-mini'
# tts-1-hd, tts-1
TTS_Model = 'tts-1'
# alloy, echo, fable, onyx, nova, shimmer
TTS_Voice = 'alloy'

# proxy
# Proxy_URL = 'http://127.0.0.1:7897'
Proxy_URL = ''