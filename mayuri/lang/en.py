# auto-translated
lang_name = ' 🇬🇧 English'
text = {
	'select_lang': "Please select the language you want to use:",
	'language_changed': "Language successfully changed to {}". format(lang_name),
	'pm_me': "Contact me on PM.",
	'not_user': "That's not a user!",
	'added_to_sudo': "User {} has been added to SUDO",
	'removed_from_sudo': "User {} has been removed from SUDO",
	'sudo_ls': "My sudo list:",
	'user_is_sudo': "User {} is already in the sudo list!",
	'user_is_not_sudo': "User {} is not in the sudo list!",
	'no_sudo': "There is no user in the sudo list!",
	'helps': "Help",
	'this_plugin_help': "This is help for the plugin **{}**:\n",
	'back': "Back",
	'refreshing_admin': "Refreshing admin cache...",
	'search_zombies': "Searching for deleted accounts...",
	'no_zombies': "Clean group. no deleted accounts :)",
	'no_zombies_schedule': "Clear group. no deleted accounts :)\n\nNext cleanup on:\n{}",
	'found_zombies': "Found {} deleted accounts.\nCleaning up...",
	'zombies_cleaned': "Successfully cleaned {} account deleted",
	'zombies_cleaned_schedule': "Successfully cleaned {} account deleted\n\nNext cleanup on:\n{}",
	'admin': "AdminTools",
	'admin_help': """
This module is used to manage groups.
[Admin Tools]
> `/admincache`
Update admin list.
> `/approve`
Adding users to the whitelist.
> `/unapproved`
Remove users from the whitelist.> `/zombies`
Find and clean deleted accounts.
	""",
	'admin_refreshed': "Admin cache refreshed successfully.",
	'admin_approved_list': "List of whitelisted users in this group:",
	'admin_no_approved': "No whitelisted users in this group yet!",
	'admin_user_added_to_approve': "User {} has been added to the whitelist",
	'admin_user_removed_to_approve': "User {} has been removed from the whitelist",
	'admin_list_text': "**List Admins in This Group**\n",
	'HELP_STRINGS': """
You can use {} to execute this bot command.
Available **Main** commands:
  - /start: get the start message
  - /help: get all the help
	""",
	'stickers': "Stickers",
	'stickers_help': """
[Stickers]
> `/stickerid`
Get the id of the sticker that was replied to

> `/getsticker`
To get a reply sticker in the form of an image/video (png/webm)

> `/kang`
To steal the sticker.
	""",
	'your_stickerid': "Id of the sticker you replied to :\n{}",
	'must_reply_to_sticker': "You must reply to the sticker message to use this command!",
	'animated_not_supported': "Animated stickers not supported!",
	'use_whisely': "Use this feature wisely!\nPlease check the image below :)",
	'processing': "Processing...",
	'cannot_kang': "It can't be Kanged!",
	'creating_pack': "Creating Stickerpacks...",
	'cannot_create_pack': "There was an error creating the Stickerpack!",
	'show_pack': "View Stickerpack",
	'sticker_kanged': "Sticker successfully restrained.",
	'stickerpackinvalid': "Sticker does not come from Stickerpack created by this bot!",
	'notyourstickerpack': "Sticker does not come from your Stickerpack!",
	'stickerinvalid': "Unable to delete sticker, make sure it is in the stickerpack created via this bot!",
	'stickerdeleted': "Sticker removed from stickerpack successfully.",
	'notreplytosticker': "Reply to the sticker you want to remove from the stickerpack!",
	'blacklist': "Blacklist",
	'blacklist_help': """This module is used to prohibit the use of a word in the message.
[Word Blacklist]
> `/addbl <word> [<mode>] [<time>] [<reason>]`
Add words to the blacklist
example :
> `/addbl foo`
> `/addbl foo kick`
> `/addbl anu mute 12h`

> `/rmbl <word>`
Removes words from the blacklist
example :
> `/rmbl foo`

> `/blacklist`
Displays a list of words that are on the blacklist

[Mode]
Optional, the default mode is delete
- delete - ban
- kick - mute

[Time]
For mute and ban mode (Optional)
list of time units:
- s = seconds
- m = minutes
- h = hours
- d = day
	""",
	'blacklist_added': "<code>{}</code> Has been added to Blacklist with mode {}",
	'blacklist_duration': " and duration for {}",
	'blacklist_reason': ".\nReason: {}",
	'blacklist_deleted': "<code>{}</code> Successfully removed from blacklist!",
	'blacklist_not_found': "Blacklist with trigger <code>{}</code> not found!",
	'what_blacklist_to_remove': "What do you want to remove from the blacklist?",
	'blacklist_list': "List of blacklisted words in this Group:\n",
	'no_blacklist': "There are no blacklisted words in this group!",
	'muted': "Muted",
	'kicked': "Kicked",
	'banned': "banned",
	'blacklist_for': " during {}",
	'user_and_reason': "\nUser : {}\nReason :",
	'blacklist_said': " Says <code>{}</code>",
	'filters': "Filters",
	'filters_help': """
This module is used to create automatic reply for a word.
[Filters]
> `/filter <word> <reply`
Added new filters

> `/stop <word>`
Remove filters

> `/filters`
Get a list of active filters
	""",
	'filter_added': "Handler <code>{}</code> Has been added in {}",
	'filter_removed': "I will stop replying to <code>{}</code> in {}!",
	'filter_not_found': "<code>{}</code> Not an active filter!",
	'what_filter_to_remove': "What do you want to remove from the filter?",
	'filter_list': "List of filters in this Group:\n",
	'no_filter_found': "No filters in {}!",
	'blpack': "Stickerpack Blacklist",
	'blpack_help': """This module is used to prohibit the use of all stickers in a Stickerpack.
[Stickerpack Blacklist]
> `/addblpack [<mode>] [<time>] [<reason>]`
Added stickerpack to blacklist
example :
> `/addblpack`
> `/addblpack kick`
> `/addblpack mute 12h`

> `/rmblpack`
Remove stickerpack from blacklist
example :
> `/rmblpack`

> `/blpack`
Displays a list of stickerpacks that are on the blacklist

[Mode]
Optional, the default mode is delete
- delete - ban
- kick - mute

[Time]
For mute and ban mode (Optional)
list of time units:
- s = seconds
- m = minutes
- h = hours
-d = day
	""",
	'blpack_added': "Sticker Pack <code>{}</code> Has been added to Blacklist with {}",
	'blpack_deleted': "Sticker Pack <code>{}</code> Removed from Blacklist successfully!",
	'blpack_not_found': "Sticker pack with name <code>{}</code> was not found in the blacklist!",
	'blpack_list': "List of Blacklisted Sticker Packs in this Group:\n",
	'no_blpack': "There are no blacklisted sticker packs in this group!",
	'blpack_send': "Sending stickers in the <code>{}</code> pack",
	'blsticker': "Sticker Blacklist",
	'blsticker_help': """This module is used to prohibit the use of a sticker.
[Sticker Blacklist]
> `/addblsticker [<mode>] [<time>] [<reason>]`
Added stickerpack to blacklist
example :
> `/addblsticker`
> `/addblsticker kick`
> `/addblsticker mute 12h`

> `/rmblsticker`
Remove sticker from blacklist
example :
> `/rmblsticker`

> `/blsticker`
Displays a list of stickers that are on the blacklist

[Mode]
Optional, the default mode is delete
- delete - ban
- kick - mute

[Time]
For mute and ban mode (Optional)
list of time units:
- s = seconds
- m = minutes
- h = hours
-d = day
	""",
	'blsticker_added': "Sticker <code>{}</code> Has been added to Blacklist with {}",
	'blsticker_deleted': "Sticker <code>{}</code> Removed from Blacklist successfully!",
	'blsticker_not_found': "Sticker with id <code>{}</code> not found in blacklist!",
	'blsticker_list': "List of blacklisted stickers in this group:\n",
	'no_blsticker': "There are no blacklisted stickers in this group!",
	'blsticker_send': "Sending <code>{}</code> stickers",
	'disable': "Disable Commands",
	'disable_help': """This module is used to disable the use of commands within the group
[Disable Commands]
> `/disable <command>`
To disable command
example :
> `/disable adminlist`

> `/enable <command>`
To reactivate commands that have been deactivated
example :
> `/enable adminlist`

> `/disabled`
To display a list of commands that have been disabled

> `/disableable`
To display a list of commands that can be disabled
	""",
	'cmd_not_found': "Command {} not available!",
	'cmd_disabled': "Command {} disabled successfully!",
	'what_cmd_to_disable': "What command do you want to disable?",
	'cmd_enabled': "Command {} enabled successfully!",
	'what_cmd_to_enable': "What command to enable?",
	'disabled_list': "List of Commands disabled in this group:\n",
	'no_cmd_disabled': "No Commands disabled in this group!",
	'can_disabled': "List of Commands that can be disabled:\n",
	'cmd_already_disabled': "Command already in disabled list!",
	'cmd_not_disabled': "Command not in disabled list!",
	'need_user_id': "Give a username or user id!",
	'why_gban_owner': "Why should I gban my master?",
	'why_gban_sudo': "Why should I gban my sudo?",
	'why_gmute_owner': "Why should I gmute my master?",
	'why_gmute_sudo': "Why should I gmute my sudo?",
	'why_gdmute_owner': "Why should I gdmute my master?",
	'why_gdmute_sudo': "Why should I gdmute my sudo?",
	'why_ungdmute_sudo': "Only Owners can ungdmute sudo!",
	'gbanned': "User {} has been banned globally",
	'gmuted': 'User {} has been muted globally',
	'gdmuted': 'User {} has been dmuted globally',
	'ungbanned': "User {} has been globally unbanned",
	'ungmuted': 'User {} has been globally unmuted',
	'ungdmuted': 'User {} has been globally undmuted',
	'user_in_gban': 'User {} is in the global banned list and has been banned from the group!',
	'user_in_gmute': 'User {} is on the global mute list and has been muted!',
	'restrict_time_left': "\nTime remaining: {}",
	'new_gban': "#GBAN\n**New Global Ban**",
	'new_gmute': "#GMUTE\n**New Global Mute**",
	'new_gdmute': "#GDMUTE\n**New Global Delete Mute**",
	'new_ungban': "#UNGBAN\n**Global Release New Tires**",
	'new_ungmute': "#UNGMUTE\n**Release New Global Mute**",
	'new_ungdmute': "#UNGDMUTE\n**Unleash New Global Delete Mute**",
	'geting_info': "Getting info...",
	'infouser_info': "**User Information**",
	'infouser_id': "\nID: `{}`",
	'infouser_firstname': "\nFirstname: {}",
	'infouser_lastname': "\nLastname: {}",
	'infouser_name': "\nUsername: @{}",
	'infouser_link': "\nLink: [link](tg://user?id={})",
	'infouser_in_gban': "\n\nUser is in the gban list.",
	'infouser_in_gmute': "\n\nUser is in the gmute list.",
	'infouser_in_gdmute': "\n\nUser is in the gdmute list.",
	'infouser_date': "\nDate: {}",
	'infouser_sudo': "\nSudo: {}",
	'infouser_duration': "\nDuration: {}",
	'infouser_is_channel': "Please reply to non-channel users!",
	'cas_log': "#ANTI_SPAM\nANTI_SPAM New Global Ban.\nChat: @{}\nUser: {}\nUser ID: `{}`\nReason: {}",
	'cas_msg': "User {} has been banned globally\nReason: {}\n\nPowered by: Combot Anti Spam API",
	'welcome_set': "Welcome message set up successfully",
	'not_forum': "This group is not a forum. Please turn on the topic option first!",
	'welcome_not_set': "Welcome message is not set in this group yet!",
	'thread_id_set': "Successful.\nAll welcome messages will be sent to this thread.",
	'welcome_enabled': "Welcome message enabled!",
	'welcome_disabled': "Welcome message disabled!",
	'welcome_settings': "**Welcome Message Settings:**\nActive: {}\nService Message Cleaner: {}\nForum Thread ID: `{}`\nCaptcha: {}\nCaptcha timeout: {}\nVerify text: {}",
	'default-welcome': "Welcome {first} to the {chatname} group!",
	'verif_text': "Click here to verify!",
	'verify_id_not_found': "Verify id not found!",
	'not_your_captcha': "ID verify and User ID do not match!",
	'captcha_enabled': "Captcha is enabled.",
	'captcha_disabled': "Captcha is disabled.",
	'captcha_timeout_format_invalid': "Timeout format is valid!",
	'captcha_timeout_set': "Captcha timeout successfully set to {}.",
	'generate_captcha': "Generating captcha...",
	'regenerate_captcha': "Re-generating captcha...",
	'verify_text_set': "Verify button text has been set to `{}`.",
	'translation_not_found': "Translation `{}` could not be found!",
}
