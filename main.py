import os
import sys
from StateTemplates import *
from GameClasses import *
from ChampionStates import *
from FightStates import *
import random
import tkinter as tk
from PIL import Image, ImageTk


random.seed()
PAUSE = False
PLAYER_NAME = 'susek'
world = World('items.txt', 'creatures.txt', 'dungeon.txt')
player = Champion(world, PLAYER_NAME, 100)   

def pause():
    global PAUSE
    PAUSE = not PAUSE




class UpdatingLabel(tk.Label):
    def __init__(self, master = None, f = lambda: -1):
        tk.Label.__init__(self, master)
        self.text_gen = f
        self.update_label()

    def update_label(self):
        self.config(text = self.text_gen())
        self.after(1000, self.update_label)

class Window(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.master = master

    def showText(self, s):
        text = tk.Label(self, text = s)
        text.pack()

    def xxxxxxx(self, label, f):
        def update():
            # self.updateworld()
            label.config(text = f())
            label.after(1000, update)
        update()

    def showUpdatingText(self, f):
        text = tk.Label(self)
        text.pack()
        self.xxxxxxx(text, f)

    def addButton(self, text, f, width = 20):
        button = tk.Button(self, text = text, width = width, command = f)
        button.pack()

    def check_conditions(self, button, condition):
        def check():
            if not condition():
                button.config(state = tk.DISABLED)
            else:
                button.config(state = tk.NORMAL)
            button.after(1000, check)
        check()

    def addConditionButton(self, text, width, command, condition):
        button = tk.Button(self, text = text, width = width, command = command)
        self.check_conditions(button, condition)
        button.pack()

    def client_exit(self):
        exit()

    def addInventorySlot(self, ind):
        tmp = InventorySlot(self, ind)
        tmp.pack()

    def addUpdatingLabel(self, f):
        tmp = UpdatingLabel(self, f)
        tmp.pack()

    #def 


class MyLabelFrame(Window, tk.LabelFrame):
    def __init__(self, master = None, text = 'Just Another LabelFrame'):
        tk.LabelFrame.__init__(self, master, text = text)


class InventorySlot(Window):
    def __init__(self, master = None, index = 0):
        Window.__init__(self, master)
        self.config(highlightbackground = "black", highlightcolor = "black", highlightthickness = 1)
        self.config(bd = 4)
        self.inv_ind = index
        self.init_slot()
        self.name = -1        

    def init_slot(self):
        tmp = player.inventory.get_ind(self.inv_ind)
        self.addConditionButton('sell', 10, lambda: player.sell_slot(self.inv_ind), lambda: player.depth == 0)
        self.addConditionButton('equip', 10, lambda: player.equip_slot(self.inv_ind), lambda: player.can_wear_slot(self.inv_ind))
        self.addButton('throw out', lambda: player.inventory.erase_ind(self.inv_ind), 10)
        self.showUpdatingText(lambda: 'cost: ' + str(self.cost()))
        self.showUpdatingText(lambda: player.inventory.get_ind_name(self.inv_ind))
        #self.addImageLabel()


    def cost(self):
        if player.inventory.get_ind(self.inv_ind) != -1:
            tmp = player.inventory.get_ind(self.inv_ind)
            return tmp.cost
        return 0




def main():

    def end_registration(master, s):
        global PLAYER_NAME
        player.set_name(s)
        master.destroy()

    EntryWindow = tk.Tk()
    NameEntry = tk.Entry(EntryWindow, width = 20)
    NameEntryLabel = tk.Label(EntryWindow, text = "Nickname:", width = 10)
    NameEntryLabel.grid(row = 0, column = 0)
    NameEntry.grid(row = 0, column = 1)
    tk.Button(EntryWindow, text = 'Ok', command = lambda: end_registration(EntryWindow, NameEntry.get())).grid(row = 0, column = 3)
    tk.mainloop()    
    
    world.set_player(player)

    root = tk.Tk()
    root.geometry("700x700")

    app = Window(root)
    app.master.title("GAME")
    app.pack(fill =  tk.BOTH, expand = 1)

    menu = tk.Menu(app.master)
    app.master.config(menu = menu)
    file = tk.Menu(menu)
    file.add_command(label = "Exit", command = app.client_exit)
    menu.add_cascade(label = "File", menu = file)

    StatusFrame = MyLabelFrame(app, 'Status')

    StatusFrame.showText(player.name)
    StatusFrame.showUpdatingText(lambda: '(' + str(player.level) + ' lvl; ' + str(player.depth) + ' depth)')
    StatusFrame.showUpdatingText(lambda: str(player.hp) + '/' + str(player.maxhp) + ' hp')
    StatusFrame.showUpdatingText(lambda: str(player.exp) + '/' + str(exp_to_next_level(player.level)) + ' exp')
    StatusFrame.showUpdatingText(lambda: 'money: ' + str(player.money))
    StatusFrame.showUpdatingText(lambda: player.status)
    StatusFrame.showUpdatingText(lambda: 'skill points: ' + str(player.skillpoints))

    # ControlButtons = Window(app)
    ControlButtons = MyLabelFrame(app, 'Control')

    ControlButtons.addButton('Return to parasha', player.return_to_town)
    ControlButtons.addButton("Go to sobirat' vilkoi gowno", player.go_dungeon)
    ControlButtons.addButton('Pause', pause)

    InventoryFrame = MyLabelFrame(app, 'Inventory')
    for i in range(6):
        tmp = InventorySlot(InventoryFrame, i)
        tmp.grid(column = i // 3, row = i % 3)


    EquipFrame = MyLabelFrame(app, 'Equip')

    tmp = []
    for i in BASE_SLOTS:
        tag = '' + i
        EquipFrame.addUpdatingLabel(lambda tag = tag: tag + ': ' + player.equip.get_tag_text(tag))

    ControlButtons.place(x = 4, y = 0)
    StatusFrame.place(x = 4, y = 100)
    InventoryFrame.place(x = 200, y = 0)
    EquipFrame.place(x = 4, y = 290)


    Updater = tk.Label(app)
    def WorldUpdater(label):
        def update():
            if not PAUSE:
                world.update()
            label.after(100, update)
        update()
    WorldUpdater(Updater)

    root.mainloop()

main()