import os
import requests

from flask import Flask, jsonify, render_template, request, redirect, session
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "my secret key"
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

usersLogged = []
channels = []
channel_messages = dict()

@app.route("/")
def index():
    if not session.get("logged"):
        return render_template("index.html")
    elif ((session.get("current-channel") != None) and (session.get("current-channel") in channels)):
        route = "/channel/" + session.get("current-channel")
        return redirect(route)
    else:
        return redirect("/home")



@app.route("/home", methods=["POST", "GET"])
def signin():

    session["current-channel"] = None

    if request.method == "POST":
        session.clear()
        username = request.form.get("username")
        if username in usersLogged:
            return render_template("error.html", message="User already exists")
        else:
            usersLogged.append(username)
            session["username"] = username
            session["logged"] = True
            session.permanent = True
            return render_template("channels.html", channels=channels, user=session.get("username"))

    elif request.method =="GET":
        if not session.get("logged"):
            return redirect("/")
        else:
            return render_template("channels.html", channels=channels, user=session.get("username") )

@app.route("/log-out")
def logout():
    try:
        usersLogged.remove(session['username'])
    except:
        pass
    session.clear()

    return redirect("/")

@app.route("/success", methods=["POST"])
def createChannel():
    channel = request.form.get("channel_name")
    if channel in channels:
        return render_template("error",message="Channel already exists")
    channels.append(channel)
    channel_messages[channel] = []
    session["current-channel"] = channel
    return redirect("/channel" + "/" + channel)

@app.route("/channel/<channel_name>")
def enter_channel(channel_name):
    session["current-channel"] = channel_name
    return render_template("channel.html", channel_name=channel_name, messages=channel_messages[channel_name], channels=channels)

@socketio.on("joined", namespace="/")
def joined_room():
    room = session.get("current-channel")
    join_room(room)

    emit('status', {"user":session.get("username"), "channel":room, "msg":session.get("username") + " has joined the channel"}, room=room)

@socketio.on("submit message")
def send_msg(data):
    date = data["timestamp"]
    message = "<" + date + "> " + session.get("username") + ": " + data["message"]
    room = session.get("current-channel")
    if len(channel_messages[room]) >100:
        channel_messages[room].pop(0)
    channel_messages[room].append(message)
    emit("announce message", {"message":message}, room=room)

@socketio.on("back home")
def back():
    message = session.get("username") + " has left the chat"
    room = session.get("current-channel")
    session["current-channel"] = None
    leave_room(room)
    emit('status', {"msg":message}, room=room)


if __name__=="__main__":
    socketio.run(app, debug=True)
