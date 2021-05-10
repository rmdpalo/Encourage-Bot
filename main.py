#python replit database methods for the module 
import replit
#imports secrets for repl in order to use .env variables
import os
#imports discord library
import discord
#imports requests which allows us to make http requests to fetch information from the API
import requests
#the API returns info in json so we have to import the json module 
import json
#imports the random module so we can get random messages from our encouragements
import random
#imports our database from repl
from replit import db
#import our webserver
from keep_alive import keep_alive

#creates an instance of a client
client = discord.Client()

#list of commands
commands_list = "```$commands - gives a list of commands.\n\n$encourage - responds with a quote.\n\n$newMsg (msg) - adds a new encouraging message.\n\n$list - shows the list of user entered encouraging messages.\n\n$delMsg (index #) - deletes the encouraging message at index #.\n\n$responding (true/false) - sets the auto response feature on or off.\n\n```"

#list of sad words
sad_words = [
    "sad", 
    "depressed", 
    "unhappy", 
    "angry", 
    "miserable", 
    "depressing", 
    "die", 
    "hopeless",
    "hate myself",
    ]

starter_encouragements = [
    "You got this!",
    "It's hard right now but you're strong.",
    "I love you.",
    "Hang in there.",
] 

if "responding" not in db.keys():
    db["responding"] = True

#helper function that allows us to get quotes from zenquotes.io
def get_quote():
    #we make a get http request to our api and store the response in a variable called response. the API endpoint goes inside the get function.
    response = requests.get("https://zenquotes.io/api/random")
    #we use the json module to convert json to a python object.
    json_data = json.loads(response.text)
    #this is the quote, this is just how its formatted in the API
    #q is quote key, a is author key.
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return(quote)

#helper func to add encouragements to db
def update_encouragements(encouraging_message):
    #checks if "encouragements is a key in our database"
    if "encouragements" in db.keys():
        #grabs the encouragements key and declares it into a variable
        encouragements = db["encouragements"]
        #appends/adds the encouraging_message into the database
        encouragements.append(encouraging_message)
        #saves our updated encouragements into the db.
        db["encouragements"] = encouragements
    #if it is not
    else:
        #initialize the encouragements key and add our first new encouraging message.
        db["encouragements"] = [encouraging_message]

#helper func to delete messages from db
def delete_encouragements(index):
    #declare our db as a var
    encouragements = db["encouragements"]
    #if our encouragements list is longer than the inputted index
    if len(encouragements) > index:
        #delete that index from our list
        del encouragements[index]
        #save updated list.
        db["encouragements"] = encouragements


#this is how you register an event 
#discord.py is an asynchronous library so it uses callbacks.

#this is what runs as soon as the bot is ready
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='out for you. $commands'))

#this function runs when a message is sent to the client
@client.event
async def on_message(message):
    #we don't want it to do anything if the message is from the bot.
    if message.author == client.user:
        return

    #makes it easier to call in a variable
    msg = message.content

    #responds with a list of commands and summary of what it does
    if msg.startswith('$commands'):
        await message.channel.send(commands_list)

    #calls our get_quote() function and responds with an encouraging/inspiring quote.
    if msg.startswith('$encourage'):
        quote = get_quote()
        await message.channel.send(quote)

    #add new encouragement
    if msg.startswith('$newMsg'): 
        #we want to add whatever text is after the command to be added to the db.
        #splits the message by the command and declares it into a var, we take the second index in the list we made.
        encouraging_message = msg.split("$newMsg ",1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("Added new encouragement: " + encouraging_message)

    #deletes encouragement
    if msg.startswith('$delMsg'):
        #encouragements as an empty list for now, we declare actual value later.
        encouragements = []
        if "encouragements" in db.keys():
            #the space after $delMsg is optional b/c we're converting to an int anyways.
            index = int(msg.split("$delMsg ",1) [1])
            delete_encouragements(index)
            encouragements = db["encouragements"]
        await message.channel.send(f"An entry was deleted.\nEncouragements: {encouragements}")

    if db["responding"]:
        #in order to have our encouragements draw from both our starters and the db
        options = starter_encouragements
        #check if encouragements has been initialized as a key.
        if "encouragements" in db.keys():
            #if so, add it to our options and call options in the random.choice function below.
            #allows us to get our data not JSON-encoded
            #the replit method here converts replits "ObservedList" to the regular list primitive data type. more info here: https://github.com/replit/replit-py/blob/fc47b96202667ca8a04827285a19e94912bdca29/docs/db_tutorial.rst
            db_encouragements = replit.database.to_primitive(db["encouragements"])
            options = options + db_encouragements

        #go through every word in sad_words and check if any of them are any of the words in msg
        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(options))

    if msg.startswith('$list'):
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = replit.database.to_primitive(db["encouragements"])
        await message.channel.send(f"Encouragements: {encouragements}")
    
    if msg.startswith('$responding'):
        #take the value by splitting from command
        value = msg.split("$responding ",1)[1]

        #if set to true => responding set to true
        if value.lower() == "true":
            db["responding"] = True
            await message.channel.send("Responding is on.")
        #anything else is assumed to be false
        else:
            db["responding"] = False
            await message.channel.send("Responding is off.")
        

#secret key for discord bot   
BOT_KEY = os.environ['BOT_KEY']

#call our keep_alive function
keep_alive()

#runs the bot
client.run(BOT_KEY)