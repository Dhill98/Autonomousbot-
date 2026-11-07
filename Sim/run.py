import threading
from api import app
from visual import main



def start_api():
    app.run(debug=False,use_reloader=False)#diable flask debuger and turns off reloader so it wont try to restart in another process

if __name__ == "__main__":
    api_thread = threading.Thread(target=start_api,daemon=True) #create thread object 
    api_thread.start()
    main()