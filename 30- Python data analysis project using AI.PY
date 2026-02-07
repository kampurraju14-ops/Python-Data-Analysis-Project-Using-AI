# Day 30- Python data analysis project using AI
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DataAnalyzerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Corporate Data Analysis Tool")
        self.root.geometry("1200x750")

        self.df = None
        self.report_df = None
        self.file_path = None
        self.chart_canvas = None

        self.create_widgets()

    # ================= GUI LAYOUT =================
    def create_widgets(self):
        title = tk.Label(self.root, text="Corporate Data Analysis Software",
                         font=("Arial", 18, "bold"))
        title.pack(pady=10)

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5)

        tk.Button(top_frame, text="Browse File", command=self.browse_file, width=15).grid(row=0, column=0, padx=5)
        tk.Button(top_frame, text="Read", command=self.read_file, width=10).grid(row=0, column=1, padx=5)

        self.file_label = tk.Label(self.root, text="No file selected", fg="blue")
        self.file_label.pack()

        self.info_label = tk.Label(self.root, text="")
        self.info_label.pack(pady=5)

        # Controls Frame
        control_frame = tk.LabelFrame(self.root, text="Report Builder", padx=10, pady=10)
        control_frame.pack(fill="x", padx=10)

        tk.Label(control_frame, text="Group By").grid(row=0, column=0)
        self.group_col = ttk.Combobox(control_frame, state="readonly", width=20)
        self.group_col.grid(row=0, column=1, padx=5)

        tk.Label(control_frame, text="Aggregation").grid(row=0, column=2)
        self.agg_func = ttk.Combobox(control_frame, state="readonly", width=15,
                                     values=["sum", "mean", "max", "min", "count", "median"])
        self.agg_func.grid(row=0, column=3, padx=5)

        tk.Label(control_frame, text="Value Column").grid(row=0, column=4)
        self.value_col = ttk.Combobox(control_frame, state="readonly", width=20)
        self.value_col.grid(row=0, column=5, padx=5)

        tk.Button(control_frame, text="Preview Report", command=self.generate_report).grid(row=0, column=6, padx=5)
        tk.Button(control_frame, text="Export Report", command=self.export_report).grid(row=0, column=7, padx=5)

        # Chart Builder
        chart_frame = tk.LabelFrame(self.root, text="Chart Builder", padx=10, pady=10)
        chart_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(chart_frame, text="Chart Type").grid(row=0, column=0)
        self.chart_type = ttk.Combobox(chart_frame, state="readonly", width=15,
                                       values=["Bar", "Column", "Line", "Pie"])
        self.chart_type.grid(row=0, column=1, padx=5)

        tk.Button(chart_frame, text="Preview Chart", command=self.generate_chart).grid(row=0, column=2, padx=5)
        tk.Button(chart_frame, text="Export Chart", command=self.export_chart).grid(row=0, column=3, padx=5)

        # Report Table
        self.tree = ttk.Treeview(self.root)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ================= FILE HANDLING =================
    def browse_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV & Excel", "*.csv *.xlsx *.xls")])
        if self.file_path:
            self.file_label.config(text=self.file_path)

    def read_file(self):
        if not self.file_path:
            messagebox.showerror("Error", "Please select a file first.")
            return

        try:
            if self.file_path.endswith(".csv"):
                self.df = pd.read_csv(self.file_path)
            else:
                self.df = pd.read_excel(self.file_path)

            rows, cols = self.df.shape
            self.info_label.config(text=f"Rows: {rows} | Columns: {cols}")

            text_cols = self.df.select_dtypes(include='object').columns.tolist()
            num_cols = self.df.select_dtypes(include='number').columns.tolist()

            self.group_col['values'] = text_cols
            self.value_col['values'] = num_cols

            messagebox.showinfo("Success", "File read successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= REPORT =================
    def generate_report(self):
        if self.df is None:
            messagebox.showerror("Error", "Read the file first.")
            return

        group = self.group_col.get()
        agg = self.agg_func.get()
        value = self.value_col.get()

        if not group or not agg or not value:
            messagebox.showerror("Error", "Please select all dropdown options.")
            return

        self.report_df = self.df.groupby(group)[value].agg(agg).sort_values(ascending=False).reset_index()

        self.display_table(self.report_df)

    def display_table(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        for row in df.to_numpy():
            self.tree.insert("", "end", values=row)

    def export_report(self):
        if self.report_df is None:
            messagebox.showerror("Error", "Generate report first.")
            return

        folder = os.path.dirname(self.file_path)
        save_path = os.path.join(folder, "Report_Output.xlsx")
        self.report_df.to_excel(save_path, index=False)
        messagebox.showinfo("Exported", f"Report saved at {save_path}")

    # ================= CHART =================
    def generate_chart(self):
        if self.report_df is None:
            messagebox.showerror("Error", "Generate report first.")
            return

        chart_type = self.chart_type.get()
        if not chart_type:
            messagebox.showerror("Error", "Select chart type.")
            return

        fig, ax = plt.subplots(figsize=(7, 4))

        x = self.report_df.iloc[:, 0]
        y = self.report_df.iloc[:, 1]

        if chart_type in ["Bar", "Column"]:
            ax.bar(x, y)
        elif chart_type == "Line":
            ax.plot(x, y)
        elif chart_type == "Pie":
            ax.pie(y, labels=x, autopct='%1.1f%%')

        ax.set_title("Report Chart")

        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True)

    def export_chart(self):
        if not self.chart_canvas:
            messagebox.showerror("Error", "Preview chart first.")
            return

        folder = os.path.dirname(self.file_path)
        save_path = os.path.join(folder, "Chart_Output.png")
        self.chart_canvas.figure.savefig(save_path)
        messagebox.showinfo("Exported", f"Chart saved at {save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DataAnalyzerApp(root)
    root.mainloop()
