######################################################
# PLEASE CHANGE FOLLOWING CONFIGS ####################
Twitch_Channel          = 'target_channel_name'

Trans_Username          = 'trans_user_name'
Trans_OAUTH             = 'oauth_for_trans_user'

#######################################################
# OPTIONAL CONFIGS ####################################
Trans_TextColor         = 'GoldenRod'
# Blue, Coral, DodgerBlue, SpringGreen, YellowGreen, Green, OrangeRed, Red, GoldenRod, HotPink, CadetBlue, SeaGreen, Chocolate, BlueViolet, and Firebrick

lang_TransToHome        = 'en' #language it should translate to
lang_HomeToOther        = 'ja' #language from which it should translate

Show_ByName             = True
Show_ByLang             = True

# If you want a custom message at end of message type it here, if not set Custom_Message_Enabled to False
Is_Custom_Message_Enabled  = True
Custom_Message          = 'Translation Bot by Sayonari'

# In case you want only one language translated set Read_Only_One => true and ad lang into Read_Only_Lang
Read_Only_Specific_Lang = True
Read_Only_Langs          = ["ja"]

# Specific Translation Settings
Specific_Trans_Command      = ':'
Is_Specific_Trans_Disabled  = True

# Ignore Settings
Ignore_Lang             = ['']
Ignore_Users            = ['Nightbot', 'StreamElements', 'SoundAlerts']
Ignore_Line             = ['http', '888', '８８８', '...']
Delete_Words            = []

# Any emvironment, set it to `True`, then text will be read by TTS voice!
# TTS_In:User Input Text, TTS_Out:Bot Output Text
TTS_In                  = True
TTS_Out                 = True
TTS_Kind                = "gTTS" # You can choice "CeVIO" if you want to use CeVIO as TTS.
# CeVIO_Cast            = "さとうささら" # When you are using CeVIO, you must set voice cast name.

# if you make TTS for only few lang, please add langID in the list
# for example, ['ja'] means Japanese only, ['ko','en'] means Korean and English are TTS!
ReadOnlyTheseLang       = []

# Select the translate engine ('deepl' or 'google')
Translator              = 'google'

# Use Google Apps Script for tlanslating
# e.g.) GAS_URL         = 'https://script.google.com/macros/s/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/exec'
GAS_URL                 = ''

# Enter the suffix of the Google Translate URL you normally use.
# Example: translate.google.co.jp -> 'co.jp'
#          translate.google.com   -> 'com'
GoogleTranslate_suffix  = 'co.jp'

# If you meet any bugs, You can check some error message using Debug mode (Debug = True)
Debug                   = False
