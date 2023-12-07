######################################################
# PLEASE CHANGE FOLLOWING CONFIGS ####################
Twitch_Channel          = 'DdotB'

Trans_Username          = 'DeeBeeTTV'
#Trans_Username          = 'ddotb'
Trans_OAUTH             = 'oauth:mqnrbkcxpowouryog1gts78m9q15mj'
#Trans_OAUTH             = 'oauth:asrboztzet3ybctrrun47rnlfhhbs5'

#######################################################
# OPTIONAL CONFIGS ####################################
Trans_TextColor         = 'CadetBlue'
# Blue, Coral, DodgerBlue, SpringGreen, YellowGreen, Green, OrangeRed, Red, GoldenRod, HotPink, CadetBlue, SeaGreen, Chocolate, BlueViolet, and Firebrick

lang_TransToHome        = 'ja'
lang_HomeToOther        = 'en'

Show_ByName             = False
Show_ByLang             = True

Ignore_Lang             = ['']
Ignore_Users            = ['Nightbot', 'BikuBikuTest', 'halo_trans', 'streamelements', 'streamlabs', 'sery_bot', 'beaneyboobutler', 'ministerofforeignaffairs', 'PokemonCommunityGame']
Ignore_Line             = ['http', 'BikuBikuTest', '888', '８８８']
Delete_Words            = ['saatanNooBow', 'BikuBikuTest']

# Any emvironment, set it to `True`, then text will be read by TTS voice!
# TTS_In:User Input Text, TTS_Out:Bot Output Text
TTS_In                  = False
TTS_Out                 = True
TTS_Kind                = "gTTS" # You can choice "CeVIO" if you want to use CeVIO as TTS.
# CeVIO_Cast            = "さとうささら" # When you are using CeVIO, you must set voice cast name.
TTS_TextMaxLength		= 10
TTS_MessageForOmitting = "以下略"

# if you make TTS for only few lang, please add langID in the list
# for example, ['ja'] means Japanese only, ['ko','en'] means Korean and English are TTS!
ReadOnlyTheseLang       = []

# Select the translate engine ('deepl' or 'google')
Translator              = 'deepl'

# Use Google Apps Script for tlanslating
# e.g.) GAS_URL         = 'https://script.google.com/macros/s/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/exec'
GAS_URL                 = ''

# Enter the suffix of the Google Translate URL you normally use.
# Example: translate.google.co.jp -> 'co.jp'
#          translate.google.com   -> 'com'
GoogleTranslate_suffix  = 'co.jp'

# If you meet any bugs, You can check some error message using Debug mode (Debug = True)
Debug                   = False
