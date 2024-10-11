from opencc import OpenCC

text_CC = OpenCC("s2twp")

file_path = input("請輸入檔案路徑：")
with open(file_path, "rw", encoding="utf-8") as f:
    text = f.read()
    text = text_CC.convert(text)
    text = f.write(text)
