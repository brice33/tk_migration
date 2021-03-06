from window import *
from sqlite3 import *
import psycopg2

data_connect_window = fenetre()
data_connect_window.create("Connectez vous au base de donnée", 600, 350)
data_connect_window = data_connect_window.fen
# variable
global base
base= connect("data")
data_save= base.cursor()

db_input = StringVar()
db_input_user = StringVar()
db_input_pass = StringVar()

db_output = StringVar()
db_output_user = StringVar()
db_output_pass = StringVar()
i=0
user_in = StringVar()
# frame

connect_frame = Frame(data_connect_window, bg="white")
main_frame = Frame(data_connect_window, bg="white")
frame_bar = Frame(main_frame, bg="white")
frame_bar_1 = Frame(main_frame, bg="white")
frame_bar_2 = Frame(main_frame, bg="white")

# Connection base de donnée input

frame_in = Frame(connect_frame, bg="white")
base_input_frame = LabelFrame(
    frame_in, text="Base de donnée source", bg='white', fg="black")
label_dbsource = Label(
    base_input_frame, text="Nom de la base de donnée initiale", bg='white', fg="black").pack()
base_input_dbsource = Entry(
    base_input_frame, bg='white', fg="black", textvariable=db_input).pack()
user_dbsource = Label(
    base_input_frame, text="Nom d'utilisateur", bg='white', fg="black").pack()
user_dbsource_in = Entry(base_input_frame, bg='white',
                         fg="black", textvariable=db_input_user).pack()
pass_dbsource = Label(base_input_frame, text="Mot de passe",
                      bg='white', fg="black").pack()
pass_dbsource_in = Entry(base_input_frame, show="*",
                         bg='white', fg="black", textvariable=db_input_pass).pack()

# Connection base de donnée output

base_output_frame = LabelFrame(
    frame_in, text="Base de donnée sortie", bg='white', fg="black")
label_dbout = Label(
    base_output_frame, text="Nom de la base de donnée sortant", bg='white', fg="black").pack()
base_input_dbout = Entry(base_output_frame, bg='white',
                         fg="black", textvariable=db_output).pack()
user_dbout = Label(base_output_frame, text="Nom d'utilisateur",
                   bg='white', fg="black").pack()
user_dbout_in = Entry(base_output_frame, bg='white',
                      fg="black", textvariable=db_output_user).pack()
pass_dbout = Label(base_output_frame, text="Mot de passe",
                   bg='white', fg="black").pack()
pass_dbout_in = Entry(base_output_frame, show="*", bg='white',
                      fg="black", textvariable=db_output_pass).pack()
base_input_frame.grid(row=0, column=0, pady=55, padx=5, ipadx=5, ipady=5)
base_output_frame.grid(row=0, column=1, ipadx=5, ipady=5)
frame_in.pack()

# Evenement


def logout(*args):
    data_save.execute("DELETE FROM log_info WHERE id=1")
    base.commit()
    data_connect_window.config(menu=NONE)
    connect_frame.pack(fill=BOTH, expand=TRUE)
    main_frame.forget()


def onglet_1(event):
    frame_bar_2.forget()
    frame_bar_1.pack(fill=BOTH, expand=TRUE)
    bar_1.config(bg="white", fg="black", activebackground="white",
                 activeforeground="black")
    bar_2.config(bg="black", fg="white", activebackground="grey",
                 activeforeground="white")


def onglet_2(event):
    frame_bar_1.forget()
    frame_bar_2.pack(fill=BOTH, expand=TRUE)
    bar_1.config(bg="black", fg="white", activebackground="grey",
                 activeforeground="white")
    bar_2.config(bg="white", fg="black", activebackground="white",
                 activeforeground="black")


def migration(*args):
    btn.pack_forget()
    it=0
    info= Label(text=f"Veuillez patienter svp! {it} ms")
    info.pack(pady=30)
    def load_migration():
        cursor = base_input.cursor()
        cursor.execute("""SELECT DISTINCT gid FROM res_groups_users_rel """)
        result = cursor.fetchall()
        names8 = []
        id8 = [x[0] for x in result]
        for ident in id8:
            cursor.execute(f"""SELECT name from res_groups where id = {ident} """)
            result = cursor.fetchone()
            name = result[0]
            if "'" in name:
                name = name.replace("'", "''")
            names8.append(name)

        cursor2 = base_output.cursor()
        id12 = []
        for name in names8:
            cursor2.execute(
                f"""SELECT id FROM res_groups WHERE name = '{name}' """)
            id = cursor2.fetchone()
            id = id[0]
            id12.append(id)

        groups_users = []


        cursor.execute(f""" SELECT DISTINCT uid FROM res_groups_users_rel """)
        users_id = cursor.fetchall()
        for user_id in users_id:
            user_id = user_id[0]
            obj = {}
            obj['user'] = user_id
            cursor.execute(
                f"""SELECT gid FROM res_groups_users_rel WHERE uid = {user_id} """)
            groups_id = cursor.fetchall()
            newResult = []
            for group_id in groups_id:
                newResult.append(group_id[0])
            obj['groups'] = newResult
            groups_users.append(obj)
        it=0
        for ligne in groups_users:
            if ligne['user'] == 1:
                ligne['user'] = 2
            else:
                ligne['user'] += 5
            
            for group in ligne['groups']:
                it+=1
                info["text"] = f"Veuillez patienter svp! {it} ms"
                try:
                    index = id8.index(group)
                    cursor2.execute(
                        "INSERT INTO res_groups_users_rel VALUES (%s,%s)", (id12[index], ligne['user']))
                except psycopg2.IntegrityError:
                    base_output.rollback()
                else:
                    base_output.commit()

                cursor2.execute(f"""SELECT DISTINCT uid from res_groups_users_rel""")
                uid = cursor2.fetchall()
                for id_user in uid:
                    id_user = id_user[0]
                    try:
                        cursor2.execute(
                            "INSERT INTO res_groups_users_rel VALUES(%s,%s)", (1, id_user))
                    except psycopg2.IntegrityError:
                        base_output.rollback()
                    else:
                        base_output.commit()
        messagebox.showinfo("Felicitation","Migration terminé sans erreur")
        info.pack_forget()
        btn.pack(pady=30)

    th= Thread(target=load_migration)
    th.start()

def validation(*args):
    base= connect("data")
    data_save= base.cursor()
    data_save.execute("SELECT * FROM log_info")
    log= data_save.fetchone()
    if log == None:
        try:
            data_save.execute(f"INSERT INTO log_info VALUES (1,'{db_input.get()}','{db_input_user.get()}','{db_input_pass.get()}','{db_output.get()}','{db_output_user.get()}','{db_output_pass.get()}')")
            base.commit()
        except Exception as e:
            messagebox.showerror("Log file error",e)
    else:
        db_input.set(log[1])
        db_input_user.set(log[2])
        db_input_pass.set(log[3])
        db_output.set(log[4])
        db_output_user.set(log[5])
        db_output_pass.set(log[6])
    try:
        global base_input
        global base_output
        base_input = psycopg2.connect(
            host="localhost",
            database=db_input.get(),
            user=db_input_user.get(),
            password=db_input_pass.get()
        )
        base_output = psycopg2.connect(
            host="localhost",
            database=db_output.get(),
            user=db_output_user.get(),
            password=db_output_pass.get()
        )
        data_connect_window.title("Activations droits d'accés pour Odoo")
        connect_frame.forget()

        # creation menu
        global main_menu
        main_menu = Menu(data_connect_window, bg="white", fg="black", relief=FLAT,
                        activebackground="white", activeforeground="black", font=("Arial", 9))
        sub_menu = Menu(main_menu, tearoff=0, bg="white", fg="black", relief=FLAT,
                        activebackground="grey", activeforeground="black", font=("Arial", 9))
        sub_menu.add_command(label="Changer de base de donnée", command=logout)
        sub_menu.add_command(label="Fermer", command=data_connect_window.quit)
        main_menu.add_cascade(label="Option", menu=sub_menu)
        data_connect_window.config(menu=main_menu)

        # creation onglet

        global bar_1
        global bar_2
        bar_1 = Button(frame_bar, text="Verification droit", width=36, highlightthickness=0, relief=FLAT,
                    background="white", fg="black", activebackground="white", activeforeground="black")
        bar_1.bind('<Button-1>', onglet_1)
        bar_2 = Button(frame_bar, text="Migration droit", width=36, highlightthickness=0,
                    relief=FLAT, activebackground="grey", activeforeground="black")
        bar_2.bind('<Button-1>', onglet_2)
        bar_1.pack(side=LEFT, anchor=NW)
        bar_2.pack(side=LEFT, anchor=NE)
        frame_bar.pack()
        frame_bar_1.pack(fill=BOTH, expand=TRUE)

        # onglet_1 (affiche droit)
        bdd_frame = LabelFrame(
            frame_bar_1, text="Base de donnée", bg="white", fg="black")
        choice = StringVar()
        base1 = Radiobutton(bdd_frame, text=db_input.get(), bg="white", fg="black", activebackground="white",
                            activeforeground="black", highlightthickness=0, border=0, variable=choice, value=db_input.get())
        base2 = Radiobutton(bdd_frame, text=db_output.get(), bg="white", fg="black", activebackground="white",
                            activeforeground="black", highlightthickness=0, border=0, variable=choice, value=db_output.get())
        bdd_frame.place(x=13, y=13)
        user_input = tkinter_pro.Combobox(
            frame_bar_1, width=33, textvariable=user_in)
        valide = Button(frame_bar_1, text="Voir")
        group_input = Listbox(frame_bar_1, width=35, bg="white", fg="black")

        def base(event):
            if choice.get() == db_input.get():
                data_db = base_input.cursor()
                data_db.execute(
                    "SELECT * FROM res_groups_users_rel ORDER BY uid")
                data_res = data_db.fetchall()

                user_ = []
                for data in data_res:
                    users = [data[1]]
                    for us in users:
                        if us in user_:
                            pass
                        else:
                            user_.append(us)
                            user_input.delete(0, END)
                            group_input.delete(0, END)
                for user in user_:
                    data_db.execute(
                        f"SELECT login,partner_id FROM res_users WHERE id = {user}")
                    res = data_db.fetchone()
                    login = res[0]
                    partner_id = res[1]
                    data_db.execute(
                        f"SELECT name FROM res_partner WHERE id = {partner_id}")
                    name = data_db.fetchone()
                    # listes des groupes
                    group_user = {}
                    group_id = []
                    name = name[0]+f" [ {user} ]"
                    if name in user_input['values']:
                        pass
                    else:
                        user_input['values'] += (str(name),)

                valide.focus()
                user_input.pack()

                def view_access(*args):
                    if group_input.get(END) == "":
                        if user_in.get() != "":
                            name = user_in.get()
                            user = name[-5:-2]
                            user = user.replace("[", "")
                            user = int(user.strip())

                        for group in data_res:
                            if group[1] == user:
                                group_id.append(str(group[0]))
                                group_user[name] = group_id

                        for name, groups in group_user.items():
                            for group in groups:
                                data_db.execute(
                                    f"SELECT name FROM res_groups WHERE id = {group}")
                                group_name = data_db.fetchone()
                                group_name = f"[ id => {group}] "+group_name[0]
                                group_input.insert(END, group_name)

                valide.bind('<Button-1>', view_access)
                group_input.pack(pady=10)
                valide.pack(pady=10)

            elif choice.get() == db_output.get():
                data_db = base_output.cursor()
                data_db.execute(
                    "SELECT * FROM res_groups_users_rel ORDER BY uid")
                data_res = data_db.fetchall()

                user_ = []
                for data in data_res:
                    users = [data[1]]
                    for us in users:
                        if us in user_:
                            pass
                        else:
                            user_.append(us)
                            user_input.delete(0, END)
                            group_input.delete(0, END)

                for user in user_:
                    data_db.execute(
                        f"SELECT login,partner_id FROM res_users WHERE id = {user}")
                    res = data_db.fetchone()
                    login = res[0]
                    partner_id = res[1]
                    data_db.execute(
                        f"SELECT name FROM res_partner WHERE id = {partner_id}")
                    name = data_db.fetchone()
                    # listes des groupes
                    group_user = {}
                    group_id = []
                    name = name[0]+f" [ {user} ]"
                    if name in user_input['values']:
                        pass
                    else:
                        user_input['values'] += (str(name),)

                    for group in data_res:
                        if group[1] == user:
                            group_id.append(str(group[0]))
                            group_user[name] = group_id
                valide.focus()
                user_input.pack()

                def view_access(event):
                    if group_input.get(END) == "":
                        if user_in.get() != "":
                            name = user_in.get()
                            user = name[-5:-2]
                            user = user.replace("[", "")
                            user = int(user.strip())

                        for group in data_res:
                            if group[1] == user:
                                group_id.append(str(group[0]))
                                group_user[name] = group_id

                        for name, groups in group_user.items():
                            for group in groups:
                                data_db.execute(
                                    f"SELECT name FROM res_groups WHERE id = {group}")
                                group_name = data_db.fetchone()
                                group_name = f"[ id => {group}] "+group_name[0]
                                group_input.insert(END, group_name)

                valide.bind('<Button-1>', view_access)
                group_input.pack(pady=10)
                valide.pack(pady=10)

        def base_choice(event):
            main_frame.pack_forget()
            user_input.delete(0, END)
            group_input.delete(0, END)
            label = Label(frame_bar_1, text="Nom d'utilisateur",
                        bg="white", fg="black").pack(pady=10)
            user_input['values'] = ""

            user_input.bind('<Button-1>', base)
            user_input.pack()
            valide.pack(pady=10)
            main_frame.focus()
            label_ = Label(frame_bar_1, text="Droit d'access",
                        bg="white", fg="black").pack()
            group_input.pack(pady=10)
            main_frame.pack(fill=BOTH, expand=TRUE)

        base1.bind('<Button-1>', base_choice)
        base2.bind('<Button-1>', base_choice)
        base1.pack(anchor=NW)
        base2.pack(anchor=SW)

        main_frame.pack(fill=BOTH, expand=TRUE)
        bdd_frame.place(x=13, y=13)

        # onglet 2 (Migration droit)
        global btn
        btn = Button(frame_bar_2, text="Migrer les données", command=migration)
        btn.pack(pady=30)

    except Exception as e:
        messagebox.showerror("Connexion echouer", e)

# Bouton de validation

data_save.execute("SELECT * FROM log_info")
log= data_save.fetchone()
if log == None:
    frame_validate = Frame(connect_frame, bg="white")
    btn_validate = tkinter_pro.Button(frame_validate, text="Connect",command=validation)
    btn_validate.grid(row=0, column=0, ipadx=4, ipady=4)
    btn_quit = tkinter_pro.Button(frame_validate, text="Quitter", command=data_connect_window.quit).grid(
        row=0, column=1, ipadx=4, ipady=4)
    frame_validate.pack()

    # frame

    connect_frame.pack(fill=BOTH, expand=TRUE)
else:
    validation()

data_connect_window.mainloop()
