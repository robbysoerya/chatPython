from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from ApiKey import *
from sys import stdout
from sys import stdin
from random import randrange
from random import randint

import os
import sys
import base64
import rsa
import platform

OS = platform.system()
interupt = ""
pnconfig = PNConfiguration()
pubnub = PubNub(pnconfig)

def main():

	global channel
	global user_name
	global uuid

	if OS == "Linux":
		os.system("clear")
	else :
		os.system("clrscr")

	stdout.write("Enter your room name: ")
	stdout.flush()
	channel = raw_input()

	stdout.write("Enter your group name (opsional): " )
	stdout.flush()
	grouproom = raw_input()

	stdout.write("Enter your nickname: ")
	stdout.flush()
	uuid = raw_input()

	pnconfig.subscribe_key = SubKey()
	pnconfig.publish_key = PublishKey()
	pnconfig.uuid = '{}-{}'.format(uuid,randint(000,999))
	pnconfig.secret_key = SecretKey()
	pnconfig.ssl = True
	user_name = pnconfig.uuid
	stdout.write("\nHello {}. Welcome to {} chatroom".format(user_name, channel))
	stdout.flush()

	pubnub.add_listener(MySubscribeCallback())

	if grouproom == "" :
		pubnub.subscribe().channels(channel).with_presence().execute()
	else :
		pubnub.subscribe().channel_groups(grouproom).channels(channel).with_presence().execute()

	while True:
		get_input()

def history_callback(result,status):
    try:
    	for i in range(0,len(result.messages)):
        	res = result.messages[i]
        	msg = res.entry['message']
        	nick = res.entry['nickname']
        	stdout.write("{} : {}".format(nick,rsa.decrypt(msg)))
       		stdout.write('\n')
		stdout.flush()
    except:

	stdout.write("History empty")
	stdout.flush()

def my_publish_callback(envelope, status):

    if not status.is_error():
        pass
    else:
        print("\nMessage cant be send")

def get_input():
	global msg
	stdout.write("\n")
	stdout.flush()
        msg = raw_input()

	try :
		global message
        	message = rsa.encrypt(msg,rsa.key())

	except :
		stdout.write("Text too large")
		stdout.flush()
		get_input()

        if msg != "":
            decmsg = rsa.decrypt(message)

            if './history' in decmsg[:9]:
                pubnub.history().channel(channel).async(history_callback)

            if './sendfiles to' in decmsg[:14]:
                decdata = rsa.decrypt(message)
                basename = decdata.rsplit(' ',1)[1]
                sendfile = open(basename,'rb').read()
                msg_object = dict(user_name=user_name, basename=basename, file=rsa.encrypt(sendfile,rsa.key()), message=message)
                pubnub.publish().should_store(True).channel(channel).message(msg_object).async(my_publish_callback)
                stdout.write('File send successfull')
		stdout.flush()

            else:
                msg_object = dict(user_name=user_name, message=message)
                pubnub.publish().should_store(True).channel(channel).message(msg_object).async(my_publish_callback)

            if decmsg[:12] in ['./list_users']:
                pubnub.here_now().channels(channel).include_uuids(True).include_state(True).async(list_user)

            if decmsg[:5] in ['./bye']:
                pubnub.unsubscribe_all()
                print("\nThank you for using our chat services")
                sys.exit()

            if decmsg[:13] in ['./add_channel']:
                new_chan = raw_input("Enter your new channel: ")
                grup = raw_input("Enter your group channel: ")
                pubnub.grant().channels(new_chan).channel_groups(grup).read(True).write(True).manage(True).sync()
                pubnub.add_channel_to_channel_group().channels(new_chan).channel_group(grup).sync()
                print("Channel created successfull")

            if decmsg[:15] in ['./list_channels']:
                grup = raw_input("Enter group you want to see channel: ")
                pubnub.list_channels_in_channel_group().channel_group(grup).async(list_channel)

def list_channel(result, status):
	print(result)

def list_user(result, status):
    print("List users online")
    print("-----------------")
    if status.is_error():
		return
    for channel_data in result.channels:
		print("Channel: %s" % channel_data.channel_name)
		print("Total: %s \n" % channel_data.occupancy)
    for occupant in channel_data.occupants:
		print("Nickname : %s \n" % (occupant.uuid))
    print("-----------------")

class MySubscribeCallback(SubscribeCallback):

    def presence(self, pubnub, presence):
        if presence.event == "join":
            print("{} joining room\n".format(presence.uuid))
        elif presence.event == "leave":
            print("\n{} leaving room\n".format(presence.uuid))

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            print("\nNetwork Disconnect")
        elif status.category == PNStatusCategory.PNConnectedCategory:
            pass
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print("\nNetwork Reconnect")
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass

    def message(self, pubnub, message):

        decrypt = rsa.decrypt(message.message['message'])
	dictfunctions = ['./list_users','./bye','./list_channels','./add_channel','./sendfiles to']
        if message.message['user_name'] != user_name:
		if decrypt not in dictfunctions:
			if './whisper to' not in decrypt[:12]:
				if './sendfiles to' not in decrypt[:14]:
					interup = "\033[A\033[K"
					stdout.write("\r{}: {}\n".format(message.message['user_name'], decrypt))
					stdout.flush()
		if './whisper to' in decrypt[:12]:
                	if user_name in decrypt:
  	                  	pesan = decrypt.replace(user_name,'')
        	          	print("{}: [PM From: {}]{}".format(message.message['user_name'], message.message['user_name'], pesan[12:]))

		if './sendfiles to' in decrypt[:14]:
			if user_name in decrypt:
                    		try:
                        		gen = str(randint(0,999))
                        		decfile = rsa.decrypt(message.message['file'])
                        		basename = message.message['basename']
                        		print 'File : ',basename
                        		open(basename,'wb').write(decfile)
                        		print "You received new file"
                    		except:
                        		print "Error not occured"

if __name__ == "__main__":
	main()
