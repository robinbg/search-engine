import webbrowser
from tkinter import *
from se import SEARCH_ENGINE

class SE_GUI:
    def __init__(self):
        ''' Create main window, add widgets, construct search engine, and run.'''
        self.add_widgets()

        self.search_engine = SEARCH_ENGINE()

        self.main_window.mainloop()



# Setting up widgets
    def add_widgets(self):
        ''' Create main window, then add all widgets to it.'''
        self.create_main_window()
        self.add_search_bar()
        self.add_search_button()
        self.add_results_label()
        self.add_results()
        self.add_prev_button()
        self.add_next_button()

# Creating Widgets
    def create_main_window(self):
        ''' Make main window, label and resize it.'''
        self.main_window = Tk()
        self.main_window.title("Search Engine Project")
        self.main_window.geometry("700x700")

    def add_search_bar(self):
        ''' Create search bar, add it to the pack layout, then make pressing enter process the search.'''
        self.search_bar = Entry(self.main_window, bd = 5, font = 'Arial')
        self.search_bar.pack(side = TOP, anchor = W, expand = True, fill = X, padx = 20, pady = 10)
        self.search_bar.bind('<Return>', self.process_search)

    def add_search_button(self):
        ''' Create search button with command as processing the search. Then, add the button to the pack layout.'''
        self.search_button = Button(self.main_window, text = 'Search', command = self.process_search)
        self.search_button.pack(side = TOP, anchor = W, expand = True, fill = X, padx = 20)

    def add_results_label(self):
        ''' Create label for displaying total search results for the queried term. Add it to the pack layout.'''
        self.results_label = Label(self.main_window, font = 'Arial')
        self.results_label.pack(side = TOP, anchor = W, expand = True, fill = X, padx = 20)

    def add_results(self):
        ''' Create 20 labels to display results when process_search is called. Add labels to the pack layout,
            and add hyperlinking for left clicking labels. Finally, add the labels to a list for later access.'''
        self.results_label_list = list()
        for i in range(20):
            label = Label(self.main_window, font = ('Arial', 10), fg = 'blue', cursor = 'hand2', anchor = W)
            label.pack(side = TOP, anchor = W, padx = 20)
            label.bind("<Button-1>", self.hyperlink)
            self.results_label_list.append(label)

    def add_next_button(self):
        ''' Create next button to paginate search results. Pressing will show the next 20 highest ranked results.'''
        self.next_button = Button(self.main_window, text = "Next Page", command = self.next_page)
        self.next_button.pack(side = LEFT, anchor = W, expand = True, fill = X, padx = 20, pady = 10)

    def add_prev_button(self):
        ''' Create previous button to paginate search results. Pressing will show the previous 20 highest ranked results.'''
        self.prev_button = Button(self.main_window, text = "Prev Page", command = self.prev_page)
        self.prev_button.pack(side = LEFT, anchor = W, expand = True, fill = X, padx = 20, pady = 10)

# Commands and functionality
    def hyperlink(self, event):
        ''' On clicking label, retrieve label's text and open it in a web browser.'''
        webbrowser.open_new(event.widget.cget('text'))

    def next_page(self):
        ''' Command for next button. Replaces the currently displayed urls with the next 20 highest ranked results.''' 
        try:
            for i in range(self.current_page * 20, (self.current_page + 1) * 20):
                self.results_label_list[i - (20 * self.current_page)]['text'] = self.search_engine.docpairs[self.search_results[i]]
            self.current_page += 1
        except IndexError:
            empty_index = i - (20 * self.current_page)
            if empty_index != 0:
                for j in range(empty_index, 20):
                    self.results_label_list[j]['text'] = ''
                self.current_page += 1

    def prev_page(self):
        ''' Command for previous button. Replaces the currently displayed urls with the previous 20 highest ranked results.'''
        previous_page = self.current_page - 1
        if previous_page > 0:
            for i in range(20):
                self.results_label_list[i]['text'] = self.search_engine.docpairs[self.search_results[i + (20 * (previous_page - 1))]]
            self.current_page -= 1

    def process_search(self, event = None):
        ''' Query the search engine object, returning the top 20 highest ranked results for the query as the new labels.'''
        try:
            self.clear_results()
            self.current_page = 1
            query = self.search_bar.get()
            self.search_results = self.search_engine.query(query)
            self.results_label['text'] = "{} results for \"{}\"".format(len(self.search_results), query)
            for i in range(20):
                try:
                    self.results_label_list[i]['text'] = self.search_engine.docpairs[self.search_results[i]]
                except IndexError:
                    pass
        except KeyError:
            self.results_label['text'] = "Search not performed - word not in index, or invalid input."

    def clear_results(self):
        ''' Clear the text in the result labels.'''
        for i in range(20):
            self.results_label_list[i]['text'] = ''



