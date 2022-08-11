import datetime
import json
import mimetypes
import os
import guizero
import lxml.html
import lxml.etree

class NotepadMini:
    def __init__(self) -> None:
        self.App = guizero.App(title="Notepad Mini", width=750, height=450)

        self.File = None
        self.FileModified = False

        self.Filetypes = [
            ("Text document", "*.txt"),
            ("HTML document", "*.html"), 
            ("Cascading StyleSheet", "*.css"), 
            ("JavaScript file", "*.js"),
            ("Python code", "*.py"),
            ("Java code", "*.java"),
            ("C# code", "*.cs"),
            ("All files","*.*"),
        ]

        self.FontFamily = "Times"
        self.FontSize = 15
        
        self.Menu = guizero.MenuBar(
            self.App,
            [
                "File", "Format"
            ],
            [
                [
                    [ "New file", self.NewFile ],
                    [ "Open file", self.OpenFile ],
                    [ "Save file", self.SaveFile ],
                    [ "File info", self.FileInfo ],
                ],
                [
                    [ "Font", self.FontSettings ],
                    [ "Format document", self.FormatDoc ]
                ],
            ],
        )

        self.Textarea = guizero.TextBox(self.App, width="fill", height="fill",multiline=True, scrollbar=True)
        self.Textarea.update_command(self.contentModified)
        self.Textarea.font = self.FontFamily
        self.Textarea.text_size = self.FontSize

        self.App.when_closed = self.closeApp


    def FormatDoc(self):
        window = guizero.Window(self.App, "Format Document",width=200, height=175, layout="box")
        
        label = guizero.Text(window, "Select Language\n")
        label.text_size = 10
        
        value = guizero.ListBox(window, [
            "JSON", "HTML"
        ], height=50, width= 175, scrollbar=True)

        guizero.PushButton(window, text="Format", command=self.FormatDocument, args=(value,window))

    
    def FormatDocument(self, pl, window):
        is_formatted = False

        if(pl.value == "JSON"):
            try:
                value = json.dumps(json.loads(self.Textarea.value), indent=4)
            except json.decoder.JSONDecodeError:
                window.error("Format document", "Parsing failed!")
            else:
                is_formatted = True
                self.Textarea.value = value

        elif(pl.value == "HTML"):
            try:
                doc = lxml.html.fromstring(self.Textarea.value)
                value = lxml.html.tostring(doc, pretty_print=True)
            except lxml.etree.ParserError:
                window.error("Format document", "Parsing failed!")
            else:
                is_formatted = True
                self.Textarea.value = value.decode()

        if is_formatted:
            self.FileModified = True
        window.destroy()


    def contentModified(self):
        if len(self.Textarea.value) > 1:
            self.FileModified = True
        else:
            if self.File:
                self.FileModified = True
            else:
                self.FileModified = False

    
    def closeApp(self):
        if self.FileModified:
            que = self.App.yesno("File modified","Do you want to save file content?")
            
            if que:
                self.SaveFile()

        self.App.destroy()


    def setFont(self, e, e1, window):
        self.FontFamily = e.value
        self.FontSize = e1.value

        self.Textarea.font = self.FontFamily
        self.Textarea.text_size = self.FontSize

        window.destroy()


    def FontSettings(self):
        window = guizero.Window(
            master=self.App, 
            title="Font Settings", 
            width=400, 
            height=300, 
            layout="grid"
        )
        
        label1 = guizero.Text(
            window,"Font family", 
            grid=[0,0], 
            align="left"
        )
        label1.text_size = 10

        family = guizero.ListBox(window,
            items=[
            "Arial", "Calibri", "Courier", "Georgia", "Verdana", "Tahoma", "Times", "Trebuchet MS"
            ], 
            grid=[0,1], 
            scrollbar=True, 
            height=100, 
            width=100, 
            selected=self.FontFamily
        )

        label2 = guizero.Text(
            window,"Font size", 
            grid=[1,0], 
            align="left"
        )
        label2.text_size = 10

        size = guizero.ListBox(
            window,
            list(x for x in range(8,32, 4))+list(x for x in range(32, 124,6)), 
            width=100, 
            height=100, 
            grid=[1, 1], 
            scrollbar=True, 
            selected=self.FontSize
        )

        guizero.PushButton(window, command=self.setFont, args=(family, size, window), text="Update font", grid=[3,3])


    def FileInfo(self):
        if not self.File:
            self.App.error("File info", "Please select a file to get details.")
            return

        stats = os.stat(self.File.name)
        window = guizero.Window(self.App, "File info : {}".format(self.File.name), width=400, height=500, layout="grid")
        window.text_size = 10

        guizero.Text(window, "", grid=[0,0])
        guizero.Text(window, "", grid=[1, 0])

        guizero.Text(window, "File : ", grid=[0,1], align="right")
        guizero.Text(window, self.File.name, grid=[1, 1], align="left")

        guizero.Text(window, "Created at : ", grid=[0,2], align="right")
        guizero.Text(window, datetime.datetime.fromtimestamp(stats.st_ctime).strftime("%d/%m/%Y %H:%M:%S"), grid=[1,2], align="left")

        guizero.Text(window, " Last modified at : ", grid=[0,3], align="right")
        guizero.Text(window, datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%d/%m/%Y %H:%M:%S"), grid=[1,3], align="left")

        guizero.Text(window, "File size : ", grid=[0,4], align="right")
        guizero.Text(window, "{:.2f} KB(s)".format(stats.st_size/1024), grid=[1,4], align="left")

        m = mimetypes.MimeTypes()
        mimetype = m.guess_type(self.File.name)[0]

        if not mimetype:
            mimetype = "Undefined"
            
        guizero.Text(window, "File type : ", grid=[0,5], align="right")
        guizero.Text(window, mimetype, grid=[1,5], align="left")

        guizero.Text(window, "Total lines : ", grid=[0,6], align="right")
        guizero.Text(window, len(self.Textarea.value.splitlines()), grid=[1,6], align="left")

        guizero.Text(window, "Total words : ", grid=[0,7], align="right")
        guizero.Text(window, len(self.Textarea.value.split(" ")), grid=[1,7], align="left")

        guizero.Text(window, "Total characters : ", grid=[0,8], align="right")
        guizero.Text(window, len(self.Textarea.value), grid=[1,8], align="left")

    
    def NewFile(self):
        self.Textarea.value = ""
        self.File = None
        self.FileModified = None
        self.App.title = "Notepad Mini"
        
    
    def OpenFile(self):
        file = guizero.filedialog.askopenfile(mode="r",filetypes=self.Filetypes)
        if not file:
            return

        try:
            self.Textarea.value = file.read()
            self.File = file
        except UnicodeDecodeError:
            self.App.error(
                "File data error",
                "File contains data in another format!"
            )
        else:
            self.App.title = "Notepad Mini File : {}".format(file.name)
        
        finally:
            file.close()
        
        self.FileModified = False
        

    def SaveFile(self):
        if not self.File:
            file = guizero.filedialog.asksaveasfile("w", 
            defaultextension=".txt", 
            filetypes=self.Filetypes
            )
            if not file:
                return
            self.File = file

        if self.File.closed:
            self.File = open(self.File.name, "w")
        self.File.write(self.Textarea.value)
        self.File.close()

        self.FileModified = False

notepad = NotepadMini()
notepad.App.display()
