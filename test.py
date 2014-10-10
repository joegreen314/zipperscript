import Tkinter as tk
import logging

class LogDisplay(tk.LabelFrame):
    """A simple 'console' to place at the bottom of a Tkinter window """
    def __init__(self, root, **options):
        tk.LabelFrame.__init__(self, root, **options);

        "Console Text space"
        self.console = tk.Text(self, height=10)
        self.console.pack(fill=tk.BOTH)

class LoggingToGUI(logging.Handler):
    """ Used to redirect logging output to the widget passed in parameters """
    def __init__(self, console):
        logging.Handler.__init__(self)

        self.console = console #Any text widget, you can use the class above or not

    def emit(self, message): # Overwrites the default handler's emit method
        formattedMessage = self.format(message)  #You can change the format here

        # Disabling states so no user can write in it
        self.console.configure(state=tk.NORMAL)
        self.console.insert(tk.END, formattedMessage) #Inserting the logger message in the widget
        self.console.configure(state=tk.DISABLED)
        self.console.see(tk.END)
        print(message) 

gui = tk.Tk()
#LogDisplay(gui)
log = LoggingToGUI(LogDisplay(gui))
log.emit("test")
print "test"