#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# VotaBot, simple telegram bot to create polls in spanish
# Copyright (C) 2015 Manuel Pol manuel.pol@gmail.com
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
"""

import logging
import config
from telegram import Updater, ReplyKeyboardMarkup, ReplyKeyboardHide, Emoji

# Enable Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

# Init poll data dict
config.act = {}


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Bot activation message."""
    bot.sendMessage(chat_id=update.message.chat_id, text="Bot de votaciones.")


def newpoll(bot, update, args):
    """Create the new poll and save the question"""
    chat_id = update.message.chat_id
    if chat_id not in config.act:
        if args:
            config.act[chat_id] = {}
            config.act[chat_id]['quo'] = ' '.join(args)
            config.act[chat_id]['act'] = False
            config.act[chat_id]['resp'] = {}
            bot.sendMessage(chat_id=chat_id,
                            text="Ahora añade posibles respuestas con el"
                            " formato /respuesta texto.")
            bot.sendMessage(chat_id=chat_id,
                            text="Cuando hayas terminado inicia la votación"
                            " con /iniciarvotacion.")
        else:
            bot.sendMessage(chat_id=chat_id,
                            text="Debes indicar la pregunta con el"
                            " formato /nuevavotacion pregunta.")
    else:
        bot.sendMessage(chat_id=chat_id,
                        text="Ya has iniciado una votación.")


def response(bot, update, args):
    """Add responses to poll"""
    chat_id = update.message.chat_id
    if chat_id in config.act:
        if not config.act[chat_id]['act']:
            if args:
                config.act[chat_id]['resp'][' '.join(args)] = 0
                lresp = '\n- '.join(config.act[chat_id]['resp'])
                bot.sendMessage(chat_id=chat_id,
                                text="Posibles respuestas:\n- " + lresp)
            else:
                bot.sendMessage(chat_id=chat_id,
                                text="Debes indicar la posible respuesta con"
                                " el formato /respuesta texto.")
        else:
            bot.sendMessage(chat_id=chat_id,
                            text="Ya has iniciado la votación."
                            " No puedes añadir más respuestas.")
    else:
        bot.sendMessage(chat_id=chat_id,
                        text="Debes crear una votación primero"
                        " con el formato /nuevavotacion pregunta.")


def initpoll(bot, update):
    """Start the poll"""
    chat_id = update.message.chat_id
    if chat_id in config.act:
        if not config.act[chat_id]['act']:
            if config.act[chat_id]['resp']:
                config.act[chat_id]['act'] = True
                custom_keyboard = [config.act[chat_id]['resp'].keys()]
                reply_markup = ReplyKeyboardMarkup(custom_keyboard,
                                                   resize_keyboard=True,
                                                   one_time_keyboard=True)
                bot.sendMessage(chat_id=chat_id,
                                text="Iniciando votación, elige una opción.",
                                reply_markup=reply_markup)
                bot.sendMessage(chat_id=chat_id,
                                text=config.act[chat_id]['quo'])
            else:
                bot.sendMessage(chat_id=chat_id,
                                text="Primero añade posibles respuestas con el"
                                " formato /respuesta texto.")
        else:
            bot.sendMessage(chat_id=chat_id,
                            text="Ya hay una votación en curso.")
    else:
        bot.sendMessage(chat_id=chat_id,
                        text="Debes crear una votación primero"
                        " con el formato /nuevavotacion pregunta.")


def receiver(bot, update):
    """Listen non command replys to bot with a valid poll response"""
    chat_id = update.message.chat_id
    text = update.message.text
    if chat_id in config.act:
        if config.act[chat_id]['act']:
            if text in config.act[chat_id]['resp']:
                config.act[chat_id]['resp'][text] += 1

                sortres = [(v, k) for k, v in
                           config.act[chat_id]['resp'].iteritems()]
                sortres.sort(reverse=True)
                ftext = "Resultado temporal:"
                for val, key in sortres:
                    ftext += ("\n%s: %d" % (key, val))

                reply_markup = ReplyKeyboardHide(selective=True)
                bot.sendMessage(chat_id=chat_id,
                                text=ftext,
                                reply_to_message_id=update.message.message_id,
                                reply_markup=reply_markup)


def endpoll(bot, update):
    """Ends poll and show results. Delete all data of poll"""
    chat_id = update.message.chat_id
    if chat_id in config.act:
        if config.act[chat_id]['act']:
            sortres = [(v, k) for k, v in
                       config.act[chat_id]['resp'].iteritems()]
            sortres.sort(reverse=True)
            ftext = config.act[chat_id]['quo'] + "\n"
            for val, key in sortres:
                ftext += ("\n%s: %d" % (key, val))

            reply_markup = ReplyKeyboardHide()
            bot.sendMessage(chat_id=chat_id,
                            # text=Emoji.BAR_CHART + " " + ftext,
                            text=Emoji.BAR_CHART +
                            ftext.encode('utf-8').strip(),
                            reply_markup=reply_markup)

            config.act.pop(chat_id, None)
        else:
            bot.sendMessage(chat_id=chat_id,
                            text="No hay ninguna votación en curso.")
    else:
        bot.sendMessage(chat_id=chat_id,
                        text="No hay ninguna votación en curso.")


def unknown(bot, update):
    """Message to unknown commands"""
    bot.sendMessage(chat_id=update.message.chat_id, text="No entiendo.")


def main():
    """Main program"""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token='KEY')

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.addTelegramCommandHandler('start', start)
    dispatcher.addTelegramCommandHandler('nuevavotacion', newpoll)
    dispatcher.addTelegramCommandHandler('respuesta', response)
    dispatcher.addTelegramCommandHandler('iniciovotacion', initpoll)
    dispatcher.addTelegramCommandHandler('finvotacion', endpoll)
    dispatcher.addUnknownTelegramCommandHandler(unknown)

    # on noncommand i.e message
    dispatcher.addTelegramMessageHandler(receiver)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
