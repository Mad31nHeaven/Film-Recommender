# from sklearn.preprocessing import MinMaxScaler
# from tensorflow.keras.models import Model
# from tensorflow.keras.layers import Input, Dense, Concatenate
# from tensorflow.keras.optimizers import Adam


import tkinter as tk
from collaborative import return_collab_filt
from tkinter import messagebox,ttk, IntVar
import hashlib
import pandas as pd
import sqlite3
import numpy as np

reader_movies = pd.read_csv("Movie/movies.csv")


connection=sqlite3.connect('User_Data.db')
cursor=connection.cursor()
command1=""" CREATE TABLE IF NOT EXISTS
login_data(user_id INTEGER PRIMARY KEY AUTOINCREMENT, USERNAME TEXT UNIQUE, PASSWORD TEXT)"""
command2="""CREATE TABLE IF NOT EXISTS
rating_data(user_id INTEGER PRIMARY KEY, cosine_sim TEXT,FOREIGN KEY(user_id) REFERENCES login_data(user_id))"""

command4="""
CREATE TABLE IF NOT EXISTS user_rated_movies (
    user_id INTEGER, movie_id INTEGER, rating INTEGER, PRIMARY KEY (user_id, movie_id), FOREIGN KEY (user_id) REFERENCES login_data(user_id))"""
command5="""CREATE TABLE IF NOT EXISTS watchlist (
user_id INTEGER, title TEXT, PRIMARY KEY (user_id, title))"""
command6="""CREATE TABLE IF NOT EXISTS saved_users (
user_id INTEGER, username TEXT, PRIMARY KEY (user_id,username))"""
cursor.execute(command1)
cursor.execute(command2)
cursor.execute(command4)
cursor.execute(command5)
cursor.execute(command6)
# cursor.execute("DELETE FROM rating_data")
# cursor.execute("DELETE FROM user_rated_movies")
# cursor.execute("DELETE FROM watchlist")



cursor.execute("SELECT * FROM user_rated_movies")
tables = cursor.fetchall()
print("Tables:", tables)
cursor.execute("SELECT * FROM rating_data")
tables = cursor.fetchall()
print("Tables:", tables)
connection.commit()
connection.close()


def convert_numpy(id):
    binarized_genres = reader_movies[reader_movies['movieId'] == id]['binarized_genres'].iloc[0]
    clean_genre=binarized_genres.strip('[]').split()
    return np.array(clean_genre,dtype=int)
def get_cos_sim(movieId):
    main_genre=convert_numpy(movieId)
    cosine_sims = []
    for i in range(len(reader_movies)):
        current_movieId = reader_movies['movieId'][i]
        current_vector = convert_numpy(current_movieId)
        dot_product = np.dot(main_genre, current_vector)
        magnitude_product = np.linalg.norm(main_genre) * np.linalg.norm(current_vector)
        if magnitude_product!=0:
            cosine_sim = dot_product / magnitude_product
        else:
            cosine_sim=0
        cosine_sims.append(cosine_sim)

    return cosine_sims

movie_titles = reader_movies['title'].tolist()
all_genres = np.array([convert_numpy(mid) for mid in reader_movies['movieId']])

class FilmSuggester:
    def __init__(self, root):
        self.show=False
        self.hash = hashlib.sha256
        self.menu = root
        self.menu.title("Film/Song Suggester")
        self.center_window(self.menu,600,300)
        self.menu.config(background='#483864')
        self.label = tk.Label(root, text="Recommender MENU")
        self.label.pack(pady=10)

        self.button_login = tk.Button(root, text="Log in", font=('Arial', 15, 'bold'),command=self.log_in)
        self.button_login.pack(pady=10)
        self.button_signup = tk.Button(root, text="Sign up", font=('Arial', 15, 'bold'),command=self.sign_up)
        self.button_signup.pack(pady=10)
        self.buttonEXIT=tk.Button(root, text="Exit", font=('Arial', 15, 'bold'),command=root.destroy)
        self.buttonEXIT.pack(pady=10)
        self.sign_up_window=None
        self.log_in_window=None
    def return_menu(self):
        if self.sign_up_window is not None and self.sign_up_window.winfo_exists():

            self.sign_up_window.withdraw()
            self.sign_up_window=None
        elif self.log_in_window is not None and self.log_in_window.winfo_exists():
            self.log_in_window.withdraw()
            self.log_in_window=None
        self.menu.deiconify()

    def sign_up(self):
        self.menu.withdraw()
        self.sign_up_window=tk.Tk()
        self.sign_up_window.title('Sign Up')
        self.center_window(self.sign_up_window,600, 400)
        self.sign_up_window.config(background='#483864')
        self.signup_label = tk.Label(self.sign_up_window, text='SIGN UP')
        self.signup_label.pack(pady=10)
        self.username_signup_label=tk.Label(self.sign_up_window,text='Enter your username')
        self.username_signup_label.pack(pady=20)
        self.username_signup_entry=tk.Entry(self.sign_up_window, width=30,background='#485864')
        self.username_signup_entry.pack(pady=10)
        self.password_signup_label = tk.Label(self.sign_up_window, text='Enter your password')
        self.password_signup_label.pack(pady=20)
        self.password_signup_entry = tk.Entry(self.sign_up_window, width=30, background='#485864',show='*')
        self.password_signup_entry.pack(pady=10)
        self.button_signup_confirm=tk.Button(self.sign_up_window,text='Confirm', font=('Arial', 15, 'bold'),command=self.confirm_signup)
        self.button_signup_confirm.pack(pady=10)
        button_return_menu=tk.Button(self.sign_up_window,text='Return', font=('Arial',15,'bold'),command=self.return_menu)
        button_return_menu.pack(pady=10)
        self.button_changeshow_signup=tk.Button(self.sign_up_window, text='Show', font=('Arial', 7, 'bold'),command=self.change_show_signup)
        self.button_changeshow_signup.pack(padx=10)
    def change_show_login(self):
        if self.show==True:
            self.password_login_entry.config(show='*')
            self.button_changeshow_login.config(text='Show')
            self.show=False
        else:
            self.password_login_entry.config(show='')
            self.button_changeshow_login.config(text='Hide')
            self.show=True
    def change_show_signup(self):
        if self.show==True:
            self.password_signup_entry.config(show='*')
            self.button_changeshow_signup.config(text='Show')
            self.show=False
        else:
            self.password_signup_entry.config(show='')
            self.button_changeshow_signup.config(text='Hide')
            self.show=True
    def log_in(self):

        self.menu.withdraw()
        self.log_in_window=tk.Tk()
        self.log_in_window.title('Log In')
        self.center_window(self.log_in_window,600,400)
        self.log_in_window.config(background='#483864')
        self.login_label = tk.Label(self.log_in_window, text='LOG IN')
        self.login_label.pack(pady=10)
        self.username_login_label = tk.Label(self.log_in_window, text='Enter your username')
        self.username_login_label.pack(pady=20)
        self.username_login_entry = tk.Entry(self.log_in_window, width=30, background='#485864')
        self.username_login_entry.pack(pady=10)
        self.password_login_label = tk.Label(self.log_in_window, text='Enter your password')
        self.password_login_label.pack(pady=20)
        self.password_login_entry = tk.Entry(self.log_in_window, width=30, background='#485864',show='*')
        self.password_login_entry.pack(pady=10)
        self.button_login_confirm = tk.Button(self.log_in_window, text='Confirm', font=('Arial', 15, 'bold'), command=self.confirm_login)
        self.button_login_confirm.pack(pady=10)
        button_return_menu = tk.Button(self.log_in_window, text='Return', font=('Arial', 15, 'bold'),
                                       command=self.return_menu)
        button_return_menu.pack(pady=5)
        self.button_changeshow_login=tk.Button(self.log_in_window, text='Show', font=('Arial', 7, 'bold'),command=self.change_show_login)
        self.button_changeshow_login.pack(padx=5)
        self.var1 = tk.IntVar(master=self.log_in_window)
        self.check_remember_later=tk.Checkbutton(self.log_in_window, text='Remember on this device',font=('Arial', 15, 'bold'),variable=self.var1, onvalue=1, offvalue=0)
        self.check_remember_later.pack(pady=5)

    def goBack_com(self):
        self.FilmsApp.withdraw()
        self.recommender_APP.deiconify()
    def goBack_frompredictions(self):

        self.ratings_root.withdraw()
        self.FilmsApp.deiconify()
    def search(self,event):
        entry=event.widget.get()
        if entry!='':
            self.dropdown_movie['values']=[movie for movie in movie_titles if entry.lower() in movie.lower() and movie not in
                                           list(self.dropdown_previous_rating['values'])]
        else:
            self.dropdown_movie['values']=[movie for movie in movie_titles if movie not in list(self.dropdown_previous_rating['values'])]

    def save(self):
        rating=self.dropdown_rating.get()
        movie=self.dropdown_movie.get()
        if rating!='' and movie!='' and rating in self.dropdown_rating['values'] and movie in self.dropdown_movie['values']:
            movie_id=reader_movies[reader_movies['title']==movie]['movieId'].iloc[0]
            print(movie_id)
            cosine_similarity=(np.array(get_cos_sim(movie_id))*int(rating)).tolist()

            connection = sqlite3.connect("User_Data.db")
            cursor = connection.cursor()
            cursor.execute('SELECT cosine_sim FROM rating_data WHERE user_id=?',(self.user_id,))
            row = cursor.fetchone()
            if row:

                previous_cosine= eval(row[0])
                new_cosine = (np.array(cosine_similarity) + np.array(previous_cosine)).tolist()

                cursor.execute("UPDATE rating_data SET cosine_sim=? WHERE user_id=?",
                               (str(new_cosine),self.user_id))
                connection.commit()


                print('existing')
            else:
                new_cosine=cosine_similarity
                cursor.execute("INSERT INTO rating_data (user_id,cosine_sim) VALUES (?,?)",
                               (self.user_id, str(new_cosine)))
                connection.commit()

                print('new')

            cursor.execute('''
                INSERT OR REPLACE INTO user_rated_movies (user_id, movie_id,rating)
                VALUES (?, ?, ?)
            ''', (self.user_id, int(movie_id), int(rating)))
            cursor.execute("SELECT * FROM user_rated_movies")
            tables = cursor.fetchall()
            print("Tables:", tables)
            connection.commit()
            connection.close()
            current_movies=list(self.dropdown_movie['values'])

            if movie in current_movies:
                current_movies.remove(movie)
            self.dropdown_movie['values']=current_movies

            current_rated=list(self.dropdown_previous_rating['values'])
            if movie not in current_rated:
                current_rated.append(movie)
            self.dropdown_previous_rating['values']=current_rated
            self.dropdown_movie.set('')
            self.dropdown_previous_rating.set('')
            self.dropdown_rating.set('')
            self.update_titles()
    def get_values(self):
        connection = sqlite3.connect("User_Data.db")
        cursor = connection.cursor()
        cursor.execute('SELECT movie_id`` FROM user_rated_movies WHERE user_id=?', (self.user_id,))
        movie_id_tuples = cursor.fetchall()
        print(movie_id_tuples)
        movie_ids = [id[0] for id in movie_id_tuples]
        connection.close()
        print(movie_ids)
        if not movie_ids:
            return []
        filtered_movies = reader_movies[reader_movies['movieId'].isin(movie_ids)]

        return filtered_movies['title'].tolist()
    def remove(self):
        movie=self.dropdown_previous_rating.get()
        if movie!='' and movie in self.dropdown_previous_rating['values']:
            movie_iden = int(reader_movies[reader_movies['title'] == movie]['movieId'].iloc[0])
            print(movie_iden)
            connection = sqlite3.connect("User_Data.db")
            cursor = connection.cursor()
            cursor.execute('SELECT cosine_sim FROM rating_data WHERE user_id=?',(self.user_id,))
            row = cursor.fetchone()
            cosine_sim = eval(row[0])
            cursor.execute('SELECT rating FROM user_rated_movies WHERE user_id=? AND movie_id=?', (self.user_id,movie_iden))
            row = cursor.fetchone()
            print(row)


            rating=row[0]
            new_cosine_similarity=(np.array(cosine_sim)-(np.array(get_cos_sim(movie_iden))*int(rating))).tolist()
            cursor.execute('DELETE FROM user_rated_movies WHERE user_id=? AND movie_id=?', (self.user_id,movie_iden))
            cursor.execute("UPDATE rating_data SET cosine_sim=? WHERE user_id=?",
                           (str(new_cosine_similarity),self.user_id))
            cursor.execute("SELECT * FROM user_rated_movies")
            tables = cursor.fetchall()
            print("Tables:", tables)
            connection.commit()
            connection.close()
            current_rated=list(self.dropdown_previous_rating['values'])
            if movie in current_rated:
                current_rated.remove(movie)
            self.dropdown_previous_rating['values']=current_rated

            current_movies=list(self.dropdown_movie['values'])
            if movie not in current_movies:
                current_movies.append(movie)
            self.dropdown_movie['values']=current_movies
            self.dropdown_movie.set('')
            self.dropdown_previous_rating.set('')
            self.dropdown_rating.set('')
            self.update_titles()
    def update_titles(self):
        connection = sqlite3.connect("User_Data.db")
        cursor = connection.cursor()
        cursor.execute('SELECT movie_id FROM user_rated_movies WHERE user_id=?', (self.user_id,))
        movie_id_tuples = cursor.fetchall()
        movie_ids = [id[0] for id in movie_id_tuples]
        cursor.execute('SELECT rating FROM user_rated_movies WHERE user_id=?', (self.user_id,))
        rating_tuples = cursor.fetchall()
        ratings = [rating[0] for rating in rating_tuples]
        cursor.execute('SELECT user_id FROM saved_users')

        if movie_ids and ratings:
            new_movieids = movie_ids
            new_userid = [self.user_id] * len(movie_ids)
            new_ratings = ratings
            self.movies_titles = return_collab_filt(new_userid, new_movieids, new_ratings)
            self.my_listbox = tk.Listbox(self.ratings_root,width=50, height=10,selectmode=tk.SINGLE)
            self.my_listbox.grid(row=0, column=2, sticky='nw')
            for i in range(len(self.movies_titles)):
                self.my_listbox.insert(i, self.movies_titles[i])
        else:
            print('empty')
            self.movies_titles = []

    def add_to_watchlist(self):
        connection = sqlite3.connect("User_Data.db")
        cursor = connection.cursor()
        selected_indices = self.my_listbox.curselection()
        if selected_indices:
            title = self.my_listbox.get(selected_indices[0])
            messagebox.showinfo("Selection", f"Selected: {title}")
            print(title)
            cursor.execute('''
                            INSERT OR REPLACE INTO watchlist (user_id,title)
                            VALUES (?, ?)
                        ''', (self.user_id, str(title)))
            connection.commit()
            connection.close()
        else:
            messagebox.showwarning("Not selected", "Please select an item.")

    def get_user_watchlist(self):
        connection = sqlite3.connect("User_Data.db")
        cursor = connection.cursor()
        cursor.execute('SELECT title FROM watchlist WHERE user_id=?', (self.user_id,))
        titles_tuples = cursor.fetchall()
        print(titles_tuples)
        titles = [title[0] for title in titles_tuples]
        print(titles)
        connection.close()
        return titles
    def Alter_Ratings_window(self):
        self.FilmsApp.withdraw()
        self.ratings_root=tk.Tk()
        self.ratings_root.title('Alter Ratings')
        self.center_window(self.ratings_root,600,300)
        self.ratings_root.config(background='#483864')
        self.values_rated = self.get_values()
        self.values_to_rate = [movie for movie in movie_titles if movie not in self.values_rated]
        self.dropdown_movie=ttk.Combobox(self.ratings_root,values=self.values_to_rate)
        self.dropdown_movie.bind('<KeyRelease>',self.search)
        self.dropdown_movie.grid(row=0,column=0,sticky='ne')



        self.dropdown_rating = ttk.Combobox(self.ratings_root, values=[1,2,3,4,5])
        self.dropdown_rating.grid(row=0,column=0,pady=30,sticky='ne')
        self.dropdown_rating.bind('<KeyRelease>')
        self.button_confirm=tk.Button(self.ratings_root,text='Confirm',command=self.save)
        self.button_confirm.grid(row=0,column=0,pady=60,sticky='ne')
        self.dropdown_previous_rating = ttk.Combobox(self.ratings_root, values=self.values_rated)
        self.dropdown_previous_rating.grid(row=0,column=1,sticky='ne')
        self.dropdown_previous_rating.bind('<KeyRelease>')
        self.button_remove=tk.Button(self.ratings_root,text='Remove',command=self.remove)
        self.button_remove.grid(row=0,column=1,pady=30,sticky='ne')
        self.button_comeback_frompredictions=tk.Button(self.ratings_root,text='Come Back', command=self.goBack_frompredictions)
        self.button_comeback_frompredictions.grid(row=3,column=0,pady=30,sticky='ne')
        self.button_add_to_watchlist=tk.Button(self.ratings_root, text='Add to watchlist',command=self.add_to_watchlist)
        self.button_add_to_watchlist.grid(row=3,column=1,pady=10,sticky='ne')

        self.update_titles()



    def Films(self):
        self.recommender_APP.withdraw()
        self.FilmsApp = tk.Tk()
        self.FilmsApp.title('Film Recommenda')
        self.center_window(self.FilmsApp, 600, 300)
        self.FilmsApp.config(background='#483864')
        self.alterRatings = tk.Button(self.FilmsApp, text='Alter Ratings', font=('Arial', 15, 'bold'),command=self.Alter_Ratings_window)
        self.alterRatings.pack(pady=10)
        self.watchlistbutton=tk.Button(self.FilmsApp, text='Watchlist', font=('Arial', 15, 'bold'),command=self.watchlist)
        self.watchlistbutton.pack(pady=10)
        self.goBack = tk.Button(self.FilmsApp, text='Return', font=('Arial', 15, 'bold'),command=self.goBack_com)
        self.goBack.pack(pady=10)
    def com_from_watchlist(self):
        self.watchlistroot.withdraw()
        self.FilmsApp.deiconify()
    def remove_watchlist_command(self):
        selected_indices=self.watchlistbox.curselection()
        if selected_indices:
            title=self.watchlistbox.get(selected_indices[0])
            connection = sqlite3.connect("User_Data.db")
            cursor = connection.cursor()
            cursor.execute('DELETE FROM watchlist WHERE user_id=? AND title=?', (self.user_id, title))
            messagebox.showinfo("Removal", f"Deleted: {title}")
            print(title)
            self.watchlistbox.delete(selected_indices[0])
            connection.commit()
            connection.close()
        else:
            messagebox.showerror("Error", "No movie was selected for removal")

    def watchlist(self):
        self.FilmsApp.withdraw()
        self.watchlistroot=tk.Tk()
        self.watchlistroot.title('Watchlist')
        self.center_window(self.watchlistroot, 600, 300)
        self.watchlistroot.config(background='#483864')
        titles=self.get_user_watchlist()
        self.watchlistscrollbar=tk.Scrollbar(self.watchlistroot,orient=tk.VERTICAL)
        self.watchlistscrollbar.grid(row=0, column=1, sticky='n')
        self.watchlistbox=tk.Listbox(self.watchlistroot,selectmode=tk.SINGLE,height=10,width=50,yscrollcommand=self.watchlistscrollbar.set)
        self.watchlistbox.grid(row=0,column=0,sticky='n')
        self.watchlistscrollbar.config(command=self.watchlistbox.yview)
        self.remove_from_watchlist=tk.Button(self.watchlistroot,text='Remove',font=('Arial',15,'bold'),command=self.remove_watchlist_command)
        self.remove_from_watchlist.grid(row=1,column=0,sticky='n')
        self.return_from_watchlist=tk.Button(self.watchlistroot,text='Return', font=('Arial',15,'bold'),command=self.com_from_watchlist)
        self.return_from_watchlist.grid(row=2,column=0,sticky='n')
        for i in range(len(titles)):
            self.watchlistbox.insert(i, titles[i])


    def log_out_com(self):
        self.recommender_APP.withdraw()
        self.menu.deiconify()
    def retrieve_saved_users(self):
        connection=sqlite3.connect("User_Data.db")
        cursor=connection.cursor()
        cursor.execute('SELECT user_id FROM saved_users')
        userids_tuples = cursor.fetchall()
        print(userids_tuples)
        self.userids_saved=[userid[0] for userid in userids_tuples if userid[0]!=self.user_id]
        cursor.execute('SELECT username FROM saved_users')
        username_tuples = cursor.fetchall()
        print(username_tuples)
        self.usernames_saved = [username[0] for username in username_tuples if username[0]!=self.username]
        connection.commit()
        connection.close()

    def command_switch_account(self):
        username_selected=self.dropdown_saved_users.get()
        connection=sqlite3.connect("User_Data.db")
        cursor=connection.cursor()
        cursor.execute('SELECT user_id FROM saved_users WHERE username=?',(username_selected,))
        self.user_id=cursor.fetchone()[0]
        self.username=username_selected
        self.username_LABEL.configure(text=f'Username: {self.username}')
        self.retrieve_saved_users()
        self.dropdown_saved_users.configure(values=self.usernames_saved)
        connection.commit()
        connection.close()
    def RECOMMENDER(self):
        self.log_in_window.withdraw()
        self.recommender_APP=tk.Tk()
        self.recommender_APP.title('Recommenda')
        self.center_window(self.recommender_APP,600,300)
        self.recommender_APP.config(background='#483864')
        self.option = tk.Label(self.recommender_APP, text='Pick an option')
        self.option.pack(pady=10)
        self.film=tk.Button(self.recommender_APP,text='FILM',font=('Arial', 15, 'bold'),command=self.Films)
        self.film.pack(pady=10)

        self.log_out=tk.Button(self.recommender_APP,text='LOG OUT',font=('Arial', 15, 'bold'),command=self.log_out_com)
        self.log_out.pack(pady=10)
        self.username_LABEL = tk.Label(self.recommender_APP, text=f'Username: {self.username}',font=('Arial', 15, 'bold'))
        self.username_LABEL.pack(padx=30)
        self.retrieve_saved_users()
        self.dropdown_saved_users = ttk.Combobox(self.recommender_APP, values=self.usernames_saved)
        self.dropdown_saved_users.pack(pady=10)
        self.button_switch_accounts=tk.Button(self.recommender_APP,text='Switch account',font=('Arial',15,'bold'),command=self.command_switch_account)
        self.button_switch_accounts.pack(pady=10)
    def confirm_login(self):
        self.username = self.username_login_entry.get().replace(" ", "")
        password = self.password_login_entry.get().replace(" ", "")
        print(password)
        username_bytes = self.username.encode('utf-8')
        password_bytes = password.encode('utf-8')
        hashed_username = self.hash(username_bytes).hexdigest()
        hashed_password = self.hash(password_bytes).hexdigest()
        details=hashed_username+","+hashed_password
        connection=sqlite3.connect("User_Data.db")
        command = "SELECT user_id FROM login_data WHERE username=? AND password=?"
        cursor=connection.cursor()
        cursor.execute(command, (hashed_username, hashed_password))
        data=cursor.fetchone()
        if data:
            self.user_id=620+data[0]
            if self.var1.get()==1:
                print('You saved')
                cursor.execute("INSERT OR REPLACE INTO saved_users (user_id,username) VALUES (?,?)",
                           (self.user_id, self.username))
                connection.commit()
                print('inserted')
            messagebox.showinfo('Success',"Account is logged in successfully!")

            self.RECOMMENDER()
            self.show = False
        else:
            messagebox.showerror("Error",'Incorrect password or username')
        connection.close()

    def confirm_signup(self):
        username = self.username_signup_entry.get().replace(" ", "")
        password = self.password_signup_entry.get().replace(" ", "")
        print(password)
        if username == "" or password == "":
            tk.messagebox.showerror("Error", "You need to enter in both fields!")
        else:
            username_bytes = username.encode('utf-8')
            password_bytes = password.encode('utf-8')
            hashed_username = self.hash(username_bytes).hexdigest()
            hashed_password = self.hash(password_bytes).hexdigest()
            connection = sqlite3.connect("User_Data.db")
            cursor = connection.cursor()


            try:
                cursor.execute("INSERT INTO login_data (username, password) VALUES (?, ?)",
                               (hashed_username, hashed_password))
                connection.commit()

                messagebox.showinfo("Success", "Account created successfully!")
                self.sign_up_window.destroy()
                new_root = tk.Tk()
                app = FilmSuggester(new_root)
                self.show = False
                new_root.mainloop()

            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username is already taken!")
            finally:
                connection.close()

    def center_window(self,window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")
if __name__ == "__main__":
    root = tk.Tk()
    app = FilmSuggester(root)
    root.mainloop()