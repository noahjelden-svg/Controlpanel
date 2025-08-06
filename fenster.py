import webview

# Erstelle ein Fenster mit einer Webseite
webview.create_window('Control', 'http://192.168.1.206:5000/', width=800, height=600, resizable=True)

# Starte die App
webview.start()
