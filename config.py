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

# set the read speed: 2.0 means 2 times faster! 
ReadSpeed               = 1.7

# if you make TTS for only few lang, please add langID in the list
# for example, ['ja'] means Japanese only, ['ko','en'] means Korean and English are TTS!
ReadOnlyTheseLang       = []

# If you meet any bugs, You can check some error message using Debug mode (Debug = True)
Debug                   = False
