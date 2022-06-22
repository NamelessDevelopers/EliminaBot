# Elimina Bot Privacy Policy

> This document explains how we use, process or store the data you(users) provide us.

## Messages

Right now, accessing the messages is not a privileged intent and all bots can be granted the `Read messages` permission.
However, after 31st August 2022, this will be made a privileged intent and thus bot developers will have to shift to slash commands. Also, the access to all messages will be removed in cases where the bot does not have any genuine reason for accessing those messages. 
Elimina is a bot that automatially deletes the messages sent by bots in the channels where the guild admins choose to toggle the bot.
The bot requires access to all the messages for that reason and no message content is stored or processed from our end, the message is simply deleted and never stored on our servers.

## Discord Data

The bot does not store any user ID or user related data however we do have to store the following data:
* Guild/Channel IDs: We need to store the channel IDs and the corresponding guild ID to keep a track of the channels which the bot has been toggled in.
* Bot IDs: For the `Ignore bot` feature we have, we need to store the IDs of the bot(s) that have been ignored in the guild.
* Messages: For the `snipe` feature, the messages are stored in the bot's cache for a minute after which it is automatically overwritten and thus never gets saved from our end.
* Media: The `snipe` feature is able to view deleted images as well. However, we do not store any user content and the images are not saved but we're simply displaying the image using the proxy URL that Discord API provides.

We do not plan to use or store any user data in the near future, and if we do so, this document will be updated before that. 
Elimina is a minimalistic bot with a simple yet effective purpose and we plan to keep it that way.
