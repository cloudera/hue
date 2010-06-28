import os
import webbrowser

def main():
    '''
    Show html documentation using webbrowser
    '''
    index_html = os.path.join(os.path.dirname(__file__), 'index.html')
    webbrowser.open(index_html)

if __name__ == '__main__':
    main()
