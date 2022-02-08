"""
COMP.CS.100 Ohjelmointi 1 / Programming 1
Student Id: 150322081
Name:       Joonas Tuominen
Email:      joonas.2.tuominen@tuni.fi


-------Program description----------------
The following program is a compilation of
quite a few late nights and caffenated
hours :D .

This is supposed to be just a basic copy
of the popular game "Flappy bird". To be
completely honest the game doesn't work
quite as intended (restarting), but I
really can't find a fix or a good work
around. I think this is mostly due to
tkinter not being ment to be used in this
way.

Any how the program still works well enough
for:

1. A user to login to the program and to
   create a username and password combination
   that can be used to store the player's stats
   into a savefile (player_data.udat).

2. A player to play an elementary and slightly
   modified version of Flappy bird and to store
   the highscore to a savefile.

To use this software and to play, just press RUN. :)


p.s. all the photos are CC0 and have been modified by a bit.
"""

# Import the following:
import tkinter as tk    # for obvious reasons
import math             # for sqrt etc
import time             # for per_counter
import random           # for random number generation
import json             # for nice file formatting and automation
import hashlib          # for password protection


# Just some files we are gonna depend on:
global_files = {"player": ["bird_flap.png", "bird_norm.png"], "pipes": ["mikontalo.png"], "data": ["player_data.udat"]}


class Vertex2D:
    """
    Vertex2D is a basically just a 2D vector, but istn't name Vector2D since I didn't wanna confuse this
    with Unity's lingo. So basically a struct (though pyhton doesn't have structs) that holds a X value and a Y value.
    """
    def __init__(self, x, y):
        """
        Constructor that takes a 2 params
        :param x: float/int, x-coordinate
        :param y: float/int, y-coordinate
        """
        self.x = x
        self.y = y

    def __add__(self, other):
        """
        Addition of two vectors together. Also allows adding a float to both components
        :param other: Vertex2D/float, coords or float to be added
        :return: Vertex2D, sum vector
        """
        if isinstance(other, Vertex2D):
            return Vertex2D(self.x + other.x, self.y + other.y)
        elif isinstance(other, float) or isinstance(other, int):
            return Vertex2D(self.x + other, self.y + other)
        else:
            raise Warning(f"Cannot add {type(other)} to a 2D vector")

    def __sub__(self, other):
        """
        Subtraction of two vectors. Also allows subtracting a float from both components
        :param other: Vertex2D/float, coords or float to be deduced
        :return: Vertex2D, resulting vector
        """
        if isinstance(other, Vertex2D):
            return Vertex2D(self.x - other.x, self.y - other.y)
        elif isinstance(other, float):
            return Vertex2D(self.x - other, self.y - other)
        else:
            raise Warning(f"Cannot subtract {type(other)} from a 2D vector")

    def __str__(self):
        """
        Converts the current Vertex2D object to a string
        :return: str, [x_coordinate, y_coordinate]
        """
        return "[{0}, {1}]".format(self.x, self.y)

    def __mul__(self, other):
        """
        Multiplication of a float or an int with this vector.
        :param other: float,int; multiplier
        :return: Vertex2D, resultant vector
        """
        if isinstance(other, float):
            return Vertex2D(self.x * other, self.y * other)
        elif isinstance(other, int):
            return Vertex2D(self.x * other, self.y * other)
        else:
            raise Warning("Can't multiply a 2D vector with a " + type(other))

    def __rmul__(self, other):
        """
        Multiplication of a float or an int with this vector (from the right).
        :param other: float,int; multiplier
        :return: Vertex2D, resultant vector
        """
        if isinstance(other, float):
            return Vertex2D(self.x * other, self.y * other)
        elif isinstance(other, int):
            return Vertex2D(self.x * other, self.y * other)
        else:
            raise Warning("Can't multiply a 2D vector with a " + type(other))


def check_for_files():
    """
    Function that checks certain dependencies for the program to run correctly.
    :return: bool, whether run successfully
    """

    print("---Checking for required files-----")
    # Go through the categories specified in global_files
    for req in global_files:
        # Check if the required dependecies (items) are installed:
        for i in global_files[req]:
            # Print file name to console
            print(i, end=" --  ")
            try:
                # Try forming a new file with the item name
                f = open(i, mode="x")
                f.close()
                # if successful the file doesn't exist
                print("NOT FOUND", end="")
                if req != "data":
                    # the data files ain't 100% necessary
                    print()
                    return False
                else:
                    # but we create them anyway
                    print("  --  File created")
            except OSError:
                # if we ran into an error in file creation,
                # we most likely had the file already
                print("FOUND")
    return True


class Debug:
    """
    Helper class for more accurate debugging and so I can do console.log() :D
    """
    def __init__(self, path):
        """
        Constuctor that takes some sort of path
        :param path: str, path to the function
        """
        self.__path = path

    def log(self, msg):
        """
        Prints a message so that it shows the function it was printed from
        :param msg: str, a message to be printed
        :return: None
        """
        print(f"{self.__path} -- {msg}")


class Menu:
    """
    A basic menu to get the user's username and highscore or to create a new user. Also provides the game instructions
    to the player.
    """

    # just some constants we aren't gonna change. These gonna be constant for all instances so we
    # have them here and also without the underscores infront
    win__name = "Flappy herwood"
    win__size = [600, 600]

    def __init__(self):
        """
        Init for the menu GUI. Should be pretty self explanatory.
        """
        # Create a window with the specified name
        self.__window = self.create_window("{0}  -  Menu".format(self.win__name))
        # Force the window to a certain size
        self.__window.geometry("{0}x{1}".format(self.win__size[0], self.win__size[1]))  # Lets not use f" cuz why not :D

        # just some variable we can store the state of the window to
        self.__alive = True
        # the username of the user
        self.__username = ""
        # the user's highscore
        self.__highscore = 0

        # Some insturctions and a welcoming message to the player...
        self.__welcome = tk.Label(text="Hello and thanks for playing Flappy birr... I mean Flappy Herwood!",
                                  font='Helvetica 12 bold')
        self.__instructions = tk.Label(text="To play this game all you need to do is to either Login\n"
                                            "or create an account. If you'd like to go nameless, just\n"
                                            "press the 'go unnamed' button.\n\n"
                                            "Once you either log in or skip this step the game starts\n"
                                            "automatically after 1 second. To fly just press the Spacebar\n\n")
        self.__welcome.pack()
        self.__instructions.pack()

        # Logging in stuff...
        self.__user_text = tk.Label(text="Username:")
        self.__user_entry = tk.Entry()
        self.__user_text.pack()
        self.__user_entry.pack()

        self.__password_text = tk.Label(text="Password:")
        self.__password_entry = tk.Entry()
        self.__password_text.pack()
        self.__password_entry.pack()

        # Variable to check if we have given "wrong password" prompt
        self.__prompt = False

        # buttons to login or skip
        self.__log_in = tk.Button(text="Login or Create user", command=self.login)
        self.__skip = tk.Button(text="Go unnamed", command=self.done)
        self.__log_in.pack()
        self.__skip.pack()

        # Finally update the window to show these fields
        self.__window.update()

    def create_window(self, name):
        """
        Function that tries to create a tkinter window with a specific name.
        :param name: str, name of the window
        :return: tkinter.Tk, the created window
        """
        # bool to check if the try ran successfully
        done = False
        try:
            win = tk.Tk(className=" " + str(name))
            done = True
        finally:
            if not done:
                win = tk.Tk()
            return win

    def login(self):
        """
        Log in functionality. Tries to get user data for the user or creates a new user if not already in database.
        :return: None
        """

        # Create console and dictionary for file info
        console = Debug("Menu-log_in")
        d = {}

        try:
            # Try openinng the data file and dump data to data dictionary
            console.log("Opening data file")
            f = open(global_files["data"][0], mode="r")
            s = f.readline()
            if s != "":
                d.update(json.loads(s))
                console.log("Updating data dictionary")
            f.close()
        except OSError:
            raise Warning("Something went wrong in fetcing user data")

        # Get the username from the entry box
        self.__username = self.__user_entry.get()

        # Check if the user exists
        if self.__username in d:
            console.log("user in database")
            # if so check if their password was correct
            # We only store hashes of the passwords and not the actual string so others can't get your stats so easily
            if d[self.__username]["password"] == hashlib.sha256((self.__password_entry.get()).encode()).hexdigest():
                console.log("password correct")
                # if so get the highscore...
                self.__highscore = d[self.__username]["score"]
                console.log("Ending")
                # ...aand end menu execution
                self.done()
            else:
                console.log("password hash mismatch")
                # if not create and display wrong password prompt
                if not self.__prompt:
                    self.__pass_wrong = tk.Label(text="Password or username wrong")
                    self.__pass_wrong.pack()
                self.__prompt = True
        else:
            console.log("user not in database")

            # If the user was not in the file, create a new user with the given password
            console.log("updating data...")
            user = {self.__username: {"password": hashlib.sha256((self.__password_entry.get()).encode()).hexdigest(),
                                      "score": 0}}
            # add this user to the data dictionary....
            d.update(user)
            console.log("dictionary updated")
            try:
                # ...and update the file
                f = open(global_files["data"][0], mode="w")
                f.write(json.dumps(d))
                console.log(f"file ({global_files['data'][0]}) updated")
                f.close()

                console.log("Ending")
                # then terminate the menu
                self.done()
            except OSError:
                raise Warning("Something went wrong in writing user data")

    def done(self):
        """
        Sets the __alive variable as false
        :return: None
        """
        self.__alive = False

    def update(self):
        """
        Calls update on the menu window
        :return: None
        """
        self.__window.update()

    def get_user_data(self):
        """
        Gets user data from the menu.
        :return: list, [username (str), highscore(float)]
        """
        return [self.__username, self.__highscore]

    def is_alive(self):
        """
        Returns __alive
        :return: bool, if alive
        """
        return self.__alive

    def kill(self):
        """
        Destroys the window
        :return: None
        """
        self.__window.destroy()


class GameObject:
    """
    A basic gameobject class that holds some things we might need.
    """
    def __init__(self, viewport, position, velocity=Vertex2D(0, 0), acceleration=Vertex2D(0, 0), rotation=0, scale=1,
                 textures=None):
        """
        Constructor for a GameObject takes
        :param viewport: tkinter.Cancas, the canvas these objects are going to be drawn on
        :param position: Vertex2D, the coordinates of the object
        :param velocity: Vertex2D, the velocity of the object
        :param acceleration: Vertex2D, the acceleration of the object
        :param rotation: float, the angle of the object
        :param scale: float, the scale factor of the object
        :param textures: tk.Photoimage/list, a singular or multiple textures for the object
        """
        # set the variable as given
        self.__viewport = viewport
        self.__position = position
        self.__velocity = velocity
        self.__acceleration = acceleration

        self.__rotation = rotation
        # not used as of the moment since I'd apparently have to create new images
        # everytime I want to rotate an image or an object

        self.__scale = scale                # not used as of the moment since tkinter's zoom functionality is so bad

        self.__textures = textures

        self.__bounding_box_size = Vertex2D(0, 0)  # Itializes a bounding box's width and height in to a 2D vector
        self.calculate_bb()  # Calculates the actual bounding box dimentions

    def calculate_bb(self):
        """
        Calculates the dimentions of the bounding box based on the textures.
        :return:
        """

        # Check the type of the textures variable
        if isinstance(self.__textures, tk.PhotoImage):
            # if it is an image set the dimentions to the width and height of the image
            self.__bounding_box_size = Vertex2D(self.__textures.width(), self.__textures.height())
        elif isinstance(self.__textures, list):
            # if it is a list of images, se the dimentions to the width and height of the first image
            self.__bounding_box_size = Vertex2D(self.__textures[0].width(), self.__textures[0].height())
        else:
            # otherwise produce an error
            raise ValueError("Image is not of type: PhotoImage but of type " + type(self.__textures))

    def draw_bounding_box(self):
        """
        ---DEBUGGING---
        Draws a red bounding box around the gameobject.
        :return: None
        """
        # Create a red rectangle with the following corners:
        self.__viewport.create_rectangle(self.__position.x - self.__bounding_box_size.x / 2,
                                         self.__position.y + self.__bounding_box_size.y / 2,
                                         self.__position.x + self.__bounding_box_size.x / 2,
                                         self.__position.y - self.__bounding_box_size.y / 2,
                                         outline="red")

    def animation(self):
        """
        Changes the texture displayed based on the player's current velocity.
        :return: None
        """
        if self.__velocity.y > 0:
            self.__viewport.itemconfig(self.__canvas_obj, image=self.get_texture(1))
        else:
            self.__viewport.itemconfig(self.__canvas_obj, image=self.get_texture(0))

    def get_texture(self, index=0):
        """
        Method for getting a texture,
        :param index: int, the index for a texture
        :return: tk.PhotoImage
        """
        # check the type of the textures variable
        if isinstance(self.__textures, tk.PhotoImage):
            return self.__textures  # if just one texture, return it
        elif isinstance(self.__textures, list):
            return self.__textures[index]  # if a list of textures, return the one at index
        else:
            # otherwise raise an error
            raise ValueError("Image is not of type: PhotoImage but of type " + type(self.__textures))

    def get_acc(self):
        """
        Getter for acceleration
        :return: Vertex2D, the 2D acceleration of the object
        """
        return self.__acceleration

    def set_acc(self, acceleration):
        """
        Sets the acceleration of the object.
        :param acceleration: Vertex2D, the acceleration to be set
        :return: None
        """
        self.__acceleration = acceleration

    def get_vel(self):
        """
        Get the velocity of the object.
        :return: Vertex2D, the 2D velocity of the object
        """
        return self.__velocity

    def set_vel(self, velocity):
        """
        Set the velocity to a value
        :param velocity: Vertex2D, The velocity to be set
        :return: None
        """
        self.__velocity = velocity

    def get_pos(self):
        """
        Get the positition of the object
        :return: Vertex2D, the 2D position of the object.
        """
        return self.__position

    def set_pos(self, position):
        """
        Set the position of the object to smt. specific.

        NOTE!! This does NOT change to position of the canvas object. To do that use the move_obj function
        :param position: the position to be set
        :return: None
        """
        self.__position = position

    def get_bb(self):
        """
        Get the size of the bounding box
        :return: Vertex2D, dimentions of the bounding box
        """
        return self.__bounding_box_size

    def move_obj(self, direction):
        """
        Move the object on canvas
        :param direction: Vertex2D, the direction and amount to be moved
        :return: None
        """
        # Update the position of the object
        self.__position = self.__position + direction
        # Move the object on canvas
        self.__viewport.move(self.__canvas_obj, direction.x, direction.y)

    def render_obj(self):
        """
        Render the object to the tkinter canvas
        :return: None
        """
        # Note: I think the viewport isn't passed as a instance, since all the obj. moving and config. now has to be
        # done via methods. aka doing things in the Engine class doesn't do anything.

        # Why can't pyhton have clear ways of telling when a variable is passed as a reference and when it creates
        # a new instance of the variable type???
        self.__canvas_obj = self.__viewport.create_image(self.__position.x, self.__position.y, image=self.get_texture())

    def delete_canvas_object(self):
        """
        Delete the canvas object
        :return: None
        """
        self.__viewport.delete(self.__canvas_obj)


class Physics:
    """
    Class that holds basic physics funtionality like collision detection and calculationg player acceleration
    """

    def __init__(self, gravity, acceleration_multiplier, velocity_multiplier):
        """
        Physics object requires some params to be able to work.
        :param gravity: float, the ammount the object is accelerated downwards
        :param acceleration_multiplier: float, a multiplier to acceleration to make the change of direction more "snappy"
        :param velocity_multiplier: float, a velocity multiplier to make in position a bit more rapid
        """
        # set the variables as given
        self.__gravity = gravity
        self.__acceleration_multiplier = acceleration_multiplier
        self.__velocity_multiplier = velocity_multiplier

        # Create a console for debugging and message logging
        self.__console = Debug("Physics Engine-")

    def calculate_player_physics(self, gameobject, delta_time):
        """
        Function for calculating the player physics
        :param gameobject: Gameobject, the player
        :param delta_time: float, time taken between the frames
        :return: tuple(Vertex2D, Vertex2D, Vertex2D); new position, new velocity and new acceleration
        """
        # Just a dummy check that we can proceed with calculations and to get proper linting
        if isinstance(gameobject, GameObject):

            # get the acc, vel and pos
            acceleration = gameobject.get_acc()
            velocity = gameobject.get_vel()
            position = gameobject.get_pos()

            # Reduce the acceleration with the given formalae:
            acceleration -= self.__acceleration_multiplier * math.sqrt(self.__gravity * delta_time)
            # not done with just self.gravity * self.delta_time, since it wasn't snappy enough
            # We use the square root so that we can the acceleration doesn't get too high

            # Calc velocity with the same logic
            velocity += acceleration * delta_time
            if velocity.y >= 0:
                velocity.y = math.sqrt(velocity.y)
            else:
                velocity.y = -math.sqrt(abs(velocity.y))

            # Finally calculate the new postition and return the new values:
            position += self.__velocity_multiplier * velocity * delta_time
            return position, velocity, acceleration

    def check_colliders(self, gameobject, objects):
        """
        Function for collision detection between player (gameobject) and other gameobjects
        :param gameobject: GameObject, the player
        :param objects: GameObject, the gameobjects in the scene
        :return: bool, if there was a collision or not
        """
        # Create a list that holds all the coordinates of the player object's corners:
        verts = [gameobject.get_pos() + Vertex2D(gameobject.get_bb().x / 2,
                                                 gameobject.get_bb().y / 2),
                 gameobject.get_pos() + Vertex2D(gameobject.get_bb().x / 2,
                                                 -gameobject.get_bb().y / 2),
                 gameobject.get_pos() + Vertex2D(-gameobject.get_bb().x / 2,
                                                 -gameobject.get_bb().y / 2),
                 gameobject.get_pos() + Vertex2D(-gameobject.get_bb().x / 2,
                                                 gameobject.get_bb().y / 2)]

        # Then loop through all the gameobjects
        for go in objects:
            # Check if the current object is not the player and get linting and autofill :D
            if gameobject != go and isinstance(gameobject, GameObject) and isinstance(go, GameObject):
                # Loop through all the corners of the players gameobject
                for v in verts:
                    # Check if we are inside another object
                    if (v.x >= go.get_pos().x - go.get_bb().x / 2) and (v.x <= go.get_pos().x + go.get_bb().x / 2):
                        if (v.y >= go.get_pos().y - go.get_bb().y / 2) and (v.y <= go.get_pos().y + go.get_bb().y / 2):
                            # if we are send a message to the console and return True as we registered a hit
                            self.__console.log("-" * 15)
                            self.__console.log("Collision".upper())
                            self.__console.log(f"Player pos: {gameobject.get_pos()} and object pos: {go.get_pos()}")
                            self.__console.log("-" * 15)

                            # NOTE! this might not work if the speed gets too high and we might
                            # need to check the pos on the next frame too!
                            return True

        # if we get this far we didn't hit anything, so return False
        return False


class Engine:
    """
    Engine class holds all the funtionality needeed for the game's operation
    """

    # Again we have the same constants (could have them as golbal_constants but idc :D )
    win__name = "Flappy herwood"
    win__size = [600, 600]

    # The range for our random number generation
    random_range = [-200, 200]

    # Indecies for our objects (min and max values) stored in a 2D vector:
    object_indecies = {"player": Vertex2D(0, 0), "pipes": Vertex2D(1, 13)}

    def __init__(self, physics_engine, flap_force, user="Nameless player", highscore=0):
        """
        The constructor for the Engine class that automatically creates a window, initializes the game and runs it.
        :param physics_engine: Physics, the physics engine that provides physics functionality
        :param flap_force: float, the force applied to the player on a flap
        :param user: str, the username of the player
        :param highscore: float, the highscore of the player
        """
        # Starts the game up by creating a window with the certain name and size
        self.__window = self.create_window(self.win__name)
        self.__window.geometry("{0}x{1}".format(self.win__size[0], self.win__size[1]))

        # Next initialize an empty list for our GameObjects and set the __phys_eng variable to our physics engine
        self.__game_objects = []
        self.__phys_eng = physics_engine

        # Also set the rest of the variables as defined in the constructor:
        self.__user = user
        self.__highscore = highscore

        self.__flap_force = flap_force

        # Once we are ready to start we initialize the game
        self.initialize_game()

        self.__window.mainloop()

    def create_window(self, name):
        """
        Function that tries to create a tkinter window with a specific name.
        :param name: str, name of the window
        :return: tkinter.Tk, the created window
        """
        # bool to check if the try ran successfully
        done = False
        try:
            win = tk.Tk(className=" " + str(name))
            done = True
        finally:
            if not done:
                win = tk.Tk()
            return win

    def initialize_game(self):
        """
        Itialization of the game and supporting functions around it
        :return: None
        """

        # Print information to the console
        print("", "-" * 20, " Running".upper(), "-" * 20, sep="\n", end="\n" * 2)
        console = Debug("Engine-initialize_game")

        self.create_gameobjects()  # Create the gameobjects and instantiate the environment
        console.log("Game initalized and created")
        self.render_objects()  # Draw the created objects to the created canvas widget
        console.log("Objects rendered")

        # Bind keypresses to the flap function, update the window and finally force the window to focus
        # so the user doesn't need to "tab over":
        self.__window.bind('<KeyPress>', self.flap)
        self.__window.update()
        self.__window.focus_force()

        # Start the game:
        console.log("Starting game....")
        self.start()

    def create_gameobjects(self):
        """
        Creates gameobjects, UI and the required tkinter variables.
        :return: None
        """
        # Create a console to this function
        console = Debug("Engine-initialize_game-create_gameobjects")

        # Create a tkinter canvas widget:
        self.__viewport = tk.Canvas(self.__window, bd=0, bg="lightblue", width=self.win__size[0], height=self.win__size[1])
        self.__viewport.pack()
        console.log("Created canvas")

        """Tried to get a background image here, but it just won't want to work for some reason"""

        # Create a player object and add it to the gameobjects list:
        self.__player = GameObject(self.__viewport, Vertex2D(int(self.win__size[0]/3), int(self.win__size[1]/2)),
                                   textures=[tk.PhotoImage(file=global_files["player"][1]),
                                             tk.PhotoImage(file=global_files["player"][0])])
        self.__game_objects.append(self.__player)
        console.log("Created player object")
        # self.__player.draw_bounding_box()

        # Next lets create some pipes:
        for i in range(6):
            # We create 6 rows so that we can be sure that we always have enough pipes on the screen

            # Start creation by getting a random y-offset
            y = random.randrange(self.random_range[0], self.random_range[1], 1)

            # Then we can just create a pair of these pipes.
            # One hanging from the ceiling and one sticking from the ground:

            # ---pipe on ceiling---
            self.__game_objects.append(GameObject(self.__viewport, Vertex2D(self.win__size[0]/1.25 + 75 * 2.5 * i, y),
                                                  textures=tk.PhotoImage(file=global_files["pipes"][0])))
            # ---pipe on ground---
            self.__game_objects.append(GameObject(self.__viewport, Vertex2D(self.win__size[0]/1.25 + 75 * 2.5 * i,
                                                                            self.win__size[1] + y),
                                                  textures=tk.PhotoImage(file=global_files["pipes"][0])))
        console.log("Created pipe objects")

        # Finally we can get to UI creation.
        # Start by creating a text object onto the canvas displaying the user's username
        self.__name = self.__viewport.create_text(3 * len(f"Player: {self.__user}"), 10, text=f"Player: {self.__user}")

        # Next we can initialize the user's score to 0 and create text objects displaying the user's current score
        # and their all time highscore (that we got from the database):
        self.__score = 0
        self.__scoreboard_score = self.__viewport.create_text(self.win__size[0] - 10 - 3 * len(f"Score: {self.__score}"),
                                                              10, text="Score: 0", justify="right")
        self.__scoreboard_highscore = self.__viewport.create_text(self.win__size[0] - 10
                                                                  - 3 * len(f"Highscore:: {self.__highscore:.2f}"), 30,
                                                                  text=f"Highscore: {self.__highscore:.2f}",
                                                                  justify="right")
        console.log("Created UI  ")

    def reset_game(self):
        """
        WARNING!! The function doesn't work quite as wanted. I really can't figure out where the error comes from.

        The funtion is supposed to move the gameobjects back to the same x-places they used to be,
        but with random y-offset again.
        :return: None
        """

        # Start logging
        console = Debug("Engine-reset_game")

        # Rebind the keypresses to the flap function:
        self.__window.bind('<KeyPress>', self.flap)
        console.log("self.play_again unbound and rebound to self.flap")
        self.__window.update()

        # Reset the player's score:
        self.__score = 0
        self.__viewport.itemconfig(self.__scoreboard_score, text=self.__score)
        console.log("Score reset")

        # Delete all the canvas objects (also tried to do this with just moving them but it didn't work):
        for obj in self.__game_objects:
            obj.delete_canvas_object()
        console.log("Canvas objects deleted")

        # Reset pipe pos:
        console.log("Resetting pipes....")
        y = random.randrange(self.random_range[0], self.random_range[1], 1)  # Get random y-offset

        # Loop through the pipes:
        for go in self.__game_objects[self.object_indecies["pipes"].x:self.object_indecies["pipes"].y]:
            # Get the index of the object in the list
            index = self.__game_objects.index(go)  # 1, 2, ..., 12

            # The upper pipes were created in the following way:
            # Vertex2D(self.win__size[0] / 1.25 + 75 * 2.5 * i, y)

            # The lower piper were created in the following way:
            # Vertex2D(self.win__size[0] / 1.25 + 75 * 2.5 * i, self.win__size[1] + y)

            # With these we can set each object's positions to the same ones they were at the start:
            if index % 2 == 1:
                # --- Upper pipes ---
                console.log(f"Setting pipes {index} and {index + 1} to {y} and {self.win__size[1] + y}")

                go.set_pos(Vertex2D(self.win__size[0] / 1.25 + 75 * 2.5 * ((index - 1) // 2), y))
            else:
                # --- Lower pipes ---
                go.set_pos(Vertex2D(self.win__size[0] / 1.25 + 75 * 2.5 * index // 2, self.win__size[1] + y))

                # Calculate a new y-offset
                y = random.randrange(self.random_range[0], self.random_range[1], 1)

        console.log("Pipes reset")

        # Reset player pos:
        self.__player.set_pos(Vertex2D(int(self.win__size[0]/3), int(self.win__size[1]/2)))
        # Check the create_gameobjects function, for why these values
        console.log("Player reset")

    def move_pipes(self, speed):
        """
        Function for moving the pipes at a certain speed.
        :param speed: float, the speed we want to move the pipes at
        :return: None
        """
        # Start off by calculating a random y-offset:
        y = random.randrange(self.random_range[0], self.random_range[1], 1)

        # Next we need to loop through all the pipe GameObjects and move them
        for go in self.__game_objects[self.object_indecies["pipes"].x:self.object_indecies["pipes"].y]:
            # To move them we first need to check if they are already well out of visible range...
            if go.get_pos().x + go.get_bb().x < - 100:
                # ...and if so we want to move this row of pipes to the back of the pipe "stack"

                # We can do this by first calculating the index of the current pipe we are moving
                index = self.__game_objects.index(go)  # 1, 2, ..., 12
                # Next, if the pipe is...
                if index % 2 == 1:
                    # odd, that means we are moving the upper pipe and we have to move it by:
                    go.move_obj(Vertex2D(100 + self.win__size[0]/1.25 + 75 * 1.2 * 6, -go.get_pos().y + y))
                else:
                    # even, then we are moving the pipe on the bottom and in that case we have to move the pipe by:
                    go.move_obj(Vertex2D(100 + self.win__size[0] / 1.25 + 75 * 1.2 * 6,
                                         self.win__size[1] - go.get_pos().y + y))
                    # in addition to moving the pipe we also want to get a new random y-offset for the next pair so
                    # we do that here:
                    y = random.randrange(self.random_range[0], self.random_range[1], 1)
            else:
                # if the pipe is still in visible range or about to be, we move it forwards by the following amount:
                go.move_obj(Vertex2D(-speed, 0))

    def move_player(self, dt):
        """
        Function that moves the player
        :param dt: float, time taken between frames
        :return: None
        """

        # Check if need to flap and thus add acceleration upwards to the player:
        if self.__flap:
            self.__player.set_acc(Vertex2D(0, self.__flap_force))
            self.__flap = False  # Immediatly se the flap variable to False to not get a positive feedback loop

        # Get the new position, velocity and acceleration from the physics engine:
        pos, vel, acc = self.__phys_eng.calculate_player_physics(self.__player, dt)

        # Calculate the difference in positional y values and set the other y values (set_pos is done in move_obj):
        dy = self.__player.get_pos().y - pos.y
        self.__player.set_acc(Vertex2D(0, acc.y))
        self.__player.set_vel(Vertex2D(0, vel.y))

        # Get the correct state for the flap animation
        self.__player.animation()

        # Finally move the object the calculated amount:
        self.__player.move_obj(Vertex2D(0, dy))

    def start(self):
        """
        Starts the actual game
        :return: None
        """

        # Instatiate a few variables:
        console = Debug("Engine-start")

        dt = 0.0001  # dt = DeltaTime = time taken between frames. Also I the way I do it here isn't optimal and that u
        # should really be doing this by swapping frame buffers, buuuuuuuttt this is a basic pyhton project so
        # Imma do this the dumb way :D

        self.__flap = False  # if we need to flap

        # Sleep for a second first so that the player can get comfortable with the environment and to get ready to play
        time.sleep(1)
        console.log("init")

        # Start a while loop, which is going to be our game
        while True:
            # Get the time when we are starting to do our calculations
            t1 = time.perf_counter()

            # Call the move move_pipes function that moves our pipes with the speed presented bellow:
            self.move_pipes((0.25 * self.__score + 50) * dt)
            # After moving the pipes we can move the player
            self.move_player(dt)
            # we use deltaTime to make our calculations unreliant on framerate and to make our animations more smooth

            # Next we check if we hit an object or a barrier and need to end the game:
            # ---- hit a object ----
            if self.__phys_eng.check_colliders(self.__player, self.__game_objects):
                console.log("Player hit object")
                break
            # ---- hit the floor ----
            if self.__player.get_pos().y + self.__player.get_bb().y / 2 >= self.win__size[1]:
                console.log("Player hit the floor")
                break
            # ---- hit the ceiling ----
            if self.__player.get_pos().y - self.__player.get_bb().y / 2 <= 0:
                console.log("Player hit the ceiling")
                break

            # if we didn't run into ending case, we continue by updating the player's score on the screen...
            self.__viewport.itemconfig(self.__scoreboard_score, text=f"Score {self.__score:.2f}")

            # ...and by lifting all the UI elements on top of the rest:
            self.__viewport.lift(self.__name)
            self.__viewport.lift(self.__scoreboard_score)
            self.__viewport.lift(self.__scoreboard_highscore)

            # Finally we can call update on the window to display the next state
            self.__window.update()

            # To end off we take the time at the end of the cycle, calculate the time difference and add the time
            # accumulated to the player's score:
            t2 = time.perf_counter()
            dt = float(t2 - t1)
            self.__score += dt

        # if end up breaking out of the loop, that means the player has died
        console.log("Player died")

        # in that case we switch to the end_game state
        console.log("Ending game...")
        self.end_game()

    def flap(self, event):
        """
        Sets the __flap variable to true if the key we pressed down was the spacebar:
        :param event: tkinter event, the <key press> event we binded to this function
        :return: None
        """
        # Set self.__flap to true if we pressed space:
        if event.char == " ":
            self.__flap = True

    def save_stats(self):
        """
        Function that stores the score of the player (under current username) to the database.
        :return: None
        """

        # Start a new console directing to this func
        console = Debug("Engine-end_game-save_stats")

        # Check if we have a username, and if not we skip this process
        if self.__user == "Nameless player":
            console.log("Nameless player. NOT saving stats")
            return

        # Otherwise we proceed with storing the state to the database:
        try:
            # Start by again first operning the database and by getting the information stored there:
            f_in = open(global_files["data"][0], mode="r")
            console.log("File opened")

            data = f_in.readline()
            if data != "":
                d = json.loads(data)
                console.log("File read")
            else:
                d = {}
                console.log("File empty")

            f_in.close()

            # Then we can set the user's payload to the following
            d[self.__user] = {"password": d[self.__user]["password"], "score": self.__highscore}
            # this is a bit dumb, but for some reason d[self.__user]["score"] didn't work so idk
            console.log("Score updated")

            # Finally we can then just rewrite the data into the database:
            f_out = open(global_files["data"][0], mode="w")

            f_out.write(json.dumps(d))
            console.log("File updated")

            f_out.close()
        except OSError:
            print("Error while saving data")

    def end_game(self):
        """
        A function or state where we handle the death animation and score saving.
        :return: None
        """

        console = Debug("Engine-end_game")

        # Initialize variables used in the animation:
        dt = 0.0001
        __time = 0

        console.log("init")

        # Start actual functionality by checking if we beat our highscore
        if self.__score > self.__highscore:
            # If we did, we need to update our highscore in the canvas and in our database:
            console.log("Updating score....")

            self.__highscore = self.__score
            self.__viewport.itemconfig(self.__scoreboard_highscore, text=f"Highscore {self.__highscore:.2f}")

            # update database:
            self.save_stats()

            console.log("Highscore updated")

        # Next we can proceed with the end animation (kinda would want to do this asynchronously, but idk how)
        console.log("End animation...")

        # Animate untill the player is well below the canvas' visible area:
        while self.__player.get_pos().y <= self.win__size[1] + 100:
            # Get the time at the start of the frame
            t1 = time.perf_counter()

            # Calculate the amount we want to move the player by (basically the equation for a parabola):
            amount = Vertex2D(-4, 10 * pow(__time, 2.5) - 40) * dt

            # Move the player object and update the move onto the canvas:
            self.__player.move_obj(amount)
            self.__window.update()

            # Get the time related stuff done:
            t2 = time.perf_counter()
            dt = float(t2 - t1)
            __time += dt

        console.log("End animation complete")

        # Finally we can go to the end screen:
        console.log("Switch to ending screen...")
        self.end_screen()

    def end_screen(self):
        """
        Final state of the game. Gives the ability to restart or stop playing.
        :return: None
        """
        # Start by showing the player instructions on how to proceed and rebind key presses to play_again funtion:
        self.__play_again = self.__viewport.create_text(self.win__size[0]/2, self.win__size[1]/2,
                                                        text=f"Press the Spacebar to play again on Q to quit:")
        self.__window.bind('<KeyPress>', self.play_again)
        self.__window.update()

    def play_again(self, event):
        """
        Since tkinter works in a totolly different way compared to e.g. Unity we need to have this function separately
        from the end_screen function. But basically this is just a continuation of the prev. function.
        :param event: tkinter.event, keyboard input event
        :return: None
        """
        # Start the logging:
        console = Debug("Engine-play_again")

        # Check if the keypress was one of the specified commands
        if event.char == " ":
            console.log("Playing again")
            # if the user pressed space, we restart the game

            console.log("Resetting game...")
            # first we remove the "play again" prompt from the canvas widget
            self.__viewport.delete(self.__play_again)
            # and then we reset the game
            self.reset_game()

            # Finally we can render the objects and call update on the window
            self.render_objects()
            console.log("Reset done")
            self.__window.update()

            # To end off we just start the game again
            console.log("Starting game...")
            self.start()

        if event.char.casefold() == "Q".casefold():
            console.log("Terminating".upper())
            # if the user wants to stop playing we start by destroying the canvas widget
            self.__viewport.destroy()

            # Next we show the following messages to the user
            self.__end_text = tk.Label(text="Bye! Thanks for playing!")
            self.__end_timer_text = tk.Label(text="Program will automatically terminate in 5 sec")
            self.__end_text.pack()
            self.__end_timer_text.pack()

            # Then we just create a while loop in which we update the canvas element until the timer runs out
            __time = 0  # Accumulated time
            while __time < 5:  # loop until 5s has passed
                t1 = time.perf_counter()  # time at the start of cycle

                # update the text element and the window:
                self.__end_timer_text.configure(text=f"Program will automatically terminate in {5-__time:.1f} sec")
                self.__window.update()

                t2 = time.perf_counter()  # time at the end of the cycle
                __time += float(t2 - t1)  # add the time take to the accumulated time

            # When the timer has run out, we can destroy the window:
            self.__window.destroy()
            console.log("Finished")

    def render_objects(self):
        """
        Function that calls the render_obj for all the GameObjects.
        :return: None
        """
        # Loop through all the game objects and call render_obj for the object:
        for go in self.__game_objects:
            go.render_obj()


def main():
    # Check if we have all the dependecies at the start:
    if not check_for_files():
        # if not we raise an error
        raise Warning("Some error happened in file management")

    # Create the menu
    menu = Menu()

    # Loop as long as the menu is alive:
    while True:
        if not menu.is_alive():
            # Check if not alive, if not then get the data before we kill the window
            user_data = menu.get_user_data()
            menu.kill()
            break
        else:
            # If the menu is still alive we update the window
            menu.update()

    # Next we create the physics engine as a separate instance...
    phys = Physics(2000, 2, 100)
    # and then we can check if whether we have a user or not and then create a engine corresponding the state we are in
    if user_data[0] != "":
        game = Engine(phys, 1000, user=user_data[0], highscore=user_data[1])
    else:
        game = Engine(phys, 1000)


if __name__ == '__main__':
    main()
