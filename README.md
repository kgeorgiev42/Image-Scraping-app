# Image-Scraping-app

Simple image scraping app made with Python 3 and the tkinter GUI.
This app is an improved version of an example one of the same type published in the book 'Learning Python' available in [Packt](www.packtpub.com).

## Requirements

 - Python version 3.6 or higher
 - beautifulsoup4 - 4.4.0
 - requests - 2.7.0
 
## Usage

To test out the app from a local server you can manually edit the `index.html` file in the `simple_server` folder.
To start the server you can either:
1. Navigate to the `simple_server`, open up a command prompt and type: `python -m http.server 8000`. This will create the server on the selected port.
2. Execute the `serve.sh` scripts which does the same as the above.
3. The corresponding URL in the app will then be: 'http://localhost:(selected port)'

## Example
#### Layout
![Layout](https://github.com/JadeBlue96/Image-Scraping-app/blob/master/layout.PNG)
#### Right-clicking a single item previews the selected image.
![Preview](https://github.com/JadeBlue96/Image-Scraping-app/blob/master/preview.PNG)
