import tkinter as tk
import numpy as np
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Treeview, Scrollbar, Style
import pandas as pd
import matplotlib.pyplot as plt
import locale
from matplotlib import ticker

def import_excel():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if file_path:
        try:
            df = pd.read_excel(file_path, header=5)
            df = df.iloc[:-1]
            
            df['Date'] = pd.to_datetime(df['Date'])
            df['City'] = df['City'].astype(str)

            x = df["Date"]
            years = sorted(x.dt.year.unique())
            months = sorted(x.dt.month.unique())
            cities = sorted(df["City"].unique())
            year_combobox['values'] = ['All'] + [str(year) for year in years]
            month_combobox['values'] = ['All'] + [str(month) for month in months]
            city_combobox['values'] = ['All'] + cities
            year_combobox.set('All')
            month_combobox.set('All')
            city_combobox.set('All')
        except Exception as e:
            print(f"Error importing file: {e}")

def filter_data():
    global df
    selected_year = year_combobox.get()
    selected_month = month_combobox.get()
    selected_city = city_combobox.get()
    donor_name = donor_name_entry.get().strip()

    if df is not None:
        filtered_data = df.copy()
        if selected_year != 'All':
            selected_year = int(selected_year)
            filtered_data = filtered_data[pd.to_datetime(filtered_data["Date"]).dt.year == selected_year]
        if selected_month != 'All':
            selected_month = int(selected_month)
            filtered_data = filtered_data[pd.to_datetime(filtered_data["Date"]).dt.month == selected_month]
        if selected_city != 'All':
            filtered_data = filtered_data[filtered_data["City"] == selected_city]
        if donor_name:
            filtered_data = filtered_data[filtered_data["Donor Name"].str.contains(donor_name, case=False, na=False)]
        else:
            filtered_data = filtered_data

        show_filtered_data_window(filtered_data)


def show_filtered_data_window(data):
    new_window = tk.Toplevel(root)
    new_window.title("Filtered Data")

    treeview = Treeview(new_window, columns=list(data.columns), show="headings")
    for col in data.columns:
        treeview.heading(col, text=col)
        treeview.column(col, anchor='center')
    for row in data.itertuples(index=False):
        treeview.insert("", "end", values=row)

    treeview.pack(pady=10, fill="both", expand=True)

    xscroll = Scrollbar(new_window, orient="horizontal", command=treeview.xview)
    xscroll.pack(side="bottom", fill="x", anchor="w")
    yscroll = Scrollbar(new_window, orient="vertical", command=treeview.yview)
    yscroll.pack(side="right", fill="y", anchor="w")

    treeview.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)

    export_button = tk.Button(new_window, text="Export to Excel", command=lambda: export_to_excel(data))
    export_button.pack(pady=5)

def export_to_excel(data):
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx;*.xls")])
    if file_path:
        try:
            data.to_excel(file_path, index=False)
            messagebox.showinfo("Export Successful", f"Filtered data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export data: {e}")

locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')

def bar_chart_yearly():
    df['Year'] = pd.to_datetime(df['Date']).dt.year
    city_data = df.groupby('Year')['Amount'].sum().reset_index()

    locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')
    fig, ax = plt.subplots(figsize=(10, 8))
    
    bars = ax.bar(city_data['Year'], city_data['Amount'])
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Amount Donated')
    ax.set_title('Total Amount Donated Every Year')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    for bar in bars:
        height = bar.get_height()
        formatted_height = locale.format_string("%d", height, grouping=True)
        ax.text(bar.get_x() + bar.get_width() / 2, height, formatted_height, ha='center', va='bottom')
    plt.show()

def table_city():
    global df
    if df is not None:
        city_data = df.groupby('City')['Amount'].sum().reset_index()
        city_data = city_data.dropna(subset=['City'])
        city_data = city_data[city_data['City'] != 'nan'] 
        city_data = city_data.sort_values(by='Amount', ascending=False)
        new_window = tk.Toplevel(root)
        new_window.title("City Donation Table")
        treeview = Treeview(new_window, columns=["City", "Total Donation"], show="headings")
        treeview.heading("City", text="City")
        treeview.heading("Total Donation", text="Total Donation")
        for index, row in city_data.iterrows():
            amount_str = locale.currency(row['Amount'], grouping=True)
            treeview.insert("", "end", values=(row['City'], amount_str))
        treeview.pack(pady=10, fill="both", expand=True)
        export_button = tk.Button(new_window, text="Export to Excel", command=lambda: export_to_excel(city_data))
        export_button.pack(pady=5)

def pie_chart_city():
    global df
    if df is not None:
        city_data = df.groupby('City')['Amount'].sum().reset_index()
        city_data = city_data.dropna(subset=['City'])
        city_data = city_data[city_data['City'] != 'nan'] 
        city_data = city_data.sort_values(by='Amount', ascending=False)
        total_amount = city_data['Amount'].sum()
        new_city_data = city_data[city_data['Amount'] >= 0.01 * total_amount]
        new_city_data.sort_values(by='Amount', ascending=True, inplace=True)

        labels = new_city_data['City']
        sizes = new_city_data['Amount']
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

        fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)

        ax.set_title('Amount of Donations Received by Various Cities')
        
        #Indian currency display
        def autopct_format(values):
            def my_format(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                formatted_val = locale.format_string("%d", val, grouping=True)
                return f'{pct:.1f}%\n({formatted_val})'
            return my_format

        autotexts = [autotexts[i] for i in range(len(autotexts))]
        for autotext in autotexts:
            autotext.set_fontsize(10)

        ax.legend(wedges, labels, title="City Donations", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        plt.show()

def bar_graph_donation_ranges():
    ranges = [(0, 10000), (10001, 25000), (25001, 50000), (50001, 100000),(100001,500000),(500001,1000000),(1000001,5000000),(5000001,np.inf)]
    list1=[]
    
    for lower_bound, upper_bound in ranges:
        filtered_data = df[(df['Amount'] >= lower_bound) & (df['Amount'] <= upper_bound)]
        filtered_data['Range'] = f'{lower_bound} to {upper_bound}'
        count = len(filtered_data)
        list1.append(count)
    max1=max(list1)
    list2=list1.copy()
    list2.remove(max1)
    max2=max(list2)
    x=['0-10,000','10,000-25,000','25,000-50,000','50,000-1,00,000','1,00,000-5,00,000','5,00,000-10,00,000','10,00,000-50,00,000','>50,00,000']
    y=list1
    for i in range(len(list1)):
      if list1[i]==max1:
        i1=i
      if list1[i]==max2:
        i2=i
    colors=[]
    for i in range(len(list1)-1):
      colors.append('blue')
    colors[i1]='red'
    colors[i2]='orange'
    plt.barh(x,y,color=colors)
    xticks = np.linspace(0,max1+15,6)
    plt.xticks(xticks)
    
    sum1=sum(list1)
    for i, v in enumerate(y):
        a=v*100/sum1
        plt.text(v + 1, i, f'{a:.1f}%', color='blue', va='center')

    plt.title("Number of donors in a particular range")
    plt.xlabel("Number of donors")
    plt.ylabel("Range of donations")
    plt.show()
    

def range_check(n):
    ranges = [(0, 10000), (10001, 25000), (25001, 50000), (50001, 100000),
              (100001, 500000), (500001, 1000000), (1000001, 5000000), (5000001, np.inf)]
    for lower_limit, upper_limit in ranges:
        if lower_limit <= n <= upper_limit:
            return f'{lower_limit} to {upper_limit}' if upper_limit != np.inf else f'>={lower_limit}'

def table_donation_ranges():
    city_data = df.groupby('Donor Name')['Amount'].sum().reset_index()
    city_data = city_data.dropna(subset=['Donor Name'])
    city_data = city_data[city_data['Donor Name'] != 'nan']
    city_data = city_data.sort_values(by='Amount', ascending=False)
    city_data['Range'] = city_data['Amount'].apply(range_check)
    new_window = tk.Toplevel(root)
    new_window.title("Donation Range Table")
    
    treeview = Treeview(new_window, columns=["Donor Name", "Total Donation", "Range"], show="headings")
    treeview.heading("Donor Name", text="Donor Name")
    treeview.heading("Total Donation", text="Total Donation")
    treeview.heading("Range", text="Range")
    
    for index, row in city_data.iterrows():
        treeview.insert("", "end", values=(row['Donor Name'], locale.currency(row['Amount'], grouping=True), row['Range']))
    
    treeview.pack(pady=10, fill="both", expand=True)
    export_button = tk.Button(new_window, text="Export to Excel", command=lambda: export_to_excel(city_data))
    export_button.pack(pady=5)

def table_purpose_of_donation():
    global df
    if df is not None:
        city_data = df.groupby('Remarks')['Amount'].sum().reset_index()
        city_data = city_data.dropna(subset=['Remarks'])
        city_data = city_data[city_data['Remarks'] != 'nan'] 
        city_data = city_data.sort_values(by='Amount', ascending=False)
        new_window = tk.Toplevel(root)
        new_window.title("Purpose of Donation Table")
        treeview = Treeview(new_window, columns=["Purpose of Donation", "Total Donation"], show="headings")
        treeview.heading("Purpose of Donation", text="Purpose of Donation")
        treeview.heading("Total Donation", text="Total Donation")
        for index, row in city_data.iterrows():
            amount_str = locale.currency(row['Amount'], grouping=True)
            treeview.insert("", "end", values=(row['Remarks'], amount_str))
        treeview.pack(pady=10, fill="both", expand=True)
        city_data = city_data.rename(columns={'Donation': 'Purpose of Donation', 'Total Amount': 'Total Amount'})
        export_button = tk.Button(new_window, text="Export to Excel", command=lambda: export_to_excel(city_data))
        export_button.pack(pady=5)

def pie_chart_purpose_of_donation():
    if df is not None:
        city_data = df.groupby('Remarks')['Amount'].sum().reset_index()
        city_data = city_data.dropna(subset=['Remarks'])
        city_data = city_data[city_data['Remarks'] != 'nan'] 
        city_data = city_data.sort_values(by='Amount', ascending=False)
        total_amount = city_data['Amount'].sum()
        new_city_data = city_data[city_data['Amount'] >= 0.01 * total_amount]
        new_city_data.sort_values(by='Amount', ascending=True, inplace=True)

        labels = new_city_data['Remarks']
        sizes = new_city_data['Amount']
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

        fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)

        ax.set_title('Amount of Donations Received for various Purposes')
        
        #Indian currency display
        def autopct_format(values):
            def my_format(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                formatted_val = locale.format_string("%d", val, grouping=True)
                return f'{pct:.1f}%\n({formatted_val})'
            return my_format

        autotexts = [autotexts[i] for i in range(len(autotexts))]
        for autotext in autotexts:
            autotext.set_fontsize(10)

        plt.show()


def pie_chart_payment_method():
    city_data = df.groupby('Payment Mode')['Amount'].sum().reset_index()
    city_data = city_data.dropna(subset=['Payment Mode'])
    total_amount = city_data['Amount'].sum()
    new_city_data = city_data[city_data['Amount'] >= 0.01 * total_amount]

    new_city_data.sort_values(by='Amount', ascending=True, inplace=True)
    labels = new_city_data['Payment Mode']
    sizes = new_city_data['Amount']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    ax.set_title('Differne Payment Methods')
    
    #Indian currency display
    def autopct_format(values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            formatted_val = locale.format_string("%d", val, grouping=True)
            return f'{pct:.1f}%\n({formatted_val})'
        return my_format
    autotexts = [autotexts[i] for i in range(len(autotexts))]
    for autotext in autotexts:
        autotext.set_fontsize(10)
    plt.show()

def pie_chart_donation_by():
    donation_by = df.groupby('Donation By')['Amount'].sum().reset_index()
    labels = donation_by['Donation By']
    sizes = donation_by['Amount']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    ax.set_title('Donation By')
    
    #Indian currency display
    def autopct_format(values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            formatted_val = locale.format_string("%d", val, grouping=True)
            return f'{pct:.1f}%\n({formatted_val})'
        return my_format
    autotexts = [autotexts[i] for i in range(len(autotexts))]
    for autotext in autotexts:
        autotext.set_fontsize(10)
    plt.show()

def get_contact(name):
    contact = df.loc[df['Donor Name'] == str(name), 'Contact No']
    return ', '.join(contact.dropna().astype(str).unique()) if not contact.empty else None

def get_purpose(name):
    purpose = df.loc[df['Donor Name'] == str(name), 'Remarks']
    return ', '.join(purpose.dropna().astype(str).unique()) if not purpose.empty else None

def table_indivisual_donation():
    data = df.loc[df['Donation By']=='Individual',:].groupby('Donor Name')['Amount'].sum().reset_index()
    data = data.sort_values(by='Amount', ascending=False)
    data['Contact No'] = data['Donor Name'].apply(get_contact)
    data['Purpose'] = data['Donor Name'].apply(get_purpose)
    new_window = tk.Toplevel(root)
    new_window.title('Amount Donated by Indivisuals')
    treeview = Treeview(new_window, columns=['Donor Name', 'Amount', 'Contact No', 'Purpose'], show='headings')
    treeview.heading('Donor Name', text='Donor Name')
    treeview.heading('Amount', text='Amount')
    treeview.heading('Contact No', text='Contact No')
    treeview.heading('Purpose', text='Purpose')
    for index, row in data.iterrows():
        amount_str = locale.currency(row['Amount'], grouping=True)
        treeview.insert("", "end", values=(row['Donor Name'], amount_str, row['Contact No'], row['Purpose']))
    treeview.pack(pady=10, fill="both", expand=True)
    export_button = tk.Button(new_window, text="Export to Excel", command=lambda: export_to_excel(data))
    export_button.pack(pady=5)
    
def load_and_print_data():
    global df
    df = import_excel()
    if df is not None:
        for widget in plot_frame.winfo_children():
            widget.destroy()



root = tk.Tk()
root.title("Data Analysis Andhjan Mandal")

root.iconphoto(False, tk.PhotoImage(file=r"icon.png"))

style = Style()
style.configure("TButton", font=("Arial", 12))
style.configure("TLabel", font=("Arial", 12))

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

import_button = tk.Button(frame, text="Import Excel File", command=lambda: import_excel())
import_button.grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(frame, text='Filter', font=("Arial",20, "bold")).grid(row=1, column=0, columnspan=2, pady=10)

tk.Label(frame, text="Filter by Year:").grid(row=2, column=0, sticky="w")
year_combobox = Combobox(frame, state="readonly")
year_combobox.grid(row=2, column=1, pady=3)

tk.Label(frame, text="Filter by Month:").grid(row=3, column=0, sticky="w")
month_combobox = Combobox(frame, state="readonly")
month_combobox.grid(row=3, column=1, pady=3)

tk.Label(frame, text="Filter by City:").grid(row=4, column=0, sticky="w")
city_combobox = Combobox(frame, state="readonly")
city_combobox.grid(row=4, column=1, pady=3)

tk.Label(frame, text="Filter by Donor Name:").grid(row=5, column=0, sticky="w")
donor_name_entry = tk.Entry(frame)
donor_name_entry.grid(row=5, column=1, pady=3)

filter_button = tk.Button(frame, text="Filter Data", command=lambda: filter_data())
filter_button.grid(row=6, column=0, columnspan=2, pady=5)

tk.Label(frame, text='Create Graphs', font=("Arial",20, "bold")).grid(row=7, column=0, columnspan=2, pady=15)

tk.Button(frame, text="Yearly Donations Bar Chart", command=lambda: bar_chart_yearly()).grid(row=8, column=0, columnspan=2, pady=3)
tk.Button(frame, text="Donation Ranges Bar Graph", command=lambda: bar_graph_donation_ranges()).grid(row=9, column=0, columnspan=2, pady=3)
tk.Button(frame, text="Donations from different cities Pie Chart", command=lambda: pie_chart_city()).grid(row=10, column=0, columnspan=2, pady=3)
tk.Button(frame, text="Purpose of Donation Pie Chart", command=lambda: pie_chart_purpose_of_donation()).grid(row=11, column=0, columnspan=2, pady=3)
tk.Button(frame, text="Donation By(Indivisual/Corporate) Pie Chart", command=lambda: pie_chart_donation_by()).grid(row=12, column=0, columnspan=2, pady=3)
tk.Button(frame, text="Donations received by different payment methods Pie Chart", command=lambda: pie_chart_payment_method()).grid(row=13, column=0, columnspan=2, pady=3)
df=None

tk.Label(frame, text='Create Tables', font=("Arial",20, "bold")).grid(row=14, column=0, columnspan=2, pady=15)

tk.Button(frame, text="Donations from different Cities", command=lambda: table_city()).grid(row=15, column=0, pady=3,columnspan=2)
tk.Button(frame, text="Donation in different Donation Ranges", command=lambda: table_donation_ranges()).grid(row=16, column=0, pady=3,columnspan=2)
tk.Button(frame, text="Donations received from Indivisuals", command=lambda: table_indivisual_donation()).grid(row=17, column=0, pady=3,columnspan=2)
tk.Button(frame, text="Purpose of Donation", command=lambda: table_purpose_of_donation()).grid(row=18, column=0, pady=3,columnspan=2)

plot_frame = tk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)

copyright_label = tk.Label(root, text="© 2024 Sneh Soni & Dhrumil Sheth. All rights reserved.", font=("Arial", 10))
copyright_label.pack(side="bottom", fill="x", pady=5)

root.mainloop()