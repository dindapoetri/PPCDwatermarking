import cv2 as cv
import numpy as np
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

# Inisialisasi jendela utama Tkinter
root = Tk()
root.config(background="light blue")
root.title("Watermarking DCT")

# Mendapatkan ukuran layar dan menyesuaikan posisi jendela
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 1180
window_height = 520
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Membuat canvas dengan scrollbar
canvas = Canvas(root, background="cyan2", scrollregion=(0, 0, 1000, 1000))
scrollbar_y = Scrollbar(root, orient=VERTICAL, command=canvas.yview)
scrollbar_x = Scrollbar(root, orient=HORIZONTAL, command=canvas.xview)
scrollable_frame = Frame(canvas, background="light blue")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

canvas.grid(row=0, column=0, sticky="nsew")
scrollbar_y.grid(row=0, column=1, sticky="ns")
scrollbar_x.grid(row=1, column=0, sticky="ew")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Tabel utama untuk menempatkan tabel pertama, tabel kedua, dan tombol Apply
frame_main = Frame(scrollable_frame, background="light blue")
frame_main.grid(row=3, column=0, columnspan=3, pady=10, sticky=NSEW)

# Tabel pertama untuk menampilkan gambar original
frame_original_img = Frame(frame_main, background="light blue", relief="sunken", borderwidth=3)
frame_original_img.grid(row=0, column=0, padx=5, pady=10, sticky=NSEW)
Label(frame_original_img, text="Original Image", background="light blue").pack()
label_original_img = Label(frame_original_img, background="light blue")
label_original_img.pack(padx=5, pady=50)

# Tabel kedua untuk menampilkan gambar watermark
frame_watermark_img = Frame(frame_main, background="light blue", relief="sunken", borderwidth=3)
frame_watermark_img.grid(row=0, column=1, padx=5, pady=10, sticky=NSEW)
Label(frame_watermark_img, text="Watermark Image", background="light blue").pack()
label_watermark_img = Label(frame_watermark_img, background="light blue")
label_watermark_img.pack(padx=5, pady=50, fill=BOTH, expand=True)

# Mengatur lebar kolom agar menyesuaikan lebar frame
frame_main.grid_columnconfigure(0, weight=1)
frame_main.grid_columnconfigure(1, weight=1)

# Bagian untuk browse gambar
Label(scrollable_frame, text="Original Image:", font="Normal 14", background="light blue").grid(row=1, column=0, sticky=E)
entry_original = Entry(scrollable_frame, font="Normal 14", background="thistle2", width=40)
entry_original.grid(row=1, column=1, padx=10)
button_original = Button(scrollable_frame, text="Browse", background="thistle3", font="Normal 14", command=lambda: open_image(entry_original, label_original_img))
button_original.grid(row=1, column=2, padx=10)

Label(scrollable_frame, text="Watermark Image:", font="Normal 14", background="light blue").grid(row=2, column=0, sticky=E)
entry_watermark = Entry(scrollable_frame, font="Normal 14", background="thistle2", width=40)
entry_watermark.grid(row=2, column=1, padx=10)
button_watermark = Button(scrollable_frame, text="Browse", background="thistle3", font="Normal 14", command=lambda: open_image(entry_watermark, label_watermark_img))
button_watermark.grid(row=2, column=2, padx=10)

# Tabel untuk menampilkan hasil gambar yang di-watermark
frame_result_img = Frame(scrollable_frame, background="light blue", relief="sunken", borderwidth=6)
frame_result_img.grid(row=6, column=0, columnspan=3, padx=5, pady=10, sticky=NSEW)
Label(frame_result_img, text="Result Image", background="light blue").pack()
label_result_img = Label(frame_result_img, background="light blue")
label_result_img.pack(padx=5, pady=5)

# Tombol Apply Watermark and Show Result
button_apply_and_show_result = Button(scrollable_frame, text="Apply Watermark and Show Result", font="Normal 14", width=113, background="cadetblue1", command=lambda: apply_watermark_and_show_result(label_result_img, label_result))
button_apply_and_show_result.grid(row=7, column=0, columnspan=3, pady=20)
button_apply_and_show_result.config(highlightbackground="light blue")

# Tombol Bandingkan Watermark dengan gambar
button_compare = Button(scrollable_frame, text="Compare Watermark to Modified Image", font="Normal 14", width=113, background="cadetblue1")
button_compare.grid(row=8, column=0, columnspan=3, pady=20)
button_compare.config(highlightbackground="light blue")

# Event binding untuk tombol compare
button_compare.bind("<ButtonPress-1>", lambda event: show_watermark_diff(label_result_img))
button_compare.bind("<ButtonRelease-1>", lambda event: reset_watermark_image(label_result_img))

# Tombol Save Image
button_save_image = Button(scrollable_frame, text="Save Watermarked Image", font="Normal 14", width=113, background="cadetblue1", command=lambda: save_image())
button_save_image.grid(row=9, column=0, columnspan=3, pady=20)
button_save_image.config(highlightbackground="light blue")

# Label untuk menampilkan pesan sukses/gagal
label_result = Label(scrollable_frame, text="", font="Normal 14", background="paleturquoise1")
label_result.grid(row=10, column=0, columnspan=3)

# Label tambahan untuk spasi
spacer_label = Label(scrollable_frame, text="", background="light blue", height=1)
spacer_label.grid(row=11, column=0, columnspan=3)

# Variabel global untuk menyimpan gambar yang di-watermark
global watermarked_img_pil
watermarked_img_pil = None

# Menambahkan fungsi untuk membuka gambar
def open_image(entry, label):
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        entry.delete(0, END)
        entry.insert(0, file_path)
        img = Image.open(file_path)
        img.thumbnail((350, 350))
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk, width=img_tk.width(), height=img_tk.height())
        label.image = img_tk

# Menambahkan fungsi untuk menerapkan watermark
def apply_watermark_and_show_result(result_label, message_label):
    global watermarked_img_pil, watermarked_img_cv
    original_path = entry_original.get()
    watermark_path = entry_watermark.get()

    if not original_path or not watermark_path:
        message_label.config(text="Please select both images.", fg="red")
        return

    try:
        original_img = cv.imread(original_path)
        watermark_img = cv.imread(watermark_path, cv.IMREAD_GRAYSCALE)
        watermark_img = cv.resize(watermark_img, (original_img.shape[1], original_img.shape[0]))

        # Apply DCT and watermark
        original_img = cv.cvtColor(original_img, cv.COLOR_BGR2YCrCb)
        y, cr, cb = cv.split(original_img)
        dct_y = cv.dct(np.float32(y) / 255.0)
        dct_y[:watermark_img.shape[0], :watermark_img.shape[1]] += watermark_img * 0.01
        idct_y = cv.idct(dct_y) * 255.0
        idct_y = np.uint8(np.clip(idct_y, 0, 255))
        watermarked_img_cv = cv.merge((idct_y, cr, cb))
        watermarked_img_cv = cv.cvtColor(watermarked_img_cv, cv.COLOR_YCrCb2BGR)

        watermarked_img_pil = Image.fromarray(cv.cvtColor(watermarked_img_cv, cv.COLOR_BGR2RGB))
        watermarked_img_pil.thumbnail((350, 350))
        watermarked_img_tk = ImageTk.PhotoImage(watermarked_img_pil)

        result_label.config(image=watermarked_img_tk, width=watermarked_img_tk.width(), height=watermarked_img_tk.height())
        result_label.image = watermarked_img_tk
        message_label.config(text="Watermark applied successfully.", fg="green")
    except Exception as e:
        message_label.config(text=f"Error: {str(e)}", fg="red")

# Fungsi untuk menampilkan perbedaan watermark
def show_watermark_diff(result_label):
    global watermarked_img_cv
    if watermarked_img_cv is not None:
        diff_img = cv.absdiff(cv.imread(entry_original.get()), watermarked_img_cv)
        diff_img_pil = Image.fromarray(cv.cvtColor(diff_img, cv.COLOR_BGR2RGB))
        diff_img_pil.thumbnail((350, 350))
        diff_img_tk = ImageTk.PhotoImage(diff_img_pil)
        result_label.config(image=diff_img_tk, width=diff_img_tk.width(), height=diff_img_tk.height())
        result_label.image = diff_img_tk

# Fungsi untuk mereset gambar yang di-watermark
def reset_watermark_image(result_label):
    global watermarked_img_pil
    if watermarked_img_pil is not None:
        watermarked_img_tk = ImageTk.PhotoImage(watermarked_img_pil)
        result_label.config(image=watermarked_img_tk, width=watermarked_img_tk.width(), height=watermarked_img_tk.height())
        result_label.image = watermarked_img_tk

# Fungsi untuk menyimpan gambar yang di-watermark
def save_image():
    global watermarked_img_pil
    if watermarked_img_pil is not None:
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        if save_path:
            watermarked_img_pil.save(save_path)
            label_result.config(text="Image saved successfully.", fg="green")
    else:
        label_result.config(text="No watermarked image to save.", fg="red")

# Menjalankan main loop Tkinter
root.mainloop()