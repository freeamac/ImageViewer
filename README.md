# ImageViewer
View images based on a custom formatted XML description file

## XML Document Type Definition
This is the Document Type Definition required in the xml file driving the ImageViewer:

```
<!-- DTD for an image slide show -->
<!ELEMENT slideshow (title, copyright?, picture+)>
<!ELEMENT title (#PCDATA)>
<!ELEMENT copyright (#PCDATA)>
<!ELEMENT picture (image, caption, date, location, asa?, roll_num?, roll_max?)>
<!ELEMENT image (#PCDATA)>
<!ELEMENT caption (#PCDATA)>
<!ELEMENT date (#PCDATA)>
<!ELEMENT location (#PCDATA)>
<!ELEMENT asa (#PCDATA)>
<!ELEMENT roll_num (#PCDATA)>
<!ELEMENT roll_max (#PCDATA)>
```

## Key Bindings
In the automated slideshow mode, the following key bindings are available:

| Key Binding | Action |
|---|---|
| \<Esc\> | Exit Slideshow |

In manual display mode, the following key bindings are available:

| Key Binding | Action |
|---|---|
| \<Left\> | Go To Previous Image |
| \<Right\> | Go To Next Image |
| \<Escape\> | Go To First Image |

## Creating Standalone Executable

Use [PyInstaller](https://pyinstaller.org/en/stable/) as follows in Powershell to create a standalone Windows executable:

```
pyinstaller ImageViewer.spec
```

and the standalone executable will be found in the *dist* folder.
